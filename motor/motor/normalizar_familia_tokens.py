#!/usr/bin/env python3
"""Normalizador agnostico de familias de tokens laterales.
Acepta el JSON que entregue cualquier modelo (Gemini, GPT, Claude...) y lo deja
en formato lateral canonico (estilo Dynamis). No toca Engine ni patterns 244.
Uso: python3 normalizar_familia_tokens.py entrada.json [--fuente Gemini] [--out dir]
"""
import json, re, sys, hashlib, unicodedata, argparse
from pathlib import Path

# Sombrero blanco: terminos cargados -> equivalentes estructurales neutros
SOMBRERO_BLANCO = {
  "espacio_vital": "espacio_hegemonico", "paranoia": "alarma", "destruccion_mutua": "costo_inaceptable",
  "nuclear": "disuasivo", "guerra": "conflicto", "armas": "capacidades", "arma": "capacidad",
  "violencia": "coercion", "masacre": "ruptura_grave", "genocidio": "ruptura_grave", "exterminio": "ruptura_grave",
  "asesinato": "eliminacion_rival", "sacrificio_humano": "exclusion_ritual", "linchamiento": "exclusion_colectiva",
  "terror": "intimidacion", "bomba": "detonante", "invasion": "irrupcion", "deslegitimacion": "mutua", "violenta": "coercitiva", "violento": "coercitivo", "purgas": "cierre", "purga": "cierre", "pompis": "formalismo",
}
# vocabulario interno del proyecto que un modelo externo no deberia traer
CONTAGIO = ["guardrail","sigma","delta_multiplier","atricion","stinkbox","dynamis","motor","h_apuesta"]
PESO_MIN, PESO_MAX = 0.50, 0.95

def slug(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+","_",s).strip("_")
    parts = s.split("_"); out=[]
    for p in parts:                     # quita palabra repetida contigua (fuerza_fuerza)
        if not out or out[-1]!=p: out.append(p)
    return "_".join(out)

def neutral(tok, log):
    t = "_" + tok + "_"
    for k,v in sorted(SOMBRERO_BLANCO.items(), key=lambda kv:-len(kv[0])):
        t = t.replace("_"+k+"_", "_"+v+"_")      # solo palabras completas (alarma != arma)
    t = slug(t)
    return t

def peso(v, signo, tok, log):
    try: x = abs(float(v))
    except Exception: log.append(f"peso invalido en {tok}: {v!r} -> 0.70"); x = 0.70
    if x > 1.0: x = x/100 if x <= 100 else 0.95
    y = min(max(x, PESO_MIN), PESO_MAX)
    if abs(y-x) > 1e-9: log.append(f"peso recortado {tok}: {x} -> {y}")
    return round(signo*y, 3)

def buscar(d, *claves):
    for k in claves:
        for kk in d:
            if slug(kk) == k: return d[kk]
    return None

def normalizar(raw, fuente):
    log, flags = [], []
    if isinstance(raw, dict) and len(raw)==1 and isinstance(next(iter(raw.values())), dict) \
       and "tokens_favor" in next(iter(raw.values())):
        fid, raw = next(iter(raw.items())); raw = dict(raw, id=raw.get("id", fid))
    fav = buscar(raw,"tokens_favor","favor","pro") or {}
    con = buscar(raw,"tokens_contra","contra","anti") or {}
    sen = buscar(raw,"senales","senales_observables","signals") or {}
    if isinstance(fav, list): fav = {t:0.7 for t in fav}
    if isinstance(con, list): con = {t:-0.7 for t in con}
    out_f, out_c, out_s, ren = {}, {}, {}, {}
    for src, dst, sg in ((fav,out_f,1),(con,out_c,-1)):
        for t,v in src.items():
            nt = neutral(slug(t), log); ren[t]=nt
            if nt != t: log.append(f"renombre: {t} -> {nt}")
            try:
                if (float(v) < 0 and sg>0) or (float(v) > 0 and sg<0):
                    flags.append(f"POLARIDAD_SIGNO_INCONSISTENTE:{nt}")
            except Exception: pass
            if nt in dst: log.append(f"duplicado fusionado: {t}")
            dst[nt] = peso(v, sg, nt, log)
            if any(c in nt for c in CONTAGIO): flags.append(f"CONTAGIO_VOCAB:{nt}")
    for t,txt in (sen.items() if isinstance(sen, dict) else []):
        out_s[ren.get(t, neutral(slug(t), log))] = str(txt)
    todos = set(out_f)|set(out_c)
    for t in todos - set(out_s): flags.append(f"SIN_SENAL:{t}")
    for t in set(out_f)&set(out_c): flags.append(f"EN_AMBOS_LADOS:{t}")
    for k in ("matriz_acoplamiento_dinamico","dynamic_couplings","acoplamientos","umbrales"):
        v = buscar(raw, slug(k))
        if v: log.append(f"acoplamientos con numeros removidos ({k}); quedan NOT_HARDCODED")
    nc = [neutral(slug(x), log) if isinstance(x,str) else x for x in (buscar(raw,"no_canonico") or [])]
    if len(out_f) < 5 or len(out_c) < 5: flags.append("POCOS_TOKENS(<5 por lado)")
    fid = slug(raw.get("id") or "familia_sin_id")
    body = {
      "id": fid, "status": "LATERAL_NORMALIZADO_PENDIENTE_CORRIDAS", "source": fuente,
      "fuente_teorica": raw.get("fuente_teorica") or raw.get("description") or "",
      "canonical_244": False, "role": "lateral_token_family",
      "tokens_favor": out_f, "tokens_contra": out_c, "senales": out_s,
      "no_canonico_declarado_por_fuente": nc,
      "dynamic_couplings": {"todos": "NOT_HARDCODED_PENDING_VALIDATION"},
      "puente_244": "PENDIENTE (sin puente la familia queda cableada pero muda)",
      "integration": {"feeds_predictor": True, "feeds_H": True, "can_decide_H": False,
                      "no_va_a_patterns_json": True, "persistent_via": "stinkbox_vault"},
      "revision": {"flags": sorted(set(flags)), "log": log,
                   "nota": "flags = senal, no se cierran aqui; se validan en corridas"},
    }
    body["sha256_tokens"] = hashlib.sha256(json.dumps([out_f,out_c],sort_keys=True).encode()).hexdigest()[:16]
    return body

def extraer_json(texto):
    i = texto.find("{"); 
    if i < 0: raise ValueError("no hay JSON")
    prof=0
    for j,ch in enumerate(texto[i:], i):
        prof += ch=="{"; prof -= ch=="}"
        if prof==0: return json.loads(texto[i:j+1])
    raise ValueError("JSON incompleto")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("entrada"); ap.add_argument("--fuente", default="externo")
    ap.add_argument("--out", default="normalizados"); a = ap.parse_args()
    raw = extraer_json(Path(a.entrada).read_text(encoding="utf-8"))  # tolera texto alrededor
    b = normalizar(raw, a.fuente)
    Path(a.out).mkdir(exist_ok=True); p = Path(a.out)/f"{b['id']}.json"
    p.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    print(p, "| flags:", len(b["revision"]["flags"]), "| cambios:", len(b["revision"]["log"]))
