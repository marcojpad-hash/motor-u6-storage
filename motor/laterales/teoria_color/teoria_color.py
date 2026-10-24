#!/usr/bin/env python3
"""LATERAL TEORIA DEL COLOR v1 — solo lee el RESULT; no decide H; no toca motor.
Ejes: interno<-P, externo<-A, situacion<-C. Fuente: motor.cuts[].{P,A,C}_FULL_244 + motor.cuts[].n_tokens
(y features.cuts[].P/A/C como masa de tokens). Pesos: predictor.candidates[].rank_fusion normalizado."""
import json, sys, math, hashlib, os
AX = ['interno', 'externo', 'situacion']; DIM = ['P', 'A', 'C']
R = lambda x: round(float(x), 6)

def ent(v):
    s = sum(v)
    if s <= 0: return None
    return R(-sum((x/s)*math.log(x/s) for x in v if x > 0)/math.log(3))

def color(vals):
    """vals: lista de 3 floats o None (hueco). Devuelve color sobre ejes con datos."""
    ok = [i for i, v in enumerate(vals) if v is not None]
    s = sum(vals[i] for i in ok)
    if not ok or s <= 0: return None
    mix = {AX[i]: (R(vals[i]/s) if vals[i] is not None else None) for i in range(3)}
    mag = math.sqrt(sum(vals[i]**2 for i in ok)/len(ok))      # RMS en [0,1]
    p = [vals[i]/s for i in ok]; pmax = max(p)
    sat = (pmax - min(p))                                      # 0 gris .. 1 puro
    return {'tono': mix, 'intensidad': R(mag), 'pureza': R(pmax),
            'eje_dominante': AX[ok[p.index(pmax)]] if p.count(pmax) == 1 else 'empate',
            'entropia_norm': R(-sum(x*math.log(x) for x in p if x > 0)/math.log(3)),
            'saturacion': R(sat), 'ejes_con_datos': [AX[i] for i in ok]}

def hexrgb(t):
    c = [t.get(a) or 0.0 for a in AX]; m = max(c) or 1
    return '#' + ''.join('%02x' % int(round(255*x/m)) for x in c)

def run(path, outdir):
    d = json.load(open(path)); cuts = d['motor']['cuts']; fcuts = d['features'].get('cuts', [])
    cands = d['predictor']['candidates']
    tot = sum(max(0, c['rank_fusion']) for c in cands)
    W = {c['family']: R(max(0, c['rank_fusion'])/tot) for c in cands}
    huecos, tray = [], []
    masa = {k: sum(len(fc.get(k) or []) for fc in fcuts) for k in DIM}
    for k in DIM:
        if masa[k] == 0: huecos.append(f'features: 0 tokens {k} en todos los cortes -> eje {AX[DIM.index(k)]} HUECO')
    per_h = {h: [] for h in W}
    for c in cuts:
        nt = c.get('n_tokens', {}); hole = [nt.get(k, 0) == 0 for k in DIM]
        for i, k in enumerate(DIM):
            if hole[i]: huecos.append(f"{c['corte']}: n_tokens {k}=0 -> {k}_FULL_244 no es dato (valor por defecto), eje {AX[i]} hueco")
        mix = [0.0]*3; wsum = [0.0]*3; cc = {}
        for h, w in W.items():
            vals = [None if hole[i] else c[k+'_FULL_244'].get(h) for i, k in enumerate(DIM)]
            col = color(vals); cc[h] = col; per_h[h].append(vals)
            for i in range(3):
                if vals[i] is not None and col: mix[i] += w*col['tono'][AX[i]]; wsum[i] += w
        tw = sum(wsum[i] for i in range(3) if mix[i] or wsum[i]) and None
        mixv = [mix[i] if wsum[i] > 0 else None for i in range(3)]
        tray.append({'corte': c['corte'], 'n_tokens': nt, 'mezcla': color(mixv)})
    # color final por hipotesis: media por corte de vals con datos
    hyp = {}
    for h, rows in per_h.items():
        avg = []
        for i in range(3):
            xs = [r[i] for r in rows if r[i] is not None]
            avg.append(sum(xs)/len(xs) if xs else None)
        col = color(avg)
        if col: col['hex_ilustrativo'] = hexrgb(col['tono'])
        hyp[h] = {'peso_rank_fusion_norm': W[h], 'vector_medio_PAC': [None if a is None else R(a) for a in avg], 'color': col}
    fin = [0.0]*3; has = [False]*3
    for h, v in hyp.items():
        if not v['color']: continue
        for i in range(3):
            t = v['color']['tono'][AX[i]]
            if t is not None: fin[i] += v['peso_rank_fusion_norm']*t; has[i] = True
    final = color([fin[i] if has[i] else None for i in range(3)])
    if final: final['hex_ilustrativo'] = hexrgb(final['tono'])
    # pigmentos identicos: misma secuencia de vectores en todos los cortes
    grp = {}
    for h, rows in per_h.items(): grp.setdefault(json.dumps(rows), []).append(h)
    ident = [g for g in grp.values() if len(g) > 1]
    # que eje mueve: mayor |delta| de tono entre cortes consecutivos
    mov = []
    for a, b in zip(tray, tray[1:]):
        if not (a['mezcla'] and b['mezcla']): mov.append({'de': a['corte'], 'a': b['corte'], 'eje': None}); continue
        dl = {x: R((b['mezcla']['tono'][x] or 0)-(a['mezcla']['tono'][x] or 0)) for x in AX
              if a['mezcla']['tono'][x] is not None and b['mezcla']['tono'][x] is not None}
        dl2 = {x: v for x, v in dl.items() if v != 0}
        mov.append({'de': a['corte'], 'a': b['corte'], 'delta': dl,
                    'eje_que_mueve': max(dl2, key=lambda x: abs(dl2[x])) if dl2 else 'sin_cambio'})
    out = {'lateral': 'teoria_color_v1', 'decide_H': False, 'fuente': path,
           'fuente_sha256': hashlib.sha256(open(path, 'rb').read()).hexdigest(),
           'mapeo': {'interno': 'P_FULL_244', 'externo': 'A_FULL_244', 'situacion': 'C_FULL_244'},
           'pesos': 'predictor.candidates[].rank_fusion / suma', 'masa_tokens_features': masa,
           'H_motor': {'H1': d['predictor'].get('H1'), 'H2': d['predictor'].get('H2')},
           'tono_final_mezcla': final, 'hipotesis': hyp, 'pigmentos_identicos': ident,
           'trayectoria': tray, 'movimiento': mov, 'huecos': huecos}
    name = os.path.basename(path).replace('.json', '')
    jp = f'{outdir}/COLOR_{name}.json'; json.dump(out, open(jp, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    # MD
    L = [f'# Teoría del color — {name}', '', 'Lateral: alimenta, NO decide H.', '',
         f"Tono final: {final['tono'] if final else 'HUECO'}  pureza={final and final['pureza']} entropía={final and final['entropia_norm']} saturación={final and final['saturacion']} hex={final and final['hex_ilustrativo']}", '',
         '| H | peso | interno | externo | situación | pureza | entropía | hex |', '|---|---|---|---|---|---|---|---|']
    for h, v in sorted(hyp.items(), key=lambda x: -x[1]['peso_rank_fusion_norm']):
        c = v['color'] or {'tono': {}}
        L.append(f"| {h} | {v['peso_rank_fusion_norm']} | {c['tono'].get('interno')} | {c['tono'].get('externo')} | {c['tono'].get('situacion')} | {c.get('pureza')} | {c.get('entropia_norm')} | {c.get('hex_ilustrativo')} |")
    L += ['', '## Trayectoria', '| corte | interno | externo | situación | pureza | entropía |', '|---|---|---|---|---|---|']
    for t in tray:
        m = t['mezcla'] or {'tono': {}}
        L.append(f"| {t['corte']} | {m['tono'].get('interno')} | {m['tono'].get('externo')} | {m['tono'].get('situacion')} | {m.get('pureza')} | {m.get('entropia_norm')} |")
    L += ['', '## Eje que mueve'] + [f"- {m['de']}→{m['a']}: {m.get('eje_que_mueve')} {m.get('delta')}" for m in mov]
    L += ['', '## Pigmentos idénticos'] + [f'- {g}' for g in ident] + ['', '## Huecos'] + [f'- {x}' for x in huecos]
    mp = jp.replace('.json', '.md'); open(mp, 'w').write('\n'.join(L) + '\n')
    # PNG
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    xs = [t['corte'] for t in tray]; fig, ax = plt.subplots(figsize=(9, 4))
    for a, col in zip(AX, ['red', 'green', 'blue']):
        ax.plot(xs, [(t['mezcla'] or {'tono': {}})['tono'].get(a) if t['mezcla'] else None for t in tray], 'o-', color=col, label=a)
    for i, t in enumerate(tray):
        if t['mezcla']: ax.axvspan(i-.5, i+.5, color=hexrgb(t['mezcla']['tono']), alpha=.25)
    ax.set_ylim(0, 1); ax.legend(); ax.set_title('Trayectoria del tono — ' + name, fontsize=9)
    pp = jp.replace('.json', '.png'); fig.savefig(pp, dpi=110, bbox_inches='tight')
    for p in (jp, mp, pp):
        open(p + '.sha256', 'w').write(hashlib.sha256(open(p, 'rb').read()).hexdigest() + '  ' + os.path.basename(p) + '\n')
    return out

if __name__ == '__main__':
    od = os.path.dirname(os.path.abspath(__file__))
    for p in sys.argv[1:]:
        o = run(p, od); print(json.dumps({'caso': p, 'final': o['tono_final_mezcla'], 'ident': o['pigmentos_identicos'],
              'mov': [(m['de'], m['a'], m.get('eje_que_mueve')) for m in o['movimiento']], 'n_huecos': len(o['huecos']),
              'tray': [(t['corte'], t['mezcla'] and t['mezcla']['tono']) for t in o['trayectoria']],
              'hyp': {h: (v['peso_rank_fusion_norm'], v['color'] and v['color']['tono'], v['color'] and v['color']['hex_ilustrativo']) for h, v in o['hipotesis'].items()}}, ensure_ascii=False))
