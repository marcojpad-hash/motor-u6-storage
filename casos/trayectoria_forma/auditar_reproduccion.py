#!/usr/bin/env python3
"""Falla cerrada: no compara otros sujetos sin reproducir la proyección original.
Solo lectura de trazas; sin llamadas al motor, H, ranking ni apuesta.
"""
import sys
sys.dont_write_bytecode = True
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GEO = REPO / "motor/motor/geometria_multicapa"
sys.path.insert(0, str(GEO))
import adaptador_convergencia_real_v1 as A
import v153_convergencia_multinivel_v0_3 as G

EXPECTED = {"giro_abs_grados": 222.5, "R0": 0.448, "b_por_anio": 0.0759,
            "radio_R2": 0.929, "omega_grados_por_anio": 8.44, "seno_R2": 0.83}
TOLERANCE_GIRO_DEG = 2.0  # declarada; no se cambia para conseguir coincidencia

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes())

def frame(P):
    # EXACTAMENTE pca3 + helix_diagnostics, eje PCA predeterminado del adaptador.
    Z, var, _ = A.pca3(P)
    h = G.helix_diagnostics(Z)
    Y = Z - np.array(h["center"])
    axis = np.array(h["axis"])
    radial = Y - np.outer(Y @ axis, axis)
    norms = np.linalg.norm(radial, axis=1)
    valid = np.flatnonzero(norms > G.EPS)
    e1 = radial[valid[0]] / norms[valid[0]]
    e2 = np.cross(axis, e1)
    e2 = e2 / (np.linalg.norm(e2) + G.EPS)
    x, y = radial @ e1, radial @ e2
    phase = np.unwrap(np.arctan2(y, x))
    # La reconstrucción coincide con el diagnóstico de la función existente.
    assert np.isclose((phase[-1]-phase[0])/(2*np.pi), h["phase_total_turns"])
    return x, y, norms, phase, var, h

def plot(label, ids, x, y, r, phase):
    k = np.arange(1, len(ids)+1)
    fig = plt.figure(figsize=(13,10), layout="constrained")
    ax = fig.add_subplot(221, projection="3d")
    ax.plot(x, y, k, "o-")
    for a,b,c,s in zip(x,y,k,ids): ax.text(a,b,c,s,fontsize=8)
    ax.set(xlabel="radial x PCA (NO eje Tusi)", ylabel="radial y PCA", zlabel="índice de corte")
    ax.set_title("Proyección candidata existente; NO validada")
    ax = fig.add_subplot(222)
    ax.plot(k, r, "o-", label="radio observado")
    ax.set(xlabel="corte", ylabel="radio", title="Perfil — sin ajuste exponencial tras fallo del gate")
    ax.set_xticks(k, ids); ax.legend(); ax.grid(alpha=.3)
    ax = fig.add_subplot(223, projection="polar")
    ax.plot(phase, r, "o-")
    for a,b,s in zip(phase,r,ids): ax.annotate(s,(a,b),fontsize=8)
    ax.set_title("Polar — no equivale a las imágenes originales")
    ax = fig.add_subplot(224)
    ax.plot(k, np.rad2deg(phase-phase[0]), "o-", label="fase acumulada")
    ax.set(xlabel="corte", ylabel="grados", title="Fase — residual original NO identificable")
    ax.set_xticks(k, ids); ax.grid(alpha=.3); ax.legend()
    fig.suptitle(label + " | DIAGNÓSTICO DE FALLO, NO COMPARACIÓN TUSI", fontsize=15)
    target = HERE / (label + "_DIAGNOSTICO_PCA_NO_TUSI.png")
    fig.savefig(target, dpi=150); plt.close(fig)
    return target.name

def main():
    protected = list((REPO/"motor/motor").rglob("*.py")) + list(REPO.rglob("Engine_V5_CANONICO_SOLO.py")) + list(REPO.rglob("patterns_final_v14.json"))
    before = {str(p.relative_to(REPO)):sha(p) for p in protected}
    fixture_path = HERE / "MOZART_P10_EXTRACTO.json"
    fixture = read(fixture_path)
    fs = sorted(fixture["cuts"][0]["P_FULL_244"])
    P = np.array([[float(c["P_FULL_244"][f]) for f in fs] for c in fixture["cuts"]])
    x,y,r,phase,var,h = frame(P)
    degrees = float(np.rad2deg(phase[-1]-phase[0]))
    gate = abs(abs(degrees) - EXPECTED["giro_abs_grados"]) <= TOLERANCE_GIRO_DEG
    # Sin proyección Tusi original tampoco una coincidencia angular autorizaría comparar.
    assert not gate, "La traza candidata ha cambiado: investigar, no aprobar automáticamente"
    pngs = [plot("MOZART_10_CORTES", [c["corte"] for c in fixture["cuts"]], x,y,r,phase)]
    cases = []
    for label in ("MOZART_ORIGINAL_20260915","GALILEO_20260924","HAWKING","CHE","MLK"):
        folder = REPO/"casos/calibracion_z90"/label
        result_path = folder/"result.json.gz"
        d = read(result_path)
        prep = read(folder/"PREPARACION_Y_SELLO.json")
        ids = [c["corte"] for c in d["motor"]["cuts"]]
        cases.append({"caso":label,"n_cortes_traza":len(ids),"cortes":ids,"z90":prep["z90"],
                      "result_sha256":sha(result_path),"estado":"NO_COMPARADO_GATE_MOZART_FALLIDO",
                      "giro":None,"R0":None,"b":None,"R2":None,"omega":None,"seno_pct":None,
                      "cambio_regimen":None,"ruptura_fase":None,"forma":None})
        if label.startswith("MOZART"):
            q = np.array([[float(c["P_FULL_244"][f]) for f in fs] for c in d["motor"]["cuts"]])
            xx,yy,rr,pp,_,_ = frame(q)
            pngs.append(plot("MOZART_7_CORTES_CALIBRACION",ids,xx,yy,rr,pp))
    after = {str(p.relative_to(REPO)):sha(p) for p in protected}
    assert before == after
    output = {"estado":"FALLO_REPRODUCCION_PROYECCION_ORIGINAL_NO_LOCALIZADA",
              "modo":"TRAYECTORIA_DESCRIPTIVA_NO_PREDICTIVA", "can_decide_H":False,
              "alimenta_motor":False,"alimenta_ranking":False,"alimenta_apuesta":False,
              "fuente_mozart_10":fixture["source_path"], "fuente_sha256":fixture["source_sha256"],
              "extracto_sha256":sha(fixture_path),
              "proyeccion_candidata":"adaptador_convergencia_real_v1.pca3(P_FULL_244) + v153_convergencia_multinivel_v0_3.helix_diagnostics(eje PCA); no se afirma equivalencia Tusi",
              "codigo_sha256":{p.name:sha(p) for p in (GEO/"adaptador_convergencia_real_v1.py",GEO/"v153_convergencia_multinivel_v0_3.py")},
              "referencia_no_verificada":EXPECTED,"tolerancia_giro_grados":TOLERANCE_GIRO_DEG,
              "mozart_observado":{"n_cortes":len(P),"giro_firmado_grados":degrees,"giro_abs_grados":abs(degrees),"PCA_varianza":var,"diagnostico_existente":h,"radio":r.tolist(),"fase_radianes":phase.tolist()},
              "R0_b_omega_seno":"NO_AJUSTADOS: gate angular falla y no hay marco Tusi original",
              "imagenes_referencia":"FALLO_ARCHIVO_NO_EXISTE en las tres rutas suministradas",
              "comparacion_detenida":True,"casos":cases,"pngs":pngs,
              "integridad":{"archivos_protegidos_comprobados":len(before),"intactos":before==after},
              "limites":"Fallo de reproducción, no refutación de los números originales ni prueba de que la forma no se repita. Origen de fase, ejes, tiempo y traza de referencia no identificados."}
    (HERE/"RESULTADOS.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
    print(output["estado"])
    print("Mozart completo, giro firmado:",degrees,"abs:",abs(degrees),"vs referencia:",EXPECTED["giro_abs_grados"])
    print("Comparación detenida. Integridad:",output["integridad"])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
