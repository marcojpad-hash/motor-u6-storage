
#!/usr/bin/env python3
"""
MOTOR_V15_3_NATIVO.py

UPGRADE NATIVO del motor (NO capa / NO sidecar / NO wrapper sobre V15.1 o V15.2).
El protocolo vive DENTRO del tubo: flujo-soluciones, latencia+décimo hombre,
polaridad/falso-problema, tortugas, integración≠nulificación, falacias in/out,
BYPASS_HASH_CAMBIO.

V15.2 fue capa (importaba limpio y envolvía). V15.3 NO repite ese patrón:
este archivo ES el motor; la API pública es una sola entrada.

Candados duros (únicos que pueden parar): Engine_V5 / patterns 244 / FREEZE / H.
Alimenta_H = NO en todas las piezas de protocolo.
Bitácora de activaciones para calibración (reporta uso; no pide a Mj).
Contrato vigente: INTEGRADO_CONTRATO_V15_3_20260923.md
ON/OFF abajo son etiquetas de salida, NO interruptor de carga ni paro.

Uso (entry única):
  from MOTOR_V15_3_NATIVO import correr_5x3
  out = correr_5x3(cuts, pregunta="caso", obstaculo=None, texto_polaridad=None)
  # alias explícito: correr_5x3_v15_3(...)
"""

from __future__ import annotations

import hashlib
import os  # U6
import importlib.util
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

BASE = Path(__file__).resolve().parent
VERSION = "V15.3_NATIVO"
HASH_CANDADO = "48333cd11b9234f1"
M = 0.998
N_CANON = 244  # valor del catálogo v14; UNICO: la validación usa len() del catálogo cargado
PATTERNS_SHA256_CANONICAL = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"
_CATALOG_INTEGRITY: Dict[str, Any] = {}
import os as _os_cat
def _PATTERNS_PATH():
    """UNICO 27-sep: ruta del catálogo configurable (MOTOR_PATTERNS_PATH); default patterns_final_v14.json junto al motor."""
    return Path(_os_cat.environ.get("MOTOR_PATTERNS_PATH") or (BASE / "patterns_final_v14.json"))
P_MIN_CANDIDATO = 0.65
MAX_CANDIDATOS = 3
ALIMENTA_H = "NO"
PARAR_SOLO_SI = ("ENGINE", "244", "FREEZE", "H_CANONICO", "CANDADO_HASH_ENGINE")

# ON/OFF: metadata JSON only. Intersection is historical. OFF ≠ halt.
ON = (
    "traza_campo_244.py",
    "plugin_reporte_3d.py",
    "plugin_familias_gloria_sacro.py",
    "plugin_otto_numinoso.py",
    "plugin_trayectoria_hosteleria.py",
    "plugin_arco_field_snyder_mckee.py",
    "plugin_picos_mesetas.py",
    "plugin_sesgo_lectura.py",
    "plugin_alias_reactivacion.py",
    "plugin_fix_entrada.py",
    "plugin_embudo_clinico.py",
    "plugin_pregunta_detras_v2.py",  # U6 A7: alias (MAPA_NOMBRES) de plugin_pregunta_detras.py, que no existe
    "plugin_metodo_rigor.py",
    "plugin_arquetipos_dinamicos.py",
    "plugin_guardia_no_cruce.py",
)
OFF = (
    "plugin_familias_gloria_sacro.py",
    "plugin_otto_numinoso.py",
    "plugin_trayectoria_hosteleria.py",
    "plugin_aquiles_h.py",
    # U6 A7: "plugin_wroas.py" quitado de la lista OFF: el archivo no existe en ningún pack y nadie lo carga (referencia muerta).
    "plugin_arco_field_snyder_mckee.py",
    "plugin_picos_mesetas.py",
    "plugin_sesgo_lectura.py",
    "plugin_alias_reactivacion.py",
    "plugin_fix_entrada.py",
    "plugin_embudo_clinico.py",
    "plugin_pregunta_detras_v2.py",  # U6 A7: alias
    "plugin_metodo_rigor.py",
)

# Laterales de protocolo (hash bypass si cambian; NO son Engine)
_PROTOCOLO_FILES = (
    "control_flujo_soluciones.py",
    "control_latencia_decimo_hombre.py",
    "plugin_polaridad_causal.py",
    "candado_plugins.py",
)

Token = Tuple[str, float]
Eje = Sequence[Token]
Corte = Dict[str, Any]


# ---------------------------------------------------------------------------
# PROTOCOLO NATIVO (helpers internos — no capa externa)
# ---------------------------------------------------------------------------

@dataclass
class EventoBitacora:
    ts: float
    piedra: str
    tipo: str
    pieza_usada: str
    accion: str
    evidencia: str
    pidio_humano: bool = False
    ok_protocolo: bool = True


_BITACORA: List[EventoBitacora] = []


def bitacora() -> List[Dict[str, Any]]:
    return [asdict(e) for e in _BITACORA]


def limpiar_bitacora() -> None:
    _BITACORA.clear()


def _log(
    piedra: str,
    tipo: str,
    pieza: str,
    accion: str,
    evidencia: str,
    *,
    pidio_humano: bool = False,
) -> Dict[str, Any]:
    ev = EventoBitacora(
        ts=time.time(),
        piedra=(piedra or "")[:300],
        tipo=tipo,
        pieza_usada=pieza,
        accion=accion,
        evidencia=(evidencia or "")[:500],
        pidio_humano=pidio_humano,
        ok_protocolo=not pidio_humano,
    )
    _BITACORA.append(ev)
    return asdict(ev)


def _sha256_file(path: Path) -> Optional[str]:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _try_import_sibling(filename: str, modname: str):
    """Importa módulo hermano si existe; None si falta (nunca drama-stop)."""
    path = BASE / filename
    if not path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(modname, str(path))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        # Prefer same-dir resolution for sibling imports inside the module
        sys.modules[modname] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:  # noqa: BLE001 — protocolo no puede caerse
        _log(str(path), "import_o_dependencia", "flujo", "contornar_import", str(e))
        return None


# --- 7) BYPASS_HASH_CAMBIO (nativo) ---
def nativo_bypass_hash(
    *,
    ruta: str | Path | None = None,
    hash_esperado: str | None = None,
    hash_actual: str | None = None,
    rol: str = "lateral_o_protocolo",
) -> Dict[str, Any]:
    """Hash distinto en laterales/protocolo → LEER + CORRER igual; bitácora.
    Solo Engine/244/FREEZE/H quedan candado duro."""
    flujo = _try_import_sibling("control_flujo_soluciones.py", "ctrl_flujo_v153")
    if flujo is not None and hasattr(flujo, "bypass_hash_cambio"):
        out = flujo.bypass_hash_cambio(
            ruta=ruta,
            hash_esperado=hash_esperado,
            hash_actual=hash_actual,
            rol=rol,
        )
    else:
        ruta_s = str(ruta) if ruta else None
        ha = hash_actual
        if ruta_s and Path(ruta_s).is_file() and not ha:
            ha = _sha256_file(Path(ruta_s))
        es_engine = rol in ("engine", "ENGINE", "244", "freeze", "FREEZE", "H_CANONICO") or (
            ruta_s
            and any(
                x in Path(ruta_s).name.lower()
                for x in ("engine_v5", "engine_v15", "patterns_final")
            )
        )
        if es_engine and hash_esperado and ha and hash_esperado != ha:
            out = {
                "bypass": False,
                "permitir_lectura": True,
                "permitir_corrida_como_canon": False,
                "accion": "AVISAR_CANDADO_ENGINE_no_sustituir_canon",
                "Alimenta_H": ALIMENTA_H,
                "codigo": "CANDADO_HASH_ENGINE",
            }
        else:
            mismatch = bool(hash_esperado and ha and hash_esperado != ha)
            out = {
                "bypass": True if mismatch or not hash_esperado else True,
                "codigo": "BYPASS_HASH_CAMBIO",
                "permitir_lectura": True,
                "permitir_corrida": True,
                "permitir_protocolo": True,
                "accion": "LEER_Y_CORRER_CON_PROTOCOLO",
                "Alimenta_H": ALIMENTA_H,
                "bitacora": {
                    "tipo": "BYPASS_HASH_CAMBIO",
                    "hash_esperado": hash_esperado,
                    "hash_actual": ha,
                    "ruta": ruta_s,
                    "rol": rol,
                },
            }
    if out.get("bypass") or out.get("codigo") == "BYPASS_HASH_CAMBIO":
        _log(
            f"hash {ruta or ''} esp={hash_esperado}",
            "hash_no_identico",
            "BYPASS_HASH_CAMBIO",
            out.get("accion", "continuar"),
            str(out.get("bitacora") or out.get("codigo")),
            pidio_humano=False,
        )
    out.setdefault("Alimenta_H", ALIMENTA_H)
    out.setdefault("permitir_protocolo", True)
    return out


def nativo_arranque_hashes() -> Dict[str, Any]:
    """Al inicio de corrida: si hash de laterales cambió → bypass, continuar, bitácora."""
    resultados = []
    for fname in _PROTOCOLO_FILES:
        p = BASE / fname
        if not p.exists():
            resultados.append(
                {
                    "file": fname,
                    "existe": False,
                    "accion": "archivo_ausente_seguir",
                    "bypass": True,
                }
            )
            _log(fname, "archivo_ausente", "flujo", "seguir_sin_archivo", "opcional")
            continue
        ha = _sha256_file(p)
        # Manifiesto opcional: si hay hash guardado distinto → bypass
        man = BASE / "manifiesto_plugins.json"
        esperado = None
        if man.exists():
            try:
                data = json.loads(man.read_text(encoding="utf-8"))
                plugins = data.get("plugins") or data.get("hashes") or data
                if isinstance(plugins, dict) and fname in plugins:
                    entry = plugins[fname]
                    esperado = entry if isinstance(entry, str) else (entry or {}).get("sha256")
            except Exception:  # noqa: BLE001
                esperado = None
        r = nativo_bypass_hash(
            ruta=p, hash_esperado=esperado, hash_actual=ha, rol="lateral_o_protocolo"
        )
        resultados.append({"file": fname, "existe": True, "sha256": ha, **{
            k: r.get(k) for k in ("bypass", "codigo", "accion", "permitir_corrida", "Alimenta_H")
        }})
    return {
        "arranque_hashes": resultados,
        "parar": False,
        "Alimenta_H": ALIMENTA_H,
        "regla": "Hash lateral distinto ≠ muro. Solo Engine/244/FREEZE/H candado duro.",
    }


# --- 1) flujo-soluciones (agua vs piedra) ---
def nativo_flujo(obstaculo: str, *, contexto: Optional[str] = None) -> Dict[str, Any]:
    flujo = _try_import_sibling("control_flujo_soluciones.py", "ctrl_flujo_v153")
    if flujo is not None and hasattr(flujo, "contornar"):
        plan = flujo.contornar(obstaculo, contexto=contexto)
    else:
        t = (obstaculo or "").lower()
        if "hash" in t:
            kind = "hash_no_identico"
            contornos = ["BYPASS_HASH_CAMBIO: leer y correr igual; bitácora."]
        elif any(k in t for k in ["50/50", "empate", "insuficiente"]):
            kind = "ambiguedad_datos"
            contornos = ["LATENCIA / décimo hombre / almacén; no fingir cierre."]
        else:
            kind = "drama_generico"
            contornos = ["PIEDRA/CONTORNO/SIGUIENTE/EVIDENCIA; seguir."]
        plan = {
            "plugin": "CONTROL_FLUJO_NATIVO",
            "tipo_piedra": kind,
            "contornos": contornos,
            "Alimenta_H": ALIMENTA_H,
            "metafora": "agua_vs_piedra",
        }
    plan.setdefault("Alimenta_H", ALIMENTA_H)
    _log(
        obstaculo,
        plan.get("tipo_piedra", "flujo"),
        "flujo_soluciones",
        "contornar",
        json.dumps(plan.get("contornos", [])[:2], ensure_ascii=False),
    )
    return plan


# --- 2) latencia + décimo hombre ---
def nativo_latencia(
    clave: str,
    *,
    p_momento: float = 0.5,
    tokens: Optional[Sequence[str]] = None,
    tema: str = "empate",
) -> Dict[str, Any]:
    lat = _try_import_sibling("control_latencia_decimo_hombre.py", "ctrl_lat_v153")
    if lat is not None and hasattr(lat, "actualizar_expediente"):
        # store aislado para no ensuciar el global del lateral
        store = BASE / "estado_latencia_v15_3_nativo.json"
        out = lat.actualizar_expediente(
            clave,
            tema=tema,
            p_momento=p_momento,
            tokens_nuevos=list(tokens or []),
            store_path=store,
        )
    else:
        # fallback nativo mínimo
        p = float(p_momento)
        empate = abs(p - 0.5) <= 0.05
        if empate:
            estado, accion = "ALMACENADO_ESPERANDO_DATOS", "ESPERAR_MAS_TOKENS"
        elif len(tokens or []) < 3:
            estado, accion = "LATENCIA", "LATENCIA_ACUMULAR_TOKENS"
        else:
            estado, accion = "RESUELTO", "LIBERAR_LATENCIA"
        out = {
            "capa": "CONTROL_LATENCIA_NATIVO",
            "accion": accion,
            "expediente": {"estado": estado, "p": p, "Alimenta_H": ALIMENTA_H},
            "Alimenta_H": ALIMENTA_H,
        }
    out.setdefault("Alimenta_H", ALIMENTA_H)
    _log(
        clave,
        "empate_50_50" if abs(float(p_momento) - 0.5) <= 0.05 else "latencia",
        "latencia_decimo_hombre",
        out.get("accion", "latencia"),
        str((out.get("expediente") or {}).get("estado")),
    )
    return out


# --- 3) polaridad / falso-problema (litote) ---
_RX_DOBLE = re.compile(
    r"(?:\bno\s+es\s+que\s+no\b|\btampoco\s+es\s+que\s+no\b)",
    re.I,
)


def nativo_polaridad(texto: str) -> Dict[str, Any]:
    pol_mod = _try_import_sibling("plugin_polaridad_causal.py", "pol_causal_v153")
    if pol_mod is not None and hasattr(pol_mod, "clasificar_polaridad_causal"):
        out = pol_mod.clasificar_polaridad_causal(texto or "")
    else:
        n = (texto or "").lower()
        if _RX_DOBLE.search(n):
            out = {
                "etiqueta": "DOBLE_NEGACION_LITOTE",
                "causalidad_negada_simple": False,
                "solo_marca": True,
                "Alimenta_H": ALIMENTA_H,
                "motivo": "litote_nativo",
            }
        else:
            out = {
                "etiqueta": "NEUTRO",
                "causalidad_negada_simple": False,
                "solo_marca": True,
                "Alimenta_H": ALIMENTA_H,
                "motivo": "sin_negacion",
            }
    out.setdefault("Alimenta_H", ALIMENTA_H)
    out.setdefault("solo_marca", True)
    _log(
        (texto or "")[:120],
        "doble_negacion" if out.get("etiqueta") == "DOBLE_NEGACION_LITOTE" else "polaridad",
        "polaridad_causal",
        "sensor_solo_marca",
        out.get("etiqueta", ""),
    )
    return out


# --- 4) tortugas: borroso → remedir, no inventar fuerza / no cambiar familia ---
def nativo_tortugas(r732: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    kappa = list((r732 or {}).get("kappa_dir") or [])
    # cerca de 1.0 = giro indistinguible de ruido → remedir
    borroso = any(k is not None and float(k) >= 0.9988 for k in kappa) if kappa else False
    flag = "TORTUGAS_REMEDIR" if borroso else "OK_RESOLUCION"
    out = {
        "tortugas_flag": flag,
        "borroso": borroso,
        "accion": "remedir_mas_fino_no_cambiar_familia" if borroso else "seguir",
        "prohibido": ["inventar_fuerza", "cambiar_familia_por_borroso"],
        "Alimenta_H": ALIMENTA_H,
    }
    if borroso:
        _log("kappa_borroso", "borroso_sin_fuerza", "tortugas", out["accion"], flag)
    return out


# --- 5) integración ≠ nulificación ---
def nativo_integracion(luces: Optional[Sequence[Any]] = None) -> Dict[str, Any]:
    n = len(list(luces or []))
    nota = (
        "Luces en conflicto se INTEGRAN (vectores); no se cancelan ni se apagan."
        if n >= 2
        else "Sin conflicto de luces reportado; regla de integración vigente."
    )
    out = {
        "integracion_nota": nota,
        "n_luces": n,
        "accion": "integrar_no_apagar",
        "Alimenta_H": ALIMENTA_H,
    }
    if n >= 2:
        _log("conflicto_luces", "conflicto_luces", "integracion", "integrar_no_apagar", nota)
    return out


# --- 6) falacias in/out: filtrar ruido de protocolo ---
_RX_RUIDO = re.compile(
    r"(?i)\b(juicio\s+est[eé]tico|fecha\s+de\s+protocolo|sombrero\s+blanco|"
    r"t[ií]tulo\s+ornamental|ruido\s+de\s+protocolo)\b"
)


def nativo_falacias(texto: Optional[str] = None) -> Dict[str, Any]:
    t = texto or ""
    es_ruido = bool(_RX_RUIDO.search(t))
    out = {
        "filtro": "falacias_in_out",
        "es_ruido_protocolo": es_ruido,
        "accion": "filtrar_ruido_seguir" if es_ruido else "dato_observable_ok",
        "regla": "Hecho observable entra; juicio/fecha/recorte de protocolo no alimenta H.",
        "Alimenta_H": ALIMENTA_H,
    }
    if es_ruido:
        _log(t[:120], "ruido_protocolo", "falacias_in_out", "filtrar_ruido_seguir", "ruido")
    return out


def nativo_aplicar_protocolo(obstaculo: str, *, evidencia: str = "") -> Dict[str, Any]:
    """Entrada única de protocolo: no parar; contornar; bitácora."""
    flujo = nativo_flujo(obstaculo)
    extras: Dict[str, Any] = {}
    t = (obstaculo or "").lower()
    if any(k in t for k in ["doble neg", "no es que no", "litote", "falso problema"]):
        extras["polaridad"] = nativo_polaridad(obstaculo)
    if any(k in t for k in ["50/50", "0.5", "empate", "indetermin", "insuficiente"]):
        extras["latencia"] = nativo_latencia("protocolo_nativo", p_momento=0.5, tokens=[])
    if "hash" in t:
        extras["bypass"] = nativo_bypass_hash(hash_esperado="old", hash_actual="new", rol="protocolo")
    return {
        "protocolo": "NATIVO_V15_3",
        "version": VERSION,
        "Alimenta_H": ALIMENTA_H,
        "parar": False,
        "motivo_no_parar": "Obstáculo tipado; protocolo nativo. Reportar, no escalar a Mj.",
        "plan_flujo": flujo,
        "extras": extras,
        "evidencia": (evidencia or "")[:300],
    }


# ---------------------------------------------------------------------------
# TUBO (cuerpo = espíritu limpio V15.1; protocolo embebido en el loop)
# ---------------------------------------------------------------------------

def _load(modname: str, filename: str):
    path = BASE / filename
    if not path.exists():
        raise FileNotFoundError(f"Falta {filename} junto a este script")
    spec = importlib.util.spec_from_file_location(modname, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_canonical() -> Tuple[Dict[str, Any], set]:
    global _CATALOG_INTEGRITY
    path = _PATTERNS_PATH()
    if not path.exists():
        raise FileNotFoundError(f"Falta catalogo de patrones: {path}")
    raw = path.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    custom = bool(_os_cat.environ.get("MOTOR_PATTERNS_PATH"))
    expected_sha = (_os_cat.environ.get("MOTOR_PATTERNS_SHA256") if custom else PATTERNS_SHA256_CANONICAL)
    if not custom and actual_sha != PATTERNS_SHA256_CANONICAL:
        raise RuntimeError(f"CANONICAL_PATTERNS_HASH_MISMATCH:expected={PATTERNS_SHA256_CANONICAL}:actual={actual_sha}")
    lib = json.loads(raw.decode("utf-8"))
    count = len(lib) if isinstance(lib, (dict, list)) else -1
    _esp = int(_os_cat.environ.get("MOTOR_N_PATRONES_ESPERADO", "0") or 0)
    if len(lib) == 0 or (_esp and len(lib) != _esp):
        raise RuntimeError(f"catalogo roto: len={len(lib)} esperado={_esp or '>0'}")
    if not custom and count != N_CANON:
        raise RuntimeError(f"CANONICAL_PATTERNS_COUNT_MISMATCH:expected={N_CANON}:actual={count}")
    if custom and expected_sha and actual_sha != expected_sha:
        raise RuntimeError(f"CUSTOM_PATTERNS_HASH_MISMATCH:expected={expected_sha}:actual={actual_sha}")
    _CATALOG_INTEGRITY = {"path": str(path), "sha256": actual_sha, "n_patterns": count,
                          "canonical_default": not custom, "hash_verified": bool(expected_sha and actual_sha == expected_sha),
                          "expected_sha256": expected_sha,
                          "status": "CANONICAL_VERIFIED" if not custom else ("CUSTOM_HASH_VERIFIED" if expected_sha and actual_sha == expected_sha else "CUSTOM_HASH_UNPINNED")}
    tokens: set = set()
    for p in lib.values() if isinstance(lib, dict) else lib:
        if not isinstance(p, dict):
            continue
        tokens |= set(p.get("tokens_favor", {}) or [])
        tokens |= set(p.get("tokens_contra", {}) or [])
    return lib, tokens


def validar_corte(cid: str, P: Eje, A: Eje, C: Eje, canonical: set) -> Dict[str, int]:
    holes = {}
    for eje, rows in (("P", P), ("A", A), ("C", C)):
        seen = []
        for tok, w in rows:
            if tok not in canonical:
                # No inferir equivalencia por subcadena: "token_prueba_nuevo" no
                # equivale a "prueba". Solo normalización exacta puede proponer alias.
                _norm_exact = lambda value: re.sub(r"\s+", " ", str(value or "").strip()).casefold()
                eq=[c for c in canonical if _norm_exact(c) == _norm_exact(tok)]
                holes.setdefault("fuera_catalogo", []).append({"corte":cid,"eje":eje,"token":tok,"equivalente":eq[0] if len(eq)==1 else None,"n_candidatos":len(eq)})
                continue
            if not (0.60 <= float(w) <= 0.84):
                raise RuntimeError(f"PESO_FUERA_DE_CODIGO {cid} {eje} {tok} {w}")
            if tok in seen:
                raise RuntimeError(f"TOKEN_DUPLICADO {cid} {eje} {tok}")
            seen.append(tok)
        # U4_todos_tokens (2026-10-11, decisión de Mj): ya no se rechaza el corte con más de 5 tokens por eje
        # (antes: RuntimeError MAS_DE_5). Todos los tokens entran; el tope de 5 pasa a ser el CUELLO de botella
        # predictivo que se aplica solo al alimentar el Engine canónico (cuello_top_k). Peso y duplicados se siguen
        # validando sobre TODOS los tokens.
        holes[eje] = max(0, CUELLO_K - len(rows))
        if len(rows) > CUELLO_K:
            holes.setdefault("cuello_top5", {})[eje] = {"n_entrada": len(rows), "n_al_engine": CUELLO_K}
    return holes


# U4_todos_tokens: cuello de botella top-k por eje y corte, SOLO para el Engine canónico (el tablero que alimenta H).
CUELLO_K = 5
CUELLO_REGLA = ("si un eje de un corte trae más de 5 tokens, al Engine canónico pasan 5: primero los que están en el catálogo 244, "
                "luego por peso descendente; a igual peso (U6) decide la EVIDENCIA observada hasta ese corte: 1) frecuencia en cortes previos, "
                "2) racha de presencia inmediatamente anterior (recencia), 3) apoyo en otros ejes del mismo corte; solo si todo empata decide la posición. "
                "No usa cortes posteriores (sin mirar el futuro). Se pasan en su orden original. "
                "Es el cuello de botella predictivo, NO un borrado: todos los tokens siguen en el input y en las capas no canónicas.")


def _evidencia_desempate_u6(token: str, eje: str, previos, corte_actual) -> Tuple[int, int, int]:
    """U6: evidencia real y determinista para desempatar a igual peso. Solo cortes ANTERIORES y el corte actual."""
    def toks(c):
        return {str(r[0] if isinstance(r, (list, tuple)) else r) for e in ("P", "A", "C") for r in (c.get(e) or [])}
    pres = [token in toks(c) for c in (previos or [])]
    frecuencia = sum(pres)
    racha = 0
    for p in reversed(pres):
        if not p: break
        racha += 1
    apoyo = 0
    if corte_actual:
        apoyo = sum(1 for e in ("P", "A", "C") if e != eje and any(str(r[0] if isinstance(r, (list, tuple)) else r) == token for r in (corte_actual.get(e) or [])))
    return frecuencia, racha, apoyo


def cuello_top_k(cid: str, eje: str, rows: Eje, canonical: set, k: int = CUELLO_K, previos=None, corte_actual=None):
    rows = list(rows)
    if len(rows) <= k:
        return rows, None
    _pos = os.environ.get("U6_DESEMPATE_CUELLO", "evidencia").strip().lower() == "posicion"
    ev = {i: ((0, 0, 0) if _pos else _evidencia_desempate_u6(str(rows[i][0]), eje, previos, corte_actual)) for i in range(len(rows))}
    orden = sorted(range(len(rows)), key=lambda i: (0 if rows[i][0] in canonical else 1, -float(rows[i][1]), -ev[i][0], -ev[i][1], -ev[i][2], i))
    # registro de cómo se resolvió cada empate en el borde (entra vs queda fuera con el mismo peso)
    _wk = float(rows[orden[k - 1]][1]); _borde = [i for i in orden if float(rows[i][1]) == _wk and rows[i][0] in canonical]
    _dentro = [i for i in _borde if i in orden[:k]]; _fuera = [i for i in _borde if i not in orden[:k]]
    _decision = []
    for a in _dentro:
        for b in _fuera:
            crit = next((n for n, x, y in zip(("frecuencia_previa", "racha_previa", "apoyo_otros_ejes"), ev[a], ev[b]) if x != y), "posicion")
            _decision.append(crit)
    keep = sorted(orden[:k])
    fuera = [i for i in range(len(rows)) if i not in keep]
    wk = float(rows[orden[k - 1]][1])
    return [rows[i] for i in keep], {
        "corte": cid, "eje": eje, "n_entrada": len(rows), "n_al_engine": k,
        "al_engine": [[rows[i][0], float(rows[i][1]), i] for i in keep],
        "quedan_fuera_del_engine": [{"corte": cid, "eje": eje, "token": rows[i][0], "w": float(rows[i][1]), "pos": i,
                                     "en_catalogo": rows[i][0] in canonical} for i in fuera],
        "peso_corte": wk,
        "empates_en_el_borde": sum(1 for i in fuera if float(rows[i][1]) == wk and rows[i][0] in canonical),
        "desempate_U6": {"regla": "posicion (legado, U6_DESEMPATE_CUELLO=posicion)" if _pos else "peso > frecuencia_previa > racha_previa > apoyo_otros_ejes > posicion",
                         "pares_borde": len(_decision), "decididos_por": {c: _decision.count(c) for c in sorted(set(_decision))},
                         "evidencia": {str(rows[i][0]): list(ev[i]) for i in _borde}},
        "nota": "cuello de botella, no borrado"}


_LIVE_ENGINES = []
_MC_AUDIT = []

def _close_engine(e):
    try:
        mem = getattr(e, "memory", None)
        cursor = getattr(mem, "cursor", None)
        if cursor is not None:
            try: cursor.close()
            except Exception: pass
            try: mem.cursor = None
            except Exception: pass
        conn = getattr(mem, "conn", None)
        if conn is not None:
            try: conn.close()
            finally:
                try: mem.conn = None
                except Exception: pass
    except Exception:
        pass

def _close_all_engines():
    while _LIVE_ENGINES:
        _close_engine(_LIVE_ENGINES.pop())

def _engine(eng, pat: str, pregunta: str):
    e = eng.TracingEngine(pat, ":memory:")
    e.start_question(pregunta)
    _LIVE_ENGINES.append(e)
    return e


def _board(eng, engine, cid: str, rows: Eje, monte_carlo: bool = True) -> Dict[str, float]:
    engine.extractor.extract_from_text = (
        lambda txt, rows=list(rows), cid=cid: [
            eng.Marker(t, t, float(w), source=f"5x3:{cid}") for t, w in rows
        ]
    )
    r = engine.process_observation(cid, monte_carlo=monte_carlo)
    mc = r.get("monte_carlo")
    _MC_AUDIT.append({
        "observation_id": cid,
        "enabled_requested": bool(monte_carlo),
        "status": "EXECUTED" if monte_carlo and isinstance(mc, dict) and int(mc.get("n_simulaciones_usadas") or 0) > 0 else ("DISABLED" if not monte_carlo else "NO_METRICS_RETURNED"),
        "simulations": int((mc or {}).get("n_simulaciones_usadas") or 0),
        "converged": (mc or {}).get("convergencia_alcanzada"),
    })
    return {h["name"]: float(h["p_final"]) for h in r["hypotheses"]}


def _top(board: Dict[str, float], k: int = 5) -> List[List[Any]]:
    return [[n, p] for n, p in sorted(board.items(), key=lambda x: -x[1])[:k]]


def _candidatos(board: Dict[str, float]) -> List[Dict[str, Any]]:
    out = []
    for n, p in sorted(board.items(), key=lambda x: -x[1]):
        if p >= P_MIN_CANDIDATO:
            out.append({"familia": n, "p": p})
        if len(out) >= MAX_CANDIDATOS:
            break
    return out


def _construir_protocolo_block(
    *,
    hash_arranque: Dict[str, Any],
    obstaculo: Optional[str],
    texto_polaridad: Optional[str],
    r732: Optional[Dict[str, Any]],
    pregunta: str,
) -> Dict[str, Any]:
    flujo = None
    if obstaculo:
        flujo = nativo_flujo(obstaculo)
    else:
        flujo = {
            "tipo_piedra": "ninguna",
            "contornos": ["sin obstáculo explícito"],
            "Alimenta_H": ALIMENTA_H,
        }

    # Latencia: si hay candidatos cerca de 0.5 o obstáculo de empate
    latencia = nativo_latencia(
        f"v153::{pregunta}",
        p_momento=0.5 if (obstaculo and ("50" in obstaculo or "empate" in (obstaculo or "").lower())) else 0.62,
        tokens=["arranque", "corte"],
        tema="corrida",
    )

    polaridad = nativo_polaridad(texto_polaridad or obstaculo or "")
    tortugas = nativo_tortugas(r732)
    integracion = nativo_integracion()
    falacias = nativo_falacias(obstaculo)

    bypass_info = None
    for item in hash_arranque.get("arranque_hashes") or []:
        if item.get("bypass"):
            bypass_info = item
            break
    if bypass_info is None and obstaculo and "hash" in (obstaculo or "").lower():
        bypass_info = nativo_bypass_hash(
            hash_esperado="old_manifest", hash_actual="new_on_disk", rol="protocolo"
        )

    return {
        "nativo": True,
        "capa": False,
        "version": VERSION,
        "flujo": flujo,
        "latencia": latencia,
        "polaridad": polaridad,
        "tortugas_flag": tortugas.get("tortugas_flag"),
        "tortugas": tortugas,
        "integracion_nota": integracion.get("integracion_nota"),
        "integracion": integracion,
        "falacias": falacias,
        "bypass": bypass_info,
        "hash_arranque": hash_arranque,
        "bitacora": bitacora(),
        "parar": False,
        "Alimenta_H": ALIMENTA_H,
        "candados_duros": list(PARAR_SOLO_SI),
        "nota_auditores": (
            "Corre este motor. No pidas a Mj que te explique candados — ya van dentro. "
            "Reportar uso en bitácora; no escalar tipografía/hash/litote/empate."
        ),
    }


def correr_5x3_v15_3(
    cuts: Sequence[Corte],
    pregunta: str = "caso",
    annex_traza: bool = True,
    obstaculo: Optional[str] = None,
    texto_polaridad: Optional[str] = None,
    monte_carlo: bool = True,
    marcador_limite: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Motor V15.3 NATIVO. Protocolo embebido en el loop (no capa).

    cuts = [
      {"id": "C1", "P": [("token", 0.72), ...], "A": [...], "C": [...]},
      ...
    ]
    """
    limpiar_bitacora()
    _MC_AUDIT.clear()
    _log("arranque", "arranque", "MOTOR_V15_3_NATIVO", "correr_5x3_v15_3", pregunta)

    # 1) Hash bypass al inicio (laterales/protocolo; nunca Engine)
    hash_arranque = nativo_arranque_hashes()

    # 2) Si hay obstáculo tipado → protocolo (no parar)
    if obstaculo:
        nativo_aplicar_protocolo(obstaculo)

    lib, canonical = load_canonical()
    eng = _load("eng_v5_v153", "Engine_V5_CANONICO_SOLO.py")

    ep = _engine(eng, str(_PATTERNS_PATH()), pregunta + "_P")
    ea = _engine(eng, str(_PATTERNS_PATH()), pregunta + "_A")
    ec = _engine(eng, str(_PATTERNS_PATH()), pregunta + "_C")

    seqP, seqA, seqC = [], [], []
    cutout = []
    holes_all = {}
    names_ref: Optional[List[str]] = None
    Xs: List[np.ndarray] = []
    cuello_log: List[Dict[str, Any]] = []

    for _iu6, raw in enumerate(cuts):
        cid = raw["id"]
        P, A, C = raw.get("P") or [], raw.get("A") or [], raw.get("C") or []
        holes_all[cid] = validar_corte(cid, P, A, C, canonical)
        _prev_u6 = list(cuts[:_iu6])
        P5, lgP = cuello_top_k(cid, "P", P, canonical, previos=_prev_u6, corte_actual=raw)
        A5, lgA = cuello_top_k(cid, "A", A, canonical, previos=_prev_u6, corte_actual=raw)
        C5, lgC = cuello_top_k(cid, "C", C, canonical, previos=_prev_u6, corte_actual=raw)
        for _lg in (lgP, lgA, lgC):
            if _lg: cuello_log.append(_lg)

        bp = _board(eng, ep, cid + "_P", P5, monte_carlo=monte_carlo)
        ba = _board(eng, ea, cid + "_A", A5, monte_carlo=monte_carlo)
        bc = _board(eng, ec, cid + "_C", C5, monte_carlo=monte_carlo)

        names = sorted(bp.keys())
        if names_ref is None:
            names_ref = names
        if names != names_ref or sorted(ba) != names_ref or sorted(bc) != names_ref:
            raise RuntimeError(f"BOARD_INCOMPLETO {cid}: no rellenar con 0.5")

        xt = np.concatenate(
            [
                np.array([bp[n] for n in names_ref], dtype=float),
                np.array([ba[n] for n in names_ref], dtype=float),
                np.array([bc[n] for n in names_ref], dtype=float),
            ]
        )
        if xt.size != 3 * len(names_ref) or len(names_ref) == 0:  # UNICO: 3 × len(catálogo) (732 con el v14)
            raise RuntimeError(f"R732_ROTO {cid} dim={xt.size} esperado={3 * len(names_ref)}")

        # Latencia nativa por corte si top candidato ~0.5
        tops = sorted(bp.values(), reverse=True)
        if tops and abs(tops[0] - 0.5) <= 0.05:
            nativo_latencia(f"{pregunta}::{cid}", p_momento=tops[0], tokens=[t for t, _ in P])

        Xs.append(xt)
        seqP.append((cid, bp))
        seqA.append((cid, ba))
        seqC.append((cid, bc))
        cutout.append(
            {
                "corte": cid,
                "n_tokens": {"P": len(P), "A": len(A), "C": len(C)},
                "holes": holes_all[cid],
                "P_top5_ANEXO": _top(bp),
                "A_top5_ANEXO": _top(ba),
                "C_top5_ANEXO": _top(bc),
                "P_candidatos_0a3": _candidatos(bp),
                "X_dim": int(xt.size),
                # Geometry fix V0.4: serialize the EXACT boards used to build xt/R732.
                # Do not regenerate them downstream with fresh Monte Carlo calls.
                "P_FULL_244": {n: float(bp[n]) for n in names_ref},
                "A_FULL_244": {n: float(ba[n]) for n in names_ref},
                "C_FULL_244": {n: float(bc[n]) for n in names_ref},
            }
        )

    Xm = np.stack(Xs)
    dX = np.diff(Xm, axis=0)
    dX_norm = np.linalg.norm(dX, axis=1).tolist()
    persist = []
    kappa = []
    for i in range(1, len(dX)):
        a, b = dX[i - 1], dX[i]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        cos = float(np.dot(a, b) / (na * nb + 1e-12))
        cos = max(-1.0, min(1.0, cos))
        persist.append(cos)
        kappa.append(float(np.sqrt(max(0.0, 1.0 - cos * cos))))

    r732 = {
        "X_shape": list(Xm.shape),
        "dX_norm": dX_norm,
        "persist_cos": persist,
        "kappa_dir": kappa,
        "nota": "dX/persist_cos/kappa_dir alimentan las dimensiones geometricas del predictor que ordena H1/H2; no determinan H por si solos. Tortugas nativas remiden si borroso.",
    }
    _ml_path = BASE / "marcador_limite_geometrico_v0_1.py"
    _ml_config = marcador_limite or {"modo": "ESTIMADO_DESDE_PREFIJO"}
    if _ml_config.get("enabled") is False:
        r732["marcador_limite_geometrico"] = {"status":"DISABLED_FOR_ABLATION","can_decide_H":False,"feeds_H":False,"rank_effect":"NONE","per_cut":[]}
    elif _ml_path.is_file():
        _ml_spec = importlib.util.spec_from_file_location("marcador_limite_geometrico_v0_1", str(_ml_path))
        if _ml_spec is None or _ml_spec.loader is None:
            raise RuntimeError("MARCADOR_LIMITE_IMPORT_ERROR")
        _ml_mod = importlib.util.module_from_spec(_ml_spec)
        sys.modules["marcador_limite_geometrico_v0_1"] = _ml_mod
        _ml_spec.loader.exec_module(_ml_mod)
        _ml_out = _ml_mod.evaluar_marcador(
            Xm.tolist(), cuts, dX_norm, persist, kappa,
            spec=_ml_config,
        )
        r732["marcador_limite_geometrico"] = _ml_out
        for _cut_row, _marker_row in zip(cutout, _ml_out.get("per_cut") or []):
            _cut_row["marcador_limite_geometrico"] = _marker_row
    else:
        raise RuntimeError("MARCADOR_LIMITE_GEOMETRICO_V0_1_AUSENTE")

    annex: Dict[str, Any] = {}
    if annex_traza:
        try:
            tc = _load("traza244_v153", "traza_campo_244.py")
            r3 = _load("rep3d_v153", "plugin_reporte_3d.py")
            annex["traza_P"] = tc.analizar(seqP)
            annex["reporte_3d_P"] = r3.leer(seqP)
        except FileNotFoundError:
            annex["traza_P"] = "plugin ausente"
            annex["reporte_3d_P"] = "plugin ausente"
            nativo_flujo("plugin ausente traza/reporte3d")

    protocolo = _construir_protocolo_block(
        hash_arranque=hash_arranque,
        obstaculo=obstaculo,
        texto_polaridad=texto_polaridad,
        r732=r732,
        pregunta=pregunta,
    )

    lastP = seqP[-1][1] if seqP else {}
    _close_all_engines()
    return {
        "version": VERSION,
        "hash_candado": HASH_CANDADO,
        "M": M,
        "nativo": True,
        "capa": False,
        "sidecar": False,
        "n_canon": len(lib),
        "catalog_integrity": dict(_CATALOG_INTEGRITY),
        "plugins_ON": list(ON),
        "plugins_OFF": list(OFF),
        "engine_executed": True,
        "top5_es_anexo": True,
        "H1": None,
        "H2": None,
        "regla_H": "Investigador=MOTOR (Mj solo input). H1/H2 salen de freeze=datos-hasta-t + vectorizacion + inercia + traza + candidatos 0-3. Prohibido H1=max(board). Usuario no formula H.",
        "sigma": None,
        "detector_no_aplica_aqui": True,
        "pregunta": pregunta,
        "n_cuts": len(cuts),
        "monte_carlo_audit": {
            "status": "EXECUTED" if _MC_AUDIT and all(x["status"] == "EXECUTED" for x in _MC_AUDIT) else ("DISABLED" if _MC_AUDIT and all(x["status"] == "DISABLED" for x in _MC_AUDIT) else "PARTIAL"),
            "engine_observation_calls": len(_MC_AUDIT),
            "engine_observation_calls_with_mc_metrics": sum(x["status"] == "EXECUTED" for x in _MC_AUDIT),
            "total_simulations": sum(x["simulations"] for x in _MC_AUDIT),
            "converged_calls": sum(x["converged"] is True for x in _MC_AUDIT),
            "nonconverged_calls": sum(x["status"] == "EXECUTED" and x["converged"] is not True for x in _MC_AUDIT),
            "calls": list(_MC_AUDIT),
        },
        "holes": holes_all,
        "cuts": cutout,
        "R732": r732,
        "candidatos_final_P_0a3": _candidatos(lastP),
        "cuello_top5_engine": {"k": CUELLO_K, "aplicado": bool(cuello_log), "regla": CUELLO_REGLA,
                               "n_ejes_con_cuello": len(cuello_log),
                               "n_tokens_entrada": sum(len(r.get(e) or []) for r in cuts for e in ("P", "A", "C")),
                               "n_tokens_al_engine": sum(len(r.get(e) or []) for r in cuts for e in ("P", "A", "C")) - sum(len(x["quedan_fuera_del_engine"]) for x in cuello_log),
                               "n_tokens_fuera_del_engine": sum(len(x["quedan_fuera_del_engine"]) for x in cuello_log),
                               "cortes": cuello_log},
        "annex": annex,
        "protocolo": protocolo,
        "Alimenta_H": ALIMENTA_H,
    }


# Entry única drop-in (alias)
def correr_5x3(
    cuts: Sequence[Corte],
    pregunta: str = "caso",
    annex_traza: bool = True,
    obstaculo: Optional[str] = None,
    texto_polaridad: Optional[str] = None,
    monte_carlo: bool = True,
    marcador_limite: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Alias drop-in → correr_5x3_v15_3 (entry única V15.3 NATIVO)."""
    return correr_5x3_v15_3(
        cuts,
        pregunta=pregunta,
        annex_traza=annex_traza,
        obstaculo=obstaculo,
        texto_polaridad=texto_polaridad,
        monte_carlo=monte_carlo,
        marcador_limite=marcador_limite,
    )


def _smoke_protocolo_helpers() -> Dict[str, Any]:
    """Unit-test helpers sin Engine (si falta) o además del full run."""
    limpiar_bitacora()
    bh = nativo_bypass_hash(hash_esperado="aaa", hash_actual="bbb", rol="protocolo")
    assert bh.get("bypass") is True and bh.get("permitir_corrida") is True, bh
    pol = nativo_polaridad("no es que no explica el resultado")
    assert pol.get("etiqueta") == "DOBLE_NEGACION_LITOTE", pol
    assert pol.get("Alimenta_H") == "NO"
    lat = nativo_latencia("smoke_empate", p_momento=0.50, tokens=["t1"])
    assert lat.get("Alimenta_H") == "NO"
    assert (lat.get("expediente") or {}).get("estado") in (
        "ALMACENADO_ESPERANDO_DATOS",
        "DESEMPATE_DECIMO",
        "LATENCIA",
    ) or lat.get("accion")
    ap = nativo_aplicar_protocolo("No puedo: hash no idéntico al marcado")
    assert ap.get("parar") is False
    assert ap.get("Alimenta_H") == "NO"
    assert len(bitacora()) >= 1
    return {
        "bypass": True,
        "polaridad": pol["etiqueta"],
        "latencia_accion": lat.get("accion"),
        "parar": False,
        "bitacora_n": len(bitacora()),
        "Alimenta_H": "NO",
    }


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "ok": True,
                "file": "MOTOR_V15_3_NATIVO_V0_9_UNICO.py",  # U6 A7: antes nombraba MOTOR_V15_3_NATIVO.py (inexistente)
                "version": VERSION,
                "nativo": True,
                "capa": False,
                "Alimenta_H": ALIMENTA_H,
                "msg": "Entry: correr_5x3. Protocolo DENTRO. No capa V15.2. No edita Engine/244.",
            },
            ensure_ascii=False,
        )
    )

######################## 
