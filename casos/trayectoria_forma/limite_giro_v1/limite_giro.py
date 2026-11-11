#!/usr/bin/env python3
"""Cotas/limites de giro neto PC12. Matemática lateral, no Engine ni predicción."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,math,time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
BASE=Path(__file__).resolve().parent;ROOT=BASE.parent;REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"control_nulo_v1"))
from proyeccion_tusi_modelo_externo import project_crudo
from control_nulo import clean,sha,load_cases,summary
from senales_por_paso import read_external
SEED=202611110537;MODELS=("iid","RW","RW_suavizada","LF1","LF2");F=244;REPS=500

def center(X):return X-X.mean(axis=0)
def polar(Q):
    r=np.hypot(Q[:,0],Q[:,1]);phase=np.unwrap(np.arctan2(Q[:,1],Q[:,0]));g=float(phase[-1]-phase[0])
    return g,r,phase

def project(X):
    C=center(np.asarray(X,float));n,f=C.shape
    if f<n:
        ev,V=np.linalg.eigh(C.T@C);ev=ev[::-1];P=C@V[:,::-1][:,:2]
    else:
        ev,U=np.linalg.eigh(C@C.T);ev=ev[::-1];P=U[:,::-1][:,:2]*np.sqrt(np.maximum(0,ev[:2]))
    chord=P[-1]-P[0]
    if np.linalg.norm(chord)<1e-12:raise ValueError("cuerda nula")
    a=np.arctan2(chord[1],chord[0]);c,s=np.cos(a),np.sin(a);Q=P@np.array([[c,-s],[s,c]])
    g,r,phase=polar(Q)
    if min(r)<=1e-12*max(r):raise ValueError("fase no definida: vertice en origen")
    return {"Q":Q,"giro":abs(np.degrees(g)),"signed":np.degrees(g),"rho":float(ev[1]/ev[0]),"min_radius_ratio":float(min(r)/max(r))}

def smoothing(n):
    t=(np.arange(n)+.5)/n;D=t[:,None]-t[None,:];S=np.exp(-.5*(D/.08)**2);return S/S.sum(axis=1,keepdims=True)

def draw(model,n,f,rng):
    if model=="iid":return rng.normal(size=(n,f))
    if model in ("RW","RW_suavizada"):
        X=np.cumsum(rng.normal(size=(n,f)),axis=0)/np.sqrt(n)
        return X if model=="RW" else smoothing(n)@X
    power=1 if model=="LF1" else 2;k=np.arange(1,min(4,n-1)+1);t=(np.arange(n)+.5)/n
    return (np.cos(np.pi*t[:,None]*k[None,:])/k[None,:]**power)@rng.normal(size=(len(k),f))

def dist(v):
    v=np.asarray(v,float);return {"n":len(v),"mean":float(v.mean()),"median":float(np.median(v)),"q025":float(np.quantile(v,.025)),"q975":float(np.quantile(v,.975)),"min":float(v.min()),"max":float(v.max()),"ge180_pct":float(100*np.mean(v>=180))}

def cos_formula(n,rho):return float(180+2*np.degrees(np.arctan(np.sqrt(rho)*np.cos(np.pi/n)/np.cos(np.pi/(2*n)))))
def parabola_formula(n,eta):return float(180+2*np.degrees(np.arctan(np.sqrt((5/3)*(n-2)/(n+2)*eta))))
def rw_population_formula(n):return float(180+2*np.degrees(np.arctan(1-1/(2*np.cos(np.pi/(2*n))**2))))

def verify():
    rows=[];oracle=[];rng=np.random.default_rng(SEED+99)
    for n in (3,4,6,10,20,30):
        for model in MODELS:
            X=draw(model,n,244,rng);p=project(X);q=project_crudo({f"f{k:03}":X[:,k] for k in range(X.shape[1])})
            e=abs(p["giro"]-q["giro_neto_absoluto_grados"]);rho=q["PCA_varianza_2"][1]/q["PCA_varianza_2"][0];er=abs(p["rho"]-rho)
            assert e<1e-7 and er<1e-7,(n,model,e,er);oracle.append({"n":n,"model":model,"error_giro":e,"error_rho":er})
    for n in range(3,31):
        eps=.001;i=np.arange(n);a=np.array([(-1)**k*math.comb(n-1,k) for k in range(n)],float);X=np.column_stack([a,-eps*i*a]);p=project(X);expected=np.degrees((n-1)*np.pi-np.arctan((n-1)*eps));err=abs(p["giro"]-expected)
        assert err<1e-3,(n,err);assert p["giro"]<180*(n-1)+1e-7
        rows.append({"tipo":"supremo_binomial","n":n,"giro":p["giro"],"esperado":expected,"error":err})
        for ratio in (.04,.16,.49):
            t=(np.arange(n)+.5)/n;X=np.column_stack([np.cos(np.pi*t),np.sqrt(ratio)*np.cos(2*np.pi*t)]);p=project(X);error=abs(p["giro"]-cos_formula(n,ratio));assert error<1e-7
            z=np.linspace(-1,1,n);a=.5*np.sqrt(15*ratio*(n-1)**2/(n*n-4));X=np.column_stack([z,a*(z*z-np.mean(z*z))]);q=project(X);errp=abs(q["giro"]-parabola_formula(n,ratio));assert errp<1e-7
            rows.append({"tipo":"formulas_cos_parabola","n":n,"rho":ratio,"error_cos":error,"error_parabola":errp})
    for eps in (.1,.01,.001,.0001):
        X=np.array([[2,0],[0,eps],[-3,-3*eps],[1,2*eps]],float);p=project(X);expected=np.degrees(np.arctan(2*eps));assert abs(p["giro"]-expected)<1e-7
        rows.append({"tipo":"contraejemplo_inferior_n4","eps":eps,"giro":p["giro"]})
    for n in range(5,31):
        X=np.zeros((n,2));X[0]=[1,0];X[-1]=[2,0];X[1:-1,0]=-3/(n-2);X[1:-1,1]=.3;X[2,1]=-(n-3)*.3;p=project(X);assert p["giro"]<1e-7
        rows.append({"tipo":"giro_cero_n_ge_5","n":n,"giro":p["giro"]})
    same=[]
    for k in (1,2):
        t=np.arange(31)/31;X=np.column_stack([np.cos(2*np.pi*k*t),.5*np.sin(2*np.pi*k*t)]);q=project(X);same.append({"frecuencia":k,"n":31,"rho":q["rho"],"giro":q["giro"]})
    assert abs(same[0]["rho"]-same[1]["rho"])<1e-10 and abs(same[1]["giro"]-same[0]["giro"])>300
    # Smooth nonzero parabolic arc: winding integral and curvature identity.
    t=np.linspace(-1,1,100001);a=.35;x=t;y=a*(t*t-1/3);dx=np.ones(len(t));dy=2*a*t
    phi=np.unwrap(np.arctan2(y,x));psi=np.unwrap(np.arctan2(dy,dx));alpha=np.unwrap(psi-phi)
    integrand=(x*dy-y*dx)/(x*x+y*y);integral=np.trapezoid(integrand,t);closed=np.pi+2*np.arctan(2*a/3)
    identity=2*np.arctan(2*a)-(alpha[-1]-alpha[0]);assert abs(integral-closed)<1e-7 and abs(identity-closed)<1e-7
    return {"svd_fiel":oracle,"ejemplos":rows,"mismo_rho_curvas_suaves_distinto_giro":same,"integral":{"parabola_a":a,"integral_grados":np.degrees(integral),"formula_grados":np.degrees(closed),"identidad_curvatura_grados":np.degrees(identity)}}

def population(n,model):
    t=(np.arange(n)+.5)/n
    if model in ("RW","RW_suavizada"):
        K=np.minimum(np.arange(n)[:,None],np.arange(n)[None,:])/n
        if model=="RW_suavizada":S=smoothing(n);K=S@K@S.T
    else:
        power=1 if model=="LF1" else 2;k=np.arange(1,min(4,n-1)+1);B=np.cos(np.pi*t[:,None]*k)/k**power;K=B@B.T
    K=K-K.mean(0)[None,:]-K.mean(1)[:,None]+K.mean();ev,U=np.linalg.eigh(K);P=U[:,-2:][:,::-1]*np.sqrt(ev[-2:][::-1]);g,_,_=polar(P)
    return {"model":model,"n":n,"giro":abs(np.degrees(g)),"rho":float(ev[-2]/ev[-1]),"rw_formula":rw_population_formula(n) if model=="RW" else None}

def get_reals():
    real=[]
    for c in load_cases():
        p=project(c["X"]);C=center(c["X"]);e=np.linalg.eigvalsh(C@C.T);parts=(e[-2:][::-1]/np.trace(C@C.T)).tolist()
        real.append({"caso":c["name"],"n":len(c["X"]),"Q":p["Q"],"giro":p["giro"],"rho":p["rho"],"signed":p["signed"],"source":c["source"],"source_sha256":c["source_sha256"],"varianza_explicada_full_PC1_PC2":parts,"tipo":"crudo_P","familias_variables":int(np.sum(np.var(C,axis=0)>1e-12)),"F_efectivo_varianzas":float(np.sum(np.var(C,axis=0))**2/np.sum(np.var(C,axis=0)**2))})
    for name,file in [("NAPOLEON_CSV","tabla_coordenadas_napoleon.csv"),("HAWKING7_CSV","tabla_coordenadas_hawking_7cortes.csv")]:
        c=read_external(name,ROOT/"coordenadas_modelo_externo"/file);Q=np.column_stack(c["coords"][:2]);ev=np.linalg.eigvalsh(np.cov(Q,rowvar=False));real.append({"caso":name,"n":len(Q),"Q":Q,"giro":abs(c["coords"][3][-1]-c["coords"][3][0]),"signed":c["coords"][3][-1]-c["coords"][3][0],"rho":float(ev[0]/ev[1]),"source":c["source"],"source_sha256":c["source_sha256"],"varianza_explicada_full_PC1_PC2":None,"tipo":"CSV_sin_crudo"})
    for c in real:
        Q=c["Q"];V=np.cov(Q,rowvar=False);ev,U=np.linalg.eigh(V);PC=center(Q)@U[:,::-1];t=(np.arange(c["n"])+.5)/c["n"];corr=[float(abs(np.corrcoef(PC[:,k],np.cos((k+1)*np.pi*t))[0,1])) for k in (0,1)]
        _,_,phases=polar(Q);phase_extrema_endpoints=bool({int(np.argmin(phases)),int(np.argmax(phases))}=={0,len(Q)-1})
        factors=np.abs((PC[[0,-1],1]/np.sqrt(ev[0]))/(PC[[0,-1],0]/np.sqrt(ev[1])))
        same_sign=bool(PC[0,0]*PC[-1,0]<0 and PC[0,1]*PC[-1,1]>0)
        exact_rho=180+sum(np.degrees(np.arctan(np.sqrt(c["rho"])*factors))) if same_sign else None
        c.update({"fase_extremos_son_min_max":phase_extrema_endpoints,"factores_de_forma_extremos_PC":factors,"formula_rho_mas_forma_extremos":exact_rho,"condicion_signos_PC_para_formula":same_sign})
        eta=V[1,1]/V[0,0];h=(Q[0,1]+Q[-1,1])/2;x0,xn=Q[0,0],Q[-1,0]
        endpoint=180+np.degrees(np.arctan(abs(h)/abs(x0))+np.arctan(abs(h)/abs(xn))) if x0<0<xn else None
        wrapped=np.angle(np.exp(1j*(np.arctan2(Q[-1,1],Q[-1,0])-np.arctan2(Q[0,1],Q[0,0]))));wind=round((np.deg2rad(c["signed"])-wrapped)/(2*np.pi))
        c.update({"eta_transversal_sobre_cuerda":eta,"cos_modes_correlacion_abs_PC1_PC2":corr,"formula_cos_n":cos_formula(c["n"],c["rho"]),"formula_cos_infty":180+2*np.degrees(np.arctan(np.sqrt(c["rho"]))),"formula_parabola_n":parabola_formula(c["n"],c["rho"]),"formula_extremos_una_pasada":endpoint,"winding_k":wind,"h_extremos":h,"extremos_x":[x0,xn],"error_extremos_y":abs(Q[-1,1]-Q[0,1])})
    return real

def asymptotics(store):
    iid=[]
    for f,ns,reps in [(2,[30,60,120,240,480,960,1920],1000),(244,[30,60,120,240],120)]:
        for n in ns:
            rng=np.random.default_rng(SEED+900000+1000*f+n);g=np.array([project(rng.normal(size=(n,f)))["giro"] for _ in range(reps)]);sigma=180*np.sqrt((n-1)/3);iid.append({"f":f,"n":n,"giro":dist(g),"abs_giro_sobre_sigma_uniforme":dist(g/sigma)});store[f"asint_iid_{f}_{n}"]=g;print("ASINT IID",f,n,flush=True)
    coupled=[];rng=np.random.default_rng(SEED+901);paths=np.cumsum(rng.normal(size=(100,257,244)),axis=1)/16
    for n in (17,33,65,129,257):
        indices=np.linspace(0,256,n).astype(int);g=np.array([project(X[indices])["giro"] for X in paths]);coupled.append({"n":n,"giro":dist(g)});store[f"rw_acoplado_{n}"]=g
    pop=[population(n,model) for n in (30,64,128,256,512) for model in MODELS[1:]]
    return {"iid_escalamiento":iid,"rw_F244_acopladas":coupled,"poblacion_F_infinito":pop,"limite_RW_Finfinito_ninfinito":180+2*np.degrees(np.arctan(.5)),"limite_LF1_Finfinito_ninfinito":180+2*np.degrees(np.arctan(.5)),"limite_LF2_Finfinito_ninfinito":180+2*np.degrees(np.arctan(.25))}

def main():
    start=time.time();protected=list((REPO/"motor/motor").rglob("*.py"))+list(REPO.rglob("Engine_V5_CANONICO_SOLO.py"))+list(REPO.rglob("patterns_final_v14.json"));before={str(p):sha(p) for p in protected};checks=verify();store={};rows=[]
    for n in range(3,31):
        row={"n":n,"modelos":{}}
        for j,model in enumerate(MODELS):
            seed=SEED+1000*n+j;rng=np.random.default_rng(seed);values=[project(draw(model,n,F,rng)) for _ in range(REPS)];g=np.array([v["giro"] for v in values]);rho=np.array([v["rho"] for v in values]);assert max(g)<=180*(n-1)+1e-7
            if n==3:assert min(g)>180-1e-7
            store[f"{model}_{n}_giro"]=g;store[f"{model}_{n}_rho"]=rho;row["modelos"][model]={"seed":seed,"giro":dist(g),"rho":dist(rho)}
        rows.append(row);print("N",n,"medianas",{m:round(row["modelos"][m]["giro"]["median"],2) for m in MODELS},flush=True)
    real=get_reals();oldp=ROOT/"control_nulo_v1/RESULTADOS.json";old=json.loads(oldp.read_text());oldmap={c["caso"]:c for c in old["casos"]}
    for c in real:
        c["rango_benchmark_isotropico"]={m:summary(c["giro"],store[f"{m}_{c['n']}_giro"]) for m in MODELS}
        c["rho_rango_benchmark"]={m:summary(c["rho"],store[f"{m}_{c['n']}_rho"]) for m in MODELS}
        c["rango_RW_iid_varianzas_emparejadas_previo"]=None if c["caso"] not in oldmap else {m:oldmap[c["caso"]]["nulos"][k]["metricas"]["giro_abs"] for m,k in [("RW","caminata_gaussiana"),("iid","iid_gaussiano")]}
        c["error_formula_cos_n"]=c["formula_cos_n"]-c["giro"]
    G=np.array([c["giro"] for c in real]);rho=np.array([c["rho"] for c in real]);pred=np.array([c["formula_cos_n"] for c in real]);err=pred-G
    analysis={"n_trazas":7,"n_personas":6,"rho_giro_correlacion_Pearson":float(np.corrcoef(rho,G)[0,1]),"formula_cos_n_MAE_grados":float(np.mean(abs(err))),"formula_cos_n_RMSE_grados":float(np.sqrt(np.mean(err*err))),"formula_cos_n_R2_descriptivo":float(1-np.sum(err*err)/np.sum((G-G.mean())**2)),"no_es_ley":"Mismo rho y misma nube pueden producir otro winding; datos seleccionados y dos versiones Hawking no independientes."}
    asym=asymptotics(store);after={str(p):sha(p) for p in protected};assert before==after
    npz=ROOT/"control_nulo_v1/DISTRIBUCIONES.npz";prior=np.load(npz);g=prior["MOZART10_permutacion_giro_abs"]
    out={"cotas":{"inferior_grados":0,"superior_grados":"180*(n-1)","tight_supremo":True,"n3_rank2_sin_origen":"180<G<360","n4":"inf G=0; ejemplo eps→0","n_ge5":"G=0 alcanzable no colineal","condicion_180":"Si extremos son min/max fase y span<360, centrado no colineal exige G>180; no es universal"},"formulas":{"giro":"abs(sum wrap_pi(arg q[i+1]-arg q[i])))","continuo":"abs(integral (x*yprime-y*xprime)/(x*x+y*y) dt)","curvatura":"Delta_phi = integral kappa ds - Delta(psi-phi)","cos_n":"G=pi+2atan(sqrt(rho)*cos(pi/n)/cos(pi/(2n)))","parabola_n":"G=pi+2atan(sqrt((5/3)*(n-2)/(n+2)*eta)), eta=Var(y)/Var(x)","parabola_continua":"G=pi+2atan(kappa_vertice*L/3)=pi+2atan(sqrt(5*rho/3)) si PC1 paralelo cuerda","RW_Finfinito":"rho_n=1/(4*cos(pi/(2n))**2); G_n=pi+2atan(1-2*rho_n)","limite_RW_Finfinito_ninfinito":"pi+2atan(1/2)=233.130102 grados","limite_general":"NO_EXISTE_UNICO; densificar curva no es generar iid nuevos","no_funcion_universal_rho":"Depende tambien de eigenfunciones/extremos y winding; mismo rho permite distinto giro"},"modo":"MATEMATICA_GEOMETRICA_NO_PREDICCION","seed":SEED,"familias_benchmark":F,"replicas_por_celda":REPS,"n_principales":list(range(3,31)),"modelo_semantica":"Benchmarks isotropicos, no nulos familiares emparejados a biografias","modelos":rows,"casos":real,"relacion_rho":analysis,"verificaciones":checks,"asintotico":asym,"mismo_rho_Mozart_permutado":{"rho_fijo":real[0]["rho"],"giro":dist(g),"source":str(npz),"source_sha256":sha(npz)},"integridad":{"archivos_protegidos":len(before),"intactos":True},"script_sha256":sha(Path(__file__)),"metodo_sha256":sha(BASE/"METODO.md"),"proyeccion_fiel_sha256":sha(ROOT/"proyeccion_tusi_modelo_externo.py"),"numpy":np.__version__,"duracion_segundos":time.time()-start}
    (BASE/"RESULTADOS.json").write_text(json.dumps(clean(out),ensure_ascii=False,indent=2,allow_nan=False)+"\n");np.savez_compressed(BASE/"DISTRIBUCIONES.npz",**store);plot(out);print("FIN",analysis,"segundos",time.time()-start,flush=True)

def plot(out):
    fig,axes=plt.subplots(2,2,figsize=(17,12),layout="constrained");colors={"iid":"gray","RW":"C1","RW_suavizada":"C0","LF1":"C2","LF2":"C4"};ns=np.arange(3,31)
    for ax in axes[0]:
        for m in MODELS:
            d=[r["modelos"][m]["giro"] for r in out["modelos"]];ax.plot(ns,[v["median"] for v in d],label=m,color=colors[m]);ax.fill_between(ns,[v["q025"] for v in d],[v["q975"] for v in d],color=colors[m],alpha=.13)
        ax.plot(ns,[rw_population_formula(n) for n in ns],"k--",label="RW F→∞ exacta",lw=1)
        for c in out["casos"]:ax.plot(c["n"],c["giro"],"ko",ms=4)
        ax.set(xlabel="n cortes",ylabel="|giro neto| grados");ax.grid(alpha=.2)
    axes[0,0].set_title("Distribuciones F244: mediana y banda 95%, 500/celda");axes[0,0].legend(fontsize=8)
    ax=axes[0,1];ax.set(ylim=(170,290),title="Zoom: siete trazas reales (seis personas)")
    offsets={"MOZART10":(12,-15),"GALILEO":(18,14),"NAPOLEON_CSV":(18,-2),"HAWKING6":(-30,12),"HAWKING7_CSV":(-15,28),"CHE":(-10,15),"MLK":(-22,-20)}
    for c in out["casos"]:ax.annotate(c["caso"],(c["n"],c["giro"]),xytext=offsets[c["caso"]],textcoords="offset points",fontsize=8,arrowprops={"arrowstyle":"-","lw":.5})
    ax=axes[1,0];rs=np.linspace(.001,.65,250)
    for n in (6,10,100000):ax.plot(rs,[cos_formula(n,r) for r in rs],label="cos1/cos2 n="+("∞" if n>1000 else str(n)),alpha=.7)
    for c in out["casos"]:ax.plot(c["rho"],c["giro"],"ko");ax.annotate(c["caso"],(c["rho"],c["giro"]),xytext=(4,4),textcoords="offset points",fontsize=7)
    ax.set(xlabel="rho=var(PC2)/var(PC1)",ylabel="|giro neto| grados",title="Relación restringida: no función universal de rho");ax.legend(fontsize=8);ax.grid(alpha=.2)
    ax=axes[1,1]
    for f in (2,244):
        q=[v for v in out["asintotico"]["iid_escalamiento"] if v["f"]==f];ax.plot([v["n"] for v in q],[v["abs_giro_sobre_sigma_uniforme"]["median"] for v in q],"o-",label="iid proyectado F="+str(f))
    ax.axhline(.67448975,color="black",ls="--",label="mediana |N(0,1)|, referencia");ax.set(xscale="log",xlabel="n (log)",ylabel="mediana |giro| / [180√((n−1)/3)]",title="iid: crecimiento ~√n; no límite angular constante");ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.suptitle("PC12 centradas + cuerda horizontal + unwrap: cotas, suavidad y límites\nEl giro no se interpreta como señal biográfica. Rotar no modifica el giro absoluto.",fontsize=15)
    fig.savefig(BASE/"GIRO_VS_N.png",dpi=145);plt.close(fig)

if __name__=="__main__":main()
