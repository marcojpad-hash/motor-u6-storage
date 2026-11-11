#!/usr/bin/env python3
"""Mediciones retrospectivas agnósticas; entrada P_FULL_244 o coordenadas externas.
No escribe ni ejecuta el Engine. No decide H, ranking ni apuesta.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from auditar_reproduccion import frame
from proyeccion_tusi_modelo_externo import project_crudo, year_decimal

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT = HERE / "geometria_existente_v1/MANIFIESTO.json"
EPS = 1e-12

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def ols(t,y):
    t,y = np.asarray(t,float),np.asarray(y,float)
    if len(t)<2 or np.ptp(t)<=EPS: return None
    a = np.column_stack([np.ones(len(t)),t])
    beta = np.linalg.lstsq(a,y,rcond=None)[0]
    fitted = a@beta
    return beta, fitted, r_squared(y,fitted)

def r_squared(y,pred):
    ss = float(np.sum((np.asarray(y)-np.mean(y))**2))
    return None if ss<=EPS else float(1-np.sum((y-pred)**2)/ss)

def fit_radius(t,r,rule="max_to_min"):
    # Regla explícita por manifiesto: máximo→mínimo o prefijo inicial no creciente.
    t,r = np.asarray(t,float),np.asarray(r,float)
    if rule=="initial_nonincreasing_prefix":
        s,e=0,0
        for k in range(1,len(r)):
            if r[k]>r[k-1]+EPS:break
            e=k
    elif rule=="max_to_min":
        s = int(np.argmax(r))
        if s>=len(r)-1: return {"estado":"SIN_CORTES_POSTERIORES_AL_MAXIMO","start":s,"end":None}
        e = s+1+int(np.argmin(r[s+1:]))
    else:raise ValueError("Regla radio desconocida: "+rule)
    base = {"start":s,"end":e,"n_fit":e-s+1,"R0":None,"b":None,"R2":None,"R2_log":None,"pred":None,"residual":None,"regime":None}
    if e-s+1<3 or np.any(r[s:e+1]<=EPS) or np.ptp(t[s:e+1])<=EPS:
        return dict(base,estado="TRAMO_INSUFICIENTE_MINIMO_3_CORTES_RADIO_POSITIVO")
    q = ols(t[s:e+1]-t[s],np.log(r[s:e+1]))
    beta,yp,r2log = q
    R0,b = float(np.exp(beta[0])),float(-beta[1])
    pred = R0*np.exp(np.clip(-b*(t-t[s]),-700,700))
    resid = r-pred
    threshold = max(2*float(np.median(np.abs(resid[s:e+1]))),1e-6*float(np.max(r)))
    flags = [int(k) for k in range(e+1,len(r)) if abs(resid[k])>threshold]
    return dict(base,estado="AJUSTADO_CONTRACCION" if b>0 else "AJUSTADO_NO_CONTRACCION",R0=R0,b=b,R2=r_squared(r[s:e+1],pred[s:e+1]),R2_log=r2log,pred=pred,residual=resid,threshold=threshold,regime=flags[0] if flags else None,regime_flags=flags,regime_status="BANDERA_DESCRIPTIVA" if flags else ("SIN_BANDERA" if e+1<len(r) else "NO_EVALUABLE_SIN_POSTRAMO"))

def fit_phase(t,phase):
    q = ols(t-t[0],phase)
    if q is None: return {"estado":"TIEMPO_NO_IDENTIFICABLE"}
    beta,pred,r2 = q
    duration = np.diff(t)
    innovation = np.diff(phase)-beta[1]*duration
    valid = duration>EPS
    threshold = max(2*float(np.median(np.abs(innovation[valid]))) if np.any(valid) else 0,np.deg2rad(5))
    flags = [int(k+1) for k in range(len(duration)) if valid[k] and abs(innovation[k])>threshold]
    duplicates = [int(k+1) for k in range(len(duration)) if not valid[k]]
    return {"estado":"AJUSTADO","phi0":float(beta[0]),"omega":float(np.rad2deg(beta[1])),"R2":r2,"pred":pred,"residual":phase-pred,"innovation":innovation,"threshold_grados":float(np.rad2deg(threshold)),"rupture":flags[0] if flags else None,"rupture_flags":flags,"saltos_sin_duracion":duplicates}

def fit_sine(t,y):
    t,y = np.asarray(t,float),np.asarray(y,float)
    duration = float(np.ptp(t)); dif=np.diff(t); positive=dif[dif>EPS]
    if len(y)<6 or duration<=EPS or not len(positive):return {"estado":"MUESTRA_INSUFICIENTE"}
    fmin,fmax = 1/(2*duration),1/(2*float(np.median(positive)))
    if fmax<fmin: return {"estado":"RANGO_FRECUENCIA_NO_IDENTIFICABLE"}
    best = None
    for frequency in np.linspace(fmin,fmax,2048):
        D=np.column_stack([np.ones(len(t)),np.sin(2*np.pi*frequency*(t-t[0])),np.cos(2*np.pi*frequency*(t-t[0]))])
        beta,_,rank,_=np.linalg.lstsq(D,y,rcond=None)
        if rank<3:continue
        pred=D@beta;rss=float(np.sum((y-pred)**2))
        if best is None or rss<best[0]: best=(rss,frequency,beta,pred)
    if best is None:return {"estado":"AJUSTE_NO_IDENTIFICABLE"}
    rss,f,beta,pred=best; r2=r_squared(y,pred)
    return {"estado":"AJUSTADO_EN_MUESTRA","pct":None if r2 is None else 100*r2,"frequency_por_anio":float(f),"periodo_anios":float(1/f),"offset":float(beta[0]),"A_sin":float(beta[1]),"B_cos":float(beta[2]),"amplitud":float(np.hypot(beta[1],beta[2])),"pred":pred,"residual":y-pred,"n":len(t),"grados_libertad_nominales":len(t)-4,"grid_n":2048,"f_min":fmin,"f_max":fmax}

def shape(x,y):
    x,y=np.asarray(x,float),np.asarray(y,float);n=len(y)
    steps=np.hypot(np.diff(x),np.diff(y));j=int(np.argmax(steps));positive=steps[steps>EPS]
    threshold=1.5*float(np.median(positive)) if len(positive) else float("inf")
    peaks=[k for k in range(n-1) if (k==0 or y[k]>y[k-1]+EPS) and y[k]>y[k+1]+EPS]
    troughs=[k for k in range(1,n-1) if y[k]<y[k-1]-EPS and y[k]<y[k+1]-EPS]
    pairs=[(a,b) for a in peaks for b in troughs if a<b<=j]
    crest,trough=pairs[0] if pairs else (peaks[0] if peaks else None,None)
    crossing=bool(abs(y[j])>EPS and abs(y[j+1])>EPS and y[j]*y[j+1]<0)
    jump=bool(steps[j]>=threshold and crossing and len(positive))
    suffix=np.arange(j+1,n)
    rise_fit=ols(suffix,y[j+1:])
    rise=bool(len(suffix)>=2 and y[-1]>y[j+1]+EPS and rise_fit and rise_fit[0][1]>0)
    return {"coincide":bool(pairs and jump and rise),"cresta":crest,"valle":trough,"salto_inicio":j,"salto_fin":j+1,"salto_largo":bool(steps[j]>=threshold),"salto_cruza_eje":crossing,"subida":rise,"salto_umbral":None if not np.isfinite(threshold) else threshold,"pasos":steps,"advertencia":"Criterio operacional dependiente del marco; no invariante a rotación/reflexión PCA."}

def shape_ordered(x,y):
    x,y=np.asarray(x,float),np.asarray(y,float);n=len(y)
    steps=np.hypot(np.diff(x),np.diff(y));positive=steps[steps>EPS]
    threshold=1.5*float(np.median(positive)) if len(positive) else float("inf")
    valley=int(np.argmin(y));crest=int(np.argmax(y[:valley])) if valley>0 else None
    crest_ok=bool(crest is not None and y[crest]>y[valley]+EPS)
    candidates=[]
    for k in range(valley,n-1):
        cross_x=abs(x[k])>EPS and abs(x[k+1])>EPS and x[k]*x[k+1]<0
        cross_y=abs(y[k])>EPS and abs(y[k+1])>EPS and y[k]*y[k+1]<0
        if steps[k]>=threshold and (cross_x or cross_y):candidates.append((k,bool(cross_x),bool(cross_y)))
    if candidates:
        j,cx,cy=candidates[0];suffix=np.arange(j+1,n);rise_fit=ols(suffix,y[j+1:]);rise=bool(len(suffix)>=2 and y[-1]>y[j+1]+EPS and rise_fit and rise_fit[0][1]>0)
    else:j,cx,cy,rise=None,False,False,False
    return {"coincide":bool(crest_ok and candidates and rise),"cresta":crest,"valle":valley,"salto_inicio":j,"salto_fin":None if j is None else j+1,"salto_largo":bool(candidates),"salto_cruza_eje":bool(cx or cy),"cruza_x_0":cx,"cruza_y_0":cy,"subida":rise,"salto_umbral":None if not np.isfinite(threshold) else threshold,"pasos":steps,"todos_saltos_candidatos":[k for k,a,b in candidates],"advertencia":"Criterio exploratorio PC12 dependiente del marco, no validación independiente."}

def decimal_year(date):
    d=dt.date.fromisoformat(date);start=dt.date(d.year,1,1)
    return d.year+(d-start).days/((dt.date(d.year+1,1,1)-start).days)

def event(k,ids,years,z90):
    if k is None:return None
    close=years[k]
    return {"corte":ids[k],"year_aproximado":float(close),"frente_z90":"EN_Z90" if abs(close-z90)<1e-8 else ("ANTES_Z90" if close<z90 else "DESPUES_Z90")}

def load_case(spec,parent):
    p=(parent/spec["file"]).resolve()
    if p.suffix.lower()==".csv":
        # Para futuras coordenadas externas: los encabezados tienen contrato explícito.
        with p.open(newline="",encoding="utf-8-sig") as handle:
            rows=list(csv.DictReader(handle))
        year_key="ano" if rows and "ano" in rows[0] else "año"
        required={"corte",year_key,"x_tusi","y_transversal","radio","fase_grados"}
        if not rows or not required<=rows[0].keys():raise ValueError("CSV requiere columnas: "+",".join(sorted(required)))
        d={"case_id":spec["case_id"],"geometry":"COORDENADAS_EXTERNAS_PC12_RESULT_FUENTE_NO_DISPONIBLE","points":rows,"z90":spec["z90"],"source":str(p),"source_sha256":sha(p),"date_warnings":[],"notes":["No se infiere transformación desde CSV sin pares de trazas verificables."]}
        ids=[q["corte"] for q in rows];years=np.array([float(q[year_key]) for q in rows]);t=years-years[0]
        x=np.array([float(q["x_tusi"]) for q in rows]);y=np.array([float(q["y_transversal"]) for q in rows]);r=np.array([float(q["radio"]) for q in rows]);phi=np.deg2rad([float(q["fase_grados"]) for q in rows]);pca=None;h=None
        d["consistencia_radio_max_error"]=float(np.max(np.abs(r-np.hypot(x,y))))
        angular_error=np.angle(np.exp(1j*(phi-np.arctan2(y,x))))
        d["consistencia_fase_modulo_360_max_error_grados"]=float(np.max(np.abs(np.rad2deg(angular_error))))
    else:
        d=json.loads(p.read_text());rows=d["points"];ids=[q["corte"] for q in rows]
        dates=[dt.date.fromisoformat(q["date"]) for q in rows];t=np.array([(q-dates[0]).days/365.2425 for q in dates]);years=np.array([decimal_year(q["date"]) for q in rows])
        if np.any(np.diff(t)<-EPS):raise ValueError("No se reordenan silenciosamente cortes con tiempo decreciente")
        if d["geometry"]=="TUSI_PC12_ROTADO_CRUDO_P":
            q=project_crudo(d["crudo_P"])
            if len(q["radio"])!=len(ids):raise ValueError("crudo_P y controles no sincronizados")
            x,y,r,phi=[np.array(q[k]) for k in ("x_tusi","y_transversal","radio","fase_grados")]
            phi=np.deg2rad(phi);years=np.array([year_decimal(row["date"]) for row in rows]);t=years-years[0]
            pca=q["PCA_varianza_2"];h={"transformacion":q["estado"],"rotation_radians":q["rotation_radians"]}
        else:
            fams=sorted(rows[0]["P_FULL_244"])
            if len(fams)!=244 or any(sorted(q["P_FULL_244"])!=fams for q in rows):raise ValueError("P_FULL_244 incompatible")
            P=np.array([[float(q["P_FULL_244"][f]) for f in fams] for q in rows]);x,y,r,phi,pca,h=frame(P)
    z=(year_decimal(d["z90"]) if d["geometry"]=="TUSI_PC12_ROTADO_CRUDO_P" else decimal_year(d["z90"])) if isinstance(d["z90"],str) else float(d["z90"])
    return d,ids,t,years,x,y,r,phi,pca,h,z,p

def clean(x):
    if isinstance(x,np.ndarray):return [clean(q) for q in x.tolist()]
    if isinstance(x,(np.integer,)):return int(x)
    if isinstance(x,(np.floating,float)):return float(x) if math.isfinite(float(x)) else None
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    return x

def plot_case(outdir,label,ids,years,x,y,r,phi,rad,pha,sine,z,geometry):
    external=geometry.startswith("COORDENADAS_EXTERNAS")
    tag="CSV externo: PC1/PC2 rotadas; RESULT fuente ausente" if external else ("crudo_P → PCA PC1/PC2 + rotación C1→Cn horizontal" if geometry=="TUSI_PC12_ROTADO_CRUDO_P" else "PCA3(P) + helix_diagnostics, eje PCA (NO Tusi externo)")
    fig=plt.figure(figsize=(15,12),layout="constrained")
    ax=fig.add_subplot(221,projection="3d");ax.plot(x,y,years,"o-")
    for a,b,c,lab in zip(x,y,years,ids):ax.text(a,b,c,lab,fontsize=7)
    ax.set(xlabel="x eje PC12 rotado" if geometry=="TUSI_PC12_ROTADO_CRUDO_P" else ("x_tusi externo" if external else "x radial"),ylabel="y transversal",zlabel="año de cierre (control)",title="Trayectoria observada")
    ax=fig.add_subplot(222);ax.plot(years,r,"o-",label="radio")
    if rad.get("pred") is not None:
        ax.plot(years,rad["pred"],"--",label="exponencial, parámetros propios")
        ax.axvspan(years[rad["start"]],years[rad["end"]],alpha=.12,color="orange",label="tramo fijado por regla")
    else:ax.text(.03,.97,"R0/b: N/D, tramo insuficiente",transform=ax.transAxes,va="top")
    ax.plot(years,y,"s-",alpha=.65,label="transversal")
    if sine.get("pred") is not None:ax.plot(years,sine["pred"],":",label="seno ajustado en muestra")
    ax.axvline(z,color="black",ls=":",label="Z90 de control");ax.set(xlabel="año aproximado",ylabel="radio / transversal (mismo marco)",title="Perfil — no probabilidad");ax.legend(fontsize=7);ax.grid(alpha=.25)
    ax=fig.add_subplot(223,projection="polar");ax.plot(phi,r,"o-")
    for a,b,lab in zip(phi,r,ids):ax.annotate(lab,(a,b),fontsize=7)
    ax.set_title("Polar — fase desenrollada, orientación propia")
    ax=fig.add_subplot(224);ax2=ax.twinx()
    if rad.get("residual") is not None:
        ax.plot(years,rad["residual"],"o-",label="residual radio")
        ax.axhline(rad["threshold"],color="C0",ls=":",alpha=.6);ax.axhline(-rad["threshold"],color="C0",ls=":",alpha=.6)
    if sine.get("residual") is not None:ax.plot(years,sine["residual"],"s-",alpha=.65,label="residual seno")
    if pha.get("residual") is not None:ax2.plot(years,np.rad2deg(pha["residual"]),"D--",color="C3",label="residual fase (°)")
    for key,color,text in [(rad.get("regime"),"C0","régimen"),(pha.get("rupture"),"C3","fase")]:
        if key is not None:ax.axvline(years[key],color=color,alpha=.6,label=text+" "+ids[key])
    ax.axhline(0,color="grey",lw=.7);ax.set(xlabel="año aproximado",ylabel="residual radio / y",title="Residuales descriptivos (sin inferencia predictiva)");ax2.set_ylabel("residual fase (°)")
    h,l=ax.get_legend_handles_labels();h2,l2=ax2.get_legend_handles_labels();ax.legend(h+h2,l+l2,fontsize=7);ax.grid(alpha=.25)
    fig.suptitle(label+" | TRAYECTORIA DESCRIPTIVA\n"+tag,fontsize=15)
    target=outdir/(label+"_TRAYECTORIA.png");fig.savefig(target,dpi=150);plt.close(fig);return target.name

def execute(manifest_path,outdir):
    manifest=json.loads(manifest_path.read_text());outdir.mkdir(parents=True,exist_ok=True)
    results=[]
    for spec in manifest["cases"]:
        d,ids,t,years,x,y,r,phi,pca,h,z,p=load_case(spec,manifest_path.parent)
        rad,pha,sine=fit_radius(t,r,manifest.get("radio_rule","max_to_min")),fit_phase(t,phi),fit_sine(t,y)
        sh=shape_ordered(x,y) if manifest.get("shape_rule")=="ordered_post_valley_axis_crossing_v2" else shape(x,y)
        obs={"caso":d["case_id"],"geometria":d["geometry"],"source":d["source"],"source_sha256":d["source_sha256"],"fixture_sha256":sha(p),"cortes":ids,"n":len(ids),"z90":d["z90"],"date_warnings":d.get("date_warnings",[]),"notes":d.get("notes",[]),"controles_coordenadas_externas":{k:v for k,v in d.items() if k.startswith("consistencia_")},"PCA_varianza":pca,"diagnostico_existente":h,
             "giro_neto_grados":float(np.rad2deg(phi[-1]-phi[0])),"giro_neto_absoluto_grados":float(abs(np.rad2deg(phi[-1]-phi[0]))),"recorrido_angular_absoluto_grados":float(np.rad2deg(np.sum(np.abs(np.diff(phi))))),
             "radio":rad,"fase":pha,"seno_transversal":sine,"forma":sh,
             "cambio_regimen":event(rad.get("regime"),ids,years,z),"ruptura_fase":event(pha.get("rupture"),ids,years,z),
             "eventos_radio":[event(k,ids,years,z) for k in rad.get("regime_flags",[])],"eventos_fase":[event(k,ids,years,z) for k in pha.get("rupture_flags",[])],
             "tabla_por_corte":[{"corte":ids[k],"year":years[k],"t_years":t[k],"x":x[k],"y":y[k],"r":r[k],"fase_grados":float(np.rad2deg(phi[k])),"frente_z90":event(k,ids,years,z)["frente_z90"]} for k in range(len(ids))]}
        obs["png"]=plot_case(outdir,d["case_id"],ids,years,x,y,r,phi,rad,pha,sine,z,d["geometry"])
        results.append(clean(obs))
    return {"modo":"TRAYECTORIA_DESCRIPTIVA_NO_PREDICTIVA","estado":"EJECUTADO_CON_LIMITES","can_decide_H":False,"alimenta_motor":False,"alimenta_ranking":False,"alimenta_apuesta":False,"metodo_sha256":sha(manifest_path.parent/"METODO_PREDECLARADO.md"),"script_sha256":sha(Path(__file__)),"shape_rule":manifest.get("shape_rule","original_radial_v1"),"radio_rule":manifest.get("radio_rule","max_to_min"),"proyeccion_pc12_sha256":sha(HERE/"proyeccion_tusi_modelo_externo.py"),"numpy":np.__version__,"matplotlib":matplotlib.__version__,"coordenadas_externas":manifest.get("coordenadas_externas"),"casos":results}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--manifest",type=Path,default=DEFAULT);ap.add_argument("--outdir",type=Path);args=ap.parse_args()
    outdir=args.outdir or args.manifest.parent
    protected=list((REPO/"motor/motor").rglob("*.py"))+list(REPO.rglob("Engine_V5_CANONICO_SOLO.py"))+list(REPO.rglob("patterns_final_v14.json"))
    before={str(p.relative_to(REPO)):sha(p) for p in protected}
    output=execute(args.manifest,outdir)
    after={str(p.relative_to(REPO)):sha(p) for p in protected}
    assert before==after
    output["integridad"]={"archivos_protegidos":len(before),"intactos":True}
    (outdir/"RESULTADOS.json").write_text(json.dumps(output,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    for c in output["casos"]:
        print(c["caso"],"giro",round(c["giro_neto_absoluto_grados"],3),"R0",c["radio"].get("R0"),"b",c["radio"].get("b"),"R2",c["radio"].get("R2"),"omega",c["fase"].get("omega"),"seno%",c["seno_transversal"].get("pct"),"forma",c["forma"]["coincide"],"regime",c["cambio_regimen"],"phase",c["ruptura_fase"])
    print("integridad",output["integridad"])

if __name__=="__main__":main()
