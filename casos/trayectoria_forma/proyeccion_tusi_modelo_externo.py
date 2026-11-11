#!/usr/bin/env python3
"""Generalización a n cortes del script fiel recibido de Mj.
Original preservado: coordenadas_modelo_externo/proyeccion_tusi_modelo_externo.py
SHA256 original: e622e9af2170a8fb7f06afeb821d93c13ba46907b690c807349d5f0b7a3c5ac6
Mismo centrado, SVD (scores=U*S), PC1/PC2 y rotación C1→Cn horizontal.
Cambios: n dinámico, API reutilizable, validación/JSON; sin rutas /home/hatch.
Post-hoc únicamente; no decide H/ranking/apuesta ni modifica el motor.
"""
import sys
sys.dont_write_bytecode = True
import argparse,csv,datetime as dt,gzip,json
from pathlib import Path
import numpy as np

def project_crudo(crudo):
    families=sorted(crudo)
    if not families:raise ValueError("crudo_P vacío")
    X=np.array([crudo[f] for f in families],dtype=float).T
    if X.ndim!=2 or X.shape[0]<3 or X.shape[1]<2 or not np.isfinite(X).all():
        raise ValueError("crudo_P debe ser familias × n_cortes>=3, finito")
    center=X.mean(axis=0);C=X-center
    U,s,Vt=np.linalg.svd(C,full_matrices=False)
    scores=U*s
    P=scores[:,:2]
    chord=P[-1]-P[0]
    if np.linalg.norm(chord)<=1e-12:raise ValueError("C1→Cn no define eje de rotación")
    angle=np.arctan2(chord[1],chord[0]);c,sin=np.cos(angle),np.sin(angle)
    rotation=np.array([[c,-sin],[sin,c]])
    Q=P@rotation
    r=np.hypot(Q[:,0],Q[:,1]);phase=np.rad2deg(np.unwrap(np.arctan2(Q[:,1],Q[:,0])))
    return {"familias":families,"center":center.tolist(),"loadings_PC1_PC2":Vt[:2].tolist(),"rotation_radians":float(angle),"x_tusi":Q[:,0].tolist(),"y_transversal":Q[:,1].tolist(),"radio":r.tolist(),"fase_grados":phase.tolist(),"giro_neto_grados":float(phase[-1]-phase[0]),"giro_neto_absoluto_grados":float(abs(phase[-1]-phase[0])),"estado":"TRANSFORMACION_GENERALIZADA_DEL_SCRIPT_FIEL", "PCA_varianza_2":(s[:2]**2/np.sum(s**2)).tolist()}

def year_decimal(value):
    d=dt.date.fromisoformat(value);s=dt.date(d.year,1,1)
    return d.year+(d-s).days/365.25

def project_result(result,inp):
    crudo=result["motor"]["annex"]["traza_P"]["crudo_P"]
    q=project_crudo(crudo);n=len(q["radio"])
    if len(inp["cuts"])!=n:raise ValueError("Input y crudo_P tienen distinto número de cortes")
    q["cortes"]=[c["id"] for c in inp["cuts"]]
    q["year"]=[year_decimal(c["date"]) for c in inp["cuts"]]
    return q

def compare_csv(projection,path,tolerance=None):
    with Path(path).open(encoding="utf-8-sig",newline="") as handle:rows=list(csv.DictReader(handle))
    if len(rows)!=len(projection["radio"]):return {"passed":False,"error":"n_cortes_distinto"}
    errors={}
    for field,key in [("ano","year"),("x_tusi","x_tusi"),("y_transversal","y_transversal"),("radio","radio"),("fase_grados","fase_grados")]:
        expected=np.array([float(r[field]) for r in rows]);observed=np.array(projection[key])
        errors[field]=float(np.max(np.abs(expected-observed)))
    ids=[r["corte"] for r in rows]
    tolerances={"ano":0.005+1e-10,"x_tusi":0.00005+1e-10,"y_transversal":0.00005+1e-10,"radio":0.00005+1e-10,"fase_grados":0.05+1e-10} if tolerance is None else {k:tolerance for k in errors}
    return {"passed":bool(ids==projection["cortes"] and all(v<=tolerances[k] for k,v in errors.items())),"tolerance_by_serialized_precision":tolerances,"max_abs_error":errors,"ids_equal":ids==projection["cortes"]}

def read_json(p):
    raw=Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith(".gz") else raw)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("result",type=Path);ap.add_argument("input",type=Path);ap.add_argument("--expected-csv",required=True,type=Path);ap.add_argument("--out",required=True,type=Path);args=ap.parse_args()
    p=project_result(read_json(args.result),read_json(args.input));p["gate_individual"]=compare_csv(p,args.expected_csv)
    args.out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n")
    print(p["gate_individual"])
    return 0 if p["gate_individual"]["passed"] else 2

if __name__=="__main__":raise SystemExit(main())
