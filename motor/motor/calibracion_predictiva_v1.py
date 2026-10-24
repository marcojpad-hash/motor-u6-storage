#!/usr/bin/env python3
"""Evaluación de calibración probabilística sobre predicciones selladas y resultados observados.

No convierte porcentaje de relleno ni rank_fusion en probabilidad. Requiere pares
(probabilidad predicha, desenlace observado) del mismo objetivo y horizonte temporal.
"""
from __future__ import annotations
import math
from typing import Iterable, Mapping, Any

VERSION = "1.0"
MIN_ROWS_FOR_REPORT = 20


def evaluate_binary_predictions(rows: Iterable[Mapping[str, Any]], bins: int = 10) -> dict[str, Any]:
    clean=[]
    for i,row in enumerate(rows):
        p=row.get("probability", row.get("probabilidad"))
        y=row.get("outcome", row.get("desenlace"))
        if not isinstance(p,(int,float)) or not math.isfinite(float(p)) or not 0 <= float(p) <= 1:
            raise ValueError(f"probabilidad_invalida_fila_{i}")
        if y not in (0,1,False,True):
            raise ValueError(f"desenlace_binario_invalido_fila_{i}")
        clean.append((float(p),int(y)))
    n=len(clean)
    if not n:
        return {"status":"NOT_CALIBRATED_NO_DATA","n":0,"brier_score":None,"log_loss":None,"ece":None,"accuracy_at_0_5":None,"reliability_bins":[]}
    eps=1e-15
    brier=sum((p-y)**2 for p,y in clean)/n
    logloss=-sum(y*math.log(max(eps,min(1-eps,p)))+(1-y)*math.log(max(eps,min(1-eps,1-p))) for p,y in clean)/n
    bins=max(2,int(bins)); groups=[[] for _ in range(bins)]
    for p,y in clean: groups[min(bins-1,int(p*bins))].append((p,y))
    table=[]; ece=0.0
    for j,g in enumerate(groups):
        if not g: continue
        mp=sum(p for p,_ in g)/len(g); rate=sum(y for _,y in g)/len(g)
        ece += len(g)/n*abs(mp-rate)
        table.append({"bin_lower":j/bins,"bin_upper":(j+1)/bins,"n":len(g),"mean_predicted":round(mp,6),"observed_rate":round(rate,6),"absolute_gap":round(abs(mp-rate),6)})
    return {"status":"EVALUATED" if n>=MIN_ROWS_FOR_REPORT else "PRELIMINARY_SMALL_SAMPLE","n":n,"brier_score":round(brier,8),"log_loss":round(logloss,8),"ece":round(ece,8),"accuracy_at_0_5":round(sum((p>=0.5)==bool(y) for p,y in clean)/n,8),"base_rate":round(sum(y for _,y in clean)/n,8),"reliability_bins":table,"minimum_n_for_report":MIN_ROWS_FOR_REPORT,"probability_target_must_match_outcome_horizon":True}


def fit_platt_scaling(rows: Iterable[Mapping[str, Any]], max_iter: int = 100) -> dict[str, Any]:
    """Fit logistic calibration on a scalar score with explicit labels; needs both classes and >=20 rows."""
    data=[]
    for i,row in enumerate(rows):
        x=row.get("score")
        y=row.get("outcome",row.get("desenlace"))
        if not isinstance(x,(int,float)) or not math.isfinite(float(x)):
            raise ValueError(f"score_invalido_fila_{i}")
        if y not in (0,1,False,True): raise ValueError(f"desenlace_binario_invalido_fila_{i}")
        data.append((float(x),int(y)))
    if len(data)<MIN_ROWS_FOR_REPORT or len({y for _,y in data})<2:
        return {"status":"NOT_FIT_INSUFFICIENT_LABELLED_DATA","n":len(data),"minimum_n":MIN_ROWS_FOR_REPORT,"needs_both_classes":True,"a":None,"b":None}
    a=0.0; b=0.0
    for _ in range(max_iter):
        g0=g1=h00=h01=h11=0.0
        for x,y in data:
            z=max(-35.0,min(35.0,a+b*x)); p=1/(1+math.exp(-z)); w=max(1e-9,p*(1-p))
            g0 += y-p; g1 += (y-p)*x; h00 += w; h01 += w*x; h11 += w*x*x
        det=h00*h11-h01*h01
        if abs(det)<1e-12: break
        da=(g0*h11-g1*h01)/det; db=(g1*h00-g0*h01)/det
        a+=da; b+=db
        if abs(da)+abs(db)<1e-8: break
    return {"status":"FIT","n":len(data),"a":round(a,10),"b":round(b,10),"transform":"sigmoid(a + b*score)","training_rows":len(data),"target":"same binary outcome and time horizon as labels"}


def apply_platt(score: float, calibration: Mapping[str, Any]) -> float:
    if calibration.get("status")!="FIT": raise ValueError("calibrador_no_ajustado")
    a=float(calibration["a"]); b=float(calibration["b"])
    z=max(-35.0,min(35.0,a+b*float(score)))
    return 1/(1+math.exp(-z))
