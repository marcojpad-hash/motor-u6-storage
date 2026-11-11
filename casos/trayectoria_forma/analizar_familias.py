#!/usr/bin/env python3
"""Hipótesis descriptiva de Mj, sin nuevos pesos ni decisiones del motor."""
import sys
sys.dont_write_bytecode = True
import json,gzip,hashlib
from pathlib import Path
import numpy as np
from proyeccion_tusi_modelo_externo import project_crudo

ROOT=Path(__file__).resolve().parent
BASE=ROOT/"tusi_pc12_v1"

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix==".gz" else p.read_bytes())
def stats(raw,ids,jump):
    q=project_crudo(raw);f=q["familias"];X=np.array([raw[k] for k in f],float).T;V=np.array(q["loadings_PC1_PC2"])
    def top(v):
        order=sorted(range(len(f)),key=lambda k:(-abs(v[k]),f[k]))[:3]
        return [{"familia":f[k],"loading":float(v[k]),"abs_loading":float(abs(v[k]))} for k in order]
    pcs={"PC1":top(V[0]),"PC2":top(V[1])}
    means=X.mean(axis=0);mx=float(means.max());global_d=[f[k] for k in range(len(f)) if abs(means[k]-mx)<=1e-12]
    counts={};per=[]
    for i in range(len(ids)):
        m=float(X[i].max());fam=[f[k] for k in range(len(f)) if abs(X[i,k]-m)<=1e-12]
        if len(fam)==1:counts[fam[0]]=counts.get(fam[0],0)+1
        per.append({"corte":ids[i],"max_crudo_P":m,"familias_dominantes_empatadas":fam,"maximo_unico":len(fam)==1})
    majority=sorted(counts,key=lambda a:(-counts[a],a))
    inc=[]
    if jump is not None:
        delta=X[jump+1]-X[jump]
        inc=[{"familia":f[k],"delta_crudo_P":float(delta[k]),"antes":float(X[jump,k]),"despues":float(X[jump+1,k])} for k in sorted(range(len(f)),key=lambda a:(-delta[a],f[a])) if delta[k]>1e-9]
    return {"estado":"CRUDO_DISPONIBLE","PC_loadings_top3_abs":pcs,"PCA_varianza_2":q["PCA_varianza_2"],"dominantes_por_corte":per,"familias_dominantes_por_media":global_d,"media_max":mx,"conteo_maximos_unicos":counts,"dominante_por_frecuencia_maximos_unicos":None if not majority else majority[0],"salto":None if jump is None else {"desde":ids[jump],"hasta":ids[jump+1],"familias_que_suben":inc,"nota":"Variación en familia, no nuevo peso. Solo aumentos positivos, sin atribuir causa."},"ambicion_o_rivalidad_en_dominantes_media":any("ambic" in fam.lower() or "rival" in fam.lower() for fam in global_d)}

def main():
    result=read(BASE/"RESULTADOS.json");gate=read(BASE/"gate_mozart/COMPARACION_CSV.json");rows=[]
    for case in result["casos"]:
        name=case["caso"]
        if name=="NAPOLEON_EXTERNO":
            st={"estado":"NO_DISPONIBLE_CSV_SIN_RESULT_NI_CRUDO_P","PC_loadings_top3_abs":None,"dominantes_por_corte":None,"familias_dominantes_por_media":None,"salto":None,"ambicion_o_rivalidad_en_dominantes_media":None}
        else:
            if name=="MOZART_EXTERNO":
                if not gate["passed"]:raise ValueError("No se vincula Mozart externo a crudo sin gate aprobado")
                p=BASE/"gate_mozart/result.json.gz";d=read(p);raw=d["motor"]["annex"]["traza_P"]["crudo_P"]
            else:
                p=BASE/"entradas"/(name+".json");d=read(p);raw=d["crudo_P"]
            st=stats(raw,case["cortes"],case["forma"]["salto_inicio"]);st["source"]=str(p);st["source_sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
            if name=="MOZART_EXTERNO":st["nota"]="Vínculo al rerun por gate de coordenadas al redondeo; corrida estándar INCOMPLETE_OUTPUT_DATA por previo_error, no calibración predictiva aprobada."
        rows.append({"caso":name,"forma_completa":case["forma"]["coincide"],**st})
    evaluable=[c for c in rows if c["ambicion_o_rivalidad_en_dominantes_media"] is not None]
    groups={str(form):[{"caso":c["caso"],"dominantes_media":c["familias_dominantes_por_media"],"ambicion_rivalidad":c["ambicion_o_rivalidad_en_dominantes_media"]} for c in evaluable if c["forma_completa"]==form] for form in (True,False)}
    out={"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"hipotesis_Mj":"La forma ~2/3 vuelta y cresta→valle→salto podría depender del rubro/familia dominante de P, p.ej. ambición/rivalidad.","criterio_dominancia":"Máximo de crudo_P por corte (todos los empates); global máximo de la media temporal crudo_P. Loadings por magnitud absoluta, con signo.","casos":rows,"comparacion_descriptiva":groups,"advertencia":"Napoleón no tiene crudo, muestra pequeña, PCA y alineación por caso pueden inducir semejanzas. Asociación no prueba causalidad ni patrón predictivo; no pesos nuevos."}
    (BASE/"FAMILIAS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    for c in rows:print(c["caso"],"forma",c["forma_completa"],"dominantes",c["familias_dominantes_por_media"],"PC1",c["PC_loadings_top3_abs"])

if __name__=="__main__":main()
