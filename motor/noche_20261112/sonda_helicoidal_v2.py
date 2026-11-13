#!/usr/bin/env python3
"""Sonda helicoidal v2 (2026-11-12, orden de Marco).

v1 usaba el PC1 como eje: un artefacto de la proyeccion, y el X/Y puede
estar distorsionado (sobre todo el X). v2 INFIERE el eje del movimiento:
la direccion (en el espacio de los 3 primeros PC, blanqueado para quitar
la distorsion de escala) que deja el radio MAS ESTABLE, con la fase
girando de verdad. El radio se mide desde ESE eje ("radio de diferencia").

Protocolo honesto (corte ciego): PCA y eje ajustados SOLO con C1..C9.
El C10 real se proyecta sobre esa base, sin reajustar.

Metodo del eje: busqueda sobre la esfera unidad (gruesa + refinado) del
vector u que minimiza CV(r) = std(r)/mean(r) de las distancias
perpendiculares al eje, exigiendo que la fase desenrollada recorra al
menos ~86 grados (si no, un radio constante sin giro es una recta
desplazada, no una helice). Espacio blanqueado: cada PC dividido por su
desviacion en el prefijo ciego, para que ninguna escala domine el ajuste.

Comparacion en el mismo C10: eje inferido (v2) vs eje PC1 (v1) vs plano
(ultimo paso). Metricas: error en espacio PC, RMSE y correlacion en las
244 familias, y acierto del top-5 de familias que suben.

Salidas: sonda_helicoidal_v2_reporte.json, sonda_helicoidal_v2.png.
"""
import json, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo/motor")
OUT = Path("/home/hatch/workspace/u6-alterno")
CASOS = {
    "MOZART": ("RESULT_MOZART_CIEGO_C9.json", "RESULT_MOZART_Z90_PRECEDENTE.json"),
    "NAPOLEON": ("RESULT_NAPOLEON_CIEGO_C9.json", "RESULT_NAPOLEON_Z90_10CORTES.json"),
}


def tableros_p(path):
    d = json.load(open(path))
    cuts = d["motor"]["cuts"]
    fams = sorted(cuts[0]["P_FULL_244"].keys())
    X = np.array([[c["P_FULL_244"][f] for f in fams] for c in cuts], dtype=float)
    return fams, X


def base_perp(u):
    """Base ortonormal (e1, e2) perpendicular a u."""
    a = np.array([0.0, 0.0, 1.0]) if abs(u[2]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = np.cross(u, a)
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(u, e1)
    return e1, e2


def helice_coords(Wc, u):
    """Coordenadas helicoidales de puntos centrados Wc alrededor del eje u."""
    e1, e2 = base_perp(u)
    h = Wc @ u
    perp = Wc - np.outer(h, u)
    r = np.linalg.norm(perp, axis=1)
    phi = np.arctan2(perp @ e2, perp @ e1)
    return h, r, phi, e1, e2, perp


def ajuste_eje(Wc):
    """Busca u que minimiza CV(r) con giro de fase >= ~86 grados."""
    def evaluar(u):
        h, r, phi, _, _, _ = helice_coords(Wc, u)
        cv = float(np.std(r) / (np.mean(r) + 1e-12))
        viento = float(np.abs(np.diff(np.unwrap(phi))).sum())
        return cv, viento
    cands = []
    for az in np.arange(0, 360, 5):
        for pol in np.arange(0, 181, 5):
            a, p = np.radians(az), np.radians(pol)
            u = np.array([np.sin(p) * np.cos(a), np.sin(p) * np.sin(a), np.cos(p)])
            cv, viento = evaluar(u)
            cands.append((cv, viento, u))
    # Mejor CV entre los que giran de verdad; si ninguno, mejor CV con aviso.
    giran = [c for c in cands if c[1] >= 1.5]
    pool = giran if giran else cands
    cv0, _, u0 = min(pool, key=lambda c: c[0])
    # Refinado local +-5 grados, paso 0.5.
    best = (cv0, u0)
    az0 = math.degrees(math.atan2(u0[1], u0[0])) % 360
    pol0 = math.degrees(math.acos(max(-1.0, min(1.0, u0[2]))))
    for az in np.arange(az0 - 5, az0 + 5.1, 0.5):
        for pol in np.arange(max(0, pol0 - 5), min(180, pol0 + 5) + 0.1, 0.5):
            a, p = np.radians(az), np.radians(pol)
            u = np.array([np.sin(p) * np.cos(a), np.sin(p) * np.sin(a), np.cos(p)])
            cv, viento = evaluar(u)
            if viento >= 1.5 and cv < best[0]:
                best = (cv, u)
    return best[1], best[0], bool(giran)


def predecir(h, r, phi):
    dphi = np.diff(np.unwrap(phi))
    return (float(h[-1] + np.median(np.diff(h))),
            float(r[-1] + np.median(np.diff(r))),
            float(phi[-1] + np.median(dphi)))


def main():
    reporte = {}
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    for row, (nombre, (ciego_f, completo_f)) in enumerate(CASOS.items()):
        fams, X9 = tableros_p(BASE / ciego_f)
        _, X10full = tableros_p(BASE / completo_f)
        assert np.allclose(X9, X10full[:9], atol=1e-12)
        X10 = X10full[9:10]

        # PCA solo con C1..C9; 3 primeros componentes.
        mu = X9.mean(axis=0)
        U, S, Vt = np.linalg.svd(X9 - mu, full_matrices=False)
        sc9 = (X9 - mu) @ Vt.T[:, :3]
        sc10r = (X10 - mu) @ Vt.T[:, :3]
        # Blanqueo: cada PC entre su desviacion del prefijo (quita la
        # distorsion de escala; sobre todo el X).
        s = sc9.std(axis=0)
        W9 = sc9 / s
        W10r = sc10r / s
        Wc = W9 - W9.mean(axis=0)
        cen = W9.mean(axis=0)

        # --- eje inferido (v2)
        u, cv_eje, gira = ajuste_eje(Wc)
        h, r, phi, e1, e2, perp = helice_coords(Wc, u)
        phi_u = np.unwrap(phi)
        h10p, r10p, phi10p = predecir(h, r, phi_u)
        # C10 real en las mismas coordenadas (misma base, mismo eje).
        W10c = W10r - cen
        h10r = float(W10c @ u)
        perp10 = W10c - h10r * u
        r10r = float(np.linalg.norm(perp10))
        phi10r_raw = float(math.atan2(perp10 @ e2, perp10 @ e1))
        dphi_real = (phi10r_raw - (phi_u[-1] % (2 * np.pi)) + np.pi) % (2 * np.pi) - np.pi
        phi10r = float(phi_u[-1] + dphi_real)
        # Reconstruccion del punto predicho -> espacio 244.
        W_pred = cen + h10p * u + r10p * (math.cos(phi10p) * e1 + math.sin(phi10p) * e2)
        sc_pred = W_pred * s
        pred_244 = mu + np.concatenate([sc_pred, np.zeros(Vt.shape[0] - 3)]) @ Vt
        real_244 = X10[0]
        err_v2_w = float(np.linalg.norm(W_pred - W10r))
        err_v2_pc = float(np.linalg.norm(sc_pred - sc10r[0]))
        rmse_v2 = float(np.sqrt(np.mean((pred_244 - real_244) ** 2)))
        corr_v2 = float(np.corrcoef(pred_244, real_244)[0, 1])
        delta_real = real_244 - X9[-1]
        top_real = [fams[i] for i in np.argsort(delta_real)[-5:][::-1]]
        top_v2 = [fams[i] for i in np.argsort(pred_244 - X9[-1])[-5:][::-1]]

        # --- eje PC1 (v1), mismo prefijo, para comparar en igualdad.
        u1 = np.array([1.0, 0.0, 0.0])
        h1, r1, phi1, _, _, _ = helice_coords(Wc, u1)
        phi1_u = np.unwrap(phi1)
        cv1 = float(np.std(r1) / (np.mean(r1) + 1e-12))
        dphi1 = np.diff(phi1_u)
        h1p, r1p, phi1p = predecir(h1, r1, phi1_u)
        W_pred1 = cen + h1p * u1 + r1p * (math.cos(phi1p) * np.array([0.0, 1.0, 0.0]) + math.sin(phi1p) * np.array([0.0, 0.0, 1.0]))
        sc_pred1 = W_pred1 * s
        pred1_244 = mu + np.concatenate([sc_pred1, np.zeros(Vt.shape[0] - 3)]) @ Vt
        err_v1_w = float(np.linalg.norm(W_pred1 - W10r))
        rmse_v1 = float(np.sqrt(np.mean((pred1_244 - real_244) ** 2)))
        corr_v1 = float(np.corrcoef(pred1_244, real_244)[0, 1])
        top_v1 = [fams[i] for i in np.argsort(pred1_244 - X9[-1])[-5:][::-1]]

        # --- plano (ultimo paso en PC blanqueado)
        W_flat = W9[-1] + (W9[-1] - W9[-2])
        sc_flat = W_flat * s
        pred_flat_244 = mu + np.concatenate([sc_flat, np.zeros(Vt.shape[0] - 3)]) @ Vt
        err_flat_w = float(np.linalg.norm(W_flat - W10r))
        rmse_flat = float(np.sqrt(np.mean((pred_flat_244 - real_244) ** 2)))
        top_flat = [fams[i] for i in np.argsort(pred_flat_244 - X9[-1])[-5:][::-1]]

        reporte[nombre] = {
            "eje_inferido_u_blanqueado": [round(float(v), 3) for v in u],
            "eje_inferido_vs_PC1_angulo_grados": round(float(math.degrees(math.acos(max(-1.0, min(1.0, abs(float(u @ u1))))))), 1),
            "eje_gira_de_verdad": gira,
            "radio_CV_eje_inferido": round(cv_eje, 3),
            "radio_CV_eje_PC1_v1": round(cv1, 3),
            "radio_por_corte_eje_inferido": [round(float(v), 3) for v in r],
            "margen_radio_eje_inferido": [round(float(r.min()), 3), round(float(r.max()), 3)],
            "radio_C10_real": round(r10r, 3),
            "fase_grados_por_corte_eje_inferido": [round(float(math.degrees(v)), 1) for v in phi_u],
            "dphi_mediana_grados_v2": round(float(math.degrees(np.median(np.diff(phi_u)))), 1),
            "dphi_desviacion_grados_v2": round(float(math.degrees(np.std(np.diff(phi_u)))), 1),
            "dphi_mediana_grados_v1_PC1": round(float(math.degrees(np.median(dphi1))), 1),
            "dphi_desviacion_grados_v1_PC1": round(float(math.degrees(np.std(dphi1))), 1),
            "avance_h_por_corte_v2": [round(float(v), 3) for v in h],
            "prediccion_C10": {
                "eje_inferido_v2": {"error_blanqueado": round(err_v2_w, 3), "error_PC": round(err_v2_pc, 3),
                                    "rmse_244": round(rmse_v2, 4), "corr_244": round(corr_v2, 3),
                                    "top5_acierto": f"{len(set(top_real) & set(top_v2))}/5",
                                    "radio_pred": round(r10p, 3), "fase_pred_grados": round(float(math.degrees(phi10p)), 1),
                                    "avance_pred": round(h10p, 3)},
                "eje_PC1_v1": {"error_blanqueado": round(err_v1_w, 3), "rmse_244": round(rmse_v1, 4),
                               "corr_244": round(corr_v1, 3), "top5_acierto": f"{len(set(top_real) & set(top_v1))}/5"},
                "plano": {"error_blanqueado": round(err_flat_w, 3), "rmse_244": round(rmse_flat, 4),
                          "top5_acierto": f"{len(set(top_real) & set(top_flat))}/5"},
                "real": {"radio": round(r10r, 3), "fase_grados": round(float(math.degrees(phi10r)), 1),
                         "avance": round(h10r, 3)},
            },
            "top5_suben_reales_C10": top_real,
            "top5_suben_predichos_v2": top_v2,
        }

        # --- figura: perfil horizontal + polar con el eje inferido
        ax = axes[row, 0]
        y9 = r * np.sin(phi_u)
        y10r = r10r * math.sin(phi10r)
        y10_v2 = r10p * math.sin(phi10p)
        y10_v1 = r1p * math.sin(phi1p)
        ax.axhspan(-r.max(), -r.min(), color="#dbeafe", alpha=0.6)
        ax.axhspan(r.min(), r.max(), color="#dbeafe", alpha=0.6)
        ax.axhline(r.max(), color="#93c5fd", ls="--", lw=1)
        ax.axhline(-r.max(), color="#93c5fd", ls="--", lw=1)
        ax.plot(h, y9, "-o", color="#1d4ed8", lw=2, ms=6, label="C1..C9 (ciego)")
        for i, lb in enumerate([f"C{i+1}" for i in range(9)]):
            ax.annotate(lb, (h[i], y9[i]), textcoords="offset points", xytext=(6, 6), fontsize=9)
        ax.scatter([h10r], [y10r], s=130, marker="*", color="red", zorder=5, label="C10 real")
        ax.scatter([h10p], [y10_v2], s=90, marker="o", facecolors="none", edgecolors="green", linewidths=2, zorder=5, label="C10 pred. eje inferido")
        ax.scatter([h1p], [y10_v1], s=90, marker="s", facecolors="none", edgecolors="purple", linewidths=2, zorder=5, label="C10 pred. eje PC1 (v1)")
        h_flat = float((W_flat - cen) @ u)
        y_flat = float((W_flat - cen) @ e2)
        ax.scatter([h_flat], [y_flat], s=90, marker="x", color="orange", linewidths=2, zorder=5, label="C10 pred. plano")
        ax.set_xlabel("avance h (eje inferido, blanqueado)")
        ax.set_ylabel("radio con signo (r·sin φ)")
        ax.set_title(f"{nombre}: perfil horizontal — margen del radio [{r.min():.2f}, {r.max():.2f}]")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc="best")

        ax = axes[row, 1]
        ax.plot(perp[:, 0], perp[:, 1], "-o", color="#1d4ed8", lw=2, ms=6, label="C1..C9 (ciego)")
        for i, lb in enumerate([f"C{i+1}" for i in range(9)]):
            ax.annotate(lb, (perp[i, 0], perp[i, 1]), textcoords="offset points", xytext=(6, 6), fontsize=9)
        circ = plt.Circle((0, 0), float(np.median(r)), color="#93c5fd", fill=False, ls="--", lw=1)
        ax.add_patch(circ)
        ax.scatter([float(perp10 @ e1)], [float(perp10 @ e2)], s=130, marker="*", color="red", zorder=5, label="C10 real")
        ax.scatter([r10p * math.cos(phi10p)], [r10p * math.sin(phi10p)], s=90, marker="o", facecolors="none", edgecolors="green", linewidths=2, zorder=5, label="C10 pred. eje inferido")
        ax.set_xlabel("perp·e1")
        ax.set_ylabel("perp·e2")
        ax.set_title(f"{nombre}: polar (mirando por el eje inferido)")
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(fontsize=8, loc="best")

    fig.suptitle("Sonda helicoidal v2 — eje inferido (PCA + eje ajustados solo con C1..C9)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT / "sonda_helicoidal_v2.png", dpi=130)
    (OUT / "sonda_helicoidal_v2_reporte.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(reporte, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
