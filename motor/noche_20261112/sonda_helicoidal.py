#!/usr/bin/env python3
"""Sonda helicoidal (2026-11-12, orden de Marco).

Pregunta: la vectorizacion del motor es plana (xt = [P(244), A(244), C(244)]
pegados; dX = cuerda recta entre cortes; kappa = angulo entre dos cuerdas).
El giro ~222-236 grados solo existe en los scripts locales de graficar,
fuera del motor. Esta sonda mide, desde los RESULT que ya existen, si una
lectura helicoidal (radio, fase, avance) predice el corte siguiente mejor
que la extrapolacion plana.

Protocolo honesto (corte ciego): el plano/eje (PCA) se ajusta SOLO con
C1..C9 (lo que se sabia al predecir). El C10 real se proyecta sobre ESA
base, sin reajustar. Nada del C10 alimenta la prediccion.

Casos: Mozart y Napoleon. Fuente: tableros P_FULL_244 por corte
(motor.cuts), que son los tableros exactos con los que se construye xt.
A y C estan planos en 0.5 en todos los cortes de estos dos casos, asi que
la helice no puede vivir en el espacio PAC: se construye sobre el tablero P.

Salidas:
- sonda_helicoidal_reporte.json (numeros)
- sonda_helicoidal.png (perfil horizontal + polar por caso, con el margen
  del radio y el C10 real vs predicho helicoidal vs predicho plano)
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
GIRO_ESPERADO = {"MOZART": 222.5, "NAPOLEON": 236.6}  # medido antes, scripts de espiral


def tableros_p(path):
    d = json.load(open(path))
    cuts = d["motor"]["cuts"]
    fams = sorted(cuts[0]["P_FULL_244"].keys())
    X = np.array([[c["P_FULL_244"][f] for f in fams] for c in cuts], dtype=float)
    return fams, X


def giro_plano_pc(p12):
    """Angulo total barrido (grados) de la trayectoria en el plano PC1-PC2,
    medido alrededor del centroide de la nube. Suma de angulos signados
    entre vectores consecutivos centroide->punto."""
    cen = p12.mean(axis=0)
    v = p12 - cen
    angs = np.arctan2(v[:, 1], v[:, 0])
    d = np.diff(np.unwrap(angs))
    return float(np.degrees(np.abs(d).sum())), float(np.degrees(d.sum()))


def pca_fit(X):
    mu = X.mean(axis=0)
    Xc = X - mu
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = (S ** 2) / (S ** 2).sum()
    return mu, Vt, var


def proyectar(X, mu, Vt):
    return (X - mu) @ Vt.T


def main():
    reporte = {}
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    for row, (nombre, (ciego_f, completo_f)) in enumerate(CASOS.items()):
        fams_c, X9 = tableros_p(BASE / ciego_f)
        fams_k, X10full = tableros_p(BASE / completo_f)
        assert fams_c == fams_k, "familias distintas entre ciego y completo"
        assert X10full.shape[0] == 10 and X9.shape[0] == 9
        # Los 9 primeros cortes del completo deben ser identicos a los del ciego.
        identicos = bool(np.allclose(X9, X10full[:9], atol=1e-12))
        X10 = X10full[9:10]

        # --- chequeo del giro conocido: PCA sobre los 10 (como el script viejo)
        mu10, Vt10, var10 = pca_fit(X10full)
        sc10 = proyectar(X10full, mu10, Vt10)
        giro_abs, giro_sig = giro_plano_pc(sc10[:, :2])

        # --- sonda: PCA ajustada SOLO con C1..C9
        mu, Vt, var = pca_fit(X9)
        sc9 = proyectar(X9, mu, Vt)          # 9 x 244 (scores)
        sc10r = proyectar(X10, mu, Vt)       # C10 real, misma base
        # Coordenadas helicoidales: eje = PC1 (avance h); plano = PC2-PC3.
        h9 = sc9[:, 0]
        r9 = np.hypot(sc9[:, 1], sc9[:, 2])
        phi9 = np.unwrap(np.arctan2(sc9[:, 2], sc9[:, 1]))
        h10r, r10r = float(sc10r[0, 0]), float(np.hypot(sc10r[0, 1], sc10r[0, 2]))
        phi10r = float(np.arctan2(sc10r[0, 2], sc10r[0, 1]))
        # Desenrollar la fase real contra la del C9 para comparar sin salto de rama.
        phi10r_unw = float(phi9[-1] + (phi10r - (phi9[-1] % (2 * np.pi)) + np.pi) % (2 * np.pi) - np.pi
                           if abs(phi10r - (phi9[-1] % (2 * np.pi))) > np.pi else phi9[-1] + (phi10r - (phi9[-1] % (2 * np.pi))))
        dphi = np.diff(phi9)
        dr = np.diff(r9)
        dh = np.diff(h9)

        # --- prediccion helicoidal: fase + mediana(dphi), radio + mediana(dr),
        #     avance + mediana(dh). Prediccion plana: ultimo paso en PC.
        phi10p = float(phi9[-1] + np.median(dphi))
        r10p = float(r9[-1] + np.median(dr))
        h10p = float(h9[-1] + np.median(dh))
        pc_hel = np.array([h10p, r10p * math.cos(phi10p), r10p * math.sin(phi10p)])
        pc_flat = sc9[-1, :3] + (sc9[-1, :3] - sc9[-2, :3])
        # Distancias en espacio PC (3 primeras) contra el C10 real.
        err_hel_pc = float(np.linalg.norm(pc_hel - sc10r[0, :3]))
        err_flat_pc = float(np.linalg.norm(pc_flat - sc10r[0, :3]))
        # Vuelta al espacio 244 (inversa PCA, 3 componentes) para el nivel familia.
        def inv(pc3):
            full = np.zeros(Vt.shape[0])
            full[:3] = pc3
            return mu + full @ Vt
        pred_hel_244 = inv(pc_hel)
        pred_flat_244 = inv(pc_flat)
        real_244 = X10[0]
        rmse_hel = float(np.sqrt(np.mean((pred_hel_244 - real_244) ** 2)))
        rmse_flat = float(np.sqrt(np.mean((pred_flat_244 - real_244) ** 2)))
        corr_hel = float(np.corrcoef(pred_hel_244, real_244)[0, 1])
        corr_flat = float(np.corrcoef(pred_flat_244, real_244)[0, 1])
        # Subidas reales en C10: familias que mas subieron de C9 a C10.
        delta_real = real_244 - X9[-1]
        top_suben = [fams_c[i] for i in np.argsort(delta_real)[-5:][::-1]]
        delta_hel = pred_hel_244 - X9[-1]
        delta_flat = pred_flat_244 - X9[-1]
        top_hel = [fams_c[i] for i in np.argsort(delta_hel)[-5:][::-1]]
        top_flat = [fams_c[i] for i in np.argsort(delta_flat)[-5:][::-1]]
        acierto_hel = len(set(top_suben) & set(top_hel))
        acierto_flat = len(set(top_suben) & set(top_flat))

        reporte[nombre] = {
            "cortes_ciego_identicos_a_completo": identicos,
            "var_PCA_ciego_PC1_PC2_PC3_pct": [round(100 * float(v), 1) for v in var[:3]],
            "giro_total_10cortes_grados": round(giro_abs, 1),
            "giro_esperado_grados": GIRO_ESPERADO[nombre],
            "radio_por_corte": [round(float(v), 3) for v in r9],
            "radio_C10_real": round(r10r, 3),
            "margen_radio_min_max": [round(float(r9.min()), 3), round(float(r9.max()), 3)],
            "fase_grados_por_corte": [round(float(math.degrees(v)), 1) for v in phi9],
            "dphi_grados_por_paso": [round(float(math.degrees(v)), 1) for v in dphi],
            "dphi_mediana_grados": round(float(math.degrees(np.median(dphi))), 1),
            "dphi_desviacion_grados": round(float(math.degrees(np.std(dphi))), 1),
            "avance_h_por_corte": [round(float(v), 3) for v in h9],
            "prediccion_C10": {
                "helicoidal": {"radio": round(r10p, 3), "fase_grados": round(float(math.degrees(phi10p)), 1),
                               "avance": round(h10p, 3), "error_PC": round(err_hel_pc, 3),
                               "rmse_244": round(rmse_hel, 4), "corr_244": round(corr_hel, 3),
                               "top5_suben_acierto": f"{acierto_hel}/5"},
                "plana": {"error_PC": round(err_flat_pc, 3), "rmse_244": round(rmse_flat, 4),
                          "corr_244": round(corr_flat, 3), "top5_suben_acierto": f"{acierto_flat}/5"},
                "real": {"radio": round(r10r, 3), "fase_grados": round(float(math.degrees(phi10r_unw)), 1),
                         "avance": round(h10r, 3)},
            },
            "top5_suben_reales_C10": top_suben,
            "top5_suben_predichos_helicoidal": top_hel,
            "top5_suben_predichos_plano": top_flat,
        }

        # --- figura: perfil horizontal (avance vs radio con signo) + polar
        ax = axes[row, 0]
        y9 = r9 * np.sin(phi9)  # perfil: seno de la fase = altura sobre el eje
        y10r = r10r * math.sin(phi10r_unw)
        y10_hel = r10p * math.sin(phi10p)
        y10_flat = pc_flat[2]  # pc3 del plano
        ax.axhspan(-r9.max(), -r9.min(), color="#dbeafe", alpha=0.6)
        ax.axhspan(r9.min(), r9.max(), color="#dbeafe", alpha=0.6)
        ax.axhline(r9.max(), color="#93c5fd", ls="--", lw=1)
        ax.axhline(-r9.max(), color="#93c5fd", ls="--", lw=1)
        ax.plot(h9, y9, "-o", color="#1d4ed8", lw=2, ms=6, label="C1..C9 (ciego)")
        for i, lb in enumerate([f"C{i+1}" for i in range(9)]):
            ax.annotate(lb, (h9[i], y9[i]), textcoords="offset points", xytext=(6, 6), fontsize=9)
        ax.scatter([h10r], [y10r], s=130, marker="*", color="red", zorder=5, label="C10 real")
        ax.scatter([h10p], [y10_hel], s=90, marker="o", facecolors="none", edgecolors="green", linewidths=2, zorder=5, label="C10 pred. helicoidal")
        ax.scatter([pc_flat[0]], [y10_flat], s=90, marker="x", color="orange", linewidths=2, zorder=5, label="C10 pred. plano")
        ax.set_xlabel("avance h (PC1)")
        ax.set_ylabel("radio con signo (r·sin φ)")
        ax.set_title(f"{nombre}: perfil horizontal — margen del radio [{r9.min():.2f}, {r9.max():.2f}]")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc="best")

        ax = axes[row, 1]
        ax.plot(sc9[:, 1], sc9[:, 2], "-o", color="#1d4ed8", lw=2, ms=6, label="C1..C9 (ciego)")
        for i, lb in enumerate([f"C{i+1}" for i in range(9)]):
            ax.annotate(lb, (sc9[i, 1], sc9[i, 2]), textcoords="offset points", xytext=(6, 6), fontsize=9)
        circ = plt.Circle((0, 0), float(np.median(r9)), color="#93c5fd", fill=False, ls="--", lw=1)
        ax.add_patch(circ)
        ax.scatter([sc10r[0, 1]], [sc10r[0, 2]], s=130, marker="*", color="red", zorder=5, label="C10 real")
        ax.scatter([pc_hel[1]], [pc_hel[2]], s=90, marker="o", facecolors="none", edgecolors="green", linewidths=2, zorder=5, label="C10 pred. helicoidal")
        ax.scatter([pc_flat[1]], [pc_flat[2]], s=90, marker="x", color="orange", linewidths=2, zorder=5, label="C10 pred. plano")
        ax.set_xlabel("PC2")
        ax.set_ylabel("PC3")
        ax.set_title(f"{nombre}: polar (mirando por el eje PC1) — giro {giro_abs:.0f}°")
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(fontsize=8, loc="best")

    fig.suptitle("Sonda helicoidal — Mozart y Napoleón (PCA ajustada solo con C1..C9)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT / "sonda_helicoidal.png", dpi=130)
    (OUT / "sonda_helicoidal_reporte.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(reporte, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
