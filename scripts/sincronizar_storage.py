#!/usr/bin/env python3
"""Sincronizador del storage comun del motor U6 (motor-u6-storage).

Uso:
  python scripts/sincronizar_storage.py antes   [--repo RUTA]
      Antes de cada corrida: trae la version mas nueva (git pull; si no hay
      git/credenciales, consulta la API publica de GitHub sin token; si no hay
      red, sigue en modo local). Reporta que cambio en motor/ y stinkbox/ y
      verifica los hashes canonicos. Sale con codigo 2 si un canonico no coincide.
  python scripts/sincronizar_storage.py despues --corrida DIR_CORRIDA [--repo RUTA] [--modelo NOMBRE]
      Despues de una corrida: agrega SOLO
        - tokens StinkBox nuevos (deduplicados, conteo, procedencia) a stinkbox/tokens.jsonl
        - un RESUMEN de la corrida a casos/resultados/resultados.jsonl
      Nunca sube la corrida completa ni salidas completas. Hace commit+push si hay
      credenciales; si no, escribe parches JSONL locales en _pendiente_subir/.
  python scripts/sincronizar_storage.py resumen --corrida DIR_CORRIDA
      Imprime el resumen de una corrida (sin escribir nada).

Reglas: nunca hace push de cambios al motor canonico ni al catalogo. Los cambios
de codigo los documenta el modelo en avances/ (antes -> despues, sha antes/despues).
Sin dependencias externas (solo biblioteca estandar + git opcional).
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, urllib.request
from datetime import datetime
from pathlib import Path

OWNER_REPO = os.environ.get('MOTOR_U6_REPO', 'marcojpad-hash/motor-u6-storage')
CANONICOS = {
    'motor/motor/Engine_V5_CANONICO_SOLO.py': '665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082',
    'motor/motor/patterns_final_v14.json': 'd827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1',
}
PERMITIDOS_PUSH = ('stinkbox/tokens.jsonl', 'casos/resultados/resultados.jsonl')

def sha_file(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None

def git(repo: Path, *args, check=False):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, check=check, timeout=120)

def es_git(repo: Path) -> bool:
    try: return git(repo, 'rev-parse', '--is-inside-work-tree').stdout.strip() == 'true'
    except Exception: return False

def verificar_canonicos(repo: Path) -> bool:
    ok = True
    for rel, esperado in CANONICOS.items():
        real = sha_file(repo / rel)
        estado = 'OK' if real == esperado else ('FALTA' if real is None else 'NO_COINCIDE')
        if estado != 'OK': ok = False
        print(f'  canonico {rel}: {estado}')
    return ok

def antes(repo: Path):
    print(f'[sincronizar] repo local: {repo}')
    if es_git(repo):
        previo = git(repo, 'rev-parse', 'HEAD').stdout.strip()
        r = git(repo, 'pull', '--ff-only')
        if r.returncode != 0:
            print('  git pull fallo (sin red o sin credenciales); sigo con la copia local.')
            print('  ' + (r.stderr.strip().splitlines() or [''])[-1])
        else:
            nuevo = git(repo, 'rev-parse', 'HEAD').stdout.strip()
            if nuevo == previo: print('  sin cambios remotos.')
            else:
                diff = git(repo, 'diff', '--stat', previo, nuevo, '--', 'motor', 'stinkbox').stdout
                print(f'  actualizado {previo[:8]} -> {nuevo[:8]}. Cambios en motor/ y stinkbox/:')
                print(diff or '  (ninguno en motor/ ni stinkbox/)')
                log = git(repo, 'log', '--oneline', f'{previo}..{nuevo}').stdout
                print('  commits nuevos:\n' + log)
    else:
        url = f'https://api.github.com/repos/{OWNER_REPO}/commits?per_page=5'
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'motor-u6-sync'}), timeout=15) as r:
                commits = json.loads(r.read())
            print('  ultimos commits remotos (API publica):')
            for c in commits: print('   ', c['sha'][:8], c['commit']['message'].splitlines()[0])
        except Exception as e:
            print(f'  sin acceso remoto ({type(e).__name__}); repo privado sin credenciales o sin red. Modo local.')
    ok = verificar_canonicos(repo)
    if not ok:
        print('ALERTA: hash canonico no coincide. No correr hasta revisar.'); sys.exit(2)
    print('[sincronizar] listo para correr.')

def _cargar(p: Path):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None

def resumen_corrida(d: Path) -> dict:
    res = _cargar(d / '_PRIMARY_RESULT.json') or {}
    def fam(h):
        if not isinstance(h, dict): return None
        return {k: h.get(k) for k in ('family', 'grado', 'peso_relativo', 'porcentaje_relleno') if k in h}
    ap = res.get('apuesta') if isinstance(res.get('apuesta'), dict) else {}
    si = res.get('salida_interpretable') if isinstance(res.get('salida_interpretable'), dict) else {}
    h1 = res.get('H1') or {}; h2 = res.get('H2') or {}
    margen = None
    try: margen = round(float(h1.get('peso_relativo')) - float(h2.get('peso_relativo')), 6)
    except Exception: pass
    inp = d / '_INPUT.json'; out = d / '_PRIMARY_RESULT.json'
    return {
        'corrida': d.name, 'case_id': res.get('case_id'),
        'case_hash_input_sha256': sha_file(inp), 'output_sha256': sha_file(out),
        'fecha': datetime.fromtimestamp(out.stat().st_mtime).strftime('%Y-%m-%d') if out.is_file() else None,
        'version_motor': res.get('version'), 'hash_candado': res.get('hash_candado'), 'patterns_sha256': res.get('patterns_sha256'),
        'H1': fam(h1), 'H2': fam(h2),
        'apuesta': {'estado': ap.get('estado'), 'escenarios': [e.get('escenario') for e in ap.get('escenarios', []) if isinstance(e, dict)]},
        'grado': si.get('grado'), 'margen_H1_H2_peso_relativo': margen,
        'metricas': {'estado_final': res.get('estado_final'), 'grado_inverso_set': si.get('grado_inverso_set'),
                     'compuerta_cierre': (res.get('compuerta_cierre') or {}).get('estado_pre_compuerta') if isinstance(res.get('compuerta_cierre'), dict) else None},
    }

def tokens_corrida(d: Path) -> list[dict]:
    out = []
    for p in list(d.glob('stinkbox_tokens_descubiertos.json')) + list(d.rglob('STINKBOX_STORAGE/stinkbox_*.json')):
        obj = _cargar(p); h = sha_file(p)
        if not isinstance(obj, dict): continue
        toks = []
        if isinstance(obj.get('tokens'), list): toks = [x.get('token') for x in obj['tokens'] if isinstance(x, dict)]
        for k in (obj.get('coactivation') or {}): toks += k.split('|')
        for t in toks:
            t = re.sub(r'\s+', ' ', str(t or '').strip()).casefold()
            if t: out.append({'token': t, 'caso': obj.get('case_id') or d.name, 'sha256_corrida': h})
    return out

def anexar_tokens(repo: Path, nuevos: list[dict], fecha: str, destino: Path) -> int:
    reg = {}
    p = repo / 'stinkbox' / 'tokens.jsonl'
    if p.is_file():
        for line in p.read_text(encoding='utf-8').splitlines():
            if line.strip(): r = json.loads(line); reg[r['token']] = r
    vistos = set(); tocados = 0
    for n in nuevos:
        clave = (n['token'], n['caso'], n['sha256_corrida'])
        if clave in vistos: continue
        vistos.add(clave)
        r = reg.get(n['token'])
        prov = {'sha256_corrida': n['sha256_corrida'], 'fecha': fecha}
        if r is None:
            r = reg[n['token']] = {'token': n['token'], 'conteo': 0, 'eventos_evidencia': 0, 'estado': 'NUEVO', 'casos': [], 'fuentes': [], 'ejes': [], 'procedencia': []}
        if prov in r['procedencia']: continue  # misma corrida ya contada
        r['conteo'] += 1; r['eventos_evidencia'] += 1; r['procedencia'].append(prov)
        if n['caso'] not in r['casos']: r['casos'].append(n['caso'])
        if len(r['casos']) > 1 and r['estado'] == 'NUEVO': r['estado'] = 'RECURRENTE'
        tocados += 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(''.join(json.dumps(reg[t], ensure_ascii=False) + '\n' for t in sorted(reg)), encoding='utf-8')
    return tocados

def despues(repo: Path, corrida: Path, modelo: str):
    res = resumen_corrida(corrida); res['modelo'] = modelo
    fecha = res['fecha'] or datetime.now().strftime('%Y-%m-%d')
    # dedupe de resumen por (case hash, output hash)
    rpath = repo / 'casos' / 'resultados' / 'resultados.jsonl'
    previos = rpath.read_text(encoding='utf-8').splitlines() if rpath.is_file() else []
    ya = any((json.loads(l).get('case_hash_input_sha256'), json.loads(l).get('output_sha256')) == (res['case_hash_input_sha256'], res['output_sha256']) for l in previos if l.strip())
    toks = tokens_corrida(corrida)
    puede_push = es_git(repo) and git(repo, 'ls-remote', 'origin', 'HEAD').returncode == 0
    if puede_push:
        n = anexar_tokens(repo, toks, fecha, repo / 'stinkbox' / 'tokens.jsonl')
        if not ya:
            rpath.parent.mkdir(parents=True, exist_ok=True)
            with rpath.open('a', encoding='utf-8') as f: f.write(json.dumps(res, ensure_ascii=False) + '\n')
        git(repo, 'add', *PERMITIDOS_PUSH)
        staged = git(repo, 'diff', '--cached', '--name-only').stdout.split()
        if any(s not in PERMITIDOS_PUSH for s in staged):
            print('ABORTO: hay cambios fuera de stinkbox/tokens.jsonl y casos/resultados/. No se sube motor ni catalogo.'); sys.exit(3)
        if staged:
            git(repo, 'commit', '-m', f'[{modelo}] corrida {corrida.name}: resumen + {n} observaciones StinkBox', check=True)
            r = git(repo, 'push')
            print('push OK' if r.returncode == 0 else 'push fallo: ' + r.stderr.strip())
            print('Recuerda registrar la entrada en avances/ si hubo cambios de codigo.')
        else: print('Nada nuevo que subir.')
    else:
        pend = repo / '_pendiente_subir'; pend.mkdir(exist_ok=True)
        tag = f'{fecha}_{corrida.name}'
        with (pend / f'stinkbox_parche_{tag}.jsonl').open('w', encoding='utf-8') as f:
            for t in toks: f.write(json.dumps({**t, 'fecha': fecha}, ensure_ascii=False) + '\n')
        if not ya:
            (pend / f'resultado_{tag}.jsonl').write_text(json.dumps(res, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'Sin credenciales/red: parches locales en {pend} (subir despues).')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('accion', choices=['antes', 'despues', 'resumen'])
    ap.add_argument('--repo', default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument('--corrida'); ap.add_argument('--modelo', default='DESCONOCIDO')
    a = ap.parse_args(); repo = Path(a.repo).resolve()
    if a.accion == 'antes': antes(repo)
    elif a.accion == 'resumen': print(json.dumps(resumen_corrida(Path(a.corrida)), ensure_ascii=False, indent=1))
    else:
        if not a.corrida: sys.exit('--corrida es obligatorio')
        despues(repo, Path(a.corrida).resolve(), a.modelo)

if __name__ == '__main__': main()
