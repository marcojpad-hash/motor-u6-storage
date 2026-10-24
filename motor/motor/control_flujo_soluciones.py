#!/usr/bin/env python3
"""control_flujo_soluciones.py — CONTROL de ejecución: agua vs piedra

NO es sidecar de contenido. Es regla de conducta del modelo al ejecutar:

  Obstáculo ≠ drama. Obstáculo = contorno.

Mj: no quiero «no puedo porque el hash no es idéntico», «me faltó una letra»,
«está bloqueado y ya». Quiero la siguiente acción útil, como el agua que
encuentra la piedra y sigue.

Encaja con:
- Notion/hash: verificar, no re-correr lo hecho; si no hay byte-idéntico, buscar equivalente
- control_latencia_decimo_hombre: info insuficiente → esperar/almacenar, no fingir cierre
- candado_plugins: avisa cambio de hash; no convierte todo en muro

Candados: Alimenta_H=NO · no toca Engine/244/FREEZE.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

__version__ = "1.0.0-flujo-20260920"
ALIMENTA_H = "NO"
SOLO_MARCA = True

# Frases que el control debe REESCRIBIR (anti-drama)
_RX_DRAMA = re.compile(
    r"(?i)\b("
    r"no\s+puedo|"
    r"est[aá]\s+bloqueado|"
    r"no\s+encuentro\s+el\s+hash\s+id[eé]ntico|"
    r"me\s+falt[oó]\s+una\s+letra|"
    r"no\s+se\s+puede\s+correr|"
    r"imposible\s+continuar|"
    r"necesito\s+que\s+alguien\s+me\s+resuelva|"
    r"estoy\s+atascad[oa]"
    r")\b"
)

# Catálogo de piedras → contornos (soluciones, no lamentos)
CONTORNOS: Dict[str, Dict[str, Any]] = {
    "hash_no_identico": {
        "piedra": "El hash no coincide byte a byte con el marcado.",
        "contornos": [
            "BYPASS_HASH_CAMBIO: leer y correr igual; el cambio de hash NO bloquea protocolo ni lectura.",
            "Buscar archivo equivalente por nombre/ruta/rol en checkpoint o Notion.",
            "Si hay manifiesto: anotar hash_viejo→hash_nuevo en bitácora; actualizar manifiesto si es lateral/protocolo (no Engine).",
            "Si el contenido es el mismo con otra huella (rebuild): declarar EQUIVALENTE + nuevo hash; no re-ejecutar lo ya verificado.",
            "Si falta el artefacto: registrar reportado/no_recibido y seguir el siguiente pendiente útil.",
        ],
        "prohibido": [
            "Parar el flujo solo porque no es idéntico.",
            "Negarse a leer/correr el protocolo por hash distinto.",
            "Pedirle al usuario que 'arregle el hash'.",
        ],
    },
    "falta_letra_typo_ruta": {
        "piedra": "Ruta/nombre con typo o una letra de menos.",
        "contornos": [
            "Listar el directorio padre y tomar el match más cercano (glob / fuzzy simple).",
            "Probar alias conocidos (sidecar_* ↔ control_*, catalogo ↔ catálogo).",
            "Si hay 1 candidato claro: usarlo y anotar la corrección.",
        ],
        "prohibido": ["Declarar 'no puedo correrlo' sin buscar el vecino."],
    },
    "archivo_ausente": {
        "piedra": "No está el archivo esperado.",
        "contornos": [
            "Buscar en CHECKPOINT actual, delta laterales, Notion adjuntos, PARA_CLAUDE.",
            "Si existe SPEC sin .py: marcar NO_IMPLEMENTADO y continuar otra pieza; no inventar código canónico.",
            "Si es opcional/lateral: OFF/LATENCIA y seguir el tubo.",
        ],
        "prohibido": ["Congelar toda la corrida por un lateral faltante."],
    },
    "import_o_dependencia": {
        "piedra": "Falla import / dependencia / cwd.",
        "contornos": [
            "Añadir sys.path del 02_TUBO y 03_LATERALES_VIGENTES.",
            "Correr desde el directorio del checkpoint.",
            "Usar el resolve multi-ruta del catálogo si aplica.",
        ],
        "prohibido": ["Reportar el traceback como fin del trabajo."],
    },
    "permiso_o_auth": {
        "piedra": "Auth / permiso / conector.",
        "contornos": [
            "Cambiar a superficie que sí esté autorizada (archivo local, otro namespace Notion).",
            "Dejar PENDIENTE_AUTH con el siguiente paso concreto; no dramatizar.",
        ],
        "prohibido": ["Quedarse en bucle pidiendo el mismo permiso."],
    },
    "ambiguedad_datos": {
        "piedra": "No alcanza la información para cerrar.",
        "contornos": [
            "Delegar a control_latencia_decimo_hombre (LATENCIA / décimo / almacén).",
            "Seguir con lo que sí se puede verificar hoy.",
        ],
        "prohibido": ["Inventar el cierre.", "Tratar la duda como fallo del Engine."],
    },
    "drama_generico": {
        "piedra": "Respuesta tipo 'no puedo / bloqueado / atascado'.",
        "contornos": [
            "Reformular a: piedra + 1 contorno + 1 siguiente acción + evidencia.",
            "Formato obligatorio: PIEDRA / CONTORNO / SIGUIENTE / EVIDENCIA.",
        ],
        "prohibido": ["Párrafos de impotencia sin acción."],
    },
}


def clasificar_piedra(texto_error: str) -> str:
    t = (texto_error or "").lower()
    if "hash" in t and ("idéntic" in t or "identic" in t or "no coincide" in t or "mismatch" in t):
        return "hash_no_identico"
    if any(k in t for k in ["no such file", "not found", "no existe", "missing file", "file not found"]):
        return "archivo_ausente"
    if any(k in t for k in ["typo", "letra", "misspell", "did you mean", "ruta"]):
        return "falta_letra_typo_ruta"
    if any(k in t for k in ["import", "modulenotfound", "no module", "sys.path", "cwd"]):
        return "import_o_dependencia"
    if any(k in t for k in ["auth", "permission", "401", "403", "login", "oauth"]):
        return "permiso_o_auth"
    if any(k in t for k in ["insuficiente", "ambiguous", "50/50", "no data", "indetermin"]):
        return "ambiguedad_datos"
    if _RX_DRAMA.search(texto_error or ""):
        return "drama_generico"
    return "drama_generico"


def contornar(piedra_o_error: str, *, contexto: Optional[str] = None) -> Dict[str, Any]:
    """Dada una piedra, devuelve contornos (soluciones) y formato de salida."""
    kind = clasificar_piedra(piedra_o_error)
    spec = CONTORNOS[kind]
    return {
        "plugin": "CONTROL_FLUJO_SOLUCIONES",
        "version": __version__,
        "rol": "control_estructural_flujo",
        "Alimenta_H": ALIMENTA_H,
        "metafora": "agua_vs_piedra",
        "tipo_piedra": kind,
        "piedra": spec["piedra"],
        "entrada": (piedra_o_error or "")[:500],
        "contexto": contexto,
        "contornos": spec["contornos"],
        "prohibido": spec["prohibido"],
        "formato_respuesta_obligatorio": [
            "PIEDRA: (qué trabó, 1 línea)",
            "CONTORNO: (qué ruta tomas)",
            "SIGUIENTE: (acción concreta ya)",
            "EVIDENCIA: (hash/ruta/resultado)",
        ],
        "regla": "Soluciones, no problemas. El obstáculo informa el contorno; no detiene el río.",
    }


def reformatear_si_drama(texto: str) -> Dict[str, Any]:
    """Si el texto es lamento, exige reformateo a flujo."""
    if not _RX_DRAMA.search(texto or ""):
        return {"es_drama": False, "ok": True, "texto": texto}
    plan = contornar(texto)
    return {
        "es_drama": True,
        "ok": False,
        "rechazo": "Respuesta tipo obstáculo-drama. Reescribir en PIEDRA/CONTORNO/SIGUIENTE/EVIDENCIA.",
        "plan": plan,
    }


def buscar_equivalente_por_nombre(dir_path: str | Path, pedazo: str, *, max_cands: int = 5) -> Dict[str, Any]:
    """Contorno práctico: typo/letra faltante → candidatos en carpeta."""
    root = Path(dir_path)
    needle = (pedazo or "").lower()
    cands: List[str] = []
    if root.is_dir() and needle:
        for p in root.rglob("*"):
            if p.is_file() and needle[: max(3, len(needle) - 1)] in p.name.lower():
                cands.append(str(p))
            if len(cands) >= max_cands:
                break
    return contornar(
        f"typo/ruta: no hallé exactamente '{pedazo}'",
        contexto=json.dumps({"dir": str(root), "candidatos": cands}, ensure_ascii=False),
    ) | {"candidatos": cands}



def bypass_hash_cambio(
    *,
    ruta: str | Path | None = None,
    hash_esperado: str | None = None,
    hash_actual: str | None = None,
    rol: str = "lateral_o_protocolo",
    motivo: str = "hash_cambio",
) -> Dict[str, Any]:
    """BYPASS explícito: hash distinto ≠ muro.

    Mj: si cambia el hash, que NO haya problema — que lea y corra el protocolo
    con el modelo (habla + memoria). Solo Engine/244/FREEZE/H canónico siguen
    candado duro.

    Returns always permitir_lectura=True / permitir_corrida=True for non-engine.
    """
    ruta_s = str(ruta) if ruta else None
    ha = hash_actual
    if ruta_s and Path(ruta_s).is_file() and not ha:
        ha = hashlib.sha256(Path(ruta_s).read_bytes()).hexdigest()
    es_engine = rol in ("engine", "ENGINE", "244", "freeze", "FREEZE", "H_CANONICO") or (
        ruta_s and any(x in Path(ruta_s).name.lower() for x in ("engine_v5", "engine_v15", "patterns_final"))
    )
    if es_engine and hash_esperado and ha and hash_esperado != ha:
        plan = contornar(
            f"hash mismatch ENGINE {hash_esperado} vs {ha}",
            contexto=ruta_s,
        )
        plan.update({
            "bypass": False,
            "permitir_lectura": True,   # leer para diagnosticar siempre
            "permitir_corrida_como_canon": False,
            "accion": "AVISAR_CANDADO_ENGINE_no_sustituir_canon",
            "Alimenta_H": ALIMENTA_H,
            "bitacora": {
                "tipo": "hash_cambio_engine",
                "hash_esperado": hash_esperado,
                "hash_actual": ha,
                "ruta": ruta_s,
            },
        })
        return plan

    plan = contornar(
        f"hash cambio (bypass): esperado={hash_esperado} actual={ha}",
        contexto=ruta_s or motivo,
    )
    plan.update({
        "bypass": True,
        "codigo": "BYPASS_HASH_CAMBIO",
        "permitir_lectura": True,
        "permitir_corrida": True,
        "permitir_protocolo": True,
        "accion": "LEER_Y_CORRER_CON_PROTOCOLO",
        "regla": (
            "Hash distinto no apaga protocolo ni lectura. "
            "Corre con el modelo (habla/memoria) + kernel. Bitácora para calibrar."
        ),
        "Alimenta_H": ALIMENTA_H,
        "bitacora": {
            "tipo": "BYPASS_HASH_CAMBIO",
            "hash_esperado": hash_esperado,
            "hash_actual": ha,
            "ruta": ruta_s,
            "rol": rol,
            "motivo": motivo,
        },
    })
    return plan

if __name__ == "__main__":
    demos = [
        "No puedo seguir: no encuentro el hash idéntico al marcado",
        "Me faltó una letra en la ruta y no puedo correrlo",
        "ModuleNotFoundError: sidecar_luces",
        "Datos insuficientes para cerrar H",
    ]
    for d in demos:
        print(json.dumps({k: contornar(d)[k] for k in ("tipo_piedra", "contornos")}, ensure_ascii=False))
    r = bypass_hash_cambio(hash_esperado="aaa", hash_actual="bbb", rol="protocolo")
    assert r["bypass"] is True and r["permitir_corrida"] is True
    print("BYPASS_HASH_CAMBIO ok")
    print("PASS_SMOKE control_flujo_soluciones", __version__)
