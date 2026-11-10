#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
RESULTS=BASE/"resultados"
MOTOR=ROOT/"motor"/"motor"
ENTRY=ROOT/"motor"/"correr_estandar.py"
CASE_PATH=BASE/"input_mozart_z90.json"
CAL_PATH=BASE/"caldero_II_input.json"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()
def dump(p,o):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf-8")
def run_cmd(cmd,env):
 t=time.time(); p=subprocess.run(cmd,cwd=str(ROOT),env=env,text=True,capture_output=True)
 return p,round(time.time()-t,3)
def run_variant(label,with_caldero):
 outdir=RESULTS/label; outdir.mkdir(parents=True,exist_ok=True)
 case=json.loads(CASE_PATH.read_text(encoding="utf-8"))
 cal=json.loads(CAL_PATH.read_text(encoding="utf-8"))
 case["case_id"]=case["case_id"]+"_"+label
 case["random_seed"]=20260930
 case["consolidado_off"]=[] if with_caldero else ["caldero_memoria"]
 if with_caldero:
  case["caldero_identity"]={}
  case["caldero_archetype_input"]={"tokens":cal["archetype"]["tokens"],"patterns":[],"families":[]}
  case["caldero_search_sources"]=cal["search_sources"]
  case["caldero_search_fixture"]=cal["search_sources"]
  case["allow_static_search_fixture"]=True
  case["caldero_llm_neighbor_hints"]=[]
  case["caldero_neighbor_store_root"]=str(outdir/"engine_neighbor_store")
  case["stinkbox_root"]=str(outdir/"stinkbox_store")
  generic_out=outdir/"CALDERO_II_RAW.json"
  generic_store=outdir/"caldero_generic_neighbor_store"
  env=os.environ.copy(); env["PYTHONHASHSEED"]="0"
  cmd=[sys.executable,str(MOTOR/"caldero_II_runner_generico.py"),str(CAL_PATH),"--out",str(generic_out),"--store",str(generic_store)]
  cp,dt=run_cmd(cmd,env)
  (outdir/"caldero_runner.stdout.log").write_text(cp.stdout,encoding="utf-8")
  (outdir/"caldero_runner.stderr.log").write_text(cp.stderr,encoding="utf-8")
  if cp.returncode!=0 or not generic_out.is_file():
   raise RuntimeError(f"CALDERO_II_RUNNER_FAILED rc={cp.returncode}: {cp.stderr[-3000:]}")
  generic=json.loads(generic_out.read_text(encoding="utf-8"))
 else:
  for k in ("caldero_identity","caldero_archetype_input","caldero_search_sources","caldero_search_fixture","allow_static_search_fixture","caldero_llm_neighbor_hints"): case.pop(k,None)
  case["_internal_analysis_no_external_search"]=True
  case["caldero_neighbor_store_root"]=str(outdir/"empty_caldero_store")
  case["stinkbox_root"]=str(outdir/"stinkbox_store")
  generic=None; dt=0.0
  dump(outdir/"CALDERO_II_ESTADO.json",{"status":"OFF","reason":"ablacion solicitada; no se ejecuta runner ni sidecar Caldero"})
 case_file=outdir/"input_efectivo.json"; dump(case_file,case)
 raw_path=outdir/"RESULT_RAW.json"
 env=os.environ.copy(); env["PYTHONHASHSEED"]="0"
 if with_caldero:
  cmd=[sys.executable,str(ENTRY),str(case_file),label,str(raw_path)]
 else:
  helper=r"""
import importlib.util, sys
from pathlib import Path
runner_path=sys.argv[1]
spec=importlib.util.spec_from_file_location("mozart_correr_estandar",runner_path)
runner=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=runner
spec.loader.exec_module(runner)
original_build=runner._build
def build_without_caldero(rd):
    original_build(rd)
    names=("plugin_circulo_monomito_v2.py","sidecar_caldero_busqueda_arquetipos.py",
           "caldero_II_runner_generico.py","caldero_buscadores.py",
           "caldero_zoomout_acero_v0_1.py","vecinos_caldero_neighbor_store.py")
    for name in names:
        for candidate in (Path(rd)/name,Path(rd)/"plugins"/name):
            if candidate.is_file(): candidate.unlink()
runner._build=build_without_caldero
args=[runner_path,*sys.argv[2:]]
sys.argv=args
raise SystemExit(runner.main(args))
"""
  cmd=[sys.executable,"-c",helper,str(ENTRY),str(case_file),label,str(raw_path)]
 cp,secs=run_cmd(cmd,env)
 (outdir/"stdout.log").write_text(cp.stdout,encoding="utf-8")
 (outdir/"stderr.log").write_text(cp.stderr,encoding="utf-8")
 if cp.returncode!=0 or not raw_path.is_file():
  raise RuntimeError(f"ENGINE_FAILED {label} rc={cp.returncode}: {cp.stderr[-5000:]}")
 raw=json.loads(raw_path.read_text(encoding="utf-8"))
 status=(raw.get("execution") or {}).get("component_status") or []
 inventory=(raw.get("execution") or {}).get("component_inventory") or []
 dump(outdir/"TRAZA_NUCLEO.json",raw.get("motor") or {})
 dump(outdir/"TRAZA_PLUGINS.json",{"component_status":status,"component_inventory":inventory,"features":raw.get("features") or {},"protocol_controls":raw.get("protocol_controls") or {}})
 hashes={}
 for x in inventory:
  n=x.get("component")
  if n and (MOTOR/n).is_file(): hashes[n]=sha(MOTOR/n)
 manifest={
  "run_id":label,"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
  "case_id":raw.get("case_id"),"input_case_id":case.get("case_id"),
  "input_provenance":json.loads(CASE_PATH.read_text(encoding="utf-8")).get("provenance"),
  "n_cuts":len(case.get("cuts") or []),"z90_date":case.get("z90_date"),
  "random_seed":case.get("random_seed"),"monte_carlo":(raw.get("execution") or {}).get("monte_carlo"),
  "caldero":"ON" if with_caldero else "OFF","caldero_generic_runner_seconds":dt,"engine_seconds":secs,
  "ablation_removed_files":[] if with_caldero else ["plugin_circulo_monomito_v2.py","sidecar_caldero_busqueda_arquetipos.py","caldero_II_runner_generico.py","caldero_buscadores.py","caldero_zoomout_acero_v0_1.py","vecinos_caldero_neighbor_store.py"],
  "python":platform.python_version(),"entrypoint":"motor/correr_estandar.py",
  "motor_sha256":sha(MOTOR/"MOTOR_V15_3_UNICO_20260927.py"),
  "engine_sha256":sha(MOTOR/"Engine_V5_CANONICO_SOLO.py"),
  "patterns_sha256":sha(MOTOR/"patterns_final_v14.json"),
  "patterns_n":len(json.loads((MOTOR/"patterns_final_v14.json").read_text(encoding="utf-8"))),
  "caldero_runner_sha256":sha(MOTOR/"caldero_II_runner_generico.py"),
  "caldero_sidecar_sha256":sha(MOTOR/"sidecar_caldero_busqueda_arquetipos.py"),
  "input_sha256":sha(case_file),"raw_sha256":sha(raw_path),
  "trace_core_sha256":sha(outdir/"TRAZA_NUCLEO.json"),
  "trace_plugins_sha256":sha(outdir/"TRAZA_PLUGINS.json"),
  "component_status":status,"component_hashes":hashes,
  "status_counts":{s:sum(1 for x in status if x.get("status")==s) for s in sorted({x.get("status","UNKNOWN") for x in status})},
  "H1":raw.get("H1"),"H2":raw.get("H2")
 }
 if with_caldero:
  manifest["caldero_generic_raw_sha256"]=sha(outdir/"CALDERO_II_RAW.json")
  manifest["caldero_generic_status"]=generic.get("persistence",{}).get("status")
 dump(outdir/"run_manifest.json",manifest)
 return raw,manifest
def family(x): return (x or {}).get("family") if isinstance(x,dict) else x
def main():
 shutil.rmtree(RESULTS,ignore_errors=True)
 RESULTS.mkdir(parents=True,exist_ok=True)
 case=json.loads(CASE_PATH.read_text(encoding="utf-8"))
 if len(case.get("cuts") or [])!=10: raise SystemExit("INPUT_REQUIRES_10_CUTS")
 if case.get("z90_date")!="1788-05-04": raise SystemExit("Z90_MISMATCH")
 a,ma=run_variant("A_CON_CALDERO",True)
 b,mb=run_variant("B_SIN_CALDERO",False)
 diff={
  "A":"A_CON_CALDERO","B":"B_SIN_CALDERO","same_input_cuts":True,
  "same_random_seed":ma["random_seed"]==mb["random_seed"],
  "same_motor_sha256":ma["motor_sha256"]==mb["motor_sha256"],
  "same_engine_sha256":ma["engine_sha256"]==mb["engine_sha256"],
  "same_patterns_sha256":ma["patterns_sha256"]==mb["patterns_sha256"],
  "H1_A":family(a.get("H1")),"H1_B":family(b.get("H1")),
  "H2_A":family(a.get("H2")),"H2_B":family(b.get("H2")),
  "H1_same":family(a.get("H1"))==family(b.get("H1")),
  "H2_same":family(a.get("H2"))==family(b.get("H2")),
  "predictor_A":a.get("predictor"),"predictor_B":b.get("predictor"),
  "component_status_A":ma["component_status"],"component_status_B":mb["component_status"],
  "caldero_feature_A":(a.get("features") or {}).get("caldero_busqueda_arquetipos"),
  "caldero_feature_B":(b.get("features") or {}).get("caldero_busqueda_arquetipos"),
  "caldero_memory_A":(a.get("features") or {}).get("caldero_neighbor_memory"),
  "caldero_memory_B":(b.get("features") or {}).get("caldero_neighbor_memory")
 }
 dump(RESULTS/"COMPARACION_DIFERENCIAL.json",diff)
 md=[
 "# Mozart — comparación A/B","",
 "- A: plugins disponibles + Caldero II 2.0; búsqueda estática explícita con fuentes históricas pre-Z90, ejecutada también por caldero_II_runner_generico.py.",
 "- B: mismos cortes, motor y semilla; Caldero II OFF. Se desactivan búsqueda, runner genérico, memoria de vecinos, cuadrantes Monomito y zoom-out Caldero solo en la copia aislada de B.",
 "- Las demás capas y plugins permanecen; sidecar Polti-Caldero se conserva como lente independiente del Caldero II objeto de esta ablación.",
 "- Monte Carlo: ON en ambas.",
 "- Input: diez cortes recuperados de RESULT histórico; el input fuente independiente no apareció en Library/paquete.",
 "- Z90: 1788-05-04.",
 "- Fuentes Caldero: siete fuentes históricas; src8 se excluyó porque contiene el estreno vienés del 7 de mayo de 1788, posterior al Z90.","",
 "## Resultados",
 f"- H1 A: {family(a.get('H1'))}","- H1 B: "+str(family(b.get("H1"))),
 "- H2 A: "+str(family(a.get("H2"))),"- H2 B: "+str(family(b.get("H2"))),
 "- H1 idéntica: "+str(diff["H1_same"]),"- H2 idéntica: "+str(diff["H2_same"]),"",
 "## Integridad",
 "- Motor V15.3 SHA-256: "+ma["motor_sha256"],
 "- Engine V5 SHA-256: "+ma["engine_sha256"],
 "- Patterns SHA-256: "+ma["patterns_sha256"]+" ("+str(ma["patterns_n"])+" patrones)",
 "- Mismo motor/Engine/patterns A/B: "+str(diff["same_motor_sha256"] and diff["same_engine_sha256"] and diff["same_patterns_sha256"]),"",
 "## Estados de componentes",
 "- A: "+json.dumps(ma["status_counts"],ensure_ascii=False),
 "- B: "+json.dumps(mb["status_counts"],ensure_ascii=False),
 "Los componentes omitidos, ausentes o con error permanecen etiquetados así en TRAZA_PLUGINS.json."
 ]
 (RESULTS/"COMPARACION_DIFERENCIAL.md").write_text("\n".join(md)+"\n",encoding="utf-8")
 lines=[]
 for p in sorted(RESULTS.rglob("*")):
  if p.is_file() and p.name!="SHA256SUMS.txt": lines.append(sha(p)+"  "+str(p.relative_to(RESULTS)))
 (RESULTS/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(json.dumps({"status":"COMPLETED","A":{"H1":family(a.get("H1")),"H2":family(a.get("H2"))},"B":{"H1":family(b.get("H1")),"H2":family(b.get("H2"))},"H1_same":diff["H1_same"],"H2_same":diff["H2_same"]},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
