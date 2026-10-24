#!/usr/bin/env python3
"""Equivalencias teoría del color <-> modelo, y rueda cromática. Lee COLOR_*.json (salida de teoria_color.py)."""
import json, math, glob, hashlib, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
AX = ['interno', 'externo', 'situacion']; R = lambda x: round(x, 6)
def hue(t):  # proyección del tono (suma 1) al plano cromático; ángulo 0=interno(R),120=externo(G),240=situación(B)
    v = [t.get(a) or 0 for a in AX]
    x = sum(v[i]*math.cos(math.radians(120*i)) for i in range(3)); y = sum(v[i]*math.sin(math.radians(120*i)) for i in range(3))
    return R(math.degrees(math.atan2(y, x)) % 360), R(min(1, math.hypot(x, y)/1.0))  # croma: 0 gris, 1 eje puro
def hx(t):
    c=[t.get(a) or 0 for a in AX]; m=max(c) or 1; return '#'+''.join('%02x'%int(round(255*x/m)) for x in c)
L = ['# Equivalencias teoría del color ↔ modelo (lateral, no decide H)', '',
     'Croma = distancia del tono al gris (1/3,1/3,1/3) en el plano cromático, escala 0 (gris) a 1 (eje puro). Matiz = ángulo: 0°=interno(R), 120°=externo(G), 240°=situación(B).', '']
res = {}
for f in sorted(glob.glob('COLOR_*.json')):
    d = json.load(open(f)); n = f[6:-5]; hy = d['hipotesis']; fin = d['tono_final_mezcla']
    huec = any(v is None for v in fin['tono'].values())
    H = {h: hue(v['color']['tono']) + (v['peso_rank_fusion_norm'],) for h, v in hy.items()}
    hf = hue(fin['tono'])
    # complementarios: |Δmatiz| en [150,210] y ambos croma>0.02
    comp = [(a, b, R(abs(H[a][0]-H[b][0]))) for a in H for b in H if a < b and 150 <= abs(H[a][0]-H[b][0]) <= 210 and min(H[a][1], H[b][1]) > .02]
    anal = [(a, b, R(min(abs(H[a][0]-H[b][0]), 360-abs(H[a][0]-H[b][0])))) for a in H for b in H if a < b and min(abs(H[a][0]-H[b][0]), 360-abs(H[a][0]-H[b][0])) <= 30]
    sumcroma = sum(w*c for _, c, w in H.values())
    neutral = R(max(0.0, 1 - hf[1]/sumcroma)) if sumcroma > 0 else None  # cuánto croma se pierde al mezclar
    temp = R((fin['tono']['interno'] or 0) - (fin['tono']['situacion'] or 0)) if not huec else None
    res[n] = dict(matiz_final=hf[0], croma_final=hf[1], neutralizacion=neutral, complementarios=comp, n_analogos=len(anal),
                  temperatura=temp, valor=fin['intensidad'], hipotesis={h: {'matiz': v[0], 'croma': v[1]} for h, v in H.items()})
    # rueda
    fig = plt.figure(figsize=(6, 6)); ax = fig.add_subplot(projection='polar')
    for h, (a, c, w) in H.items():
        ax.scatter(math.radians(a), c, s=3000*w, color=hx(hy[h]['color']['tono']), edgecolor='k'); ax.annotate(h[:22], (math.radians(a), c), fontsize=7)
    ax.scatter(math.radians(hf[0]), hf[1], marker='*', s=300, color='k'); ax.annotate('MEZCLA', (math.radians(hf[0]), hf[1]), fontsize=8, weight='bold')
    ax.set_xticks([0, math.radians(120), math.radians(240)]); ax.set_xticklabels(['interno (P)', 'externo (A)', 'situación (C)'])
    ax.set_ylim(0, max([c for _, c, _ in H.values()] + [hf[1], .05])*1.25); ax.set_title('Rueda — ' + n + (' [ejes A/C HUECO]' if huec else ''), fontsize=8)
    p = f'RUEDA_{n}.png'; fig.savefig(p, dpi=110, bbox_inches='tight')
    open(p+'.sha256','w').write(hashlib.sha256(open(p,'rb').read()).hexdigest()+'  '+p+'\n')
json.dump(res, open('EQUIVALENCIAS.json','w'), ensure_ascii=False, indent=1, sort_keys=True)
k = list(res); U6 = res[k[0]] if 'U6' in k[0] else res[k[1]]; U10 = res[k[1]] if 'U6' in k[0] else res[k[0]]
def s(r, key): return r[key]
rows = [
 ('Tríada primaria (R,G,B / C,M,Y)', 'Tríada P/A/C = interno/externo/situación', 'APLICABLE', 'Ejes del lateral', 'U10: 3 ejes con datos. U6: solo P (A,C hueco)'),
 ('Mezcla aditiva RGB', 'Suma de evidencia por eje (FULL_244) normalizada', 'APLICABLE', 'tono_e = v_e / Σv', f"U10 tono final {json.load(open(glob.glob('COLOR_*u10.json')[0]))['tono_final_mezcla']['tono']}"),
 ('Mezcla sustractiva CMY', 'Restricción (un eje que "absorbe" a otro)', 'NO APLICABLE', '—', 'Los FULL_244 son activaciones ≥0 que se suman; no hay filtro que reste. Forzarlo sería inventar'),
 ('Círculo cromático / matiz', 'Ángulo del tono en el plano P/A/C', 'APLICABLE', 'matiz=atan2(Σv_i sin120i, Σv_i cos120i)', f"U10 matiz final {U10['matiz_final']}°; U6 {U6['matiz_final']}° (trivial: 1 eje)"),
 ('Saturación / croma', 'Pureza de la lectura (qué tan lejos del gris)', 'APLICABLE', 'croma=|proyección|; saturación=max−min', f"U10 croma {U10['croma_final']} (muy bajo); U6 1.0 por hueco, no por dato"),
 ('Gris / neutralización', 'Mezcla plana: hipótesis que juntas pierden pureza', 'APLICABLE', 'neutralización=1−croma_mezcla/Σ(w·croma_H)', f"U10 {U10['neutralizacion']}; U6 {U6['neutralizacion']}"),
 ('Complementarios', 'Hipótesis que se anulan en la mezcla (Δmatiz≈180°)', 'APLICABLE (resultado vacío)', '150°≤|Δmatiz|≤210°, croma>0.02', f"U10 pares: {U10['complementarios'] or 'ninguno'}; U6 no evaluable"),
 ('Análogos', 'Hipótesis vecinas en matiz (mismo tono, distinto nombre cercano)', 'APLICABLE', 'Δmatiz≤30°', f"U10 {U10['n_analogos']} pares análogos de {len(U10['hipotesis'])*(len(U10['hipotesis'])-1)//2}; U6 todos (trivial)"),
 ('Tríada armónica (3 matices a 120°)', 'Hipótesis que cubren los tres ejes repartidos', 'PARCIAL', 'buscar H con matiz ≈0/120/240', 'U10: ninguna H cerca de 120° (externo); 4 H en ~0–14° (interno) y 2 en 267–292° (entre situación e interno): diada, no tríada'),
 ('Valor / luminosidad', 'Intensidad (magnitud RMS de la activación)', 'APLICABLE', 'valor=√(Σv²/n)', f"U10 {U10['valor']}; U6 {U6['valor']} (solo P)"),
 ('Temperatura cálido/frío', 'interno (cálido, R) vs situación (frío, B)', 'PARCIAL', 'temp=tono_interno−tono_situación', f"U10 {U10['temperatura']} (levemente cálido = sesgo interno). Convención arbitraria; solo ilustrativa"),
 ('Pigmento idéntico (metamerismo)', 'Dos nombres con el mismo vector en todos los cortes', 'APLICABLE', 'igualdad exacta de vectores P/A/C C1..C10', 'U10: ninguno exacto; casi: arquetipo_el_creador/schwartz_10/utopia_liberal tienen externo≈situación (A≈C). U6: ninguno exacto'),
]
L += ['| Regla clásica | Concepto del modelo | Estado | Fórmula | Resultado Mozart |', '|---|---|---|---|---|'] + ['| ' + ' | '.join(map(str, r)) + ' |' for r in rows]
open('EQUIVALENCIAS.md','w').write('\n'.join(L)+'\n')
for p in ('EQUIVALENCIAS.md','EQUIVALENCIAS.json'): open(p+'.sha256','w').write(hashlib.sha256(open(p,'rb').read()).hexdigest()+'  '+p+'\n')
print(json.dumps({n:{x:y for x,y in r.items() if x!='hipotesis'} for n,r in res.items()}, ensure_ascii=False)); print({n:r['hipotesis'] for n,r in res.items()})
