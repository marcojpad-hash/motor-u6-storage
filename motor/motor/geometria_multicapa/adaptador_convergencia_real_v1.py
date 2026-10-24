#!/usr/bin/env python3
"""adaptador_convergencia_real_v1.py — LATERAL. can_decide_H=False. No escribe H1/H2, no reordena, no toca motor ni catálogo.
Construye trayectorias reales por corte desde el RESULT guardado (solo lectura) y aplica el módulo geométrico v0_3.
Tableros P/A/C = tres trayectorias paralelas (NO niveles jerárquicos). R732 = concatenación P|A|C (verificada contra motor.R732.dX_norm).
Tusi: fórmula del motor (motor/tusi_par_indice_exploratorio_v0_1.py, funciones extraídas por AST sin ejecutar el script).
"""
import ast, hashlib, json, random, sys, copy
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import v153_convergencia_multinivel_v0_3 as G
sys.dont_write_bytecode = True
SEED = 20261019; NNULL = 200; R = lambda x, n=6: None if x is None else round(float(x), n)
BOARDS = ("P", "A", "C")

def cargar_tusi_motor(motor: Path):
    src = (motor / "tusi_par_indice_exploratorio_v0_1.py").read_text()
    tree = ast.parse(src); keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("dps", "tusi")]
    ns = {"pi": np.pi}; exec(compile(ast.Module(body=keep, type_ignores=[]), "tusi_motor", "exec"), ns)
    return ns["dps"], ns["tusi"], hashlib.sha256(src.encode()).hexdigest()

def trayectorias(result):
    cuts = result["motor"]["cuts"]; ids = [c["corte"] for c in cuts]
    fams = sorted(cuts[0]["P_FULL_244"]); assert len(fams) == 244
    X = {b: np.array([[float(c[f"{b}_FULL_244"][f]) for f in fams] for c in cuts]) for b in BOARDS}
    X["R732"] = np.hstack([X[b] for b in BOARDS])
    stored = np.array(result["motor"]["R732"]["dX_norm"]); recon = np.linalg.norm(np.diff(X["R732"], axis=0), axis=1)
    chk = {"dX_norm_guardado": [R(v, 4) for v in stored], "dX_norm_reconstruido": [R(v, 4) for v in recon],
           "max_abs_diff": R(np.abs(stored - recon).max()), "coincide_hasta_redondeo_4_decimales": bool(np.abs(stored - recon).max() < 2e-3)}
    return ids, fams, X, chk

def pca3(Y):
    c = Y.mean(0); U, s, Vt = np.linalg.svd(Y - c, full_matrices=False)
    var = s ** 2 / max((s ** 2).sum(), 1e-12)
    return (Y - c) @ Vt[:3].T, [R(v, 4) for v in var[:3]], Vt

def helice_tablero(X, rng):
    Z, var, _ = pca3(X)
    hp = G.helix_diagnostics(Z)
    drift = Z[-1] - Z[0]; hd = G.helix_diagnostics(Z, axis=drift) if np.linalg.norm(drift) > 1e-12 else None
    # nulo: permutar orden de cortes (seed fija); fracción helix_like y radius_cv
    hl, cv = [], []
    for _ in range(NNULL):
        Zp, _, _ = pca3(X[rng.permutation(len(X))]); h = G.helix_diagnostics(Zp)
        hl.append(bool(h.get("helix_like"))); cv.append(h.get("radius_cv", np.nan))
    keep = ("helix_like", "radius_mean", "radius_cv", "phase_total_turns", "phase_direction_consistency", "axial_displacement", "pitch_per_turn_median", "n_points", "low_n_warning")
    f = lambda h: None if h is None else {k: (R(h[k]) if isinstance(h.get(k), float) else h.get(k)) for k in keep}
    cvn = np.array(cv, float)
    return {"varianza_explicada_pca3": var, "eje_pca": f(hp), "eje_deriva_primer_ultimo_corte": f(hd),
            "nulo_orden_permutado": {"n": NNULL, "seed": SEED, "frac_helix_like_pct": R(100 * np.mean(hl), 2),
                                     "radius_cv_mediana": R(np.nanmedian(cvn), 4),
                                     "frac_radius_cv_menor_o_igual_observado_pct": R(100 * np.nanmean(cvn <= hp.get("radius_cv", np.inf)), 2)},
            "advertencia": "8 puntos es muy poco: fase ambigua, eje PCA sesgado hacia la deriva global; descriptivo, no prueba de hélice."}

def pares_tableros(ids, X):
    out = {}; boards = list(BOARDS)
    for i, a in enumerate(boards):
        for b in boards[i + 1:]:
            filas = []
            for k in range(3, len(ids) + 1):   # solo C1..Ck
                A, B = X[a][:k], X[b][:k]
                step = np.mean([np.linalg.norm(np.diff(M, axis=0), axis=1).mean() for M in (A, B)])
                tau = 0.1 * step
                S = np.vstack([A, B]); c = S.mean(0); _, s, Vt = np.linalg.svd(S - c, full_matrices=False)
                r = int((s > 1e-10).sum()); Ar, Br = (A - c) @ Vt[:r].T, (B - c) @ Vt[:r].T  # rotación completa: preserva distancias
                cmp = G.compare_trajectories(Ar, Br, projection_dims=list(range(min(3, r))), tol=tau)
                pt = cmp["projection_test"]
                filas.append({"k": ids[k - 1], "cortes_usados": ids[:k], "tau_0.1xpaso_medio": R(tau),
                              "d_full_en_Ck": R(cmp["distance_sequence"][-1]), "d_proj3_en_Ck": R(pt["projected_distance_sequence"][-1]),
                              "d_full_min_C1..Ck": R(cmp["minimum_distance"]), "monotono_no_creciente": cmp["monotone_nonincreasing"],
                              "convergencia_full_en_Ck": cmp["observed_endpoint_convergence"],
                              "interseccion_proyeccion_en_Ck": bool(pt["projected_distance_sequence"][-1] <= tau),
                              "falso_positivo_proyeccion_en_Ck": pt["per_cut_projection_false_positive"][-1],
                              "cociente_proj_full_en_Ck": R(pt["projected_distance_sequence"][-1] / cmp["distance_sequence"][-1], 4),
                              "familias_crudas_coinciden_en_Ck_pct": R(100 * np.mean(np.abs(A[-1] - B[-1]) <= tau), 2),
                              "falso_positivo_si_se_proyecta_a_familias_coincidentes": bool(np.any(np.abs(A[-1] - B[-1]) <= tau) and cmp["distance_sequence"][-1] > tau)})
            full = [np.linalg.norm(X[a][t] - X[b][t]) for t in range(len(ids))]
            out[f"{a}~{b}"] = {"d_full_244_por_corte": dict(zip(ids, [R(v, 4) for v in full])),
                               "final_sobre_inicial": R(full[-1] / full[0], 4), "por_prefijo": filas}
    return out

def tusi_bloque(ids, X, fams, dps, tusi, rng, cuts, motor):
    # (a) entrada original del motor: series P top5 (billar v0_1.extraer_series_p)
    sys.path.insert(0, str(motor)); import billar_circular_convergencia_v0_1 as V1
    _ids, series = V1.extraer_series_p(copy.deepcopy(cuts))
    def tabla(D, pares):
        filas = []
        for a, b, da, db in pares:
            t, n = tusi(da, db)
            if t is None: continue
            nul = []
            for _ in range(NNULL):
                q = db[:]; rng.shuffle(q); tn, _ = tusi(da, q)
                if tn is not None: nul.append(tn)
            mu = np.mean(nul) if nul else None; sd = np.std(nul) if nul else None
            loc = G.tusi_local_coupling([0 if x is None else x for x in da], [0 if y is None else y for y in db])
            filas.append({"par": [a, b], "tusi_motor": R(t, 4), "n_pasos_vivos": n, "z_vs_nulo": R((t - mu) / sd, 3) if sd else None,
                          "tusi_local_modulo_externo": R(loc["mean_local_index"], 4)})
        return filas
    D = {f: dps(series[f]) for f in series}; nm = sorted(D)
    a_rows = tabla(D, [(x, y, D[x], D[y]) for i, x in enumerate(nm) for y in nm[i + 1:]])
    # (b) extensión: misma familia entre tableros, incrementos de FULL_244
    b_rows = []
    for i, p in enumerate(BOARDS):
        for q in BOARDS[i + 1:]:
            dP = np.diff(X[p], axis=0); dQ = np.diff(X[q], axis=0)
            rows = tabla(None, [(f"{p}:{f}", f"{q}:{f}", dP[:, j].tolist(), dQ[:, j].tolist()) for j, f in enumerate(fams)])
            zs = [r["z_vs_nulo"] for r in rows if r["z_vs_nulo"] is not None]
            dif = [abs(r["tusi_motor"] - r["tusi_local_modulo_externo"]) for r in rows if r["tusi_local_modulo_externo"] is not None]
            rows.sort(key=lambda r: -(r["z_vs_nulo"] or -9))
            b_rows.append({"par_tableros": f"{p}~{q}", "n_familias": len(rows), "tusi_motor_mediana": R(np.median([r["tusi_motor"] for r in rows]), 4),
                           "n_z_mayor_2": int(sum(z > 2 for z in zs)), "esperado_por_azar_aprox_z_mayor_2": R(0.023 * len(zs), 1),
                           "diferencia_motor_vs_local_mediana": R(np.median(dif), 4), "diferencia_motor_vs_local_max": R(max(dif), 4),
                           "top5_por_z": rows[:5]})
    return {"a_entrada_motor_P_top5": a_rows, "b_familia_entre_tableros_FULL_244": b_rows,
            "lectura": "retrospectiva sobre todos los cortes del RESULT; sin corrección por comparaciones múltiples salvo el conteo esperado por azar."}

def run(result_path: Path, motor: Path, sidecar_out: Path, sidecar_py: Path):
    raw = result_path.read_bytes(); result = json.loads(raw); rsha = hashlib.sha256(raw).hexdigest()
    sys.path.insert(0, str(sidecar_py.parent)); import sidecar_latentes_v1 as SL
    h0 = SL.huella_H(result)
    rng_np = np.random.default_rng(SEED); rng = random.Random(SEED)
    ids, fams, X, chk = trayectorias(result)
    dps, tusi, tsha = cargar_tusi_motor(motor)
    hel = {b: helice_tablero(X[b], rng_np) for b in ("P", "A", "C", "R732")}
    pares = pares_tableros(ids, X)
    vel = {b: dict(zip(ids[1:], [R(v, 4) for v in np.linalg.norm(np.diff(X[b], axis=0), axis=1)])) for b in X}
    tus = tusi_bloque(ids, X, fams, dps, tusi, rng, result["motor"]["cuts"], motor)
    g = (((result.get("laterales_unico") or {}).get("sensores_pre") or {}).get("marco_7783_geometria") or {}).get("anillos") or {}
    marco = {"fuente": "RESULT.laterales_unico.sensores_pre.marco_7783_geometria.anillos (guardado; no recalculado)",
             "anillos": g.get("anillos", "TORTUGAS"), "tusi_anillos_guardado": (g.get("helice") or {}).get("tusi_anillos", "TORTUGAS")}
    s = json.loads(sidecar_out.read_text())
    ev = {}
    for r in s.get("4_reconvergencia") or []:
        ev.setdefault(r["corte_reaparicion"], []).append(f'{r["relacion"]}:{r["veredicto"]}')

    rel = []
    for k, cid in enumerate(ids):
        fila = {"corte": cid, "cortes_usados": ids[:k + 1], "n_reconvergencias_sidecar": len(ev.get(cid, [])),
                "reconvergencias_sidecar": sorted(ev.get(cid, [])),
                "velocidad_paso": {b: vel[b].get(cid) for b in ("P", "A", "C")}}
        for pk, pv in pares.items():
            pr = [x for x in pv["por_prefijo"] if x["k"] == cid]
            fila[f"{pk}_d_full"] = pv["d_full_244_por_corte"][cid]
            if pr: fila[f"{pk}_falso_positivo_proj"] = pr[0]["falso_positivo_proyeccion_en_Ck"]
        rel.append(fila)
    h1 = SL.huella_H(json.loads(result_path.read_bytes()))
    return {"version": "ADAPTADOR_CONVERGENCIA_REAL_V1_20261019_GENERICO_U6UNIF", "can_decide_H": False, "Alimenta_H": "NO", "reordena": False,
            "result": str(result_path), "result_sha256": rsha, "tusi_motor_sha256": tsha, "cortes": ids, "chequeo_R732": chk,
            "jerarquia_recursiva": {"estado": "OMITIDA", "razon": "No hay jerarquía sincronizada guardada: P/A/C son tableros paralelos (no niveles); no hay sub-cortes; los tokens por corte son 2 por tablero (n_tokens) y el mapa familia->token del catálogo no da trayectoria hija sincronizada. Además fit_affine_map_holdout es no identificable con 8 cortes en 244-D."},
            "helice_por_tablero": hel, "convergencia_pares_tableros": pares, "velocidad_por_tablero": vel,
            "tusi": tus, "marco_7783_guardado": marco, "relacion_sidecar_latentes": rel,
            "verificacion_H": {"huella_antes": h0, "huella_despues": h1, "H_intacto": h0 == h1}}

if __name__ == "__main__":
    # uso: adaptador_convergencia_real_v1.py RESULT.json MOTOR_DIR SIDECAR_OUT.json SALIDA.json
    a = sys.argv
    out = run(Path(a[1]), Path(a[2]), Path(a[3]), HERE / "sidecar_latentes_v1.py")
    Path(a[4]).write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    print("ok", out["verificacion_H"])
