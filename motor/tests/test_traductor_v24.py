import json, sys
sys.path.insert(0, 'motor/motor')
from lateral_traduccion_salida_v1 import traducir

cases = [
    ('LIMBO', 'motor/RESULT_LIMBO_6C.json', 'motor/corridas_ciegas_20261113/entrada_LIMBO_6C.json'),
    ('MOZART_NINO', 'motor/RESULT_MOZART_NINO_7C.json', 'motor/corridas_ciegas_20261113/entrada_MOZART_NINO_7C.json'),
    ('TESLA_7C', 'motor/RESULT_TESLA_7C.json', 'motor/corridas_ciegas_20261113/entrada_CAL_F001_02_TESLA_7C.json'),
]
outs = {}
for name, rp, ep in cases:
    res = json.load(open(rp))
    ent = json.load(open(ep))
    out = traducir(res, ent)
    outs[name] = out
    print(f"===== {name} | violaciones: {out['violaciones']} | registro: {out['anexo']['registro']} | version: {out['anexo']['version']}")
    print(out['lectura'])
    print()
json.dump(outs['LIMBO'], open('LECTURA_LIMBO_6C_v28.json', 'w'), ensure_ascii=False, indent=1)
print("LIMBO v2.8 guardado en LECTURA_LIMBO_6C_v28.json")
