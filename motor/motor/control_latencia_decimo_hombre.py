#!/usr/bin/env python3
"""control_latencia_decimo_hombre.py — CONTROL ESTRUCTURAL del modelo (siempre-on en ejecución) (dinámica)

NO es sidecar ni plugin de contenido.
Es CONTROL ESTRUCTURAL (plano de cierre): corre con el modelo en ejecución,
constante, no «al lado». Polaridad/pregunta son sensores; este módulo decide
si hay datos suficientes para resolver o hay que LATENCIA / décimo hombre / almacén.
NO es un arreglo de archivo para «doble negación».
Es la regla general para NO ATORARSE cuando el corte no cuadra con la ejecución:

1) Lectura momentánea → si hay ambigüedad / empate ≈50% → LATENCIA (no cierre).
2) Se siguen tomando tokens/datos en cortes siguientes.
3) Décimo hombre: si p≈0.5 → se rehace la tirada (desempate).
4) Si sigue empate → ALMACENADO_ESPERANDO_DATOS (no inventar resolución).
5) Cuando hay tokens suficientes y p se separa del 0.5 → se libera la latencia.

Candados: Alimenta_H=NO · no Engine/244/FREEZE. Solo marca estado de proceso.
Polaridad/doble-negación es UN consumidor de esta capa, no el dueño.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

__version__ = "1.0.0-dinamica-20260920"
ALIMENTA_H = "NO"
SOLO_MARCA = True
M_MAX = 0.998  # no cierre 0/100
P_EMPATE = 0.50
BANDA_EMPATE = 0.05  # ~45–55% cuenta como 50%
N_MIN_TOKENS_DEFAULT = 3

HERE = Path(__file__).resolve().parent
STORE = HERE / "estado_latencia_decimo_hombre.json"


def _clip01(x: float) -> float:
    return max(0.0, min(float(x), M_MAX))


def en_banda_empate(p: float, banda: float = BANDA_EMPATE) -> bool:
    return abs(_clip01(p) - P_EMPATE) <= banda


@dataclass
class ExpedienteLatencia:
    clave: str
    tema: str
    estado: str  # LATENCIA | DESEMPATE_DECIMO | ALMACENADO_ESPERANDO_DATOS | RESUELTO | OFF
    p: float
    tokens: List[str] = field(default_factory=list)
    historial_p: List[float] = field(default_factory=list)
    n_desempates: int = 0
    nota: str = ""
    actualizado_ts: float = 0.0
    Alimenta_H: str = "NO"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_store(path: Path = STORE) -> Dict[str, Any]:
    if not path.exists():
        return {"version": __version__, "expedientes": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_store(data: Dict[str, Any], path: Path = STORE) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_from(clave: str, tokens: Sequence[str], n_desempate: int) -> int:
    h = hashlib.sha256(f"{clave}|{'|'.join(tokens)}|{n_desempate}".encode()).hexdigest()
    return int(h[:16], 16)


def decimo_hombre_retira(p: float, clave: str, tokens: Sequence[str], n: int) -> float:
    """Re-tirada de desempate (determinista por clave+tokens+n). No inventa verdad."""
    rng = random.Random(_seed_from(clave, tokens, n))
    # jitter pequeño alrededor de p; si no hay señal, se queda cerca de 0.5
    jitter = rng.uniform(-0.08, 0.08)
    # ligera inclinación por volumen de tokens (más tokens → menos ruido)
    ancla = min(len(tokens), 12) / 12.0
    mezcla = (1 - 0.35 * ancla) * p + (0.35 * ancla) * (0.5 + jitter)
    return _clip01(mezcla)


def actualizar_expediente(
    clave: str,
    *,
    tema: str,
    p_momento: float,
    tokens_nuevos: Optional[Sequence[str]] = None,
    n_min_tokens: int = N_MIN_TOKENS_DEFAULT,
    forzar_desempate_si_empate: bool = True,
    store_path: Path = STORE,
) -> Dict[str, Any]:
    """Paso dinámico: toma p del momento + tokens, aplica latencia/décimo hombre.

    Retorna dict de acción para el modelo (qué hacer AHORA), sin tocar H.
    """
    data = _load_store(store_path)
    exps: Dict[str, Any] = data.setdefault("expedientes", {})
    prev = exps.get(clave) or {}
    tokens = list(prev.get("tokens") or [])
    for t in tokens_nuevos or []:
        t = str(t).strip()
        if t and t not in tokens:
            tokens.append(t)
    historial = list(prev.get("historial_p") or [])
    p0 = _clip01(p_momento)
    historial.append(p0)
    n_des = int(prev.get("n_desempates") or 0)

    # 1) empate ≈50% → décimo hombre
    if forzar_desempate_si_empate and en_banda_empate(p0):
        n_des += 1
        p1 = decimo_hombre_retira(p0, clave, tokens, n_des)
        historial.append(p1)
        if en_banda_empate(p1):
            estado = "ALMACENADO_ESPERANDO_DATOS"
            nota = (
                "Décimo hombre: seguía ~50% tras desempate. "
                "No cerrar. Guardar y seguir tomando tokens."
            )
            p_out = p1
            accion = "ESPERAR_MAS_TOKENS"
        else:
            estado = "DESEMPATE_DECIMO"
            nota = "Décimo hombre separó del 50%. Seguir midiendo; aún no coronar."
            p_out = p1
            accion = "SEGUIR_CON_P_DESEMPATADA"
    # 2) no empate pero pocos tokens → latencia (no confiar del todo)
    elif len(tokens) < n_min_tokens:
        estado = "LATENCIA"
        nota = (
            f"Señal con <{n_min_tokens} tokens: no atorar ni cerrar. "
            "Seguir leyendo trayectoria."
        )
        p_out = p0
        accion = "LATENCIA_ACUMULAR_TOKENS"
    # 3) suficiente separación + tokens → resuelto (marca de proceso, no H)
    elif not en_banda_empate(p0) and len(tokens) >= n_min_tokens:
        estado = "RESUELTO"
        nota = "Tokens suficientes y p fuera de banda 50%. Liberar latencia (solo marca)."
        p_out = p0
        accion = "LIBERAR_LATENCIA"
    else:
        estado = "LATENCIA"
        nota = "Trayectoria en curso."
        p_out = p0
        accion = "MANTENER_LATENCIA"

    exp = ExpedienteLatencia(
        clave=clave,
        tema=tema,
        estado=estado,
        p=p_out,
        tokens=tokens,
        historial_p=[round(x, 4) for x in historial[-24:]],
        n_desempates=n_des,
        nota=nota,
        actualizado_ts=time.time(),
    )
    exps[clave] = exp.to_dict()
    data["version"] = __version__
    data["actualizado_ts"] = time.time()
    _save_store(data, store_path)

    return {
        "capa": "CONTROL_LATENCIA_DECIMO_HOMBRE",
        "rol": "control_estructural_no_sidecar",
        "version": __version__,
        "Alimenta_H": ALIMENTA_H,
        "solo_marca": SOLO_MARCA,
        "accion": accion,
        "expediente": exp.to_dict(),
        "candados": {
            "TOCA_F": "NO",
            "TOCA_244": "NO",
            "TOCA_Engine_V5": "NO",
            "TOCA_FREEZE": "NO",
            "Alimenta_H": "NO",
            "cierre_0_100": "NO",
            "M_MAX": M_MAX,
        },
        "regla": (
            "Ambigüedad/empate → latencia; décimo hombre si ~50%; "
            "si no desempata → almacenar hasta tokens suficientes; dinámico."
        ),
    }


def polaridad_con_latencia(
    texto: str,
    *,
    clave: Optional[str] = None,
    tokens_contexto: Optional[Sequence[str]] = None,
    store_path: Path = STORE,
) -> Dict[str, Any]:
    """Puente: polaridad momentánea → capa dinámica (no atascarse en la etiqueta).

    Doble negación «ya no es doble» cuando tokens posteriores la desambiguan.
    """
    from plugin_polaridad_causal import clasificar_polaridad_causal

    pol = clasificar_polaridad_causal(texto)
    et = pol["etiqueta"]
    # map etiqueta → p momentánea (no probabilidad epistemológica dura)
    if et == "NIEGA":
        p = 0.18
    elif et == "DOBLE_NEGACION_LITOTE":
        p = 0.50  # zona de ambigüedad operativa → latencia/décimo
    elif et == "NEUTRO":
        p = 0.55
    else:
        p = 0.50

    toks = list(tokens_contexto or [])
    # el propio texto aporta tokens crudos baratos
    for w in texto.lower().replace(".", " ").split():
        w = w.strip()
        if len(w) >= 4 and w not in toks:
            toks.append(w)
            if len(toks) >= 12:
                break

    clave = clave or f"polaridad::{hashlib.sha256(texto.encode()).hexdigest()[:12]}"
    dyn = actualizar_expediente(
        clave,
        tema="polaridad_causal",
        p_momento=p,
        tokens_nuevos=toks,
        store_path=store_path,
    )
    return {
        "lectura_momento": pol,
        "dinamica": dyn,
        "interpretacion": (
            "La etiqueta del corte no es sentencia. "
            "Si queda ~50%/litote → LATENCIA y se sigue tomando datos; "
            "décimo hombre si empata; si no se desempató → almacenar."
        ),
        "Alimenta_H": "NO",
    }


if __name__ == "__main__":
    # demo: litote → empate → décimo → (casi siempre) esperar datos
    store = HERE / "estado_latencia_decimo_hombre_DEMO.json"
    if store.exists():
        store.unlink()
    r1 = polaridad_con_latencia(
        "no es que no explica el resultado",
        clave="demo_litote",
        tokens_contexto=["corte_A"],
        store_path=store,
    )
    # más tokens en corte B (desambiguación)
    r2 = actualizar_expediente(
        "demo_litote",
        tema="polaridad_causal",
        p_momento=0.72,  # ya no se ve como 50/50
        tokens_nuevos=["corte_B", "aclara", "de_hecho", "confirma"],
        store_path=store,
    )
    # empate duro persistente
    if store.exists():
        pass
    r3 = actualizar_expediente(
        "demo_empate",
        tema="general",
        p_momento=0.50,
        tokens_nuevos=["t1"],
        store_path=store,
    )
    print(json.dumps({
        "v": __version__,
        "litote_momento": r1["lectura_momento"]["etiqueta"],
        "litote_accion": r1["dinamica"]["accion"],
        "litote_estado": r1["dinamica"]["expediente"]["estado"],
        "tras_mas_tokens_accion": r2["accion"],
        "tras_mas_tokens_estado": r2["expediente"]["estado"],
        "empate_accion": r3["accion"],
        "empate_estado": r3["expediente"]["estado"],
        "Alimenta_H": ALIMENTA_H,
    }, ensure_ascii=False, indent=2))
