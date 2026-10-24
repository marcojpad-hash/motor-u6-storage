#!/usr/bin/env python3
"""Prueba negativa: copia un recibo+resultado reales a /tmp, inyecta fallas conocidas y verifica que el detector
y el verificador las marcan. No toca resultados reales. Uso: python3 u5/test_u5_detector.py RECIBO_U5.json"""
import sys, json, shutil, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import u5_detector as D, u5_verificar as V, u5_monitor as M
from u5_comun import self_hash
rp = Path(sys.argv[1]); rec = json.loads(rp.read_text())
td = Path(tempfile.mkdtemp(prefix="u5test_"))
res_src = Path(next(a["path"] for a in rec["archivos_clave"] if a["rol"] == "resultado"))
R = json.loads(res_src.read_text())
P = R["predictor"]; c = P["candidates"]
fam = c[0]["family"]; P.setdefault("own_evidence", {}).setdefault(fam, {}).setdefault("favor_tokens", []).append("TOKEN_INYECTADO_U5")
c[0]["operational_rank"], c[-1]["operational_rank"] = c[-1]["operational_rank"], c[0]["operational_rank"]
P["empates"] = {"top1_top2_empate": True, "grupos_empate_top10": []}
R["consulta_dirigida"] = {"adaptador": "test", "z_idx": 0, "z": "x", "filas": [{"pregunta_id": "Q1", "corte": (json.loads(Path(rec['archivos_clave'][0]['path']).read_text()).get('cuts') or [{}])[-1].get("id"), "tokens_entregados_al_motor": ["a", "b", "c"]}] * 5}
res2 = td / res_src.name; res2.write_text(json.dumps(R))
for a in rec["archivos_clave"]:
    if a["rol"] == "resultado": a["path"] = str(res2)
rec2 = json.loads(json.dumps(rec)); rec2["H"]["H1"] = "OTRA_FAMILIA"; rec2["self_sha256"] = self_hash(rec2)
p1 = td / "r1.json"; p1.write_text(json.dumps(rec)); p2 = td / "r2.json"; p2.write_text(json.dumps(rec2))
det = D.por_corrida(p1); tipos = {a["tipo"] for a in det["anomalias"]}
esper = {"A4_TOKEN_DISPARA_SIN_FUENTE_EN_INPUT", "A3_LATERAL_REORDENA_FUERA_DE_BANDA", "A9_EMPATE_TOP1_TOP2", "A5_CONSULTA_EXCEDE_PREGUNTAS", "A5_CONSULTA_EXCEDE_TOKENS", "A5_CONSULTA_FUGA_POST_Z", "A5_CONSULTA_TOKEN_NO_CANONICO"}
cross = {a["tipo"] for a in D.entre_corridas([det, D.por_corrida(p2)], [rec, rec2])}
mon = M.monitorear([str(p1), str(p2)])
rec3 = json.loads(p2.read_text()); rec3["H"]["H2"] = "MANIPULADO"; p3 = td / "r3.json"; p3.write_text(json.dumps(rec3))
v = V.verificar(p3)
out = {"faltan": sorted(esper - tipos), "A2_detectado": "A2_CAMBIO_H1_MISMO_INPUT" in cross,
       "monitor_marca_deriva_H1": any(d["campo"] == "H.H1" for x in mon for d in x.get("deriva", [])), "verificador_rechaza_manipulado": not v["ok"]}
out["ok"] = not out["faltan"] and out["A2_detectado"] and out["monitor_marca_deriva_H1"] and out["verificador_rechaza_manipulado"]
print(json.dumps(out, ensure_ascii=False)); shutil.rmtree(td); sys.exit(0 if out["ok"] else 1)
