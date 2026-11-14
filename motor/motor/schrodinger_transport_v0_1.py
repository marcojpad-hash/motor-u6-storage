#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""schrodinger_transport_v0_1.py — Puente de Schrödinger V0_1 (IMPLEMENTADO).

Propuesta para aprobación de Mj (Marco Juárez). Ver SPEC_SCHRODINGER_V0_1.md.
Sustituye al esqueleto schrodinger_transport_esqueleto_v0_1.py (que queda intacto
como registro de la propuesta original); este archivo implementa costo(),
sinkhorn() y memento_inversa(), que en el esqueleto eran NotImplementedError.

Contrato: Alimenta_H=NO, writes_H=False. No importa Engine ni 244. No decide H,
no escribe H, no toca el catálogo. Es un lateral/sensor: solo lee la traza P
por corte y produce la trayectoria regularizada (la trayectoria que oscila
menos) y sus métricas. Solo Python estándar + numpy.

Idea (SPEC §1): la trayectoria es el camino marcado por donde va la
vectorización del movimiento del eje geométrico (la línea dinámica / eje vial
de Mj; término de Mj: "trayectoria"). El puente de Schrödinger es el transporte
óptimo entrópico entre las medidas μ_t de cortes consecutivos. Su interpolación
de desplazamiento (el camino del puente) es la trayectoria regularizada: oscila
menos que la trayectoria cruda. El costo penaliza el transporte de masa entre
familias de polaridad transversal opuesta, que es lo que hace oscilar la
trayectoria (SPEC §5).
"""
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

ESTADO = "V0_1_IMPLEMENTADO"
ALIMENTA_H = "NO"
VERSION = "SCHRODINGER_TRANSPORT_V0_1_20261111"
PARAMS_DEFAULT = {"alpha": 1.0, "beta": 1.0, "gamma": 1.0, "delta": 0.1, "lam": 1.0, "epsilon": 0.05}
# PRE-REGISTRO (heredado del esqueleto): alpha/beta/gamma/lam=1.0, epsilon=0.05.
# CORRECCIÓN MEDIDA (V0_1): el pre-registro traía delta=1.0, pero un cruce de eje
# costaba 1.0 = 20*epsilon y el kernel quedaba casi bloque-diagonal: Sinkhorn no
# convergía en 5000 iteraciones en la transición Napoleón C5->C6 (err 8.6e-05).
# Con delta=0.1 (el cruce cuesta 2*epsilon, en la escala de los demás términos)
# converge en <1000 iteraciones. Ver SPEC §4. Decisión de Pecas, abierta a Mj.


# ------------------------------------------------------------------ medidas
def candidatos(cut: Dict[str, Any], soporte_acero: Optional[List[str]], billar_fams: List[str], eps: float = 1e-9) -> List[str]:
    """Adoptado verbatim del esqueleto: familias vivas en el corte (p != 0.5)."""
    vivos = [k for k, p in (cut.get("P_FULL_244") or {}).items() if p is not None and abs(float(p) - 0.5) > eps]
    return sorted(set(vivos) | set(soporte_acero or []) | set(billar_fams))


def _excesos(cut: Dict[str, Any]) -> Dict[str, float]:
    """Exceso con signo por familia: e = p - 0.5. Positivo = activa, negativo = déficit."""
    return {k: float(v) - 0.5 for k, v in (cut.get("P_FULL_244") or {}).items() if v is not None}


def mu_t(cut: Dict[str, Any], K: List[str]) -> Dict[str, float]:
    """Adoptado verbatim del esqueleto (SPEC §2): μ_t = max(0, p-0.5) normalizado.

    Es la medida de las familias ACTIVAS en el corte (exceso positivo).
    """
    P = cut.get("P_FULL_244") or {}
    w = {k: max(0.0, float(P.get(k) or 0.5) - 0.5) for k in K}
    s = sum(w.values())
    return {k: (v / s if s else 0.0) for k, v in w.items()}


def mu_t_neg(cut: Dict[str, Any], K: List[str]) -> Dict[str, float]:
    """Medida de DÉFICIT (complemento de μ_t, añadido en V0_1, SPEC §2).

    μ_t^- = max(0, 0.5-p) normalizado: las familias en déficit en el corte.
    Sin ella la trayectoria pierde la mitad de la señal (el exceso con signo
    es lo que define la posición en el plano; μ_t solo lleva el lado positivo).
    Decisión de Pecas, abierta a corrección de Mj.
    """
    P = cut.get("P_FULL_244") or {}
    w = {k: max(0.0, 0.5 - float(P.get(k) or 0.5)) for k in K}
    s = sum(w.values())
    return {k: (v / s if s else 0.0) for k, v in w.items()}


def masas(cut: Dict[str, Any]) -> Tuple[float, float]:
    """Masas sin normalizar: (Z+ = suma de excesos positivos, Z- = suma de déficits)."""
    e = _excesos(cut)
    zp = sum(v for v in e.values() if v > 0.0)
    zn = sum(-v for v in e.values() if v < 0.0)
    return zp, zn


# ------------------------------------------------------- coordenadas (plano)
def coordenadas_familias(cortes: Sequence[Dict[str, Any]]):
    """Coordenadas de cada familia en el plano de la trayectoria (SPEC §3).

    Misma construcción que tabla_coordenadas.py (análisis post-hoc de Pecas):
    matriz P (cortes x familias), centrada por familia, SVD; PC1 = eje Tusi,
    PC2 = transversal; rotación para que el diámetro C1->Cn quede horizontal.
    Devuelve (coords, pos_pca, singulares):
      coords: {familia: (tau, upsilon)} — tau = eje Tusi, upsilon = transversal.
      pos_pca: [(x, y) por corte] — la trayectoria cruda en ese plano.
      singulares: valores singulares (para verificar que PC1/PC2 dominan).
    Requiere numpy. Si no hay varianza (S[0]==0) devuelve coordenadas cero.
    """
    import numpy as np
    fams = sorted({k for c in cortes for k in (c.get("P_FULL_244") or {}).keys()})
    n = len(cortes)
    X = np.array([[float((c.get("P_FULL_244") or {}).get(f, 0.5)) for f in fams] for c in cortes], dtype=float)
    Xc = X - X.mean(axis=0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    if len(S) == 0 or S[0] <= 0.0:
        return {f: (0.0, 0.0) for f in fams}, [(0.0, 0.0)] * n, list(S)
    scores = U * S
    pc1, pc2 = scores[:, 0], scores[:, 1]
    dx, dy = float(pc1[-1] - pc1[0]), float(pc2[-1] - pc2[0])
    th = math.radians(-math.degrees(math.atan2(dy, dx)))
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    L = R @ Vt[:2]  # (2, n_fams): fila 0 = tau, fila 1 = upsilon
    rot = scores[:, :2] @ R.T
    coords = {f: (float(L[0, j]), float(L[1, j])) for j, f in enumerate(fams)}
    pos = [(float(rot[t, 0]), float(rot[t, 1])) for t in range(n)]
    return coords, pos, [float(s) for s in S]


# ------------------------------------------------------------------ costo
def _signo(v: float) -> int:
    return 1 if v > 0.0 else (-1 if v < 0.0 else 0)


def costo(i: str, j: str, ctx: Dict[str, Any], prm: Dict[str, float] = PARAMS_DEFAULT) -> float:
    """Costo de transición entre la familia i (corte t) y la familia j (corte t+1).

    SPEC §5. ctx lleva:
      "polaridad": {fam: upsilon} (coordenada transversal de la familia),
      "tusi": {fam: tau} (coordenada de progresión),
      "exceso_t": {fam: exceso positivo o déficit en t} (según el lado),
      "exceso_t1": {fam: exceso positivo o déficit en t+1}.
    C(i,j) = alpha*|υ_i - υ_j| + beta*|τ_i - τ_j| + gamma*|e_i(t) - e_j(t+1)|
             + delta*[signo(υ_i) != signo(υ_j) y ambos != 0]
    El término alpha y el término delta penalizan el transporte de masa entre
    familias de polaridad transversal opuesta: ese cruce de eje es lo que hace
    oscilar la trayectoria. El término beta penaliza saltos grandes en el eje
    de progresión (Tusi) y gamma penaliza mover masa entre activaciones muy
    distintas. Todos los términos son >= 0; C(i,i) puede ser > 0 si la familia
    cambia de activación entre cortes.
    """
    pol = ctx.get("polaridad") or {}
    tus = ctx.get("tusi") or {}
    et = ctx.get("exceso_t") or {}
    et1 = ctx.get("exceso_t1") or {}
    ui, uj = float(pol.get(i, 0.0)), float(pol.get(j, 0.0))
    ti, tj = float(tus.get(i, 0.0)), float(tus.get(j, 0.0))
    ei, ej = float(et.get(i, 0.0)), float(et1.get(j, 0.0))
    cruce = 1.0 if (_signo(ui) * _signo(uj) < 0) else 0.0
    return (float(prm.get("alpha", 1.0)) * abs(ui - uj)
            + float(prm.get("beta", 1.0)) * abs(ti - tj)
            + float(prm.get("gamma", 1.0)) * abs(ei - ej)
            + float(prm.get("delta", 1.0)) * cruce)


def _matriz_costo(soporte: List[str], ctx: Dict[str, Any], prm: Dict[str, float]):
    import numpy as np
    n = len(soporte)
    C = np.zeros((n, n), dtype=float)
    for a, i in enumerate(soporte):
        for b, j in enumerate(soporte):
            C[a, b] = costo(i, j, ctx, prm)
    return C


# ------------------------------------------------------------- Sinkhorn (OT)
def sinkhorn(mu, nu, C, eps: float, max_iter: int = 5000, tol: float = 1e-9):
    """Transporte óptimo entrópico entre mu y nu con matriz de costo C (SPEC §5).

    Algoritmo de Sinkhorn-Knopp (escalado iterativo) en el dominio lineal con
    piso en las marginales para evitar 0/0. mu y nu son vectores no negativos
    que suman 1 y tienen la misma longitud que C. eps es la regularización
    entrópica (PARAMS_DEFAULT["epsilon"]): a mayor eps, plan más difuso.
    Devuelve (plan, info): plan[i,j] = masa transportada de i a j;
    info trae iteraciones, error marginal (L1) y costo total del plan.
    """
    import numpy as np
    mu = np.asarray(mu, dtype=float).ravel()
    nu = np.asarray(nu, dtype=float).ravel()
    C = np.asarray(C, dtype=float)
    mu = np.maximum(mu, 1e-12); mu = mu / mu.sum()
    nu = np.maximum(nu, 1e-12); nu = nu / nu.sum()
    K = np.exp(-C / float(eps))
    K = np.maximum(K, 1e-300)
    u = np.ones_like(mu)
    v = np.ones_like(nu)
    err = float("inf")
    it = 0
    for it in range(1, max_iter + 1):
        u = mu / (K @ v)
        v = nu / (K.T @ u)
        P = u[:, None] * K * v[None, :]
        err = float(np.abs(P.sum(axis=1) - mu).sum() + np.abs(P.sum(axis=0) - nu).sum())
        if err < tol:
            break
    P = u[:, None] * K * v[None, :]
    info = {"iteraciones": it, "error_marginal": err, "epsilon": float(eps),
            "costo_total": float((P * C).sum()), "convergio": bool(err < tol)}
    return P, info


# ------------------------------------------------------- trayectoria regularizada
def medir_oscilacion(y: Sequence[float]) -> Dict[str, float]:
    """Oscilación de la transversal y (SPEC §1): variación total y amplitud.

    Los cruces se cuentan respecto a la media de y (no respecto a 0), porque
    la trayectoria lleva un desplazamiento constante y el 0 no es significativo.
    cambios_direccion = número de veces que la primera diferencia cambia de
    signo (picos/valles de la onda).
    """
    y = [float(v) for v in y]
    if len(y) < 2:
        return {"variacion_total": 0.0, "amplitud_pico_valle": 0.0, "cruces_media": 0, "cambios_direccion": 0}
    tv = sum(abs(y[t + 1] - y[t]) for t in range(len(y) - 1))
    media = sum(y) / len(y)
    cruces = sum(1 for t in range(len(y) - 1) if (y[t] - media) * (y[t + 1] - media) < 0.0)
    difs = [y[t + 1] - y[t] for t in range(len(y) - 1)]
    cambios = sum(1 for t in range(len(difs) - 1) if difs[t] * difs[t + 1] < 0.0)
    return {"variacion_total": float(tv), "amplitud_pico_valle": float(max(y) - min(y)),
            "cruces_media": int(cruces), "cambios_direccion": int(cambios)}


def transportar_trayectoria(cortes: Sequence[Dict[str, Any]], prm: Dict[str, float] = None) -> Dict[str, Any]:
    """Puente de Schrödinger sobre la trayectoria (SPEC §7).

    Entrada: cortes con P_FULL_244 (los de motor["cuts"]). Salida: la
    trayectoria cruda (posición por corte, exceso con signo) y la trayectoria
    regularizada (interpolación de desplazamiento del puente), con la
    oscilación antes/después. Los extremos quedan anclados (C1 y Cn no se
    mueven); el puente suaviza el interior. lam (fuerza del puente): 1.0 =
    totalmente la posición transportada; 0.0 = la cruda.
    Requiere >= 3 cortes (con 2 no hay interior que suavizar).
    """
    import numpy as np
    prm = dict(PARAMS_DEFAULT, **(prm or {}))
    n = len(cortes)
    if n < 3:
        return {"estado": "SIN_TRAYECTORIA", "n_cortes": n,
                "nota": "se requieren >= 3 cortes para regularizar la trayectoria (con 2 no hay interior que suavizar)"}
    coords, pos_pca, sing = coordenadas_familias(cortes)
    tau = {f: c[0] for f, c in coords.items()}
    ups = {f: c[1] for f, c in coords.items()}
    lam = float(prm.get("lam", 1.0))
    eps = float(prm.get("epsilon", 0.05))

    # Medidas y masas por corte (lado + y lado -).
    mus_p, mus_n, zp, zn = [], [], [], []
    for c in cortes:
        K = candidatos(c, None, [])
        mus_p.append(mu_t(c, K))
        mus_n.append(mu_t_neg(c, K))
        a, b = masas(c)
        zp.append(a); zn.append(b)

    # Posición por corte (exceso con signo): pos = Z+*m+ - Z-*m-.
    # Es la trayectoria cruda en el plano; su forma (TV, amplitud) coincide con
    # la del PCA (tabla_coordenadas.py) salvo un desplazamiento constante.
    pos = []
    for t in range(n):
        mp = np.array([mus_p[t].get(f, 0.0) for f in coords], dtype=float)
        mn = np.array([mus_n[t].get(f, 0.0) for f in coords], dtype=float)
        L = np.array([[tau[f], ups[f]] for f in coords], dtype=float)
        mpos = mp @ L
        mneg = mn @ L
        pos.append((float(zp[t] * mpos[0] - zn[t] * mneg[0]),
                    float(zp[t] * mpos[1] - zn[t] * mneg[1])))

    # Transporte por transición (lado + y lado -) y puntos medios del puente.
    transiciones = []
    mid_pos = []
    for t in range(n - 1):
        fams = sorted(coords.keys())
        idx = {f: j for j, f in enumerate(fams)}
        et_p = {f: max(0.0, float((cortes[t].get("P_FULL_244") or {}).get(f, 0.5)) - 0.5) for f in fams}
        et1_p = {f: max(0.0, float((cortes[t + 1].get("P_FULL_244") or {}).get(f, 0.5)) - 0.5) for f in fams}
        et_n = {f: max(0.0, 0.5 - float((cortes[t].get("P_FULL_244") or {}).get(f, 0.5))) for f in fams}
        et1_n = {f: max(0.0, 0.5 - float((cortes[t + 1].get("P_FULL_244") or {}).get(f, 0.5))) for f in fams}
        ctx_p = {"polaridad": ups, "tusi": tau, "exceso_t": et_p, "exceso_t1": et1_p}
        ctx_n = {"polaridad": ups, "tusi": tau, "exceso_t": et_n, "exceso_t1": et1_n}
        L = np.array([[tau[f], ups[f]] for f in fams], dtype=float)
        planes = {}
        mids = {}
        for lado, mu_a, mu_b, ctx in (("+", mus_p[t], mus_p[t + 1], ctx_p), ("-", mus_n[t], mus_n[t + 1], ctx_n)):
            soporte = sorted(set(mu_a) | set(mu_b))
            # Soporte común: familias con masa en alguno de los dos cortes.
            vec_a = np.array([mu_a.get(f, 0.0) for f in soporte], dtype=float)
            vec_b = np.array([mu_b.get(f, 0.0) for f in soporte], dtype=float)
            if vec_a.sum() <= 0.0 or vec_b.sum() <= 0.0:
                planes[lado] = {"soporte": soporte, "vacio": True, "info": {"iteraciones": 0, "error_marginal": 0.0, "costo_total": 0.0, "convergio": True}}
                mids[lado] = (0.0, 0.0)
                continue
            C = _matriz_costo(soporte, ctx, prm)
            P, info = sinkhorn(vec_a, vec_b, C, eps)
            planes[lado] = {"soporte": soporte, "vacio": False, "info": info,
                            "costo_medio": float(C.mean()), "costo_max": float(C.max())}
            # Punto medio del puente (interpolación de desplazamiento s=0.5):
            # mid = sum_ij P(i,j) * (L_i + L_j)/2. Su media es (m(t)+m(t+1))/2
            # por la propiedad de las marginales; el plan determina el acople y
            # la dispersión de la medida interpolada, no la media (SPEC §5).
            # (P@Ls).sum = m(t+1); (P.T@Ls).sum = m(t); el promedio es el punto medio.
            Ls = np.array([[tau[f], ups[f]] for f in soporte], dtype=float)
            mid = ((P @ Ls).sum(axis=0) + (P.T @ Ls).sum(axis=0)) / 2.0
            # La dispersión transversal de la medida interpolada (sí depende del plan).
            mid_ups = (Ls[:, 1][:, None] + Ls[:, 1][None, :]) / 2.0
            media_mid_ups = float((P * mid_ups).sum())
            var_mid = float((P * (mid_ups - media_mid_ups) ** 2).sum())
            # Control: mismo cálculo con el acople independiente (eps -> infinito).
            Pi = np.outer(vec_a / vec_a.sum(), vec_b / vec_b.sum())
            var_ind = float((Pi * (mid_ups - float((Pi * mid_ups).sum())) ** 2).sum())
            mids[lado] = (float(mid[0]), float(mid[1]))
            planes[lado]["dispersion_transversal_mid"] = var_mid ** 0.5
            planes[lado]["dispersion_transversal_independiente"] = var_ind ** 0.5
        zm_p = (zp[t] + zp[t + 1]) / 2.0
        zm_n = (zn[t] + zn[t + 1]) / 2.0
        mid_pos.append((zm_p * mids["+"][0] - zm_n * mids["-"][0],
                        zm_p * mids["+"][1] - zm_n * mids["-"][1]))
        transiciones.append({"de": cortes[t].get("corte"), "a": cortes[t + 1].get("corte"),
                             "planes": {k: {kk: vv for kk, vv in v.items() if kk != "soporte"} for k, v in planes.items()}})

    # Trayectoria regularizada: extremos anclados, interior por el puente.
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
    osc_y_antes = medir_oscilacion(y_antes)
    osc_y_despues = medir_oscilacion(y_despues)
    osc_x_antes = medir_oscilacion(x_antes)
    osc_x_despues = medir_oscilacion(x_despues)
    return {"estado": "TRANSPORTE_OK", "n_cortes": n, "parametros": prm,
            "cortes": [c.get("corte") for c in cortes],
            "trayectoria_cruda": [{"corte": cortes[t].get("corte"), "x_tusi": round(pos[t][0], 4), "y_transversal": round(pos[t][1], 4)} for t in range(n)],
            "trayectoria_regularizada": [{"corte": cortes[t].get("corte"), "x_tusi": round(pos_reg[t][0], 4), "y_transversal": round(pos_reg[t][1], 4)} for t in range(n)],
            "trayectoria_pca_referencia": [{"corte": cortes[t].get("corte"), "x_tusi": round(pos_pca[t][0], 4), "y_transversal": round(pos_pca[t][1], 4)} for t in range(n)],
            "puntos_medios_puente": [{"de": cortes[t].get("corte"), "a": cortes[t + 1].get("corte"), "x_tusi": round(mid_pos[t][0], 4), "y_transversal": round(mid_pos[t][1], 4)} for t in range(n - 1)],
            "transiciones": transiciones,
            "oscilacion": {"transversal_antes": osc_y_antes, "transversal_despues": osc_y_despues,
                           "tusi_antes": osc_x_antes, "tusi_despues": osc_x_despues,
                           "reduccion_variacion_total_transversal": round(osc_y_antes["variacion_total"] - osc_y_despues["variacion_total"], 4),
                           "reduccion_amplitud_transversal": round(osc_y_antes["amplitud_pico_valle"] - osc_y_despues["amplitud_pico_valle"], 4)},
            "singulares_pca": [round(s, 4) for s in sing[:5]],
            "nota": "La trayectoria cruda es el exceso con signo (forma igual a la del PCA salvo desplazamiento constante). La regularizada es la interpolación de desplazamiento del puente (extremos anclados, lam=%s)." % lam}


# ------------------------------------------------------------- memento inverso
def memento_inversa(estado: Dict[str, Any], orden: Sequence[str] = ("P", "A", "C")) -> Dict[str, Any]:
    """Orden de recuperación del memento (SPEC §6).

    estado: dict con claves "P", "A", "C" (los tres componentes del estado).
    orden: permutación (o subconjunto) de ("P","A","C"). Por defecto P->A->C:
    P primero porque la trayectoria se define por P; A y C están planos en
    0.5 en las corridas actuales y no aportan señal. Decisión de Pecas,
    abierta a corrección de Mj.
    Devuelve el estado recuperado en ese orden y las claves faltantes.
    """
    orden = [str(k) for k in orden]
    if len(set(orden)) != len(orden) or any(k not in ("P", "A", "C") for k in orden):
        raise ValueError("memento_inversa: orden debe ser una permutación (o subconjunto) de ('P','A','C'), recibido %r" % (orden,))
    estado = estado or {}
    return {"orden": orden,
            "recuperado": {k: estado.get(k) for k in orden if k in estado},
            "faltantes": [k for k in orden if k not in estado],
            "nota": "P primero: la trayectoria se define por P (A y C planos en 0.5 en las corridas actuales)."}


# ------------------------------------------------------------------ salidas
def salida_vacia(case_id: str) -> Dict[str, Any]:
    """Compatibilidad con el esqueleto: salida vacía (sin resultado numérico)."""
    return {"estado": ESTADO, "Alimenta_H": ALIMENTA_H, "writes_H": False, "alimenta_convergencia": True,
            "case_id": case_id, "por_transicion": [], "null": None, "future_hidden": True,
            "nota": "Esqueleto: no hay resultado numérico."}


def salida(case_id: str, transporte: Dict[str, Any]) -> Dict[str, Any]:
    """Salida del puente V0_1 (SPEC §7)."""
    return {"estado": ESTADO, "Alimenta_H": ALIMENTA_H, "writes_H": False, "alimenta_convergencia": True,
            "case_id": case_id, "transporte": transporte,
            "nota": "Puente V0_1: transporte óptimo entrópico entre μ_t consecutivas; trayectoria regularizada (oscila menos)."}


if __name__ == "__main__":
    import json
    print(json.dumps(salida_vacia("DEMO"), ensure_ascii=False))
