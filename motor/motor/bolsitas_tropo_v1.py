#!/usr/bin/env python3
"""bolsitas_tropo_v1.py — CATÁLOGO BOLSITAS_TROPO (ids A–F) + ruteo · 2026-11-13

Qué es
  La spec SPEC_TROPOS_BOLSITAS_ARQUETIPOS.txt (2026-09-14, Marco → Claude) define las
  bolsitas como FAMILIAS DE MARCAJE (como arquetipos, no como destino): cada hallazgo de
  lenguaje figurado se mete en una bolsita (id corto A–F) que lo rutea a un ESTANTE.
  El catálogo estaba listado como "PRÓXIMO CÓDIGO (cuando se autorice implementar)"
  y nunca se escribió: el guardián de tropos (guardian_tropos_beristain_v1.py) SÍ corre
  y SÍ aparece en el RESULT (bloque TROPOS_BERISTAIN), pero sus hallazgos no se ruteaban
  a ninguna bolsita, así que "BOLSITAS_TROPO" tenía 0 menciones en los RESULT.

Qué hace este plugin
  `rastrear(bloques)` recibe los bloques de guardianes que produce correr_guardianes
  (guardianes_control_v1.py) y rutea cada hallazgo a su bolsita. Es SOLO ruteo
  (highlight): no decide H, no bloquea, no escribe Engine ni el catálogo 244,
  no sube p del 244, no congela H, no es Top1 de vida. can_decide_H=False.

Bolsitas (v0 — calibración, de la spec):
  A) ATENUACION        — LITOTE, EUFEMISMO                       → PERFIL / MARCO_EVALUATIVO
  B) INTENSIDAD        — HIPERBOLE (ironía/sarcasmo DESCARTADO) → PERFIL / MARCO_EVALUATIVO
  C) PARTE_POR_TODO    — SINECDOQUE, METONIMIA                  → PREGUNTA_SESGO si toca sellado
                                                                    (origen question); si no, PERFIL_VENTANA
  D) LOGICA_ENUNCIATIVA — POST_HOC_TEMPORAL (+ polaridad NIEGA /
                         DOBLE_NEGACION_LITOTE)                 → PREGUNTA_SESGO / LOGICA
                         severidad hard solo cuando el post_hoc afirma causa (DETECTADA)
  E) ELIPSIS           — ELIPSIS                                → PREGUNTA_SESGO si elide sellado
                                                                    (el riesgo del hallazgo menciona
                                                                    sellado/desenlace); si no, CAMPO
  F) DISFEMISMO ★      — DISFEMISMO (REGULARIZADO: rasgo de perfil estable, no veredicto
                         de violencia/autoridad)                  → PERFILAMIENTO, bandera PERFIL_DISFEMISMO

Lo que NO tiene bolsita en v0
  Los demás tropos del inventario del guardián (METAFORA, HIPALAGE, OXIMORON,
  SINESTESIA, CATACRESIS, ANTONOMASIA, IMAGEN, PARADOJA, ANTITESIS, ALUSION,
  PERIFRASIS, COMPARACION, ALEGORIA, PROSOPOPEYA) y los tipos de pregunta
  dirigida que no son post_hoc quedan en "sin_bolsita_v0" con su motivo: no se
  inventa una bolsita y no se pierde el hallazgo (sigue en su bloque de guardián).
  IRONIA queda excluida por la spec (DESCARTADO) y se registra como tal.
"""
from __future__ import annotations

from typing import Any, Dict, List

VERSION = "1.0.0-20261113"
CANDADOS = {"can_decide_H": False, "escribe_H": False, "escribe_patterns": False, "reordena_candidatos": False,
            "funcion": "ruteo de hallazgos de tropos a bolsitas de marcaje (highlight only, no bloquea)",
            "fuente": "SPEC_TROPOS_BOLSITAS_ARQUETIPOS.txt (2026-09-14), ids A–F"}

# id → {nombre, formas que caza, estante, severidad, nota}
BOLSITAS_TROPO: Dict[str, Dict[str, Any]] = {
    "A": {"nombre": "ATENUACION", "formas": ["LITOTE", "EUFEMISMO"], "estante": "PERFIL / MARCO_EVALUATIVO",
          "severidad": "soft",
          "descripcion": "lítotes (no + adj / no + V + adj) y eufemismo (suavizar lo duro)"},
    "B": {"nombre": "INTENSIDAD", "formas": ["HIPERBOLE"], "estante": "PERFIL / MARCO_EVALUATIVO",
          "severidad": "soft",
          "descripcion": "hipérbole (superlativo + exclusividad temporal); ironía/sarcasmo DESCARTADO por la spec"},
    "C": {"nombre": "PARTE_POR_TODO", "formas": ["SINECDOQUE", "METONIMIA"],
          "estante": "PREGUNTA_SESGO si toca sellado (origen question); si no, PERFIL_VENTANA",
          "severidad": "soft",
          "descripcion": "sinécdoque y metonimia (tabla por sujeto/caso, no detección sintáctica genérica)"},
    "D": {"nombre": "LOGICA_ENUNCIATIVA", "formas": ["POST_HOC_TEMPORAL", "NIEGA", "DOBLE_NEGACION_LITOTE"],
          "estante": "PREGUNTA_SESGO / LOGICA",
          "severidad": "soft salvo hard cuando el post_hoc afirma causa (DETECTADA)",
          "descripcion": "post_hoc temporal→causal (+ polaridad del claim causal)"},
    "E": {"nombre": "ELIPSIS", "formas": ["ELIPSIS"],
          "estante": "PREGUNTA_SESGO si elide sellado; si no, CAMPO",
          "severidad": "soft",
          "descripcion": "omisión de núcleo recuperable por contexto"},
    "F": {"nombre": "DISFEMISMO", "formas": ["DISFEMISMO"], "estante": "PERFILAMIENTO",
          "severidad": "soft", "bandera": "PERFIL_DISFEMISMO",
          "descripcion": "nombrar lo duro con registro áspero; REGULARIZADO = rasgo de perfil estable, "
                         "no veredicto de violencia/autoridad por default"},
}

# Tropo del guardián → bolsita. IRONIA no entra (spec: DESCARTADO).
_TROPO_A_BOLSITA = {"LITOTE": "A", "EUFEMISMO": "A", "HIPERBOLE": "B", "SINECDOQUE": "C",
                    "METONIMIA": "C", "ELIPSIS": "E", "DISFEMISMO": "F"}
# Bloques que alimentan las bolsitas (los demás bloques no son tropos/lógica enunciativa).
_BLOQUES_FUENTE = ("TROPOS_BERISTAIN", "PREGUNTA_DIRIGIDA_POST_HOC", "POLARIDAD_CAUSAL")


def _estante(bolsita: str, hallazgo: Dict[str, Any]) -> str:
    """Estante del hallazgo dentro de su bolsita (regla determinista, del propio hallazgo)."""
    if bolsita == "C":
        return "PREGUNTA_SESGO" if hallazgo.get("origen") == "question" else "PERFIL_VENTANA"
    if bolsita == "E":
        riesgo = str(hallazgo.get("riesgo") or "")
        if "sellado" in riesgo or "desenlace" in riesgo:
            return "PREGUNTA_SESGO"
        return "CAMPO"
    return BOLSITAS_TROPO[bolsita]["estante"]


def _severidad(bolsita: str, marca: Dict[str, Any]) -> str:
    if bolsita == "D" and marca.get("tipo") == "POST_HOC_TEMPORAL" and marca.get("estado") == "DETECTADA":
        return "hard"
    return BOLSITAS_TROPO[bolsita].get("severidad", "soft")


def _resumen_hallazgo(guardian: str, marca: Dict[str, Any], tropo: Dict[str, Any]) -> Dict[str, Any]:
    ev = marca.get("evidencia") or {}
    out: Dict[str, Any] = {"guardian": guardian, "tipo": marca.get("tipo"), "estado": marca.get("estado"),
                           "tropo": tropo.get("tropo"), "subtipo": tropo.get("subtipo"),
                           "origen": ev.get("origen"), "fragmento": ev.get("fragmento"),
                           "regla": (ev.get("regla") if isinstance(ev, dict) else None)}
    if tropo.get("riesgo"):
        out["riesgo"] = tropo.get("riesgo")
    return out


def rastrear(bloques: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Rutea los hallazgos de los bloques de guardianes a las bolsitas A–F.

    Entrada: lista de bloques como los que devuelve correr_guardianes (cada bloque trae
    "guardian" y "marcas"). Salida: dict con el catálogo, una entrada por bolsita
    (prendió, n, estante, hallazgos) y los hallazgos sin bolsita en v0. Puro ruteo:
    no toca H, no bloquea, no escribe nada fuera de este dict.
    """
    per: Dict[str, Dict[str, Any]] = {}
    for bid, spec in BOLSITAS_TROPO.items():
        per[bid] = {"id": bid, "nombre": spec["nombre"], "prendio": False, "n": 0,
                    "estante": spec["estante"], "severidad": spec["severidad"],
                    "descripcion": spec["descripcion"], "hallazgos": []}
    sin_bolsita: List[Dict[str, Any]] = []
    n_derivadas = 0
    for b in bloques or []:
        g = b.get("guardian")
        if g not in _BLOQUES_FUENTE:
            continue
        for m in b.get("marcas") or []:
            tipo = str(m.get("tipo") or "")
            if g == "TROPOS_BERISTAIN":
                tropo = m.get("tropo")
                if not isinstance(tropo, dict):
                    # Marca derivada (TOKEN_POSIBLEMENTE_FIGURADO_EN_TABLERO, VECINO_*): ya está
                    # cubierta por su tropo padre; no se vuelve a rutear.
                    n_derivadas += 1
                    continue
                nombre = str(tropo.get("tropo") or "")
                if nombre == "IRONIA":
                    sin_bolsita.append({"guardian": g, "tipo": tipo, "tropo": nombre,
                                        "estado": m.get("estado"),
                                        "motivo": "excluida_por_spec (ironía/sarcasmo DESCARTADO)"})
                    continue
                bid = _TROPO_A_BOLSITA.get(nombre)
                if bid is None:
                    sin_bolsita.append({"guardian": g, "tipo": tipo, "tropo": nombre,
                                        "estado": m.get("estado"), "motivo": "sin_bolsita_en_v0"})
                    continue
                h = _resumen_hallazgo(g, m, tropo)
                h["estante"] = _estante(bid, {**tropo, "origen": h.get("origen")})
                h["severidad"] = _severidad(bid, m)
                if bid == "F":
                    h["bandera"] = "PERFIL_DISFEMISMO"
                    h["regularizado"] = True
                    h["no_es_veredicto_de_hostilidad"] = True
                per[bid]["hallazgos"].append(h)
                per[bid]["n"] += 1
            elif g == "PREGUNTA_DIRIGIDA_POST_HOC":
                if tipo != "POST_HOC_TEMPORAL":
                    sin_bolsita.append({"guardian": g, "tipo": tipo, "tropo": None,
                                        "estado": m.get("estado"),
                                        "motivo": "sin_bolsita_en_v0 (pregunta dirigida, no post_hoc)"})
                    continue
                ev = m.get("evidencia") or {}
                h = {"guardian": g, "tipo": tipo, "estado": m.get("estado"), "tropo": "POST_HOC_TEMPORAL",
                     "subtipo": "POST_HOC_TEMPORAL", "origen": ev.get("origen"), "fragmento": ev.get("fragmento"),
                     "regla": None, "estante": BOLSITAS_TROPO["D"]["estante"],
                     "severidad": _severidad("D", m)}
                per["D"]["hallazgos"].append(h)
                per["D"]["n"] += 1
            elif g == "POLARIDAD_CAUSAL":
                if tipo not in ("NIEGA", "DOBLE_NEGACION_LITOTE"):
                    sin_bolsita.append({"guardian": g, "tipo": tipo, "tropo": None,
                                        "estado": m.get("estado"), "motivo": "sin_bolsita_en_v0"})
                    continue
                ev = m.get("evidencia") or {}
                h = {"guardian": g, "tipo": tipo, "estado": m.get("estado"), "tropo": tipo,
                     "subtipo": tipo, "origen": ev.get("origen"),
                     "fragmento": (ev.get("texto") or "")[:200] or ev.get("fragmento"),
                     "regla": None, "estante": BOLSITAS_TROPO["D"]["estante"],
                     "severidad": _severidad("D", m),
                     "nota": "la polaridad es parte de la bolsita D (post_hoc + polaridad); "
                             "DOBLE_NEGACION_LITOTE además confirma el lítote (A) por vecinos"}
                per["D"]["hallazgos"].append(h)
                per["D"]["n"] += 1
    for bid in per:
        per[bid]["prendio"] = per[bid]["n"] > 0
    n_ruteados = sum(per[bid]["n"] for bid in per)
    return {"catalogo": "BOLSITAS_TROPO", "version": VERSION, "status": "EXECUTED", **CANDADOS,
            "bolsitas": per,
            "n_bolsitas_prendidas": sum(1 for bid in per if per[bid]["prendio"]),
            "n_hallazgos_ruteados": n_ruteados,
            "sin_bolsita_v0": {"n": len(sin_bolsita), "hallazgos": sin_bolsita},
            "n_marcas_derivadas_no_ruteadas": n_derivadas,
            "bandera_perfil_disfemismo": per["F"]["prendio"],
            "nota": "Bolsita prende → highlight + estante; varias bolsitas a la vez OK (capas no se anulan). "
                    "No sube p del 244; no congela H; no es Top1 de vida."}
