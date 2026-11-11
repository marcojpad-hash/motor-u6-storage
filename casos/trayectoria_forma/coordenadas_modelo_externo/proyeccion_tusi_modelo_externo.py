#!/usr/bin/env python3
"""Origen: script del otro modelo pasado por Mj 2026-11-11 (copia fiel; rutas /home/hatch originales).
Tabla de coordenadas: x = eje Tusi (PC1 rotado para que el diametro C1->C10 quede horizontal),
y = transversal (PC2 rotado), r = distancia al eje, fase = angulo desenvuelto (grados), ano decimal.
Analisis post-hoc sobre traza_P del RESULT; NO es parte del motor."""
import json, math, datetime
import numpy as np

def load(res_path, inp_path):
    d = json.load(open(res_path))
    crudo = d["motor"]["annex"]["traza_P"]["crudo_P"]
    fams = sorted(crudo.keys())
    X = np.array([[crudo[f][t] for f in fams] for t in range(10)])
    inp = json.load(open(inp_path))
    years = np.array([datetime.date.fromisoformat(c["date"]).year +
                      (datetime.date.fromisoformat(c["date"]).timetuple().tm_yday - 1) / 365.25
                      for c in inp["cuts"]])
    Xc = X - X.mean(axis=0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    scores = U * S
    pc1, pc2 = scores[:, 0], scores[:, 1]
    dx, dy = pc1[-1] - pc1[0], pc2[-1] - pc2[0]
    th = math.radians(-math.degrees(math.atan2(dy, dx)))
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    rot = scores[:, :2] @ R.T
    rx, ry = rot[:, 0], rot[:, 1]
    r = np.hypot(rx, ry)
    phi = np.degrees(np.unwrap(np.arctan2(ry, rx)))
    return rx, ry, r, phi, years

M = "/home/hatch/workspace/u6-alterno/motor-cameo/motor/RESULT_MOZART_Z90_PRECEDENTE.json"
N = "/home/hatch/workspace/u6-alterno/motor-cameo/motor/RESULT_NAPOLEON_Z90_10CORTES.json"
MI = "/home/hatch/workspace/u6-alterno/mozart/INPUT_FROZEN.json"
NI = "/home/hatch/workspace/u6-alterno/motor-cameo/casos/precedentes/NAPOLEON_10_CORTES/entrada.json"
OUT = "/home/hatch/workspace/u6-alterno/mozart"

if __name__ == "__main__":
    for name, res, inp in [("MOZART", M, MI), ("NAPOLEON", N, NI)]:
        rx, ry, r, phi, years = load(res, inp)
        lines = ["corte,ano,x_tusi,y_transversal,radio,fase_grados"]
        for i in range(10):
            lines.append(f"C{i+1},{years[i]:.2f},{rx[i]:.4f},{ry[i]:.4f},{r[i]:.4f},{phi[i]:.1f}")
        open(f"{OUT}/tabla_coordenadas_{name.lower()}.csv", "w").write("\n".join(lines) + "\n")
        print(f"giro total {name}: {phi[-1]-phi[0]:.1f} grados")
