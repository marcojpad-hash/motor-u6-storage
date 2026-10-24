#!/usr/bin/env python3
"""LATERAL filogenia + mezcla (revisión). NO integra al motor, NO escribe canónico,
NO re-corre el motor. Lee un RESULT json existente y produce JSON + MD.
Agnóstico: busca las fuentes por ruta y declara las que faltan.
Determinista: sin timestamps, claves ordenadas, redondeo fijo.
Uso: python3 filogenia_mezcla.py RESULT.json [outdir] [--prefix NOMBRE]
"""
import hashlib, json, math, os, sys
from itertools import combinations

R = 6
def rd(x): return round(float(x), R)
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def get(d, path):
    for k in path.split('.'):
        if isinstance(d, dict) and k in d: d = d[k]
        else: return None
    return d

def cut_order(c):
    s = str(c)
    n = ''.join(ch for ch in s if ch.isdigit())
    return (int(n) if n else 10**9, s)

# ---------- 1. ENTRADA ----------
def omega(res, fuentes, faltan):
    cands = get(res, 'predictor.candidates')
    if isinstance(cands, list) and cands and 'rank_fusion' in cands[0]:
        fuentes['omega'] = 'predictor.candidates[].rank_fusion'
        sc = {c['family']: float(c['rank_fusion']) for c in cands}
    else:
        si = get(res, 'salida_interpretable') or {}
        sc = {v['familia']: float(v['peso_relativo']) for k, v in sorted(si.items())
              if k.startswith('H') and isinstance(v, dict) and 'peso_relativo' in v}
        fuentes['omega'] = 'salida_interpretable.H*.peso_relativo' if sc else None
        if not sc: faltan.append('puntajes de la decisión final (omega)')
    orden = sorted(sc, key=lambda f: (-sc[f], f))
    return [(f'H{i+1}', f, sc[f]) for i, f in enumerate(orden)]

def cortes_input(res):
    cs = get(res, 'features.cuts')
    out = {}
    if isinstance(cs, list):
        for c in cs:
            cid = c.get('id') or c.get('corte')
            toks = []
            for dim in ('P', 'A', 'C'):
                for t in c.get(dim, []) or []:
                    toks.append((dim, t[0], float(t[1])))
            out[cid] = toks
    return out

def soporte(res, fams, cin, fuentes, faltan):
    """por hipótesis -> por corte -> lista (dim, token, peso)"""
    ph = get(res, 'predictibilidad_021.paso_inverso.por_hipotesis')
    sup, contra = {}, {}
    if isinstance(ph, dict) and all(f in ph for f in fams):
        fuentes['soporte_tokens'] = 'predictibilidad_021.paso_inverso.por_hipotesis[H].cortes[].tokens_explicados/tokens_en_contra'
        for f in fams:
            sup[f], contra[f] = {}, {}
            for c in ph[f]['cortes']:
                sup[f][c['corte']] = [(t[0], t[1], float(t[2])) for t in c.get('tokens_explicados', [])]
                contra[f][c['corte']] = [(t[0], t[1], float(t[2])) for t in c.get('tokens_en_contra', [])]
        return sup, contra
    oe = get(res, 'predictor.own_evidence') or {}
    if cin and oe:
        fuentes['soporte_tokens'] = 'predictor.own_evidence[H].favor_tokens ∩ features.cuts (fallback)'
        for f in fams:
            ft = set(oe.get(f, {}).get('favor_tokens', []))
            ct = set(oe.get(f, {}).get('contra_tokens', []))
            sup[f] = {c: [t for t in ts if t[1] in ft] for c, ts in cin.items()}
            contra[f] = {c: [t for t in ts if t[1] in ct] for c, ts in cin.items()}
        return sup, contra
    faltan.append('tokens por corte que sostienen cada hipótesis')
    return {f: {} for f in fams}, {f: {} for f in fams}

def patron_por_corte(res, fams, fuentes, faltan):
    cuts = get(res, 'motor.cuts')
    out = {f: {} for f in fams}
    if isinstance(cuts, list) and cuts and 'P_FULL_244' in cuts[0]:
        fuentes['patron_por_corte'] = 'motor.cuts[].P_FULL_244[H] (+A_FULL_244, C_FULL_244)'
        for c in cuts:
            for f in fams:
                out[f][c['corte']] = {d: rd(c.get(f'{d}_FULL_244', {}).get(f, float('nan')))
                                      for d in ('P', 'A', 'C') if f in c.get(f'{d}_FULL_244', {})}
    else:
        faltan.append('activación de patrón por corte (P_FULL_244)')
    return out

def latentes(res, path, fuentes):
    ks = sorted(k for k in res if 'latent' in k.lower())
    base = os.path.splitext(path)[0]
    side = [p for p in (base + '_SIDECAR_LATENTES.json', base + '_MOTOR_SIDECAR_LATENTES.json') if os.path.exists(p)]
    fuentes['sidecar_latentes'] = {'claves_en_result': ks, 'archivos': [os.path.abspath(p) for p in side]}
    return bool(ks or side)

# ---------- main ----------
def main():
    args = [a for a in sys.argv[1:]]
    prefix = None
    if '--prefix' in args:
        i = args.index('--prefix'); prefix = args[i+1]; del args[i:i+2]
    path = args[0]
    outdir = args[1] if len(args) > 1 else os.path.dirname(os.path.abspath(__file__))
    res = json.load(open(path))
    fuentes, faltan = {}, []
    om = omega(res, fuentes, faltan)
    fams = [f for _, f, _ in om]
    hid = {f: h for h, f, _ in om}
    cin = cortes_input(res)
    fuentes['tokens_input_por_corte'] = 'features.cuts[].P/A/C' if cin else None
    if not cin: faltan.append('tokens del input por corte')
    sup, contra = soporte(res, fams, cin, fuentes, faltan)
    pat = patron_por_corte(res, fams, fuentes, faltan)
    oe = get(res, 'predictor.own_evidence')
    fuentes['own_evidence'] = 'predictor.own_evidence (cruce de masa por corte)' if oe else None
    has_lat = latentes(res, path, fuentes)
    if not has_lat: faltan.append('sidecar de latentes (no presente para esta corrida)')
    cortes = sorted(set(cin) | {c for f in fams for c in sup[f]} | {c for f in fams for c in pat[f]}, key=cut_order)

    # ---------- 2. MEZCLA ----------
    tot = sum(s for _, _, s in om)
    prop = {f: (s / tot if tot else 0) for _, f, s in om}
    N = len(om)
    ent = -sum(p * math.log(p) for p in prop.values() if p > 0)
    mezcla = {
        'fuente': fuentes['omega'],
        'receta': [{'H': h, 'familia': f, 'puntaje': rd(s), 'proporcion': rd(prop[f])} for h, f, s in om],
        'pureza_proporcion_max': rd(max(prop.values()) if prop else 0),
        'entropia_normalizada': rd(ent / math.log(N) if N > 1 else 0),
        'n_efectivo_exp_entropia': rd(math.exp(ent)),
        'nota': 'mezcla no excluyente; proporciones = puntajes normalizados, no probabilidades',
    }

    # ---------- 3. APERTURA RETROSPECTIVA ----------
    linajes = {}
    for f in fams:
        rec = []
        for c in reversed(cortes):  # desde Ω hacia atrás
            toks = sorted(sup[f].get(c, []), key=lambda t: (t[0], t[1]))
            rec.append({'corte': c, 'tokens': [[d, t, rd(w)] for d, t, w in toks],
                        'masa': rd(sum(w for _, _, w in toks)),
                        'contra': [[d, t, rd(w)] for d, t, w in sorted(contra[f].get(c, []))],
                        'patron': pat[f].get(c, {}),
                        'own_evidence_favor_mass': (rd(oe[f]['favor_mass'][cortes.index(c)])
                                                    if oe and f in oe and len(oe[f].get('favor_mass', [])) == len(cortes) else None)})
        sost = [r['corte'] for r in rec if r['masa'] > 0]
        linajes[f] = {'H': hid[f], 'recorrido_desde_omega': rec,
                      'cortes_sostenidos': sorted(sost, key=cut_order),
                      'masa_total': rd(sum(r['masa'] for r in rec)),
                      'raiz_mas_temprana': (min(sost, key=cut_order) if sost else None)}

    # ---------- 4. GRAFO ----------
    nodos, aristas = {}, []
    def nid(c, d, t): return f'{c}|{d}|{t}'
    uso = {}  # nodo -> set de linajes
    for f in fams:
        for c in cortes:
            for d, t, w in sup[f].get(c, []):
                n = nid(c, d, t)
                nodos[n] = {'tipo': 'token', 'corte': c, 'dim': d, 'token': t, 'peso': rd(w)}
                uso.setdefault(n, set()).add(f)
            pp = pat[f].get(c, {}).get('P')
            if pp is not None:
                nodos[f'{c}|PAT|{f}'] = {'tipo': 'patron', 'corte': c, 'familia': f, 'P': pp}
    for f in fams:
        sc = linajes[f]['cortes_sostenidos']
        for c in sc:
            for d, t, w in sup[f][c]:
                aristas.append({'de': nid(c, d, t), 'a': f'{c}|PAT|{f}', 'rel': 'sostuvo a', 'linaje': f, 'peso': rd(w)})
        for a, b in zip(sc, sc[1:]):
            aristas.append({'de': f'{a}|PAT|{f}', 'a': f'{b}|PAT|{f}', 'rel': 'sostuvo a', 'linaje': f,
                            'peso': rd(sum(w for *_, w in sup[f][a]))})
        if sc:
            aristas.append({'de': f'{sc[-1]}|PAT|{f}', 'a': f'OMEGA|{hid[f]}|{f}', 'rel': 'sostuvo a', 'linaje': f,
                            'peso': rd(sum(w for *_, w in sup[f][sc[-1]]))})
            nodos[f'OMEGA|{hid[f]}|{f}'] = {'tipo': 'omega', 'H': hid[f], 'familia': f, 'proporcion': rd(prop[f])}
    aristas.sort(key=lambda e: (e['linaje'], cut_order(e['de'].split('|')[0]), e['de'], e['a']))

    # ancestros comunes: nodos token usados por 2+ linajes
    anc = []
    for n in sorted(uso, key=lambda n: (cut_order(n.split('|')[0]), n)):
        if len(uso[n]) >= 2:
            anc.append({'nodo': n, 'corte': nodos[n]['corte'], 'token': nodos[n]['token'], 'dim': nodos[n]['dim'],
                        'peso': nodos[n]['peso'], 'linajes': sorted(uso[n], key=fams.index),
                        'H': [hid[f] for f in sorted(uso[n], key=fams.index)]})
    def toks_at(f, c): return {(d, t) for d, t, _ in sup[f].get(c, [])}
    def nodes_upto(f, k):
        return {(c, d, t) for c in cortes[:k+1] for d, t, _ in sup[f].get(c, [])}

    diverg, converg = [], []
    for a, b in combinations(fams, 2):
        for i, c in enumerate(cortes):
            sh = toks_at(a, c) & toks_at(b, c)
            if sh and i + 1 < len(cortes):
                c2 = cortes[i+1]
                ta, tb = toks_at(a, c2), toks_at(b, c2)
                if (ta or tb) and not (ta & tb):
                    diverg.append({'corte_comun': c, 'corte_divergencia': c2, 'linajes': [a, b], 'H': [hid[a], hid[b]],
                                   'tokens_comunes': sorted(t for _, t in sh),
                                   'rama_a': sorted(f'{d}:{t}' for d, t in ta), 'rama_b': sorted(f'{d}:{t}' for d, t in tb),
                                   'peso_rama_a': rd(sum(w for *_, w in sup[a].get(c2, []))),
                                   'peso_rama_b': rd(sum(w for *_, w in sup[b].get(c2, [])))})
            # convergencia: sin ningún nodo compartido hasta c, ambos sostienen el mismo corte con tokens disjuntos
            if not (nodes_upto(a, i) & nodes_upto(b, i)):
                ta, tb = toks_at(a, c), toks_at(b, c)
                if ta and tb:
                    converg.append({'corte': c, 'linajes': [a, b], 'H': [hid[a], hid[b]],
                                    'tokens_a': sorted(f'{d}:{t}' for d, t in ta), 'tokens_b': sorted(f'{d}:{t}' for d, t in tb),
                                    'peso_a': rd(sum(w for *_, w in sup[a][c])), 'peso_b': rd(sum(w for *_, w in sup[b][c])),
                                    'sostienen': f'mismo corte {c} (evidencia disjunta, sin raíz común previa)'})

    # reticulación: un linaje combina en un corte tokens que antes pertenecían EXCLUSIVAMENTE a dos linajes distintos
    retic = []
    own_hist = {}  # token(dim,tok) -> set linajes que lo usaron antes
    for i, c in enumerate(cortes):
        for f in fams:
            T = toks_at(f, c)
            orig = {}
            for tk in T:
                prev = own_hist.get(tk, set()) - {f}
                if len(own_hist.get(tk, set())) == 1 and prev:
                    orig.setdefault(next(iter(prev)), []).append(f'{tk[0]}:{tk[1]}')
            if len(orig) >= 2:
                retic.append({'corte': c, 'linaje_resultante': f, 'H': hid[f],
                              'combina': {g: sorted(v) for g, v in sorted(orig.items())},
                              'peso': rd(sum(w for *_, w in sup[f][c]))})
        for f in fams:
            for tk in toks_at(f, c): own_hist.setdefault(tk, set()).add(f)
    # reticulación a nivel Ω: soporte total de H = unión de soportes de 2+ otros linajes
    allT = {f: {(d, t) for c in cortes for d, t, _ in sup[f].get(c, [])} for f in fams}
    for f in fams:
        if not allT[f]: continue
        cubre = [g for g in fams if g != f and allT[g] and allT[g] <= allT[f] and allT[g] != allT[f]]
        if len(cubre) >= 2 and set().union(*[allT[g] for g in cubre]) == allT[f]:
            retic.append({'corte': 'OMEGA', 'linaje_resultante': f, 'H': hid[f],
                          'combina': {g: sorted(f'{d}:{t}' for d, t in allT[g]) for g in cubre}, 'peso': linajes[f]['masa_total']})

    # no resuelto: activación de patrón sube vs corte previo sin token propio en ese corte,
    # o token propio sin antecedente en el input previo con subida de masa
    noref = []
    for f in fams:
        prevP, prevM = None, 0.0
        for i, c in enumerate(cortes):
            P = pat[f].get(c, {}).get('P')
            m = sum(w for *_, w in sup[f].get(c, []))
            if P is not None and prevP is not None and P > prevP + 1e-9 and m == 0:
                noref.append({'corte': c, 'linaje': f, 'H': hid[f], 'tipo': 'patron_sube_sin_token_explicado',
                              'P_prev': prevP, 'P': P, 'delta': rd(P - prevP), 'tokens': [],
                              'origen': 'NO RESUELTO (no se infiere)'})
            if m > prevM + 1e-9:
                for d, t, w in sup[f].get(c, []):
                    antes = any(t == tt for cc in cortes[:i] for _, tt, _ in cin.get(cc, []))
                    if not antes and i > 0:
                        noref.append({'corte': c, 'linaje': f, 'H': hid[f], 'tipo': 'token_nuevo_sin_antecedente_en_input',
                                      'tokens': [f'{d}:{t}'], 'peso': rd(w), 'delta_masa': rd(m - prevM),
                                      'origen': 'NO RESUELTO (primera aparición en el input; no se infiere)'})
            if P is not None: prevP = P
            prevM = m

    # ---------- 5. CIERRE ----------
    clas = {}
    for f in fams:
        T = allT[f]
        if not T:
            clas[f] = {'H': hid[f], 'estado': 'NO_SE_SOSTIENE', 'motivo': 'sin tokens que lo sostengan en ningún corte'}; continue
        iguales = [g for g in fams if g != f and allT[g] == T]
        super_ = [g for g in fams if g != f and T < allT[g]]
        propios = T - set().union(*[allT[g] for g in fams if g != f])
        if iguales:
            est, mot = 'LINAJE_EQUIVALENTE', f'mismo soporte exacto que {sorted(hid[g] for g in iguales)}: no separable con la evidencia de la corrida'
            if super_: mot += f'; además contenido en {sorted(hid[g] for g in super_)}'
        elif super_:
            est, mot = 'COMPONENTE_DE_LINAJE_COMPUESTO', f'su soporte está contenido en {sorted(hid[g] for g in super_)}'
        elif propios and (T - propios):
            est, mot = 'LINAJE_PROPIO_CON_COMPONENTE_COMPARTIDO', 'tokens propios + tokens que también sostienen otros linajes'
        elif propios:
            est, mot = 'LINAJE_PROPIO', 'tiene tokens que ningún otro linaje usa'
        else:
            est, mot = 'COMPUESTO_SIN_PROPIOS', 'todo su soporte lo comparten otros linajes'
        r = {'H': hid[f], 'estado': est, 'motivo': mot,
             'tokens_propios': sorted(f'{d}:{t}' for d, t in propios),
             'tokens_compartidos': sorted(f'{d}:{t}' for d, t in T - propios)}
        if any(x['linaje_resultante'] == f and x['corte'] == 'OMEGA' for x in retic):
            r['tambien'] = 'RETICULADO (unión de otros linajes)'
        clas[f] = r
    # componentes conexos por tokens compartidos (raíces independientes)
    par = {f: f for f in fams}
    def fnd(x):
        while par[x] != x: x = par[x]
        return x
    for a, b in combinations(fams, 2):
        if allT[a] & allT[b]: par[fnd(a)] = fnd(b)
    grupos = {}
    for f in fams:
        if allT[f]: grupos.setdefault(fnd(f), []).append(f)
    raices = sorted([sorted(g, key=fams.index) for g in grupos.values()], key=lambda g: fams.index(g[0]))
    # cobertura mínima: linajes con soporte único (no equivalentes duplicados)
    # cobertura mínima: quitar (del más débil al más fuerte) todo linaje cuyo soporte ya cubren los demás
    minimo, vistos = [], []
    for f in fams:
        if allT[f] and allT[f] not in vistos: minimo.append(f); vistos.append(allT[f])
    for f in sorted(list(minimo), key=lambda f: (prop[f], f)):
        resto = [g for g in minimo if g != f]
        if resto and allT[f] <= set().union(*[allT[g] for g in resto]): minimo.remove(f)
    minimo.sort(key=fams.index)
    cub = set().union(*[allT[f] for f in minimo]) if minimo else set()
    todo = set().union(*allT.values()) if allT else set()
    cierre = {
        'raices_independientes': [[hid[f] + ':' + f for f in g] for g in raices],
        'n_raices': len(raices),
        'ancestro_unico': len(raices) == 1,
        'estructura_minima': [hid[f] + ':' + f for f in minimo],
        'estructura_minima_cubre_todo_soporte': cub == todo,
        'clasificacion': {f: clas[f] for f in fams},
        'regla': 'no se fuerza ancestro único; raíces = componentes conexos por nodos-token compartidos',
    }

    out = {
        'lateral': 'FILOGENIA_MEZCLA_V1', 'integra_motor': False, 'escribe_canonico': False, 're_corre_motor': False,
        'entrada': {'ruta': os.path.abspath(path), 'sha256': sha(path), 'case_id': res.get('case_id'),
                    'version_motor': res.get('version'), 'patterns_sha256': res.get('patterns_sha256'), 'cortes': cortes},
        'fuentes': fuentes, 'datos_no_presentes': faltan,
        'mezcla': mezcla, 'linajes': linajes,
        'grafo': {'n_nodos': len(nodos), 'n_aristas': len(aristas),
                  'nodos': {k: nodos[k] for k in sorted(nodos)}, 'aristas': aristas},
        'ancestros_comunes': anc, 'divergencias': diverg, 'convergencias': converg,
        'reticulaciones': retic, 'no_resueltos': noref, 'cierre': cierre,
        'limitacion': 'Ramas de evidencia dentro de esta corrida (tokens del input explicados por patrones del catálogo), '
                      'no ancestros históricos ni causales. Un ancestro común es un token compartido, no un origen real.',
    }
    blob = json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)
    out_hash = hashlib.sha256(blob.encode()).hexdigest()
    pre = prefix or os.path.splitext(os.path.basename(path))[0]
    jp = os.path.join(outdir, f'FILOGENIA_MEZCLA_{pre}.json')
    open(jp, 'w').write(blob + '\n')
    open(jp + '.sha256', 'w').write(out_hash + '\n')
    open(os.path.join(outdir, f'FILOGENIA_MEZCLA_{pre}.md'), 'w').write(md(out, out_hash))
    print(jp, out_hash)

def md(o, h):
    L = [f"# LATERAL Filogenia + Mezcla — {o['entrada']['case_id']}", '',
         f"- RESULT: `{o['entrada']['ruta']}`", f"- sha256 RESULT: `{o['entrada']['sha256']}`",
         f"- sha256 salida JSON (contenido): `{h}`", f"- Cortes: {', '.join(o['entrada']['cortes'])}",
         '- No integra motor / no escribe canónico / no re-corre motor.', '', '## Fuentes usadas']
    for k, v in sorted(o['fuentes'].items()): L.append(f'- {k}: `{v}`')
    L += ['', '## Datos no presentes (declarados)'] + [f'- {x}' for x in o['datos_no_presentes']] or ['- ninguno']
    m = o['mezcla']
    L += ['', '## Mezcla (receta)', '', '| H | familia | puntaje | proporción |', '|---|---|---|---|']
    L += [f"| {r['H']} | {r['familia']} | {r['puntaje']} | {r['proporcion']:.4f} |" for r in m['receta']]
    L += ['', f"Pureza (proporción máx): {m['pureza_proporcion_max']:.4f} · Entropía normalizada: {m['entropia_normalizada']:.4f} · N efectivo: {m['n_efectivo_exp_entropia']:.3f}", '',
          '## Linajes (recorrido desde Ω hacia atrás)']
    for f, l in o['linajes'].items():
        L += ['', f"### {l['H']} {f} — masa {l['masa_total']}, raíz más temprana {l['raiz_mas_temprana']}", '',
              '| corte | tokens (dim:token peso) | masa | P patrón |', '|---|---|---|---|']
        for r in l['recorrido_desde_omega']:
            L.append(f"| {r['corte']} | {', '.join(f'{d}:{t} {w}' for d, t, w in r['tokens']) or '—'} | {r['masa']} | {r['patron'].get('P', 'n/d')} |")
    L += ['', '## Ancestros comunes'] + [f"- {a['corte']} {a['dim']}:{a['token']} ({a['peso']}) ← {', '.join(a['H'])}" for a in o['ancestros_comunes']]
    L += ['', '## Divergencias'] + [f"- {d['H'][0]}/{d['H'][1]}: comparten {d['tokens_comunes']} en {d['corte_comun']}, se separan en {d['corte_divergencia']} → {d['rama_a'] or '∅'} ({d['peso_rama_a']}) vs {d['rama_b'] or '∅'} ({d['peso_rama_b']})" for d in o['divergencias']]
    L += ['', '## Convergencias (por par; mismo corte sostenido con evidencia disjunta y sin raíz común previa)']
    pares = {}
    for c in o['convergencias']: pares.setdefault(tuple(c['H']), []).append(c)
    for k in sorted(pares):
        v = pares[k]
        L.append(f"- {k[0]}/{k[1]}: cortes {[c['corte'] for c in v]}; tokens {sorted({t for c in v for t in c['tokens_a']})} vs {sorted({t for c in v for t in c['tokens_b']})}; peso {round(sum(c['peso_a'] for c in v),4)} vs {round(sum(c['peso_b'] for c in v),4)}")
    L += ['', '## Reticulaciones'] + [f"- {r['corte']} {r['H']} {r['linaje_resultante']} combina {r['combina']} (peso {r['peso']})" for r in o['reticulaciones']] or ['- ninguna']
    L += ['', '## No resueltos'] + [f"- {n['corte']} {n['H']} {n['linaje']}: {n['tipo']} {n.get('tokens')} delta={n.get('delta', n.get('delta_masa'))} — {n['origen']}" for n in o['no_resueltos']]
    c = o['cierre']
    L += ['', '## Cierre', f"- Raíces independientes ({c['n_raices']}): {c['raices_independientes']}", f"- Ancestro único: {c['ancestro_unico']}",
          f"- Estructura mínima: {c['estructura_minima']} (cubre todo: {c['estructura_minima_cubre_todo_soporte']})", '']
    for f, v in c['clasificacion'].items():
        L.append(f"- {v['H']} {f}: **{v['estado']}** — {v['motivo']}; propios {v.get('tokens_propios')}; compartidos {v.get('tokens_compartidos')}{' · ' + v['tambien'] if 'tambien' in v else ''}")
    L += ['', '## Limitación', o['limitacion'], '']
    return '\n'.join(L)

if __name__ == '__main__':
    main()
