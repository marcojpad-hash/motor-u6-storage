"""Re-filtra stinkbox/tokens.jsonl con filtro_tokens_arquetipos_v2 (A5 2026-11-07) y escribe reporte de brechas.
Los descartados NO se pierden: quedan en cuarentena en stinkbox/tokens_descartados_v2_<fecha>.jsonl.
Lee el catálogo 244 solo en modo lectura. Uso: python3 scripts/limpiar_tokens_stinkbox.py"""
import sys, json, collections
from datetime import date
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R / 'motor' / 'motor'))
import filtro_tokens_arquetipos_v2 as f
P = R / 'stinkbox' / 'tokens.jsonl'; r = [json.loads(l) for l in P.open(encoding='utf-8') if l.strip()]
keep = [x for x in r if f.conservar(x['token'])]; drop = [x for x in r if not f.conservar(x['token'])]
# Cuarentena: lo descartado queda recuperable con su motivo, no se borra en silencio.
Q = R / 'stinkbox' / f'tokens_descartados_v2_{date.today():%Y%m%d}.jsonl'
Q.write_text(''.join(json.dumps({**x, 'motivo_descarte_v2': f.motivo_descarte(x['token'])}, ensure_ascii=False) + '\n' for x in drop), encoding='utf-8')
P.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in keep), encoding='utf-8')
voc = f.vocabulario_catalogo(R / 'motor' / 'motor')
gap = f.brechas([x['token'] for x in keep], voc); byt = {x['token']: x for x in keep}
gr = sorted(gap, key=lambda t: (-len(byt[t]['casos']), -byt[t]['conteo'], t))
mot = collections.Counter(f.motivo_descarte(x['token']) for x in drop)
topd = sorted(drop, key=lambda x: -x['conteo'])[:40]
rec = [t for t in gr if len(byt[t]['casos']) >= 3]
L = [f'# Limpieza StinkBox tokens.jsonl — filtro_tokens_arquetipos_v2 ({date.today()})', '',
     f'- Descartados en cuarentena: {Q.name} ({len(drop)} tokens, con motivo)', '',
     f'- Antes: {len(r)} tokens únicos', f'- Después: {len(keep)} tokens únicos (descartados {len(drop)})',
     '- Motivos: ' + ', '.join(f'{k}={v}' for k, v in mot.most_common()),
     f'- Vocabulario de catálogo leído (244 + familias_tokens, solo lectura): {len(voc)} tokens',
     f'- Tokens conservados SIN equivalente en catálogo (brechas): {len(gap)}; de ellos en ≥3 casos: {len(rec)}', '',
     '## Top descartados (por conteo)', '', ', '.join(f"`{x['token']}`({x['conteo']})" for x in topd), '',
     '## Candidatos a familias faltantes (brechas, por nº de casos) — top 200', '',
     '| token | casos | conteo |', '|---|---|---|'] + [f"| {t} | {len(byt[t]['casos'])} | {byt[t]['conteo']} |" for t in gr[:200]] + ['',
     'Nota: brecha = token sin equivalente léxico (ni raíz) en el catálogo; NO es familia confirmada. Agrupar por tema antes de proponer familia.']
(R / 'stinkbox' / f'REPORTE_FILTRO_TOKENS_{date.today():%Y%m%d}.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('\n'.join(L[:7])); print(gr[:100])
