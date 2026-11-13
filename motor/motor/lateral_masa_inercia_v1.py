# lateral_masa_inercia_v1.py — Fórmula Masa-Inercia (observación)
#
# Contrato: FORMULA_MASA_INERCIA_V1.md
#   can_decide_H = False (SENSOR, solo observa; no toca H1/H2 ni ranking).
#   No toca Engine ni catálogo 244. Solo lee P_FULL_244 por corte.
#
# Mide por caso:
#   M_c  = masa por corte (suma P_FULL_244)
#   r_c  = radio por corte (PCA centrada a 2 comp. de la matriz P_FULL_244)
#   V_c  = |r_c - r_{c-1}| (violencia radial)
#   k    = corr(V, M) (constante de amortiguamiento del caso)
#   N_sup, D = familias suprimidas (< 0.5) y déficit (el "no")
#   era  = pre-s.XX (< 1900) o s.XX (>= 1900) por birth_date
#   k_esperada, veredicto SOSTIENE / NO_SOSTIENE
#
# Uso:
#   from lateral_masa_inercia_v1 import observar
#   out = observar(p_full_244_por_corte, birth_year=1756)
#   out = observar_desde_result(result_dict)  # lee /motor/cuts + birth_date

CAN_DECIDE_H = False
CONTRATO = "FORMULA_MASA_INERCIA_V1"
VERSION = "v1_20261113"

K_GENERAL = -0.46
K_PRE_XX = -0.73
K_XX = -0.19
TOL_ERA = 0.30
UMBRAL_N_SUP = 10.0
UMBRAL_K_FUERTE = -0.5


def _corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / (dx * dy)


def _pca2_radios(matriz):
    """Radio por corte: PCA centrada a 2 componentes (SVD numpy) de la matriz
    (n_cortes x 244). r = hypot(PC1, PC2). Invariante a rotación y signo."""
    import numpy as np
    X = np.asarray(matriz, dtype=float)
    X = X - X.mean(axis=0)
    # SVD: X = U S Vt ; scores = U * S
    U, S, _ = np.linalg.svd(X, full_matrices=False)
    scores = U * S
    pc1 = scores[:, 0]
    pc2 = scores[:, 1] if scores.shape[1] > 1 else np.zeros(len(pc1))
    return [float((a * a + b * b) ** 0.5) for a, b in zip(pc1, pc2)]


def observar(p_full_244_por_corte, birth_year=None):
    """p_full_244_por_corte: lista de dicts {familia: peso} o lista de listas.
    birth_year: año de nacimiento (int) o None (era desconocida)."""
    # Normalizar a matriz (n x 244) en orden de familias estable
    if isinstance(p_full_244_por_corte[0], dict):
        fams = sorted(p_full_244_por_corte[0].keys())
        matriz = [[float(c.get(f, 0.5)) for f in fams] for c in p_full_244_por_corte]
    else:
        matriz = [[float(x) for x in c] for c in p_full_244_por_corte]
    n = len(matriz)
    masas = [sum(fila) for fila in matriz]
    # El "no": familias bajo la base 0.5
    n_sup = [sum(1 for x in fila if x < 0.5) for fila in matriz]
    deficit = [sum(0.5 - x for x in fila if x < 0.5) for fila in matriz]
    radios = _pca2_radios(matriz)
    violencia = [abs(radios[i] - radios[i - 1]) for i in range(1, n)]
    masa_mid = [(masas[i] + masas[i - 1]) / 2.0 for i in range(1, n)]
    k = _corr(violencia, masa_mid)
    # Era y k esperada
    if birth_year is None:
        era = "DESCONOCIDA"
        k_esperada = K_GENERAL
    elif birth_year < 1900:
        era = "PRE_S_XX"
        k_esperada = K_PRE_XX
    else:
        era = "S_XX"
        k_esperada = K_XX
    n_sup_medio = sum(n_sup) / n if n else None
    deficit_medio = sum(deficit) / n if n else None
    # Veredicto
    if k is None:
        veredicto = "SIN_DATOS"
        ok_era = None
        ok_umbral = None
    else:
        ok_era = abs(k - k_esperada) <= TOL_ERA
        ok_umbral = (n_sup_medio < UMBRAL_N_SUP and k < UMBRAL_K_FUERTE) or \
                    (n_sup_medio >= UMBRAL_N_SUP and k >= UMBRAL_K_FUERTE)
        veredicto = "SOSTIENE" if (ok_era and ok_umbral) else "NO_SOSTIENE"
    return {
        "contrato": CONTRATO,
        "version": VERSION,
        "can_decide_H": CAN_DECIDE_H,
        "n_cortes": n,
        "masa_por_corte": [round(m, 2) for m in masas],
        "masa_media": round(sum(masas) / n, 2) if n else None,
        "delta_masa": round(masas[-1] - masas[0], 2) if n else None,
        "radio_por_corte": [round(r, 4) for r in radios],
        "violencia_por_paso": [round(v, 4) for v in violencia],
        "violencia_media": round(sum(violencia) / len(violencia), 4) if violencia else None,
        "k_medido": round(k, 3) if k is not None else None,
        "k_general": K_GENERAL,
        "era": era,
        "k_esperada": k_esperada,
        "n_sup_por_corte": n_sup,
        "n_sup_medio": round(n_sup_medio, 1) if n_sup_medio is not None else None,
        "deficit_medio": round(deficit_medio, 3) if deficit_medio is not None else None,
        "ok_era": ok_era,
        "ok_umbral": ok_umbral,
        "veredicto": veredicto,
    }


def observar_desde_result(result):
    """Lee un RESULT del motor (/motor/cuts[].P_FULL_244) y el birth_date."""
    motor = result.get("motor", {})
    cuts = motor.get("cuts", [])
    p_full = [c.get("P_FULL_244", {}) for c in cuts]
    # birth_year: del input/caso (birth_date 'YYYY-MM-DD' o año)
    birth_year = None
    for clave in ("birth_date", "fecha_nacimiento"):
        v = result.get(clave)
        if v:
            try:
                birth_year = int(str(v)[:4])
            except ValueError:
                pass
            break
    if birth_year is None:
        # buscar en freeze / entrada
        fr = result.get("freeze", {}) or {}
        v = fr.get("birth_date") or fr.get("z90_date")
        if v:
            try:
                birth_year = int(str(v)[:4])
            except ValueError:
                pass
    out = observar(p_full, birth_year=birth_year)
    out["case_id"] = result.get("case_id")
    return out
