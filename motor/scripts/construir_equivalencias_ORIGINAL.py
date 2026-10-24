#!/usr/bin/env python3
"""Construye MATRIZ_EQUIVALENCIAS_ESCALA.json y PUENTE_244_FAMILIAS.json aplicando reglas_equivalencias.py.
Solo lee: familias normalizadas y patterns_final_v14.json (verifica sha d827dcc3...). No escribe nada fuera de esta carpeta.
Uso: python3 construir_equivalencias.py [--familias DIR] [--patterns RUTA]
"""
import json, hashlib, glob, argparse, os, sys, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reglas_equivalencias as R

SHA_PATTERNS = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"
DEF_FAM = "/workspace/TOKENS_GEMINI_FAMILIAS_20260927/normalizados"
DEF_PAT = "/workspace/COMPARATIVO_VERSIONES_EXPEDIENTE_20260927/runs/UNIF_V0_9_ORIG__G0924__FULL__r1/patterns_final_v14.json"
DEF_INPUTS = "/workspace/CONSOLIDADO_DIAGNOSTICO_20260927/inputs"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def cargar_patterns(p):
    s = sha(p)
    if s != SHA_PATTERNS: raise SystemExit(f"patterns sha incorrecto {s}")
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    assert len(d) == 244, len(d)
    return d, s

def dinamica(fam, tok):
    if fam == "kishotenketsu_estructura_giro": return "K0", "R0_control_kishotenketsu"
    if tok in R.EXCEPCIONES_DINAMICA:
        d, why = R.EXCEPCIONES_DINAMICA[tok]; return d, "EXCEPCION: " + why
    for rid, d, keys in R.REGLAS_DINAMICA:
        for k in keys:
            if k in tok: return d, f"{rid} (clave '{k}')"
    return "otra/propia", "R9_sin_coincidencia"

ORD = {"micro": 0, "meso": 1, "macro": 2}
def escala(fam, tok):
    base, why = R.ESCALA_FAMILIA[fam]
    for k in R.ESCALA_BAJA_MICRO:
        if k in tok: return "micro", f"E3 baja a micro (clave '{k}')"
    for lvl, keys in R.ESCALA_SUBE:
        for k in keys:
            if k in tok and ORD[lvl] > ORD[base]: return lvl, f"E2 sube a {lvl} (clave '{k}')"
    return base, f"E1 escala de la familia: {why}"

def polaridad(lado, tok):
    if tok in R.EXCEPCIONES_POLARIDAD:
        p, why = R.EXCEPCIONES_POLARIDAD[tok]; return p, "P2 EXCEPCION: " + why
    return ("empuja", "P1 tokens_favor") if lado == "favor" else ("frena", "P1 tokens_contra")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--familias", default=DEF_FAM); ap.add_argument("--patterns", default=DEF_PAT)
    ap.add_argument("--inputs", default=DEF_INPUTS); a = ap.parse_args()
    pats, psha = cargar_patterns(a.patterns)
    vocab = collections.defaultdict(set)   # palabra -> patrones que la tienen (favor o contra)
    for pn, pv in pats.items():
        for t in list(pv.get("tokens_favor", {})) + list(pv.get("tokens_contra", {})): vocab[t].add(pn)
    # vocabulario realmente usado en los inputs del diagnostico
    in_vocab = set()
    for f in sorted(glob.glob(os.path.join(a.inputs, "*_FULL.json"))):
        for c in json.load(open(f))["cuts"]:
            for L in "PAC":
                for t, w in c.get(L) or []: in_vocab.add(t)
    filas = []; fam_meta = {}
    for f in sorted(glob.glob(os.path.join(a.familias, "*.json"))):
        d = json.load(open(f, encoding="utf-8")); fam = d["id"]
        fam_meta[fam] = {"archivo": f, "sha256_archivo": sha(f), "fuente_teorica": d.get("fuente_teorica", ""),
                         "n_favor": len(d["tokens_favor"]), "n_contra": len(d["tokens_contra"]), "n_senales": len(d.get("senales") or {})}
        sen = d.get("senales") or {}
        fam_meta[fam]["senales_sin_token"] = sorted(set(sen) - set(d["tokens_favor"]) - set(d["tokens_contra"]))
        for lado, key in (("favor", "tokens_favor"), ("contra", "tokens_contra")):
            for tok, w in d[key].items():
                D, rd = dinamica(fam, tok); E, re_ = escala(fam, tok); P, rp = polaridad(lado, tok)
                filas.append({"familia": fam, "token": tok, "lado": lado, "peso_familia": w, "senal": sen.get(tok, ""),
                              "dinamica": D, "regla_dinamica": rd, "dinamica_secundaria_info": R.SECUNDARIA.get(tok),
                              "escala": E, "regla_escala": re_, "polaridad": P, "regla_polaridad": rp})
    # ---- tabla de huecos
    Ds = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
    huecos = {}
    for D in Ds + ["K0", "otra/propia"]:
        cel = {}
        for E in ("micro", "meso", "macro"):
            xs = [r for r in filas if r["dinamica"] == D and r["escala"] == E]
            cel[E] = {"total": len(xs), "empuja": sum(r["polaridad"] == "empuja" for r in xs), "frena": sum(r["polaridad"] == "frena" for r in xs),
                      "familias": sorted({r["familia"] for r in xs})}
        huecos[D] = {"celdas": cel, "escalas_sin_tokens": [E for E in cel if cel[E]["total"] == 0],
                     "escalas_sin_token_que_empuje": [E for E in cel if cel[E]["empuja"] == 0]}
    reglas_txt = {"dinamicas": R.DINAMICAS, "escala_familia": R.ESCALA_FAMILIA, "escala_sube": R.ESCALA_SUBE,
                  "escala_baja_micro": R.ESCALA_BAJA_MICRO, "reglas_dinamica_en_orden": R.REGLAS_DINAMICA,
                  "excepciones_dinamica": R.EXCEPCIONES_DINAMICA, "excepciones_polaridad": R.EXCEPCIONES_POLARIDAD,
                  "orden": "R0 (kishotenketsu->K0) > EXCEPCION > primera regla R* que coincide > R9 otra/propia; escala: E3 > E2 > E1; polaridad: P2 > P1"}
    cuenta_regla = collections.Counter(r["regla_dinamica"].split(" ")[0].rstrip(":") for r in filas)
    matriz = {"version": "EQUIVALENCIAS_ESCALA_20260927", "can_decide_H": False, "no_toca_canon": True,
              "patterns_sha256": psha, "familias": fam_meta, "n_tokens": len(filas),
              "asignacion_por_tipo_de_regla": dict(cuenta_regla), "reglas": reglas_txt, "tokens": filas, "huecos": huecos}
    (HERE / "MATRIZ_EQUIVALENCIAS_ESCALA.json").write_text(json.dumps(matriz, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- puente
    idx = {(r["familia"], r["token"]): r for r in filas}
    faltan_def = [t for (_, t) in idx if t not in R.PUENTE]
    sobran_def = [t for t in R.PUENTE if t not in {t for (_, t) in idx}]
    ptoks = []
    for (fam, tok), r in idx.items():
        spec = R.PUENTE.get(tok, {})
        palabras = {}; descartadas = []
        for tier in ("alta", "media", "baja"):
            ok = [w for w in spec.get(tier, []) if w in vocab]; descartadas += [w for w in spec.get(tier, []) if w not in vocab]
            palabras[tier] = ok
        pat_exp = [p for p in spec.get("patrones", []) if p in pats]
        pat_exp_mal = [p for p in spec.get("patrones", []) if p not in pats]
        am = palabras["alta"] + palabras["media"]
        pat_por_palabra = sorted({p for w in am for p in vocab[w]})
        pat_por_palabra_baja = sorted({p for w in palabras["baja"] for p in vocab[w]} - set(pat_por_palabra))
        conf = "alta" if (palabras["alta"] or pat_exp) else "media" if palabras["media"] else "baja" if palabras["baja"] else "sin_puente"
        ptoks.append({"familia": fam, "token": tok, "dinamica": r["dinamica"], "escala": r["escala"], "polaridad": r["polaridad"],
                      "confianza_max": conf, "palabras_244": palabras, "palabras_no_encontradas_en_244": descartadas,
                      "patrones_explicitos": pat_exp, "patrones_explicitos_no_encontrados": pat_exp_mal,
                      "patrones_por_palabra_alta_media": pat_por_palabra, "patrones_extra_por_palabra_baja": pat_por_palabra_baja,
                      "palabras_presentes_en_inputs_diagnostico": sorted(w for w in am + palabras["baja"] if w in in_vocab),
                      "base_documental": spec.get("base", "lista escrita en reglas_equivalencias.PUENTE")})
    cob = {}
    for fam in fam_meta:
        xs = [p for p in ptoks if p["familia"] == fam]; n = len(xs)
        con = [p for p in xs if p["confianza_max"] != "sin_puente"]
        am = [p for p in xs if p["confianza_max"] in ("alta", "media")]
        inp = [p for p in xs if p["palabras_presentes_en_inputs_diagnostico"]]
        cand_am = set(); cand_all = set()
        for p in xs:
            cand_am |= set(p["patrones_por_palabra_alta_media"]) | set(p["patrones_explicitos"])
            cand_all |= set(p["patrones_por_palabra_alta_media"]) | set(p["patrones_explicitos"]) | set(p["patrones_extra_por_palabra_baja"])
        cob[fam] = {"n_tokens": n, "con_puente_cualquier_confianza": len(con), "pct_con_puente": round(100 * len(con) / n, 1),
                    "con_puente_alta_o_media": len(am), "pct_alta_o_media": round(100 * len(am) / n, 1),
                    "con_palabra_presente_en_inputs": len(inp), "pct_presente_en_inputs": round(100 * len(inp) / n, 1),
                    "candidatos_244_tocados_alta_media": len(cand_am), "candidatos_244_tocados_con_baja": len(cand_all),
                    "constante_en_244": len(cand_am) == 244,
                    "sin_puente": [p["token"] for p in xs if p["confianza_max"] == "sin_puente"]}
    puente = {"version": "PUENTE_244_FAMILIAS_20260927", "can_decide_H": False, "patterns_sha256": psha,
              "criterio": {"alta": "misma raiz y mismo concepto, o patron 244 que nombra el mismo concepto",
                           "media": "sinonimo cercano de la lista escrita", "baja": "palabra relacionada pero amplia",
                           "sin_puente": "no hay palabra del 244 con base; se deja muda a proposito",
                           "pesos": "ninguno nuevo; el puente solo dice QUE palabra enciende QUE token"},
              "vocabulario_244_palabras": len(vocab), "vocabulario_inputs_diagnostico": len(in_vocab),
              "control_definiciones": {"tokens_sin_definicion_de_puente": faltan_def, "definiciones_sin_token": sobran_def},
              "cobertura_por_familia": cob, "tokens": sorted(ptoks, key=lambda p: (p["familia"], p["token"]))}
    (HERE / "PUENTE_244_FAMILIAS.json").write_text(json.dumps(puente, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"n_tokens": len(filas), "reglas": dict(cuenta_regla), "faltan_def": faltan_def, "sobran_def": sobran_def,
                      "descartadas": sorted({w for p in ptoks for w in p["palabras_no_encontradas_en_244"]}),
                      "patrones_mal": sorted({w for p in ptoks for w in p["patrones_explicitos_no_encontrados"]})}, ensure_ascii=False, indent=1))
if __name__ == "__main__": main()
