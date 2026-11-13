#!/usr/bin/env python3
"""NICHO_CAMPO_V1 — lateral de campo semántico. NO toca F ni el Engine ni el 244.

Contrato: NICHO_CAMPO_V1_20261113. can_decide_H = False. feeds_predictor = False.
Autorizado por Marco 2026-11-13 (nota "NOTA PARA CLAUDE — NO AUTORIZADO",
dossier 2026-09-07). La integración al 244/V5 queda FUERA por orden de Marco.

Fórmula (de la nota, literal):
    w'_i = w_i * (1 + alpha * n_campo / n_corte)
    n_campo = cuantos tokens del mismo campo semántico están activos en ESTA
              ventana (corte). Incluye al propio token (la nota no lo excluye).
    n_corte = cuantos tokens activos hay en el corte (P+A+C, peso >= 0.5).
    alpha   = 0.1 .. 0.3 a estimar (nota). Por defecto 0.2 (punto medio del
              rango de la nota); la sensibilidad se mide con 0.1 y 0.3.
    cap     = 0.999 (máximo de la escala de pesos 0.01-0.999) para que no
              explote 30_ambicion otra vez. Además el factor está acotado
              por (1+alpha) cuando n_campo == n_corte.

Campos (nota: conquista | agencia | clinico | sacro). Fuentes:
    conquista = favor de 30_ambicion + favor de situacion_dramatica_ambicion
                + CONQUISTA de plugin_fix_entrada.
    agencia   = AGENCIA de plugin_fix_entrada.
    clinico   = CLINICO de plugin_embudo_clinico.
    sacro     = tokens de plugin_familias_gloria_sacro.EXTRA.
Solape (un token en dos campos): se asigna a un solo campo por prioridad
documentada conquista > agencia > clinico > sacro (el orden de la nota).
Así humildad -> agencia (no sacro) y escalada_status -> conquista (no sacro).

Esto NO sustituye el remapeo ambicion→autonomia (fix_entrada). El remapeo
evita ficha equivocada; el boost evita ficha correcta débil (nota).

Salida: traza paralela/observación. NO modifica F, NO modifica la entrada,
NO decide H. El motor corre igual con o sin este lateral.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

CONTRATO = "NICHO_CAMPO_V1_20261113"
CAN_DECIDE_H = False
ALPHA_DEFAULT = 0.2
ALPHAS_SENSIBILIDAD = (0.1, 0.3)
CAP = 0.999
UMBRAL_ACTIVO = 0.5

CONQUISTA = {"ambicion", "codicia", "maquiavelismo", "poder", "competencia",
             "sed_de_mando", "escalada", "escalada_status"}
AGENCIA = {"autonomia", "inconformismo", "desafio_autoridad", "humildad"}
CLINICO = {"consumo_sustancias", "cronicidad_sintomatica", "estancamiento_crisis"}
SACRO = {"desafio_sagrado", "devocion", "estatus_social", "humildad_religiosa",
         "olvido", "orgullo", "piedad", "reconocimiento", "redes_prestigio"}

CAMPOS = {"conquista": CONQUISTA, "agencia": AGENCIA, "clinico": CLINICO, "sacro": SACRO}
# prioridad de asignación en caso de solape (orden de la nota)
PRIORIDAD = ("conquista", "agencia", "clinico", "sacro")
CAMPO_DE_TOKEN = {}
for _campo in PRIORIDAD:
    for _t in CAMPOS[_campo]:
        CAMPO_DE_TOKEN.setdefault(_t, _campo)

# Foco de la nota: la ficha que no debe explotar ni quedar débil.
FICHA_30_AMBICION_FAVOR = ("ambicion", "codicia", "maquiavelismo", "poder",
                           "competencia", "sed_de_mando")


def _w_prima(w: float, n_campo: int, n_corte: int, alpha: float) -> float:
    if n_corte <= 0:
        return w
    return min(CAP, w * (1.0 + alpha * n_campo / n_corte))


def nicho(cortes: Sequence[Tuple[str, Sequence[Tuple[str, float]]]],
          alpha: float = ALPHA_DEFAULT,
          alphas_sensibilidad: Sequence[float] = ALPHAS_SENSIBILIDAD) -> Dict:
    """cortes = [(id, tokens P+A+C de ese corte), ...]. Devuelve la traza."""
    por_corte = []
    top_boosts = []
    for cid, toks in cortes:
        activos = [(t, v) for t, v in toks if v >= UMBRAL_ACTIVO]
        n_corte = len(activos)
        campos_activos = [CAMPO_DE_TOKEN[t] for t, _ in activos if t in CAMPO_DE_TOKEN]
        filas = []
        for t, v in activos:
            campo = CAMPO_DE_TOKEN.get(t)
            if campo is None:
                filas.append({"token": t, "campo": None, "w": v, "n_campo": 0,
                              "w_prima": v, "w_prima_sensibilidad": {}})
                continue
            n_campo = sum(1 for c in campos_activos if c == campo)
            wp = _w_prima(v, n_campo, n_corte, alpha)
            wps = {str(a): _w_prima(v, n_campo, n_corte, a) for a in alphas_sensibilidad}
            filas.append({"token": t, "campo": campo, "w": v, "n_campo": n_campo,
                          "n_corte": n_corte, "w_prima": round(wp, 4),
                          "w_prima_sensibilidad": {k: round(x, 4) for k, x in wps.items()},
                          "boost_pct": round(100.0 * (wp - v) / v, 2) if v else 0.0})
            top_boosts.append((filas[-1]["boost_pct"], cid, t, campo, v, wp))
        max_boost = max((f["boost_pct"] for f in filas if f["campo"]), default=0.0)
        por_corte.append({"corte": cid, "n_corte": n_corte,
                          "n_con_campo": len(campos_activos),
                          "por_token": filas, "max_boost_pct": max_boost})
    top_boosts.sort(reverse=True)
    # foco 30_ambicion: ¿el nicho empuja la ficha?
    foco = []
    for pc in por_corte:
        for f in pc["por_token"]:
            if f["token"] in FICHA_30_AMBICION_FAVOR and f["campo"] == "conquista":
                foco.append({"corte": pc["corte"], "token": f["token"], "w": f["w"],
                             "n_campo": f["n_campo"], "w_prima": f["w_prima"],
                             "boost_pct": f["boost_pct"]})
    return {
        "plugin": "NICHO_CAMPO_V1",
        "contrato": CONTRATO,
        "can_decide_H": CAN_DECIDE_H,
        "alpha": alpha,
        "alphas_sensibilidad": list(alphas_sensibilidad),
        "cap": CAP,
        "nota": "Traza paralela. NO modifica F ni la entrada ni H. n_campo incluye al propio token (fórmula literal de la nota).",
        "campos": {k: sorted(v) for k, v in CAMPOS.items()},
        "por_corte": por_corte,
        "foco_30_ambicion": foco,
        "top_boosts": [{"boost_pct": b, "corte": c, "token": t, "campo": f, "w": w, "w_prima": wp}
                       for b, c, t, f, w, wp in top_boosts[:10]],
        "max_boost_pct_global": max((b for b, *_ in top_boosts), default=0.0),
    }


def nicho_de_caso(cortes_pac: Sequence[Tuple[str, List[Tuple[str, float]]]],
                  alpha: float = ALPHA_DEFAULT) -> Dict:
    """Atajo: cortes ya con P+A+C combinados."""
    return nicho(cortes_pac, alpha=alpha)


if __name__ == "__main__":
    import json
    # Prueba rápida: Monroe-tipo (ambicion sola) vs Alejandro-tipo (conquista junta).
    monroe = [("C2", [("ambicion", 0.80), ("autonomia", 0.70), ("inconformismo", 0.70), ("oportunidad", 0.70)])]
    alej = [("C2", [("ambicion", 0.84), ("poder", 0.84), ("liderazgo", 0.80), ("audacia", 0.80), ("conquista", 0.80), ("triunfo", 0.80)])]
    print("MONROE C2:", json.dumps(nicho(monroe)["por_corte"][0]["por_token"], ensure_ascii=False))
    print("ALEJANDRO C2:", json.dumps(nicho(alej)["por_corte"][0]["por_token"], ensure_ascii=False))
