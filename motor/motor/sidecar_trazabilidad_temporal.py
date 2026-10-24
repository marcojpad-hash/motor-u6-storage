#!/usr/bin/env python3
"""
sidecar_trazabilidad_temporal.py

Capa general de trazabilidad temporal.
Cableada al bus Capa 2 vía sidecar_luces_gemini_packs (hilado por corte).
NO se fusiona al tubo limpio / Engine / 244 / F / FREEZE.

Candados:
TOCA_F: NO
TOCA_244: NO
TOCA_Engine_V5: NO

Modelo mínimo por token:
  ON        evidencia presente en el corte actual
  PARPADEO  última evidencia hace 1..k cortes
  NO_APARECIDO_AUN  todavía no hubo una primera aparición
  OFF       última evidencia hace más de k cortes

PATCH 004 (2026-10-06): el estado "todavía no apareció" se llamaba LATENCIA; se renombra
NO_APARECIDO_AUN porque LATENTE/LATENCIA en el vocabulario de Mj = factor faltante
(cierre en espera de datos), no "token aún no visto". Lee cortes con clave `tokens`
(bus Capa 2 / luces) Y cortes P/A/C del contrato de entrada ([token, peso] por eje).

La capa registra observaciones temporales. No decide H1/H2, no suma evidencia,
no clasifica falacias y no sustituye los sidecars de dominio.
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping, Sequence

ESTADOS = ("ON", "PARPADEO", "NO_APARECIDO_AUN", "OFF")
EJES_PAC = ("P", "A", "C")
K_PROPUESTO = 2
TOKEN_RECUPERACION_DEFECTO = "salud_recuperacion"


def _items(raw: Any) -> set[str]:
    if isinstance(raw, Mapping):
        return {str(k) for k in raw}
    out: set[str] = set()
    for item in raw or []:
        if isinstance(item, str):
            out.add(item)
        elif isinstance(item, Mapping) and "token" in item:
            out.add(str(item["token"]))
        elif isinstance(item, (list, tuple)) and item:
            out.add(str(item[0]))
    return out


def _tokens_por_eje(cut: Mapping[str, Any]) -> Dict[str, set]:
    """PATCH 004: ejes P/A/C del contrato de entrada ([token, peso])."""
    return {e: _items(cut.get(e)) for e in EJES_PAC if cut.get(e)}


def _tokens(cut: Mapping[str, Any]) -> set[str]:
    out = _items(cut.get("tokens", []))
    for toks in _tokens_por_eje(cut).values():
        out |= toks
    return out


def _cut_id(cut: Mapping[str, Any], fallback: int) -> Any:
    return cut.get("id", fallback)


def _normalizar_recuperaciones(
    cut: Mapping[str, Any],
    recovery_tokens: set[str],
) -> bool:
    names = _tokens(cut)
    if names & recovery_tokens:
        return True
    # Permite una marca explícita genérica sin obligar al sidecar a conocer
    # dominios concretos.
    return bool(cut.get("recuperacion", False))


def _estado(aparece: bool, ultima: int | None, actual: int, k: int) -> str:
    if aparece:
        return "ON"
    if ultima is None:
        return "NO_APARECIDO_AUN"
    gap = actual - ultima
    return "PARPADEO" if gap <= k else "OFF"


def trazar_temporal(
    cortes: Sequence[Mapping[str, Any]],
    *,
    k: int = K_PROPUESTO,
    recovery_tokens: Iterable[str] | None = None,
    known_tokens: Iterable[str] | None = None,
    geometria: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Traza todos los tokens conservando su aparición por corte.

    PATCH 009: `geometria` (opcional, aditivo) = compacto del puente Souriau/Caldero/Polti
    (laterales_unico_v1.marco_7783_geometria). Si llega, se adjunta y se alinea por corte con
    los tokens ON de cada corte. No cambia ningún estado de token; sin `geometria` la salida es idéntica.

    k es una propuesta de diseño, no una constante del motor canónico.
    """
    if not isinstance(k, int) or k < 1:
        raise ValueError("k debe ser entero >= 1")

    cuts = list(cortes)
    rec_tokens = set(recovery_tokens or (TOKEN_RECUPERACION_DEFECTO,))
    names_by_cut = [_tokens(c) for c in cuts]
    observed_tokens = set().union(*names_by_cut) if names_by_cut else set()
    all_tokens = sorted(observed_tokens | set(str(x) for x in (known_tokens or ())))

    records: List[Dict[str, Any]] = []
    for token in all_tokens:
        appearances = [i for i, names in enumerate(names_by_cut) if token in names]
        first = appearances[0] if appearances else None
        last = appearances[-1] if appearances else None
        current = len(cuts) - 1
        state = _estado(token in (names_by_cut[current] if cuts else set()), last, current, k) if cuts else "NO_APARECIDO_AUN"

        recovery_between: List[Any] = []
        if len(appearances) >= 2:
            for a, b in zip(appearances, appearances[1:]):
                if any(_normalizar_recuperaciones(cuts[j], rec_tokens) for j in range(a + 1, b)):
                    recovery_between.append({
                        "desde": _cut_id(cuts[a], a),
                        "hasta": _cut_id(cuts[b], b),
                    })

        records.append({
            "token": token,
            "primera_aparicion": _cut_id(cuts[first], first) if first is not None else None,
            "ultima_aparicion": _cut_id(cuts[last], last) if last is not None else None,
            "apariciones": [_cut_id(cuts[i], i) for i in appearances],
            "ejes_por_aparicion": {str(_cut_id(cuts[i], i)): sorted(e for e, ts in _tokens_por_eje(cuts[i]).items() if token in ts) for i in appearances},
            "estado_actual": state,
            "hay_recuperacion_entre": bool(recovery_between),
            "recuperaciones_entre": recovery_between,
            "confirmacion_automatica": False,
        })

    # Segmentos generales: una recuperación separa episodios candidatos para
    # los sidecars que decidan consumir esta salida. La capa no interpreta el
    # dominio ni bautiza los episodios como "reactivación".
    segmentos: List[Dict[str, Any]] = []
    if cuts:
        inicio = 0
        for i, cut in enumerate(cuts):
            if i > inicio and _normalizar_recuperaciones(cut, rec_tokens):
                segmentos.append({
                    "inicio": _cut_id(cuts[inicio], inicio),
                    "fin": _cut_id(cuts[i - 1], i - 1),
                    "cortes": [_cut_id(cuts[j], j) for j in range(inicio, i)],
                })
                inicio = i
        segmentos.append({
            "inicio": _cut_id(cuts[inicio], inicio),
            "fin": _cut_id(cuts[-1], len(cuts) - 1),
            "cortes": [_cut_id(cuts[j], j) for j in range(inicio, len(cuts))],
        })

    out = {
        "plugin": "sidecar_trazabilidad_temporal",
        "estado": "CABLEADO_BUS_LATERAL",
        "k_estado": "PROPUESTA_EMPIRICA",
        "TOCA_F": "NO",
        "TOCA_244": "NO",
        "TOCA_Engine_V5": "NO",
        "k": k,
        "k_es": "ventana_de_cortes_para_parpadeo",
        "k_justificacion": "valor_propuesto_para_continuidad_corta; requiere_validacion_empirica_antes_de_cualquier_candado",
        "recovery_tokens": sorted(rec_tokens),
        "known_tokens": sorted(set(str(x) for x in (known_tokens or ()))),
        "tokens": records,
        "conteo_estados": {e: sum(1 for r in records if r["estado_actual"] == e) for e in ESTADOS},
        "lectura_entrada": "tokens|P/A/C (PATCH 004)",
        "nota_estados": "NO_APARECIDO_AUN = token conocido aún no visto; NO es LATENTE (factor faltante, vocabulario Mj)",
        "segmentos": segmentos,
        "falacias": None,
        "copi": None,
    }
    if geometria:
        # PATCH 009: capa geométrica aditiva (no decide; no altera tokens/estados).
        geo_by = {str(g.get("corte")): g for g in (geometria.get("por_corte") or []) if isinstance(g, Mapping)}
        ani_by = {str(g.get("corte")): g for g in ((geometria.get("anillos") or {}).get("por_corte") or []) if isinstance(g, Mapping)}
        alineado = []
        for i, c in enumerate(cuts):
            cid = _cut_id(c, i)
            g = geo_by.get(str(cid)) or {}
            a = ani_by.get(str(cid)) or {}
            alineado.append({
                "corte": cid,
                "n_tokens_en_corte": len(names_by_cut[i]),
                "n_tokens_primera_aparicion": sum(1 for r in records if r["primera_aparicion"] == cid),
                "zona_7783": g.get("zona"), "vector_funciones": g.get("vector_funciones"),
                "cuadrantes": g.get("cuadrantes"), "polti_idx": g.get("polti_idx"),
                "fase_anillos": a.get("fase"), "vector_interseccion": a.get("vector_interseccion"),
            })
        out["capa_geometrica_souriau_caldero_polti"] = {
            "fuente": geometria.get("fuente"), "aditivo_no_decide": True, "can_decide_H": False,
            "alineado_por_corte": alineado, "deltas": geometria.get("deltas"), "resumen": geometria.get("resumen"),
            "anillos": geometria.get("anillos"), "vector_schema": geometria.get("vector_schema"),
            "brecha_7783": geometria.get("brecha_7783"),
        }
    return out


# Alias legible para callers que prefieran "analizar".
def analizar_temporal(cortes: Sequence[Mapping[str, Any]], **kwargs: Any) -> Dict[str, Any]:
    return trazar_temporal(cortes, **kwargs)


__all__ = [
    "ESTADOS", "K_PROPUESTO", "TOKEN_RECUPERACION_DEFECTO",
    "trazar_temporal", "analizar_temporal",
]
