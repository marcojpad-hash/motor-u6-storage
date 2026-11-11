#!/usr/bin/env python3
"""Candidatos locales retrospectivos y null condicionado a linealidad; solo sidecar."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import csv,json,hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from control_nulo import BASE,ROOT,REPO,SEED,TYPES,load_cases,generate,matrix_projection,summary,clean,sha
from proyeccion_tusi_modelo_externo import year_decimal
METRICS=("arco_residual_abs","distancia_euclidea","arco_bruto")

def local_metrics(coords,t):
    x,y,r,deg=[np.asarray(a,float) for a in coords];t=np.asarray(t,float);phase=np.deg2rad(deg)
    D=np.column_stack([np.ones(len(t)),t-t[0]]);beta=np.linalg.lstsq(D,phase,rcond=None)[0]
    predicted=D@beta;ss=np.sum((phase-phase.mean())**2)
    R2=1-np.sum((phase-predicted)**2)/ss if ss>1e-12 else np.nan
    delta=np.diff(phase);expected=beta[1]*np.diff(t);epsilon=delta-expected;rb=(r[1:]+r[:-1])/2
    signed=rb*epsilon
    return {"omega_grados":float(np.rad2deg(beta[1])),"fase_R2":R2,"delta_fase_grados":np.rad2deg(delta),"esperado_grados":np.rad2deg(expected),"residual_grados":np.rad2deg(epsilon),"radio_medio":rb,"arco_residual_firmado":signed,"arco_residual_abs":abs(signed),"distancia_euclidea":np.hypot(np.diff(x),np.diff(y)),"arco_bruto":rb*abs(delta),"min_y":float(y.min()),"profundidad_valle":float(-y.min()),"profundidad_reflejada":float(y.max()),"extremo_abs_y":float(max(abs(y))),"valle_index":int(y.argmin())}

def adjust_holm(metrics):
    items=sorted((m["p_superior"],i,m) for i,m in enumerate(metrics) if m.get("p_superior") is not None);acc=0
    for rank,(p,_,m) in enumerate(items):
        acc=max(acc,min(1,(len(items)-rank)*p));m["p_holm"]=acc;m["holm_m"]=len(items)

def summarize(real,arrays,ids,t,mask=None,geometry=False):
    n=len(arrays["fase_R2"]);mask=np.ones(n,bool) if mask is None else mask
    count=int(mask.sum());steps=[]
    for i in range(len(ids)-1):
        row={"paso":ids[i]+"→"+ids[i+1],"i":i,"delta_t":float(t[i+1]-t[i]),"delta_t_cero":bool(t[i+1]==t[i]),"metricas":{}}
        for key in METRICS:
            q=summary(real[key][i],arrays[key][mask,i]);q["p_vs_max_pasos_nulo"]=summary(real[key][i],arrays[key][mask].max(axis=1))["p_superior"] if count else None
            row["metricas"][key]=q
        steps.append(row)
    scalar={k:summary(real[k],arrays[k][mask]) for k in ("profundidad_valle","extremo_abs_y")}
    scalar["min_y"]=summary(real["min_y"],-arrays["profundidad_valle"][mask])
    if geometry:
        lo=np.minimum(arrays["profundidad_valle"][mask],arrays["profundidad_reflejada"][mask]);hi=np.maximum(arrays["profundidad_valle"][mask],arrays["profundidad_reflejada"][mask])
        a=summary(real["profundidad_valle"],hi);b=summary(real["profundidad_valle"],lo)
        scalar["min_y"]={"real":real["min_y"],"n_validos":count,"percentil_cota_inferior":None if b["percentil"] is None else 100-b["percentil"],"percentil_cota_superior":None if a["percentil"] is None else 100-a["percentil"],"nota":"Cotas por orientacion desconocida"}
        scalar["profundidad_valle"]={"real":real["profundidad_valle"],"n_validos":count,"percentil_cota_inferior":a["percentil"],"percentil_cota_superior":b["percentil"],"p_superior_cota_inferior":b["p_superior"],"p_superior_cota_superior":a["p_superior"],"nota":"Orientacion SVD de crudo_P desconocida; no dar punto preciso de min_y."}
    maxima={k:summary(float(max(real[k])),arrays[k][mask].max(axis=1)) for k in METRICS}
    return {"n_pool":n,"n_aceptados":count,"estado":"BAJA_MUESTRA" if count<30 else "DESCRIPTIVO","pasos":steps,"valle":scalar,"maximos":maxima}

def run_null(real,coords_list,t,ids,seed,store,tag,geometry=False):
    ms=[local_metrics(c,t) for c in coords_list]
    arrays={k:np.array([m[k] for m in ms]) for k in (*METRICS,"fase_R2","profundidad_valle","profundidad_reflejada","extremo_abs_y")}
    keep=arrays["fase_R2"]>=real["fase_R2"]-1e-12
    for k,v in arrays.items():store[tag+"_"+k]=v
    store[tag+"_linealidad_aceptado"]=keep
    out=summarize(real,arrays,ids,t,geometry=geometry);out["seed"]=seed
    out["condicionado_fase_lineal"]=summarize(real,arrays,ids,t,mask=keep,geometry=geometry)
    out["condicionado_fase_lineal"]["criterio_R2_minimo"]=real["fase_R2"]
    return out

def audit_che():
    src=REPO/"casos/originales_z90/inputs/001_Ernesto_Che_Guevara_9f3baec1110e/_cuts_che_run.json";frozen=REPO/"casos/calibracion_z90/CHE/entrada.json";prep=REPO/"casos/calibracion_z90/CHE/PREPARACION_Y_SELLO.json";table=ROOT/"tusi_pc12_v1/tablas_por_corte/CHE.csv"
    original=json.loads(src.read_text());original=original if isinstance(original,list) else original["cuts"];inp=json.loads(frozen.read_text());p=json.loads(prep.read_text())
    by_id={c["id"]:c for c in inp["cuts"]};same=all({k:v for k,v in c.items() if k!="date"}=={k:v for k,v in by_id[c["id"]].items() if k!="date"} for c in original)
    records=[{"id":c["id"],"date_original":c.get("date"),"date_calibrada":by_id[c["id"]]["date"],"year_decimal":year_decimal(by_id[c["id"]]["date"]),"year_redondeado_2dec":f'{year_decimal(by_id[c["id"]]["date"]):.2f}',"hecho_original":c["hecho"]} for c in original]
    out={"estado":"INCONSISTENCIA_DE_IDS_Y_CRITERIO_DE_CIERRE_NO_ERROR_NUEVO_DE_LA_GRAFICA","fuentes":{str(q.relative_to(REPO)):sha(q) for q in (src,frozen,prep,table)},"orden_original":[c["id"] for c in original],"orden_ejecucion":[c["id"] for c in inp["cuts"]],"datos":records,"hechos_tokens_pesos_intactos":same,"fechas_reconstruidas":p["fechas_reconstruidas"],"conclusion":"El original ya trae C2 (estudios c1948-1953) antes de C3 (viaje1951-1952), sin date. La calibracion reconstruyo fechas de CIERRE de intervalos: C3=1952-12-31 antes de C2=1953-12-31, orden explicitamente documentado. Son periodos solapados; no hay prueba de fecha historica exacta ni errata. Las etiquetas 1953.00/1954.00 son redondeo del ano decimal, no fechas civiles1953/1954. No corregir automaticamente IDs, fechas ni tokens.","modificaciones_fuentes":False}
    assert same
    return out

def read_external(name,path):
    with path.open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
    coords=tuple(np.array([float(r[k]) for r in rows]) for k in ("x_tusi","y_transversal","radio","fase_grados"))
    t=np.array([float(r["ano"]) for r in rows]) if "ano" in rows[0] else np.arange(len(rows),dtype=float)
    t=t-t[0]
    return {"caso":name,"source":str(path),"source_sha256":sha(path),"ids":[r["corte"] for r in rows],"t":t,"coords":coords,"real":local_metrics(coords,t)}

def main():
    n=1000;cases=load_cases();draws={};rows=[]
    protected=list((REPO/"motor/motor").rglob("*.py"))+list(REPO.rglob("Engine_V5_CANONICO_SOLO.py"))+list(REPO.rglob("patterns_final_v14.json"));before={str(p):sha(p) for p in protected}
    for i,c in enumerate(cases):
        coords=matrix_projection(c["X"],c["fams"]);real=local_metrics(coords,c["t"])
        row={"caso":c["name"],"source":c["source"],"source_sha256":c["source_sha256"],"ids":c["ids"],"t":c["t"],"real":real,"nulos":{}}
        for j,kind in enumerate(TYPES):
            seed=SEED+i*100+j;data,_=generate(kind,c["X"],np.random.default_rng(seed),n)
            row["nulos"][kind]=run_null(real,(matrix_projection(sample,c["fams"]) for sample in data),c["t"],c["ids"],seed,draws,c["name"]+"_"+kind)
        rows.append(row);print(c["name"],"faseR2",real["fase_R2"],"aceptados",{k:v["condicionado_fase_lineal"]["n_aceptados"] for k,v in row["nulos"].items()},flush=True)
    for key in METRICS:
        adjust_holm([s["metricas"][key] for c in rows for null in c["nulos"].values() for s in null["pasos"]])
        adjust_holm([null["maximos"][key] for c in rows for null in c["nulos"].values()])
        adjust_holm([s["metricas"][key] for c in rows for null in c["nulos"].values() for s in null["condicionado_fase_lineal"]["pasos"]])
        adjust_holm([null["condicionado_fase_lineal"]["maximos"][key] for c in rows for null in c["nulos"].values()])
    for key in ("profundidad_valle","extremo_abs_y"):adjust_holm([null["valle"][key] for c in rows for null in c["nulos"].values()])
    external=[]
    for name,file,seed in [("NAPOLEON_CSV","tabla_coordenadas_napoleon.csv",SEED+950),("HAWKING7_CSV","tabla_coordenadas_hawking_7cortes.csv",SEED+902)]:
        c=read_external(name,ROOT/"coordenadas_modelo_externo"/file);XY=np.column_stack(c["coords"][:2])
        # H7 same sequence as original geometry control, Nap seed single stream.
        rng=np.random.default_rng(seed);orders=np.array([rng.permutation(len(XY)) for _ in range(n)])
        c["nulos"]={"permutacion_geometria2D":run_null(c["real"],(matrix_projection(XY[order],["x","y"]) for order in orders),c["t"],c["ids"],seed,draws,name+"_permutacion_geometria2D",geometry=True)}
        if name=="HAWKING7_CSV":
            h6=cases[2];N=7;z=np.arange(N,dtype=float);z=(z-z.mean())/z.std(ddof=1);proxy=h6["X"].mean(0)+z[:,None]*h6["X"].std(0,ddof=1)[None,:]
            for j,kind in enumerate(TYPES[1:]):
                seed_proxy=SEED+900+j;data,_=generate(kind,proxy,np.random.default_rng(seed_proxy),n)
                c["nulos"][kind+"_PROXY_H6"]=run_null(c["real"],(matrix_projection(sample,h6["fams"]) for sample in data),c["t"],c["ids"],seed_proxy,draws,name+"_"+kind)
        c.pop("coords");external.append(c);print(name,"faseR2",c["real"]["fase_R2"],"aceptados",{k:v["condicionado_fase_lineal"]["n_aceptados"] for k,v in c["nulos"].items()},flush=True)
    after={str(p):sha(p) for p in protected};assert before==after
    out={"estado":"EJECUTADO_DESCRIPTIVO_CANDIDATOS_POST_HOC","no_senales":["giro_total","y_inicio_igual_y_fin","radio_en_U"],"casos":rows,"externos":external,"integridad":{"archivos_protegidos":len(before),"intactos":True},"script_sha256":sha(Path(__file__)),"metodo_sha256":sha(BASE/"METODO_SENALES_POR_PASO.md"),"n_pool_por_celda":n,"numpy":np.__version__,"condicional":"R2_fase_nulo>=R2_real; subconjunto del pool fijo1000, muestra aceptada explicita. No empareja omega. No validacion confirmatoria."}
    (BASE/"SENALES_POR_PASO.json").write_text(json.dumps(clean(out),ensure_ascii=False,indent=2,allow_nan=False)+"\n");np.savez_compressed(BASE/"SENALES_DISTRIBUCIONES.npz",**draws)
    (BASE/"AUDITORIA_FECHAS_CHE.json").write_text(json.dumps(clean(audit_che()),ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    plot(rows,external)

def plot(rows,external):
    show=rows+[external[0]];fig,axes=plt.subplots(3,2,figsize=(16,12),layout="constrained")
    for ax,c in zip(axes.flat,show):
        for key,null in c["nulos"].items():
            values=[r["metricas"]["arco_residual_abs"]["percentil"] for r in null["pasos"]];ax.plot(np.arange(len(values)),values,"o-",label=key)
            cond=null["condicionado_fase_lineal"]
            if key in ("caminata_gaussiana","permutacion_geometria2D"):
                ax.plot(np.arange(len(values)),[s["metricas"]["arco_residual_abs"]["percentil"] for s in cond["pasos"]],"s--",label="mismo nulo R²fase≥real n="+str(cond["n_aceptados"]))
        ax.set_xticks(np.arange(len(c["ids"])-1),[c["ids"][i]+"→"+c["ids"][i+1] for i in range(len(c["ids"])-1)],rotation=45,ha="right",fontsize=8)
        ax.axhline(95,color="gray",ls=":");ax.set(ylim=(-1,101),ylabel="Percentil |r_medio·residual fase|",title=c["caso"]);ax.grid(alpha=.2);ax.legend(fontsize=7)
    fig.suptitle("Candidatos locales frente a nulos: arco residual, NO giro global ni radio en U\nPercentiles descriptivos por slot; 95 NO es umbral corregido. Napoleón: solo geometría2D, sin raw.",fontsize=13)
    fig.savefig(BASE/"SENALES_POR_PASO.png",dpi=140);plt.close(fig)

if __name__=="__main__":main()
