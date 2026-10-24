#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sidecar_corte_memento.py

CORTE MEMENTO — PRE-freeze.

No es "luces para saltar a H". Luces = insumo.
Memento = el mismo gesto que la ingeniería inversa, pero ANTES de lanzar H:
caminar el corte HACIA ATRÁS (último → penúltimo → … → inicio) y ver si la
proto-hipótesis SE SOSTIENE en cada momento anterior.

Si el presente es H, miras G, luego F, … hasta A.
El hombre de acero entra después (o enganchado) para validar en retrospectiva
si, quitando el pilar más fuerte, la lectura sigue en pie — sin reescribir freeze.

Candados: TOCA_F/244/Engine/FREEZE = NO. EMITE_PROTO_H = SÍ. ES_FREEZE = NO.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

VERSION = "0.3"
SCHEMA = "corte_memento_cadena_atras_v1"
PLUGIN = "sidecar_corte_memento"

CANDADOS = {
    "TOCA_F": "NO",
    "TOCA_244": "NO",
    "TOCA_Engine_V5": "NO",
    "TOCA_FREEZE": "NO",
    "EMITE_PROTO_H": "SI",
    "ES_FREEZE": "NO",
    "MOMENTO": "PRE_FREEZE_CADENA_ATRAS",
}

NEAR_TIE_ABS = 0.05
N_PERSIST_HILO = 3


# ---------------------------------------------------------------------------
# helpers tablero
# ---------------------------------------------------------------------------

def _as_ranked(items: Any) -> List[Tuple[str, float]]:
    out: List[Tuple[str, float]] = []
    if items is None:
        return out
    if isinstance(items, Mapping):
        for k, v in items.items():
            try:
                out.append((str(k), float(v)))
            except (TypeError, ValueError):
                continue
        return sorted(out, key=lambda x: -x[1])
    for it in items:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            try:
                out.append((str(it[0]), float(it[1])))
            except (TypeError, ValueError):
                continue
        elif isinstance(it, Mapping):
            tok = it.get("token") or it.get("familia") or it.get("name")
            sc = it.get("p", it.get("score", it.get("w")))
            if tok is None:
                continue
            try:
                out.append((str(tok), float(sc)))
            except (TypeError, ValueError):
                continue
        elif isinstance(it, str):
            out.append((it, 0.0))
    return sorted(out, key=lambda x: -x[1])


def _near_ties(ranked: List[Tuple[str, float]], eps: float) -> List[Dict[str, Any]]:
    if len(ranked) < 2:
        return []
    top_sc = ranked[0][1]
    return [
        {"token": tok, "score": sc, "delta_vs_top": round(top_sc - sc, 6)}
        for tok, sc in ranked[1:]
        if abs(top_sc - sc) <= eps
    ]


def _cut_id(c: Mapping[str, Any], i: int) -> str:
    return str(c.get("id", c.get("corte", f"C{i+1}")))


def _tokens_in_cut(c: Mapping[str, Any]) -> Dict[str, Set[str]]:
    """token → ejes presentes en ese corte."""
    out: Dict[str, Set[str]] = {}
    for ax in ("P", "A", "C"):
        for tok, _sc in _as_ranked(c.get(ax) or c.get(f"{ax}_top") or []):
            out.setdefault(tok, set()).add(ax)
    for tok in c.get("tokens") or []:
        t = tok if isinstance(tok, str) else str(tok.get("token", tok))
        out.setdefault(t, set()).add("?")
    return out


def _persistencia(cuts: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    tok_cuts: Dict[str, Set[str]] = {}
    tok_axes: Dict[str, Set[str]] = {}
    order: List[str] = []
    for i, c in enumerate(cuts):
        cid = _cut_id(c, i)
        order.append(cid)
        for tok, axes in _tokens_in_cut(c).items():
            tok_cuts.setdefault(tok, set()).add(cid)
            tok_axes.setdefault(tok, set()).update(axes)

    def max_consec(cs: Set[str]) -> int:
        best = cur = 0
        for cid in order:
            if cid in cs:
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        return best

    out: Dict[str, Dict[str, Any]] = {}
    for t, cs in tok_cuts.items():
        out[t] = {
            "n_cortes": len(cs),
            "consec_max": max_consec(cs),
            "cortes": sorted(cs, key=lambda x: order.index(x) if x in order else 999),
            "ejes": sorted(tok_axes.get(t, [])),
        }
    return out


# ---------------------------------------------------------------------------
# luces = INSUMO (no es Memento)
# ---------------------------------------------------------------------------

def build_luces(
    board_z: Mapping[str, Any],
    *,
    cuts: Optional[Sequence[Mapping[str, Any]]] = None,
    r732: Optional[Mapping[str, Any]] = None,
    ya_vistos: Optional[Iterable[str]] = None,
    near_tie_eps: float = NEAR_TIE_ABS,
) -> Dict[str, Any]:
    P = _as_ranked(board_z.get("P") or board_z.get("P_top5") or board_z.get("P_top5_ANEXO"))
    A = _as_ranked(board_z.get("A") or board_z.get("A_top5") or board_z.get("A_top5_ANEXO"))
    C = _as_ranked(board_z.get("C") or board_z.get("C_top5") or board_z.get("C_top5_ANEXO"))
    luces = {
        "P": [{"token": t, "score": s} for t, s in P[:8]],
        "A": [{"token": t, "score": s} for t, s in A[:8]],
        "C": [{"token": t, "score": s} for t, s in C[:8]],
    }
    empates = {"P": _near_ties(P, near_tie_eps), "A": _near_ties(A, near_tie_eps), "C": _near_ties(C, near_tie_eps)}
    persist = _persistencia(cuts or []) if cuts else {}
    persist_top = sorted(
        ({"token": t, **v} for t, v in persist.items()),
        key=lambda x: (-x["consec_max"], -x["n_cortes"], x["token"]),
    )[:15]
    vistos = {str(x) for x in (ya_vistos or [])}
    board_toks = {t for t, _ in P[:5]} | {t for t, _ in A[:5]} | {t for t, _ in C[:5]}
    almost = sorted(board_toks - vistos) if vistos else sorted({x["token"] for ax in empates.values() for x in ax})
    alertas: List[str] = []
    if empates["P"]:
        alertas.append("empate_o_casi_empate_en_P — no coronar Top1")
    if empates["C"]:
        alertas.append("rival_en_C_casi_empatado")
    if empates["A"]:
        alertas.append("presion_o_rival_en_A — posible rival de colapso/obstaculo")
    if r732:
        pk = r732.get("persist_cos") or r732.get("last_persist_cos")
        kk = r732.get("kappa_dir") or r732.get("last_kappa_dir")
        if isinstance(pk, (int, float)) and pk < 0.2:
            alertas.append("R732_persist_bajo — vector sucio; no forzar Top1")
        if isinstance(kk, (int, float)) and kk > 0.95:
            alertas.append("R732_kappa_alto — dirección rígida; mirar rivales")
    return {
        "luces_Z": luces,
        "casi_empates": empates,
        "persistencia_top": persist_top,
        "almost_missed": almost,
        "alertas": alertas,
        "r732": dict(r732) if r732 else None,
    }


def solo_luces(board_z: Mapping[str, Any], **kw: Any) -> Dict[str, Any]:
    """Solo insumo. NO es Corte Memento."""
    return {"plugin": "solo_luces", "nota": "NO es Memento", **build_luces(board_z, **kw)}


# ---------------------------------------------------------------------------
# proto-H desde hilos (candidata; no freeze)
# ---------------------------------------------------------------------------

def _proto_desde_hilos(
    persist_top: Sequence[Mapping[str, Any]],
    luces: Mapping[str, Any],
    empates: Mapping[str, Any],
    *,
    proto_override: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    if proto_override:
        return {
            "fuente": "operador",
            "H1_candidata": proto_override.get("H1_candidata") or proto_override.get("h1"),
            "H2_candidatas": list(proto_override.get("H2_candidatas") or proto_override.get("h2") or []),
            "apuesta_candidata": proto_override.get("apuesta_candidata") or proto_override.get("apuesta"),
            "nucleo_tokens": list(proto_override.get("nucleo_tokens") or []),
            "raw": dict(proto_override),
        }

    hilos = [r for r in persist_top if int(r.get("consec_max") or 0) >= N_PERSIST_HILO]
    by_axis: Dict[str, List[str]] = {"P": [], "A": [], "C": []}
    nucleo_tokens: List[str] = []
    for h in hilos:
        if h["token"] not in nucleo_tokens:
            nucleo_tokens.append(h["token"])
        for ax in h.get("ejes") or []:
            if ax in by_axis and h["token"] not in by_axis[ax]:
                by_axis[ax].append(h["token"])

    nucleo_parts = [f"{ax}:{'+'.join(by_axis[ax][:3])}" for ax in ("P", "A", "C") if by_axis[ax]]
    nucleo = " | ".join(nucleo_parts) if nucleo_parts else None

    if nucleo:
        h1 = f"configuracion_por_hilos_persistentes [{nucleo}] (no Top1)"
    else:
        tops = []
        for ax in ("P", "A", "C"):
            luc = (luces or {}).get(ax) or []
            if luc:
                tops.append(f"{ax}:{luc[0]['token']}")
        h1 = (
            "SIN_HILO_PERSISTENTE_CLARO — no coronar Top1; "
            f"board_top=[{', '.join(tops)}]; exigir más cortes o override operador"
        )

    h2: List[str] = []
    for ax, ties in (empates or {}).items():
        for t in ties:
            h2.append(f"rival_{ax}={t['token']} (casi-empate vs Top1)")
    luc_c = (luces or {}).get("C") or []
    if luc_c and (not by_axis["C"] or luc_c[0]["token"] not in by_axis["C"]):
        lab = f"rival_C_top={luc_c[0]['token']} (prestigio/fama vs nucleo)"
        if lab not in h2:
            h2.append(lab)
    luc_a = (luces or {}).get("A") or []
    if luc_a and (not by_axis["A"] or luc_a[0]["token"] not in by_axis["A"]):
        lab = f"rival_A_top={luc_a[0]['token']} (presion/colapso vs nucleo)"
        if lab not in h2:
            h2.append(lab)

    if nucleo and h2:
        apuesta = "H1_configuracion > rivales_declarados en tramo sellado post-Z"
    elif nucleo:
        apuesta = "H1_configuracion se sostiene; rivales aún no tipificados"
    else:
        apuesta = "NO_APOSTAR_AUN — falta hilo o override operador"

    return {
        "fuente": "heuristica_hilos",
        "H1_candidata": h1,
        "H2_candidatas": h2,
        "apuesta_candidata": apuesta,
        "nucleo_tokens": nucleo_tokens,
        "nucleo_hilos": {
            "por_eje": by_axis,
            "hilos": [
                {"token": h["token"], "consec_max": h["consec_max"], "ejes": h.get("ejes")}
                for h in hilos[:8]
            ],
        },
        "regla": "H1 = configuración de hilos, nunca Top1 solo porque gane el board",
    }


# ---------------------------------------------------------------------------
# CADENA HACIA ATRÁS — núcleo del Memento
# ---------------------------------------------------------------------------

def _sostiene_en_prefijo(
    nucleo_tokens: Sequence[str],
    prefix_cuts: Sequence[Mapping[str, Any]],
    *,
    min_nucleo_visibles: int = 1,
) -> Dict[str, Any]:
    """
    ¿La proto se 've' ya en este momento anterior?
    Criterio operativo: cuántos tokens del núcleo aparecen en el prefijo
    (cortes desde el inicio hasta este inclusive).
    """
    present: Set[str] = set()
    for c in prefix_cuts:
        present |= set(_tokens_in_cut(c).keys())
    visibles = [t for t in nucleo_tokens if t in present]
    faltan = [t for t in nucleo_tokens if t not in present]
    if not nucleo_tokens:
        holds = False
        motivo = "sin_nucleo_declarado"
    elif len(visibles) >= min_nucleo_visibles:
        holds = True
        motivo = f"nucleo_visible_{len(visibles)}/{len(nucleo_tokens)}"
    else:
        holds = False
        motivo = f"nucleo_ausente_o_insuficiente_{len(visibles)}/{len(nucleo_tokens)}"
    return {
        "holds": holds,
        "motivo": motivo,
        "nucleo_visibles": visibles,
        "nucleo_faltan": faltan,
        "n_cortes_prefijo": len(prefix_cuts),
    }


def caminata_atras(
    cuts: Sequence[Mapping[str, Any]],
    nucleo_tokens: Sequence[str],
    *,
    min_nucleo_visibles: int = 1,
) -> Dict[str, Any]:
    """
    Si el último corte es H, camina H → G → F → … → A.
    En cada paso pregunta: ¿la proto se sostiene mirando solo hasta aquí?
    """
    if not cuts:
        return {
            "orden": "atras",
            "pasos": [],
            "sostenida_hasta_inicio": False,
            "primer_quiebre": None,
            "nota": "sin cortes — no hay cadena",
        }

    n = len(cuts)
    # Letras en orden cronológico: primer corte = A, luego B, C, … (máx Z)
    # La caminata empieza en la ÚLTIMA letra y baja hasta A.
    if n > 26:
        chrono_letters = [f"C{i}" for i in range(n)]  # fallback si >26
    else:
        chrono_letters = [chr(ord("A") + i) for i in range(n)]

    pasos: List[Dict[str, Any]] = []
    primer_quiebre = None
    for back_rank in range(n):  # 0 = último, n-1 = inicio
        idx = n - 1 - back_rank
        letter = chrono_letters[idx]
        prefix = cuts[: idx + 1]
        cid = _cut_id(cuts[idx], idx)
        check = _sostiene_en_prefijo(
            nucleo_tokens, prefix, min_nucleo_visibles=min_nucleo_visibles
        )
        paso = {
            "letra": letter,  # A.. en cronología
            "pasos_desde_el_final": back_rank,  # 0=último, 1=penúltimo, ...
            "indice_cronologico": idx,
            "corte_id": cid,
            "rol": (
                "ultimo"
                if idx == n - 1
                else ("inicio_A" if idx == 0 else "intermedio")
            ),
            **check,
        }
        pasos.append(paso)
        if not check["holds"] and primer_quiebre is None:
            primer_quiebre = {
                "letra": letter,
                "corte_id": cid,
                "indice_cronologico": idx,
                "motivo": check["motivo"],
            }

    sostenida_hasta_inicio = bool(pasos) and all(p["holds"] for p in pasos)
    holds_at_A = bool(pasos) and pasos[-1]["holds"]

    return {
        "orden": "atras_ultima_letra_hacia_A",
        "letras_cronologicas": chrono_letters,
        "n_cortes": n,
        "pasos": pasos,
        "sostenida_en_toda_la_cadena": sostenida_hasta_inicio,
        "sostenida_al_llegar_al_inicio": holds_at_A,
        "primer_quiebre": primer_quiebre,
        "lectura": (
            "proto se sostiene mirando hacia atrás hasta A"
            if sostenida_hasta_inicio
            else (
                f"quiebra al llegar a {primer_quiebre['letra']} ({primer_quiebre['corte_id']})"
                if primer_quiebre
                else "cadena incompleta"
            )
        ),
    }


def _marcaje_atencion(luces_pack: Mapping[str, Any]) -> Dict[str, Any]:
    demasiada: List[str] = []
    insuficiente: List[str] = []
    for ax, ties in (luces_pack.get("casi_empates") or {}).items():
        if ties:
            top = (luces_pack.get("luces_Z") or {}).get(ax) or []
            if top:
                demasiada.append(
                    f"Top1_{ax}={top[0]['token']} (hay casi-empate; coronarlo sería sobreatención)"
                )
            for t in ties:
                insuficiente.append(f"rival_{ax}={t['token']} (casi empatado; fácil de ignorar)")
    for row in (luces_pack.get("persistencia_top") or [])[:6]:
        if int(row.get("consec_max") or 0) >= N_PERSIST_HILO:
            top_tokens = {
                x["token"]
                for ax in ("P", "A", "C")
                for x in ((luces_pack.get("luces_Z") or {}).get(ax) or [])[:1]
            }
            if row["token"] not in top_tokens:
                insuficiente.append(
                    f"hilo_persistente={row['token']} "
                    f"(consec={row['consec_max']}, ejes={row.get('ejes')}; no es Top1 Z)"
                )
    for tok in luces_pack.get("almost_missed") or []:
        insuficiente.append(f"almost_missed={tok}")

    def uniq(xs: List[str]) -> List[str]:
        seen, out = set(), []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    return {
        "demasiada_atencion_si_se_lanza_ya": uniq(demasiada),
        "insuficiente_atencion_si_se_lanza_ya": uniq(insuficiente),
        "nota": (
            "Marcaje PRE-H. La ingén. inversa POST-Z-final repite la pregunta "
            "contra el freeze sellado; no reescribe H. El hombre de acero valida pilares."
        ),
    }


def _evidencias_desde_hilos(
    persist_top: Sequence[Mapping[str, Any]],
    nucleo_tokens: Sequence[str],
) -> List[Dict[str, Any]]:
    """Piezas para enganchar hombre de acero (read-only)."""
    by_tok = {r["token"]: r for r in persist_top}
    evidencias = []
    for i, tok in enumerate(nucleo_tokens):
        row = by_tok.get(tok) or {}
        ejes = row.get("ejes") or ["P"]
        evidencias.append(
            {
                "id": f"M{i+1}",
                "token": tok,
                "axis": ejes[0] if ejes else "P",
                "cuts": list(row.get("cortes") or []),
                "lenses": [f"tubo_{ejes[0]}" if ejes else "tubo"],
                "consec": int(row.get("consec_max") or 0),
                "pac_direct": True,
            }
        )
    return evidencias


def enganchar_acero(
    evidencias: Sequence[Mapping[str, Any]],
    *,
    n_persist: int = 4,
) -> Dict[str, Any]:
    """
    Valida en retrospectiva (estilo hombre de acero) si la proto se sostiene
    quitando pilares fuertes. No reescribe freeze ni proto.
    """
    try:
        from sidecar_ablacion_hombre_acero import ablar_hombre_acero
    except ImportError:
        try:
            from sidecar_ablacion_hombre_acero import run_ablacion as _run

            return {
                "enganchado": True,
                "fuente": "run_ablacion",
                "reporte": _run({"evidencias": list(evidencias), "n_persist": n_persist}),
            }
        except ImportError as e:
            return {"enganchado": False, "error": f"acero_no_importable: {e}"}

    try:
        rep = ablar_hombre_acero(list(evidencias), n_persist=n_persist)
        return {"enganchado": True, "fuente": "ablar_hombre_acero", "reporte": rep}
    except TypeError:
        # firma distinta
        try:
            from sidecar_ablacion_hombre_acero import run_ablacion

            return {
                "enganchado": True,
                "fuente": "run_ablacion",
                "reporte": run_ablacion({"evidencias": list(evidencias), "n_persist": n_persist}),
            }
        except Exception as e:
            return {"enganchado": False, "error": str(e)}
    except Exception as e:
        return {"enganchado": False, "error": str(e)}


# ---------------------------------------------------------------------------
# API principal
# ---------------------------------------------------------------------------

def corte_memento(
    board_z: Mapping[str, Any],
    *,
    cuts: Optional[Sequence[Mapping[str, Any]]] = None,
    r732: Optional[Mapping[str, Any]] = None,
    ya_vistos: Optional[Iterable[str]] = None,
    near_tie_eps: float = NEAR_TIE_ABS,
    proto_override: Optional[Mapping[str, Any]] = None,
    min_nucleo_visibles: int = 1,
    con_acero: bool = True,
    n_persist_acero: int = 4,
) -> Dict[str, Any]:
    """
    Memento = caminata atrás + proto-H (+ acero opcional).

    Orden mental: si estás en H, miras G, F, … hasta A y preguntas
    en cada momento si la proto se sostiene. Luces solo alimentan.
    """
    cuts = list(cuts or [])
    luces_pack = build_luces(
        board_z,
        cuts=cuts,
        r732=r732,
        ya_vistos=ya_vistos,
        near_tie_eps=near_tie_eps,
    )
    proto = _proto_desde_hilos(
        luces_pack.get("persistencia_top") or [],
        luces_pack.get("luces_Z") or {},
        luces_pack.get("casi_empates") or {},
        proto_override=proto_override,
    )
    nucleo = list(proto.get("nucleo_tokens") or [])
    cadena = caminata_atras(cuts, nucleo, min_nucleo_visibles=min_nucleo_visibles)
    marcaje = _marcaje_atencion(luces_pack)

    evidencias = _evidencias_desde_hilos(luces_pack.get("persistencia_top") or [], nucleo)
    acero = enganchar_acero(evidencias, n_persist=n_persist_acero) if con_acero and evidencias else {
        "enganchado": False,
        "motivo": "sin_evidencias_o_con_acero_false",
    }

    return {
        "plugin": PLUGIN,
        "schema": SCHEMA,
        "version": VERSION,
        "candados": dict(CANDADOS),
        "distincion": {
            "luces": "INSUMO",
            "memento": "PRODUCTO = caminata atrás (H→…→A) + proto-H + ¿se sostiene?",
            "hombre_de_acero": "VALIDA en retrospectiva pilares; no reescribe freeze",
            "ingenieria_inversa_post": "POST-Z-final contra freeze sellado; paso distinto",
        },
        "insumo_luces": {
            "luces_Z": luces_pack["luces_Z"],
            "casi_empates": luces_pack["casi_empates"],
            "persistencia_top": luces_pack["persistencia_top"],
            "almost_missed": luces_pack["almost_missed"],
            "alertas": luces_pack["alertas"],
            "r732": luces_pack["r732"],
        },
        "proto_hipotesis": proto,
        "cadena_atras": cadena,
        "marcaje_atencion": marcaje,
        "hombre_de_acero": acero,
        "para_retrospectiva": {
            "usar_despues": (
                "Comparar proto + cadena_atras + veredicto acero vs H congelada "
                "y vs outcome. Documentar delta; no reescribir freeze."
            ),
            "prohibido": "No promover proto a freeze sin paso de congelado explícito.",
        },
        "prohibiciones": [
            "NO_confundir_luces_con_memento",
            "NO_tratar_proto_como_freeze",
            "NO_usar_hechos_post_Z",
            "NO_coronar_Top1_como_H1",
            "NO_tocar_F_ni_244_ni_Engine",
        ],
        "nota": (
            "Memento = ir hacia atrás corte a corte y ver si la proto se sostiene. "
            "Acero valida pilares en ese marco retrospectivo."
        ),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Corte Memento: caminata atrás H→A + proto-H (+ acero)"
    )
    ap.add_argument("-i", "--input", required=True, help="JSON path o '-'")
    ap.add_argument("-o", "--out", help="ruta JSON salida")
    ap.add_argument("--solo-luces", action="store_true", help="Solo insumo luces (NO Memento)")
    ap.add_argument("--sin-acero", action="store_true", help="No enganchar hombre de acero")
    args = ap.parse_args(list(argv) if argv is not None else None)

    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))

    board = data.get("board_z") or data.get("board") or data
    if args.solo_luces:
        report = solo_luces(
            board,
            cuts=data.get("cuts") or data.get("cortes"),
            r732=data.get("r732"),
            ya_vistos=data.get("ya_vistos"),
            near_tie_eps=float(data.get("near_tie_eps", NEAR_TIE_ABS)),
        )
    else:
        report = corte_memento(
            board,
            cuts=data.get("cuts") or data.get("cortes"),
            r732=data.get("r732"),
            ya_vistos=data.get("ya_vistos"),
            near_tie_eps=float(data.get("near_tie_eps", NEAR_TIE_ABS)),
            proto_override=data.get("proto_override") or data.get("proto"),
            min_nucleo_visibles=int(data.get("min_nucleo_visibles", 1)),
            con_acero=not args.sin_acero and data.get("con_acero", True),
            n_persist_acero=int(data.get("n_persist_acero", 4)),
        )

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
