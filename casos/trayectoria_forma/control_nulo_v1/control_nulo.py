#!/usr/bin/env python3
"""Nulos reproducibles, 1000 por caso/tipo. Solo sidecar; no Engine/H/ranking/apuesta."""
import sys
sys.dont_write_bytecode=True
import argparse,csv,datetime,gzip,hashlib,json,math,time
from pathlib import Path
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from proyeccion_tusi_modelo_externo import project_crudo,year_decimal
from medir_trayectorias import fit_radius,fit_sine,shape_ordered
BASE=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
SEED=202611110503
TYPES=("permutacion","caminata_gaussiana","iid_gaussiano")
EPS=1e-12

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix==".gz" else p.read_bytes())
def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(np.integer,)):return int(x)
    if isinstance(x,(np.floating,float)):return float(x) if math.isfinite(float(x)) else None
    if isinstance(x,(np.bool_,)):return bool(x)
    return x

class SineCache:
    def __init__(self,t):
        t=np.asarray(t,float);diff=np.diff(t);positive=diff[diff>EPS];T=np.ptp(t)
        self.t=t
        self.frequencies=np.linspace(1/(2*T),1/(2*np.median(positive)),2048)
        a=2*np.pi*self.frequencies[:,None]*(t-t[0])[None,:]
        D=np.stack([np.ones_like(a),np.sin(a),np.cos(a)],axis=-1)
        U,s,V=np.linalg.svd(D,full_matrices=False)
        good=(s>np.finfo(float).eps*max(len(t),3)*s[:,0,None]).sum(axis=1)==3
        self.U=U[good]
    def percent(self,Y):
        Y=np.atleast_2d(Y);norm=(Y*Y).sum(axis=1)
        ss=((Y-Y.mean(axis=1,keepdims=True))**2).sum(axis=1)
        result=[]
        for start in range(0,len(Y),64):
            y=Y[start:start+64]
            dots=np.einsum("bn,knp->bkp",y,self.U,optimize=True)
            best=(dots*dots).sum(axis=2).max(axis=1)
            rss=np.maximum(0,norm[start:start+len(y)]-best)
            valid=ss[start:start+len(y)]>EPS
            vals=100*(1-rss/np.maximum(ss[start:start+len(y)],EPS));vals[~valid]=np.nan
            result.extend(vals)
        return np.array(result)

def matrix_projection(X,fams):
    q=project_crudo({f:X[:,k] for k,f in enumerate(fams)})
    return tuple(np.array(q[k]) for k in ("x_tusi","y_transversal","radio","fase_grados"))

def info(X,sigma,sh,x,y,fams):
    j=sh["salto_inicio"]
    if j is None:return {"jump_pos":-1,"jump_ratio":np.nan,"rise_zmax":np.nan,"winner_ids":[],"winner_families":[],"winner_delta":None}
    steps=np.hypot(np.diff(x),np.diff(y));positive=steps[steps>EPS]
    ratio=steps[j]/np.median(positive)
    if X is None:return {"jump_pos":j,"jump_ratio":ratio,"rise_zmax":np.nan,"winner_ids":[],"winner_families":[],"winner_delta":None}
    delta=X[j+1]-X[j];mx=delta.max();w=np.flatnonzero((np.abs(delta-mx)<=1e-10)&(delta>1e-9))
    active=sigma>EPS;z=float(max(0,np.max(delta[active]/sigma[active]))) if np.any(active) else np.nan
    return {"jump_pos":j,"jump_ratio":ratio,"rise_zmax":z,"winner_ids":w.tolist(),"winner_families":[fams[k] for k in w],"winner_delta":float(mx) if len(w) else None}

def measure(X,fams,t,sigma,coords=None):
    x,y,r,phase=matrix_projection(X,fams) if coords is None else coords
    rad=fit_radius(t,r,"initial_nonincreasing_prefix");sh=shape_ordered(x,y)
    out={"giro_abs":float(abs(phase[-1]-phase[0])),"giro_signed":float(phase[-1]-phase[0]),"forma":bool(sh["coincide"]),"b":rad.get("b",np.nan),"r2_radio":rad.get("R2",np.nan),"fit_radio":rad["estado"],"radio_n_fit":rad.get("n_fit",0),"shape":sh}
    out.update(info(X,sigma,sh,x,y,fams));out["b"]=np.nan if out["b"] is None else out["b"];out["r2_radio"]=np.nan if out["r2_radio"] is None else out["r2_radio"]
    return out,y

def generate(kind,X,rng,n):
    N,F=X.shape;mu=X.mean(axis=0);sigma=X.std(axis=0,ddof=1);sigma[sigma<=EPS]=0
    orders=None
    if kind=="permutacion":
        orders=np.array([rng.permutation(N) for _ in range(n)]);data=X[orders]
    elif kind=="caminata_gaussiana":
        data=np.cumsum(rng.normal(size=(n,N,F)),axis=1)*(sigma/np.sqrt((N+1)/6))[None,None,:]+mu[None,None,:]
    elif kind=="iid_gaussiano":data=rng.normal(size=(n,N,F))*sigma[None,None,:]+mu[None,None,:]
    else:raise ValueError(kind)
    return data,orders

def summary(real,values):
    v=np.array(values,float);v=v[np.isfinite(v)]
    if real is None or not np.isfinite(real) or len(v)==0:return {"real":clean(real),"n_validos":len(v),"percentil":None,"p_superior":None}
    equal=np.isclose(v,real,rtol=1e-10,atol=1e-10)
    lower=(v<real)&(~equal)
    return {"real":real,"n_validos":len(v),"percentil":100*(lower.sum()+.5*equal.sum())/len(v),"p_superior":(1+np.count_nonzero(v>=real-1e-10))/(len(v)+1),"mediana_nulo":float(np.median(v)),"q025":float(np.quantile(v,.025)),"q975":float(np.quantile(v,.975))}

def simulate(case,kind,n,seed,cache,draw_store,tag):
    X,fams,t,real=case["X"],case["fams"],case["t"],case["real"]
    sigma=X.std(axis=0,ddof=1);sigma[sigma<=EPS]=0
    data,orders=generate(kind,X,np.random.default_rng(seed),n)
    arrays={k:np.full(n,np.nan) for k in ("giro_abs","giro_signed","b","r2_radio","sine_pct","jump_ratio","rise_zmax")};forms=np.zeros(n,bool);positions=np.full(n,-1,int);family_hit=np.zeros(n,bool);winner_counts=Counter();Ys=[];realw=set(real["winner_ids"])
    # Extra H7 proxy uses var/mean from H6 but N=7, handled by X proxy matrix below.
    for k,sample in enumerate(data):
        m,y=measure(sample,fams,t,sigma);Ys.append(y)
        for key in arrays:
            if key!="sine_pct":arrays[key][k]=m[key]
        forms[k]=m["forma"];positions[k]=m["jump_pos"]
        family_hit[k]=bool(realw.intersection(m["winner_ids"]))
        winner_counts.update(m["winner_families"])
    arrays["sine_pct"]=cache.percent(np.array(Ys))
    has=positions>=0
    metrics={key:summary(real.get(key),v) for key,v in arrays.items() if key!="giro_signed"}
    active=sigma>EPS
    ratios=np.var(data[:,:,active],axis=1,ddof=1)/(sigma[active]**2)[None,:]
    out={"n":n,"seed":seed,"n_cortes":len(t),"n_familias":len(fams),"forma_pct":100*forms.mean(),"giro_ge_180_pct":100*np.mean(arrays["giro_abs"]>=180),"ajuste_radio_valido_pct":100*np.mean(np.isfinite(arrays["b"])),"salto_pct":100*has.mean(),"metricas":metrics,"varianza_muestral_ratio_media":float(ratios.mean()),"ordenes_unicos":None if orders is None else len(set(map(tuple,orders))),"frecuencia_familias_ganadoras":dict(winner_counts)}
    if real["jump_pos"]>=0:
        same=(positions==real["jump_pos"])
        out.update({"mismo_slot_pct_total":100*same.mean(),"mismo_slot_pct_cond_salto":100*same.sum()/has.sum() if has.sum() else None,"misma_familia_pct_total":100*family_hit.mean() if realw else None,"misma_familia_pct_cond_salto":100*family_hit.sum()/has.sum() if realw and has.sum() else None})
    for key,v in arrays.items():draw_store[tag+"_"+key]=v
    draw_store[tag+"_forma"]=forms;draw_store[tag+"_jump_pos"]=positions;draw_store[tag+"_same_family"]=family_hit
    print(case["name"],kind,"giro percentil",metrics["giro_abs"]["percentil"],"forma%",out["forma_pct"],flush=True)
    return out

def h7_permutation_geometry(coords,t,n,seed,cache,draw_store,real):
    # Permuting full rows leaves the family covariance and top-2 PCA subspace
    # unchanged. The known 2-D scores suffice for invariant radius/|turn|/sine
    # metrics, but the unknown full-SVD handedness prevents an exact shape rate.
    X=np.column_stack(coords[:2]);fams=["coordenada_x_NO_FAMILIA","coordenada_y_NO_FAMILIA"]
    rng=np.random.default_rng(seed);orders=np.array([rng.permutation(len(X)) for _ in range(n)])
    sigma=X.std(axis=0,ddof=1);arrays={key:np.full(n,np.nan) for key in ("giro_abs","giro_signed","b","r2_radio","sine_pct")};a=[];b=[];ys=[]
    for k,order in enumerate(orders):
        q=matrix_projection(X[order],fams);m,y=measure(X[order],fams,t,sigma,coords=q)
        for key in arrays:
            if key!="sine_pct":arrays[key][k]=m[key]
        a.append(shape_ordered(q[0],q[1])["coincide"]);b.append(shape_ordered(q[0],-q[1])["coincide"]);ys.append(y)
    arrays["sine_pct"]=cache.percent(np.array(ys));a=np.array(a);b=np.array(b)
    for key,v in arrays.items():draw_store["HAWKING7_EXTERNO_PROXY_permutacion_geometria2D_"+key]=v
    draw_store["HAWKING7_GEOMETRIA2D_forma_ambas"]=a&b;draw_store["HAWKING7_GEOMETRIA2D_forma_alguna"]=a|b
    result={"n":n,"seed":seed,"n_cortes":len(X),"n_familias":None,"n_coordenadas_observadas":2,"forma_pct_orientacion_2D":float(100*a.mean()),"forma_pct_limite_inferior":float(100*np.mean(a&b)),"forma_pct_limite_superior":float(100*np.mean(a|b)),"metricas":{key:summary(real.get(key),v) for key,v in arrays.items() if key!="giro_signed"},"ordenes_unicos":len(set(map(tuple,orders))),"nota":"Permutación de geometría 2-D conocida, no reconstrucción de crudo_P. La covarianza familiar no cambia al permutar filas: bajo el supuesto PC2/PC3 no degeneradas se identifica el mismo subespacio PC12 hasta orientación; la brecha no se puede verificar sin crudo_P H7. Radios, giro absoluto y R²/seno son invariantes a reflexión; forma depende de handedness desconocida del SVD completo, por eso solo se dan límites. No hay familia del salto identificable."}
    print("HAWKING7 permutacion_geometria2D",result["metricas"]["giro_abs"]["percentil"],"forma bounds",result["forma_pct_limite_inferior"],result["forma_pct_limite_superior"],flush=True)
    return result

def load_cases():
    cases=[]
    base=ROOT/"tusi_pc12_v1"
    for name,folder in [("MOZART10",None),("GALILEO","GALILEO"),("HAWKING6","HAWKING"),("CHE","CHE"),("MLK","MLK")]:
        if folder is None:
            rp=base/"gate_mozart/result.json.gz";ip=base/"gate_mozart/entrada.json";d=read(rp);inp=read(ip);raw=d["motor"]["annex"]["traza_P"]["crudo_P"];ids=[c["id"] for c in inp["cuts"]];dates=[c["date"] for c in inp["cuts"]]
        else:
            rp=base/"entradas"/(folder+".json");d=read(rp);raw=d["crudo_P"];ids=[c["corte"] for c in d["points"]];dates=[c["date"] for c in d["points"]]
        fams=sorted(raw);X=np.array([raw[f] for f in fams]).T;years=np.array([year_decimal(c) for c in dates]);t=years-years[0];sigma=X.std(axis=0,ddof=1);sigma[sigma<=EPS]=0
        real,y=measure(X,fams,t,sigma);cache=SineCache(t);pct=float(cache.percent(y)[0]);reference=fit_sine(t,y)["pct"]
        assert abs(pct-reference)<1e-7,(pct,reference)
        real["sine_pct"]=pct
        # Validate cached sine against exact reference also on independent synthetic outputs.
        test_rng=np.random.default_rng(7123+len(cases))
        for _ in range(3):
            v=test_rng.normal(size=len(t));a=cache.percent(v)[0];b=fit_sine(t,v)["pct"];assert abs(a-b)<1e-7
        cases.append({"name":name,"X":X,"fams":fams,"t":t,"ids":ids,"source":str(rp),"source_sha256":sha(rp),"real":real,"cache":cache,"sine_cache_reference_abs_error":abs(pct-reference)})
    return cases

def holm(rows,key):
    targets=[]
    for c in rows:
        for kind,n in c["nulos"].items():
            p=n["metricas"][key]["p_superior"]
            if p is not None:targets.append((p,c["caso"],kind,n["metricas"][key]))
    targets.sort(key=lambda a:a[:3]);m=len(targets);acc=0
    for rank,(p,_,__,metric) in enumerate(targets):
        acc=max(acc,min(1,(m-rank)*p));metric["p_superior_holm"]=acc;metric["n_comparaciones_holm"]=m

def plot_hist(rows,draw_store):
    fig,axes=plt.subplots(3,2,figsize=(15,13),layout="constrained");colors=["C0","C1","C2"]
    for ax,c in zip(axes.flat,rows):
        vals=[draw_store[c["caso"]+"_"+kind+"_giro_abs"] for kind in c["nulos"]]
        hi=max(max(v) for v in vals);bins=np.linspace(0,hi+5,42)
        for (kind,n),v in zip(c["nulos"].items(),vals):
            label=kind+(" forma∈["+str(round(n["forma_pct_limite_inferior"],1))+","+str(round(n["forma_pct_limite_superior"],1))+"]%" if "forma_pct_limite_inferior" in n else " forma="+str(round(n["forma_pct"],1))+"%")
            ax.hist(v,bins=bins,density=True,histtype="step",lw=1.3,label=label,color={"permutacion":"C0","permutacion_geometria2D":"C0","caminata_gaussiana":"C1","iid_gaussiano":"C2"}[kind])
        ax.axvline(c["real"]["giro_abs"],color="black",lw=2,label="real "+str(round(c["real"]["giro_abs"],1))+"°")
        ax.set(title=c["caso"]+(" — PROXY varianzas H6" if c.get("proxy") else ""),xlabel="|giro neto| grados",ylabel="densidad");ax.legend(fontsize=7);ax.grid(alpha=.2)
    fig.suptitle("PC1/PC2 rotadas — 1000 muestras por nulo/caso; no predicción\nHawking7: permutación geométrica 2D (forma acotada) + RW/iid proxy H6; sin crudo_P",fontsize=14)
    p=BASE/"GIRO_REAL_VS_NULOS.png";fig.savefig(p,dpi=140);plt.close(fig)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--n",type=int,default=1000);args=ap.parse_args()
    n=args.n;start=time.time();protected=list((REPO/"motor/motor").rglob("*.py"))+list(REPO.rglob("Engine_V5_CANONICO_SOLO.py"))+list(REPO.rglob("patterns_final_v14.json"));before={str(p):sha(p) for p in protected}
    cases=load_cases();draws={};rows=[]
    for index,case in enumerate(cases):
        row={"caso":case["name"],"n_cortes":len(case["t"]),"n_familias":len(case["fams"]),"source":case["source"],"source_sha256":case["source_sha256"],"real":clean(case["real"]),"ids":case["ids"],"nulos":{},"sine_cache_reference_abs_error":case["sine_cache_reference_abs_error"]}
        for j,kind in enumerate(TYPES):row["nulos"][kind]=simulate(case,kind,n,SEED+index*100+j,case["cache"],draws,case["name"]+"_"+kind)
        rows.append(row)
    for key in ("jump_ratio","rise_zmax"):holm(rows,key)
    observed_count=sum(c["real"]["forma"] for c in rows)
    joint={}
    for kind in TYPES:
        count=np.sum([draws[c["caso"]+"_"+kind+"_forma"] for c in rows],axis=0)
        joint[kind]={"formas_reales":observed_count,"distribucion_cuenta_0_a_5":{str(k):int(np.sum(count==k)) for k in range(6)},"p_superior_MC_exploratorio":float((1+np.sum(count>=observed_count))/(n+1)),"advertencia":"Nulos independientes entre casos; casos/criterio elegidos tras observación, no prueba confirmatoria ni independencia demostrada de biografías."}
    # H7 additional proxy, not a fabricated 7x244 historical observation.
    source=ROOT/"coordenadas_modelo_externo/tabla_coordenadas_hawking_7cortes.csv"
    with source.open(newline="",encoding="utf-8") as handle:ext=list(csv.DictReader(handle))
    coords=tuple(np.array([float(q[k]) for q in ext]) for k in ("x_tusi","y_transversal","radio","fase_grados"));h6=cases[2];N=7;t=np.arange(N,dtype=float)
    # Construct deterministic reference matrix of N points with H6 mean/variance,
    # used ONLY to parameterize the generators. It is NOT a reconstructed crudo_P.
    z=np.arange(N,dtype=float);z=(z-z.mean())/z.std(ddof=1);mu=h6["X"].mean(0);sigma=h6["X"].std(0,ddof=1);Xproxy=mu+z[:,None]*sigma[None,:]
    real,y=measure(None,h6["fams"],t,sigma,coords);cache=SineCache(t);real["sine_pct"]=float(cache.percent(y)[0]);assert abs(real["sine_pct"]-fit_sine(t,y)["pct"])<1e-7
    case={"name":"HAWKING7_EXTERNO_PROXY","X":Xproxy,"fams":h6["fams"],"t":t,"real":real}
    proxy={"caso":case["name"],"proxy":True,"n_cortes":7,"n_familias_nulo":len(h6["fams"]),"source":str(source),"source_sha256":sha(source),"real":clean(real),"nulos":{},"permutacion_crudo_P":"NO_EVALUABLE_SIN_CRUDO_P_7_CORTES; ver permutacion_geometria2D para control de subespacio conocido","familias_salto":"NO_EVALUABLE_SIN_CRUDO_P","tiempo":"índice de corte, no año","variance_proxy_source":h6["source"],"nota":"RW/iid N=7 usan sigma/medias de H6. No son nulos emparejados del H7 real; no se usan para concluir significancia de H7."}
    for j,kind in enumerate(TYPES[1:]):proxy["nulos"][kind]=simulate(case,kind,n,SEED+900+j,cache,draws,case["name"]+"_"+kind)
    proxy["nulos"]["permutacion_geometria2D"]=h7_permutation_geometry(coords,t,n,SEED+902,cache,draws,real)
    after={str(p):sha(p) for p in protected};assert before==after
    out={"estado":"EJECUTADO_NULOS_CINCO_CASOS_Y_PROXY_H7","seed":SEED,"n_por_celda":n,"n_simulaciones_principales":5*3*n,"n_simulaciones_proxy":2*n,"n_permutaciones_geometria_h7":n,"modo":"GEOMETRICO_DESCRIPTIVO_NO_PREDICTIVO","casos":rows,"cuenta_formas_conjunta_exploratoria":joint,"hawking7_proxy":proxy,"integridad":{"archivos_protegidos":len(before),"intactos":True},"script_sha256":sha(Path(__file__)),"metodo_sha256":sha(BASE/"METODO.md"),"proyeccion_sha256":sha(ROOT/"proyeccion_tusi_modelo_externo.py"),"metricas_sha256":sha(ROOT/"medir_trayectorias.py"),"numpy":np.__version__,"duracion_segundos":time.time()-start}
    (BASE/"RESULTADOS.json").write_text(json.dumps(clean(out),ensure_ascii=False,indent=2,allow_nan=False)+"\n");np.savez_compressed(BASE/"DISTRIBUCIONES.npz",**draws);plot_hist(rows+[proxy],draws)
    print("FIN",out["duracion_segundos"],"segundos",flush=True)

if __name__=="__main__":main()
