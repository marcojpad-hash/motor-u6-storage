#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""schrodinger_transport_v0_2.py — Puente de Schrödinger V0_2 (IMPLEMENTADO).

Propuesta para aprobación de Mj (Marco Juárez). Ver SPEC_SCHRODINGER_V0_1.md §9.
Complementa (NO sustituye) al V0_1 (`schrodinger_transport_v0_1.py`, que queda
intacto): el V0_1 estabiliza (suavizado por interpolación de desplazamiento, con
marginales duras); el V0_2 transforma (marginales suaves: el costo mueve la
media). Decisión de Mj (2026-11-11): AMBOS. Su razón: para que algo sea,
también tuvo que dejar de ser — uno estabiliza y el otro transforma. Es la
misma dualidad que la tríada billar / Poincaré / Forman-Ricci del motor
(billar_circular_convergencia_v0_1.py: el billar circular en el borde ES
rotación de Poincaré; ricci_forman_coocurrencia_v0_1.py y el hub
'negativo_ricci_vs_billar': el voto negativo de Ricci-Forman vs billar).

Contrato: Alimenta_H=NO, writes_H=False. No importa Engine ni 244. No decide H,
no escribe H, no toca el catálogo. Es un lateral/sensor: solo lee la traza P
por corte y produce la trayectoria transformada (la trayectoria cuya media el
costo encogió hacia el eje) y sus métricas. Solo Python estándar + numpy.

Idea (SPEC §9): transporte óptimo NO balanceado entre las medidas μ_t de
cortes consecutivos. El plan P ya no está obligado a reproducir exactamente μ_t
y μ_{t+1}: sus marginales se pueden desviar de ellas pagando una penalización
KL con peso `rho`. Cuando transportar masa a través del eje (cruzar la
polaridad transversal) cuesta más que destruirla y recrearla al otro lado, el
plan destruye esa masa (deja de ser) y la recrea (llega a ser) donde el costo
es menor. La media de la medida interpolada — y con ella la trayectoria — se
mueve hacia el eje: el costo SÍ mueve la media, no solo la dispersión.
Cuando rho -> infinito se recupera el V0_1 (marginales duras, Sinkhorn
balanceado); cuando rho -> 0 el plan es libre de destruir toda la masa y la
trayectoria colapsa. El `rho` por defecto se elige por medida (SPEC §9).

Reutiliza del V0_1 (misma fuente de verdad: mismas medidas, mismo costo, mismas
coordenadas; si no, la comparación V0_1/V0_2 no valdría): candidatos, mu_t,
mu_t_neg, masas, coordenadas_familias, costo, medir_oscilacion, memento_inversa.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# El V0_2 vive en el mismo directorio que el V0_1; hacerlo importable también
# cuando se ejecuta standalone (python3 schrodinger_transport_v0_2.py).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import schrodinger_transport_v0_1 as v01

ESTADO = "V0_2_IMPLEMENTADO"
ALIMENTA_H = "NO"
VERSION = "SCHRODINGER_TRANSPORT_V0_2_20261111"
PARAMS_DEFAULT = dict(v01.PARAMS_DEFAULT, **{"rho": 0.1})
# rho (penalización KL por desviarse de las marginales): 0.1 por defecto, elegido
# por medida (barrido en probar_puente_schrodinger_v02.py, SPEC §9). Escala:
# el cruce de eje cuesta delta=0.1; destruir masa cuesta ~rho por unidad de masa
# destruida. Con rho >> 0.1 las marginales se quedan duras (V0_1); con
# rho << 0.1 el plan destruye demasiada masa y la trayectoria colapsa.
# Decisión de Pecas, abierta a corrección de Mj.


# ------------------------------------------------- Sinkhorn NO balanceado (OT)
def _kl_generalizada(a, b) -> float:
    """KL generalizada KL(a|b) = Σ a·log(a/b) − a + b (convención 0·log 0 = 0).

    a y b son medidas no negativas (vectores numpy). Es la divergencia que
    penaliza desviarse de la marginal de referencia en el OT no balanceado.
    """
    import numpy as np
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    b = np.maximum(b, 1e-300)
    term = np.where(a > 0.0, a * np.log(np.maximum(a, 1e-300) / b), 0.0)
    return float((term - a + b).sum())


def sinkhorn_no_balanceado(mu, nu, C, eps: float, rho: float, max_iter: int = 5000, tol: float = 1e-7):
    """Transporte óptimo entrópico NO balanceado entre mu y nu (SPEC §9).

    Minimiza sobre el plan P >= 0:
        <P, C> + eps·KL(P | mu⊗nu) + rho·KL(P·1 | mu) + rho·KL(P^T·1 | nu)
    (Chizat et al. 2018, "Scaling algorithms for unbalanced optimal transport
    problems"). Las marginales del plan (P·1 y P^T·1) ya no tienen que ser
    exactamente mu y nu: se desvían pagando rho por unidad de KL. Eso es lo
    que deja que el costo mueva la media.

    Actualización de Sinkhorn no balanceado (exponente q = rho/(rho+eps)):
        u <- mu / (K v)^q ;  v <- nu / (K^T u)^q ;  P = diag(u) K diag(v)
    (OJO: solo el denominador (K v) lleva el exponente q; mu queda a la
    potencia 1. Elevar también mu a q infla el plan y crea masa, M > 1.)
    Con rho -> infinito, q -> 1 y se recupera el Sinkhorn balanceado del V0_1.
    Con rho -> 0, q -> 0, u -> mu, v -> nu y P -> mu⊗nu ⊙ K: las marginales
    son libres y el plan destruye masa sin freno.

    tol=1e-7 (no 1e-9 como el balanceado): la iteración no balanceada contrae
    más lento cuando rho es grande (q -> 1), y el criterio es el cambio
    relativo del plan P (invariante de gauge). 1e-7 deja el plan estable a 7
    decimales, muy por debajo de la precisión de la trayectoria (4 decimales).

    mu y nu son vectores no negativos que suman 1 (las μ_t del V0_1).
    Devuelve (plan, info): info trae iteraciones, residuo de punto fijo,
    convergencia, masa transportada M = P.sum() (1.0 = balanceado; < 1.0 =
    masa destruida), penalización KL pagada, y costo total del plan.
    """
    import numpy as np
    mu = np.asarray(mu, dtype=float).ravel()
    nu = np.asarray(nu, dtype=float).ravel()
    C = np.asarray(C, dtype=float)
    mu = np.maximum(mu, 1e-12); mu = mu / mu.sum()
    nu = np.maximum(nu, 1e-12); nu = nu / nu.sum()
    eps = float(eps); rho = float(rho)
    q = rho / (rho + eps) if (rho + eps) > 0.0 else 1.0
    K = np.exp(-C / eps)
    K = np.maximum(K, 1e-300)
    u = np.ones_like(mu)
    v = np.ones_like(nu)
    P_prev = np.zeros_like(K)
    err = float("inf")
    it = 0
    for it in range(1, max_iter + 1):
        # u = mu / (K v)^q ; v = nu / (K^T u)^q  (solo el denominador lleva q).
        u_new = mu / np.power(np.maximum(K @ v, 1e-300), q)
        v_new = nu / np.power(np.maximum(K.T @ u_new, 1e-300), q)
        # Convergencia: cambio relativo del PLAN P (invariante de gauge).
        # Medir el cambio de u y v es engañoso: u y v tienen libertad de gauge
        # (u->c·u, v->v/c deja P igual), así que su cambio relativo baja lento
        # cerca de q≈1 aunque el plan ya convergió.
        P_new = u_new[:, None] * K * v_new[None, :]
        err = float(np.max(np.abs(P_new - P_prev)) / max(float(np.max(P_new)), 1e-300))
        u, v, P_prev = u_new, v_new, P_new
        if err < tol:
            break
    P = P_prev
    a = P.sum(axis=1)  # marginal suave en t (ya no es mu)
    b = P.sum(axis=0)  # marginal suave en t+1 (ya no es nu)
    M = float(P.sum())
    kl_pen = rho * (_kl_generalizada(a, mu) + _kl_generalizada(b, nu))
    info = {"iteraciones": it, "residuo": err, "epsilon": eps, "rho": rho,
            "q_exponente": float(q), "convergio": bool(err < tol),
            "masa_transportada": M, "masa_destruida": float(1.0 - M),
            "penalizacion_kl": float(kl_pen),
            "costo_total": float((P * C).sum()),
            "costo_mas_penalizacion": float((P * C).sum() + kl_pen)}
    return P, info


# ------------------------------------------------------- trayectoria transformada
def transportar_trayectoria_v02(cortes: Sequence[Dict[str, Any]], prm: Dict[str, float] = None) -> Dict[str, Any]:
    """Puente de Schrödinger V0_2 sobre la trayectoria (SPEC §9).

    Misma construcción que el V0_1 (`transportar_trayectoria`), pero el plan de
    cada transición es NO balanceado: sus marginales son suaves, así que el
    punto medio del puente ya NO es (pos(t)+pos(t+1))/2 — la media se mueve
    hacia el eje en la medida en que el costo destruye la masa que cruzaría
    el eje y la recrea del lado barato. Los extremos quedan anclados (C1 y Cn
    no se mueven), igual que en el V0_1: mismas condiciones de borde, para que
    la comparación V0_1/V0_2 sea manzana con manzana (el interior es lo que
    transforma). lam tiene el mismo sentido que en el V0_1.
    Requiere >= 3 cortes (con 2 no hay interior que transformar).
    """
    import numpy as np
    prm = dict(PARAMS_DEFAULT, **(prm or {}))
    n = len(cortes)
    if n < 3:
        return {"estado": "SIN_TRAYECTORIA", "n_cortes": n,
                "nota": "se requieren >= 3 cortes para transformar la trayectoria (con 2 no hay interior que transformar)"}
    coords, pos_pca, sing = v01.coordenadas_familias(cortes)
    tau = {f: c[0] for f, c in coords.items()}
    ups = {f: c[1] for f, c in coords.items()}
    lam = float(prm.get("lam", 1.0))
    eps = float(prm.get("epsilon", 0.05))
    rho = float(prm.get("rho", 0.1))

    # Medidas y masas por corte (lado + y lado -), igual que el V0_1.
    mus_p, mus_n, zp, zn = [], [], [], []
    for c in cortes:
        K = v01.candidatos(c, None, [])
        mus_p.append(v01.mu_t(c, K))
        mus_n.append(v01.mu_t_neg(c, K))
        a, b = v01.masas(c)
        zp.append(a); zn.append(b)

    # Posición cruda por corte (exceso con signo), igual que el V0_1.
    pos = []
    for t in range(n):
        mp = np.array([mus_p[t].get(f, 0.0) for f in coords], dtype=float)
        mn = np.array([mus_n[t].get(f, 0.0) for f in coords], dtype=float)
        L = np.array([[tau[f], ups[f]] for f in coords], dtype=float)
        mpos = mp @ L
        mneg = mn @ L
        pos.append((float(zp[t] * mpos[0] - zn[t] * mneg[0]),
                    float(zp[t] * mpos[1] - zn[t] * mneg[1])))

    # Transporte NO balanceado por transición (lado + y lado -) y puntos medios.
    # La diferencia con el V0_1 está SOLO en el plan: las marginales suaves
    # hacen que el punto medio ya no sea el promedio de las posiciones crudas.
    transiciones = []
    mid_pos = []
    for t in range(n - 1):
        fams = sorted(coords.keys())
        et_p = {f: max(0.0, float((cortes[t].get("P_FULL_244") or {}).get(f, 0.5)) - 0.5) for f in fams}
        et1_p = {f: max(0.0, float((cortes[t + 1].get("P_FULL_244") or {}).get(f, 0.5)) - 0.5) for f in fams}
        et_n = {f: max(0.0, 0.5 - float((cortes[t].get("P_FULL_244") or {}).get(f, 0.5))) for f in fams}
        et1_n = {f: max(0.0, 0.5 - float((cortes[t + 1].get("P_FULL_244") or {}).get(f, 0.5))) for f in fams}
        ctx_p = {"polaridad": ups, "tusi": tau, "exceso_t": et_p, "exceso_t1": et1_p}
        ctx_n = {"polaridad": ups, "tusi": tau, "exceso_t": et_n, "exceso_t1": et1_n}
        planes = {}
        mids = {}
        for lado, mu_a, mu_b, ctx in (("+", mus_p[t], mus_p[t + 1], ctx_p), ("-", mus_n[t], mus_n[t + 1], ctx_n)):
            soporte = sorted(set(mu_a) | set(mu_b))
            vec_a = np.array([mu_a.get(f, 0.0) for f in soporte], dtype=float)
            vec_b = np.array([mu_b.get(f, 0.0) for f in soporte], dtype=float)
            if vec_a.sum() <= 0.0 or vec_b.sum() <= 0.0:
                planes[lado] = {"soporte": soporte, "vacio": True,
                                "info": {"iteraciones": 0, "residuo": 0.0, "convergio": True,
                                         "masa_transportada": 0.0, "masa_destruida": 1.0,
                                         "penalizacion_kl": 0.0, "costo_total": 0.0,
                                         "costo_mas_penalizacion": 0.0}}
                mids[lado] = (0.0, 0.0)
                continue
            C = v01._matriz_costo(soporte, ctx, prm)
            P, info = sinkhorn_no_balanceado(vec_a, vec_b, C, eps, rho)
            planes[lado] = {"soporte": soporte, "vacio": False, "info": info,
                            "costo_medio": float(C.mean()), "costo_max": float(C.max())}
            # Punto medio del puente con marginales SUAVES: las sumas no
            # normalizadas bajo las marginales del plan (ya incluyen la masa
            # destruida M). (P.T@Ls) = suma bajo la marginal suave en t;
            # (P@Ls) = suma bajo la marginal suave en t+1. En el V0_1 estas
            # sumas son exactamente m(t) y m(t+1); aquí ya no: la media se movió.
            Ls = np.array([[tau[f], ups[f]] for f in soporte], dtype=float)
            mid = ((P.T @ Ls).sum(axis=0) + (P @ Ls).sum(axis=0)) / 2.0
            mids[lado] = (float(mid[0]), float(mid[1]))
            # Dispersión transversal de la medida interpolada (depende del plan).
            mid_ups = (Ls[:, 1][:, None] + Ls[:, 1][None, :]) / 2.0
            media_mid_ups = float((P * mid_ups).sum() / max(P.sum(), 1e-300))
            var_mid = float((P * (mid_ups - media_mid_ups) ** 2).sum() / max(P.sum(), 1e-300))
            Pi = np.outer(vec_a / vec_a.sum(), vec_b / vec_b.sum())
            var_ind = float((Pi * (mid_ups - float((Pi * mid_ups).sum())) ** 2).sum())
            planes[lado]["dispersion_transversal_mid"] = var_mid ** 0.5
            planes[lado]["dispersion_transversal_independiente"] = var_ind ** 0.5
        zm_p = (zp[t] + zp[t + 1]) / 2.0
        zm_n = (zn[t] + zn[t + 1]) / 2.0
        mid_pos.append((zm_p * mids["+"][0] - zm_n * mids["-"][0],
                        zm_p * mids["+"][1] - zm_n * mids["-"][1]))
        transiciones.append({"de": cortes[t].get("corte"), "a": cortes[t + 1].get("corte"),
                             "planes": {k: {kk: vv for kk, vv in v.items() if kk != "soporte"} for k, v in planes.items()}})

    # Trayectoria transformada: extremos anclados, interior por el puente V0_2.
    pos_reg = [pos[0]]
    for t in range(1, n - 1):
        m = ((mid_pos[t - 1][0] + mid_pos[t][0]) / 2.0, (mid_pos[t - 1][1] + mid_pos[t][1]) / 2.0)
        pos_reg.append(((1.0 - lam) * pos[t][0] + lam * m[0],
                        (1.0 - lam) * pos[t][1] + lam * m[1]))
    pos_reg.append(pos[-1])

    y_antes = [p[1] for p in pos]
    y_despues = [p[1] for p in pos_reg]
    x_antes = [p[0] for p in pos]
    x_despues = [p[0] for p in pos_reg]
    osc_y_antes = v01.medir_oscilacion(y_antes)
    osc_y_despues = v01.medir_oscilacion(y_despues)
    osc_x_antes = v01.medir_oscilacion(x_antes)
    osc_x_despues = v01.medir_oscilacion(x_despues)
    # Desplazamiento de la media: cuánto se movió la trayectoria respecto a la
    # cruda (por corte y en promedio), y qué tan cerca del eje quedó.
    desp_y = [d - a for d, a in zip(y_despues, y_antes)]
    media_abs_y_antes = float(sum(abs(v) for v in y_antes) / len(y_antes))
    media_abs_y_despues = float(sum(abs(v) for v in y_despues) / len(y_despues))
    masa_media = float(sum(pl["info"]["masa_transportada"]
                           for tr in transiciones for pl in tr["planes"].values()
                           if not pl.get("vacio")) / max(1, sum(1 for tr in transiciones for pl in tr["planes"].values() if not pl.get("vacio"))))
    kl_media = float(sum(pl["info"]["penalizacion_kl"]
                         for tr in transiciones for pl in tr["planes"].values()
                         if not pl.get("vacio")) / max(1, sum(1 for tr in transiciones for pl in tr["planes"].values() if not pl.get("vacio"))))
    return {"estado": "TRANSPORTE_OK", "n_cortes": n, "parametros": prm,
            "cortes": [c.get("corte") for c in cortes],
            "trayectoria_cruda": [{"corte": cortes[t].get("corte"), "x_tusi": round(pos[t][0], 4), "y_transversal": round(pos[t][1], 4)} for t in range(n)],
            "trayectoria_transformada": [{"corte": cortes[t].get("corte"), "x_tusi": round(pos_reg[t][0], 4), "y_transversal": round(pos_reg[t][1], 4)} for t in range(n)],
            "trayectoria_pca_referencia": [{"corte": cortes[t].get("corte"), "x_tusi": round(pos_pca[t][0], 4), "y_transversal": round(pos_pca[t][1], 4)} for t in range(n)],
            "puntos_medios_puente": [{"de": cortes[t].get("corte"), "a": cortes[t + 1].get("corte"), "x_tusi": round(mid_pos[t][0], 4), "y_transversal": round(mid_pos[t][1], 4)} for t in range(n - 1)],
            "transiciones": transiciones,
            "oscilacion": {"transversal_antes": osc_y_antes, "transversal_despues": osc_y_despues,
                           "tusi_antes": osc_x_antes, "tusi_despues": osc_x_despues,
                           "reduccion_variacion_total_transversal": round(osc_y_antes["variacion_total"] - osc_y_despues["variacion_total"], 4),
                           "reduccion_amplitud_transversal": round(osc_y_antes["amplitud_pico_valle"] - osc_y_despues["amplitud_pico_valle"], 4)},
            "desplazamiento_media": {"por_corte_y": [round(v, 4) for v in desp_y],
                                     "media_abs_desplazamiento_y": round(float(sum(abs(v) for v in desp_y) / len(desp_y)), 4),
                                     "max_abs_desplazamiento_y": round(float(max(abs(v) for v in desp_y)), 4),
                                     "media_abs_y_antes": round(media_abs_y_antes, 4),
                                     "media_abs_y_despues": round(media_abs_y_despues, 4),
                                     "reduccion_media_abs_y": round(media_abs_y_antes - media_abs_y_despues, 4)},
            "costo_transformacion": {"masa_transportada_media": round(masa_media, 4),
                                     "masa_destruida_media": round(1.0 - masa_media, 4),
                                     "penalizacion_kl_media": round(kl_media, 4)},
            "singulares_pca": [round(s, 4) for s in sing[:5]],
            "nota": "V0_2: marginales suaves (rho=%s). La media se mueve hacia el eje en la medida en que el costo destruye la masa que cruzaría el eje. Extremos anclados, lam=%s." % (rho, lam)}


# ------------------------------------------------------------- memento inverso
def memento_inversa(estado: Dict[str, Any], orden: Sequence[str] = ("P", "A", "C")) -> Dict[str, Any]:
    """Orden de recuperación del memento (SPEC §6, mismo que el V0_1)."""
    return v01.memento_inversa(estado, orden)


# ------------------------------------------------------------------ salidas
def salida_vacia(case_id: str) -> Dict[str, Any]:
    """Compatibilidad con el esqueleto: salida vacía (sin resultado numérico)."""
    return {"estado": ESTADO, "Alimenta_H": ALIMENTA_H, "writes_H": False, "alimenta_convergencia": True,
            "case_id": case_id, "por_transicion": [], "null": None, "future_hidden": True,
            "nota": "Esqueleto: no hay resultado numérico."}


def salida(case_id: str, transporte: Dict[str, Any]) -> Dict[str, Any]:
    """Salida del puente V0_2 (SPEC §9)."""
    return {"estado": ESTADO, "Alimenta_H": ALIMENTA_H, "writes_H": False, "alimenta_convergencia": True,
            "case_id": case_id, "transporte": transporte,
            "nota": "Puente V0_2: transporte óptimo NO balanceado entre μ_t consecutivas; la media se mueve hacia el eje (el costo transforma la trayectoria)."}


if __name__ == "__main__":
    import json
    print(json.dumps(salida_vacia("DEMO"), ensure_ascii=False))
