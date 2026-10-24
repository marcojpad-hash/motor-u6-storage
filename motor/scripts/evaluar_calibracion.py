#!/usr/bin/env python3
"""Evalúa calibración a partir de pares de predicción sellada y desenlace observado.

Uso: python scripts/evaluar_calibracion.py archivo.json salida.json
Entrada: {"rows":[{"probability":0.7,"outcome":1}, ...]}
Opcional: cada fila puede incluir score; el ajuste Platt requiere >=20 etiquetas y ambas clases.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'motor'))
from calibracion_predictiva_v1 import evaluate_binary_predictions, fit_platt_scaling

def main(argv):
    if len(argv)<2:
        print('uso: python scripts/evaluar_calibracion.py entrada.json salida.json',file=sys.stderr); return 2
    src=Path(argv[1]); out=Path(argv[2]) if len(argv)>2 else src.with_name(src.stem+'_CALIBRACION.json')
    raw=json.loads(src.read_text(encoding='utf-8'))
    rows=raw.get('rows') if isinstance(raw,dict) else raw
    if not isinstance(rows,list): raise ValueError('entrada debe ser una lista o contener rows:list')
    report={'schema':'PREDICTIVE_CALIBRATION_REPORT_V1','input':str(src.resolve()),'n_rows':len(rows),'metrics':evaluate_binary_predictions(rows)}
    if rows and all('score' in r for r in rows): report['platt_scaling']=fit_platt_scaling(rows)
    report['warning']='No mezclar objetivos ni horizontes temporales. Los porcentajes de relleno estructural y rank_fusion no son probabilidades.'
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'ok':True,'status':report['metrics']['status'],'n':report['n_rows'],'output':str(out.resolve())},ensure_ascii=False)); return 0
if __name__=='__main__': raise SystemExit(main(sys.argv))
