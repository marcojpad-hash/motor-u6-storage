#!/usr/bin/env python3
"""Prueba de coactivacion de escalas (LATERAL OPCIONAL, can_decide_H=False).
Dado un input de cortes (P/A/C con [token, peso]), enciende tokens laterales SOLO via PUENTE_244_FAMILIAS.json
y calcula, por corte y por dinamica, que escalas (micro/meso/macro) se encienden juntas.
No llama al motor, no toca el ranking, no escribe H, no modifica Engine ni patterns.

Uso:
  python3 coactivacion_escalas.py                      # corre los 7 casos FULL del diagnostico
  python3 coactivacion_escalas.py --input caso.json    # un caso cualquiera (lista 'cuts' o dict de cortes)
  --tiers alta,media (defecto) | alta | alta,media,baja ; --perm 2000
Reglas:
  - token lateral encendido en un corte: alguna de sus palabras puente (en los tiers elegidos) aparece en P, A o C del corte.
  - (D, escala) ENCENDIDA: >=1 token 'empuja' encendido y n_empuja >= n_frena en esa celda (conteo, sin pesos).
  - COACTIVACION: la misma D encendida en >=2 escalas en el mismo corte.
    * INDEPENDIENTE: al menos dos de esas escalas tienen cada una una palabra 'empuja' que no enciende a la otra.
    * TRIVIAL: todas las escalas se encienden con las mismas palabras (p.ej. 'escalada' enciende Karpman, Senge y Tucidides).
  - Nulos: P1 baraja la etiqueta de dinamica entre tokens D1..D8 (conserva escala, polaridad y puente);
           P2 baraja la etiqueta de escala entre tokens D1..D8. p = (1+#perm>=obs)/(1+N).
"""
import json, glob, os, sys, random, argparse, collections, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
DEF_INPUTS = "/workspace/CONSOLIDADO_DIAGNOSTICO_20260927/inputs"
DEF_PAT = "/workspace/COMPARATIVO_VERSIONES_EXPEDIENTE_20260927/runs/UNIF_V0_9_ORIG__G0924__FULL__r1/patterns_final_v14.json"
SHA_PATTERNS = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"
ESC = ("micro", "meso", "macro"); DS = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
SEED = 20260927

def cortes(case):
    c = case.get("cuts")
    if isinstance(c, dict): c = [dict(v, id=k) for k, v in c.items()]
    out = []
    for x in c or []:
        obs = {}
        for L in ("P", "A", "C"):
            for pair in x.get(L) or []:
                t = str(pair[0]); obs[t] = max(obs.get(t, 0.0), float(pair[1]))
        out.append((str(x.get("id")), obs))
    return out

def cargar_puente(tiers):
    p = json.load(open(HERE / "PUENTE_244_FAMILIAS.json", encoding="utf-8"))
    toks = []
    for t in p["tokens"]:
        words = set()
        for tier in tiers: words |= set(t["palabras_244"][tier])
        toks.append({"familia": t["familia"], "token": t["token"], "D": t["dinamica"], "E": t["escala"], "pol": t["polaridad"], "words": words})
    return toks

def analizar_corte(obs, toks, Dlab=None, Elab=None):
    cel = collections.defaultdict(lambda: {"empuja": {}, "frena": {}})
    for i, t in enumerate(toks):
        hit = sorted(t["words"] & set(obs))
        if not hit: continue
        D = Dlab[i] if Dlab else t["D"]; E = Elab[i] if Elab else t["E"]
        cel[(D, E)][t["pol"]][t["familia"] + ":" + t["token"]] = hit
    res = {}
    for D in DS + ["K0", "otra/propia"]:
        lit = {}
        for E in ESC:
            c = cel.get((D, E))
            if not c: continue
            ne, nf = len(c["empuja"]), len(c["frena"])
            if ne >= 1 and ne >= nf:
                lit[E] = {"n_empuja": ne, "n_frena": nf, "tokens_empuja": c["empuja"], "tokens_frena": c["frena"],
                          "palabras_empuja": sorted({w for ws in c["empuja"].values() for w in ws})}
        estado = "apagada"; indep = False
        if len(lit) == 1: estado = "una_escala"
        elif len(lit) >= 2:
            Es = list(lit)
            for a in range(len(Es)):
                for b in range(a + 1, len(Es)):
                    wa, wb = set(lit[Es[a]]["palabras_empuja"]), set(lit[Es[b]]["palabras_empuja"])
                    if wa - wb and wb - wa: indep = True
            estado = "coactivacion_independiente" if indep else "coactivacion_trivial"
        res[D] = {"escalas_encendidas": sorted(lit, key=ESC.index), "estado": estado, "detalle": lit}
    return res

def estadistico(casos, toks, Dlab=None, Elab=None):
    n_ind = n_triv = 0
    for _, cs in casos:
        for _, obs in cs:
            r = analizar_corte(obs, toks, Dlab, Elab)
            for D in DS:
                n_ind += r[D]["estado"] == "coactivacion_independiente"; n_triv += r[D]["estado"] == "coactivacion_trivial"
    return n_ind, n_triv

def lente_constancia(casos, toks, pats):
    """Imita la lente por candidato del motor: palabras propias del patron del candidato ∩ observadas en los 3 ultimos cortes."""
    out = {}
    own = {pn: set(pv.get("tokens_favor", {})) | set(pv.get("tokens_contra", {})) for pn, pv in pats.items()}
    fams = sorted({t["familia"] for t in toks})
    for name, cs in casos:
        recent = set().union(*[set(o) for _, o in cs[-3:]])
        out[name] = {}
        for fam in fams:
            ft = [t for t in toks if t["familia"] == fam]
            sc = [sum(1 for t in ft if t["words"] & own[pn] & recent) for pn in pats]
            out[name][fam] = {"min": min(sc), "max": max(sc), "candidatos_con_senal": sum(1 for s in sc if s > 0),
                              "constante_guardia_la_saca": max(sc) == min(sc)}
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--input", action="append"); ap.add_argument("--tiers", default="alta,media")
    ap.add_argument("--perm", type=int, default=2000); ap.add_argument("--out", default=str(HERE / "COACTIVACION_RESULTADOS.json"))
    ap.add_argument("--patterns", default=DEF_PAT); a = ap.parse_args()
    tiers = a.tiers.split(","); toks = cargar_puente(tiers)
    files = a.input or sorted(glob.glob(os.path.join(DEF_INPUTS, "*_FULL.json")))
    casos = [(Path(f).stem, cortes(json.load(open(f, encoding="utf-8")))) for f in files]
    # control: el PREFIX es el FULL sin el corte retenido (no se corre dos veces)
    prefix_check = {}
    for f in files:
        pf = f.replace("_FULL.json", "_PREFIX.json")
        if pf != f and os.path.exists(pf):
            A = cortes(json.load(open(f))); B = cortes(json.load(open(pf)))
            prefix_check[Path(f).stem] = {"prefix_es_subconjunto_inicial": A[:len(B)] == B, "n_full": len(A), "n_prefix": len(B)}
    por_corte = []; resumen = collections.defaultdict(lambda: collections.Counter())
    for name, cs in casos:
        for cid, obs in cs:
            r = analizar_corte(obs, toks)
            por_corte.append({"caso": name, "corte": cid, "dinamicas": r})
            for D in DS + ["K0"]: resumen[D][r[D]["estado"]] += 1
    n_cortes = len(por_corte)
    obs_ind, obs_triv = estadistico(casos, toks)
    rng = random.Random(SEED)
    idxD = [i for i, t in enumerate(toks) if t["D"] in DS]
    perms = {}
    for tag in ("P1_baraja_dinamica", "P2_baraja_escala"):
        ge = 0; vals = []
        for _ in range(a.perm):
            Dlab = [t["D"] for t in toks]; Elab = [t["E"] for t in toks]
            lab = [Dlab[i] for i in idxD] if tag.startswith("P1") else [Elab[i] for i in idxD]
            rng.shuffle(lab)
            for j, i in enumerate(idxD):
                if tag.startswith("P1"): Dlab[i] = lab[j]
                else: Elab[i] = lab[j]
            v, _ = estadistico(casos, toks, Dlab, Elab); vals.append(v); ge += v >= obs_ind
        vals.sort()
        perms[tag] = {"n_perm": a.perm, "media_nula": round(sum(vals) / len(vals), 2), "p5": vals[int(.05 * len(vals))],
                      "p95": vals[int(.95 * len(vals)) - 1], "p_valor_una_cola": round((1 + ge) / (1 + a.perm), 4)}
    # tabla por dinamica x caso
    tabla = {}
    for D in DS + ["K0"]:
        tabla[D] = {}
        for name, _ in casos:
            xs = [pc for pc in por_corte if pc["caso"] == name]
            tabla[D][name] = {"cortes": len(xs), "encendida_alguna_escala": sum(pc["dinamicas"][D]["estado"] != "apagada" for pc in xs),
                              "coact_indep": sum(pc["dinamicas"][D]["estado"] == "coactivacion_independiente" for pc in xs),
                              "coact_trivial": sum(pc["dinamicas"][D]["estado"] == "coactivacion_trivial" for pc in xs)}
    # combinaciones de escalas por dinamica
    combos = {D: dict(collections.Counter("+".join(pc["dinamicas"][D]["escalas_encendidas"]) or "ninguna" for pc in por_corte)) for D in DS + ["K0"]}
    # tokens senalados por Mj (stasis, sobreextension, recriminacion, gogo)
    foco = ["stasis_fractura_civil_interna", "etapa_recriminacion_paralisis_politica", "fuga_talento_etapa_recriminacion",
            "sobreextension_imperial_logistica", "trampa_gogo_expansion_desenfocada", "etapa_gogo_crecimiento_acelerado",
            "crecimiento_con_subinversion_cuello", "urgencia_generatividad_estancamiento", "sobreproduccion_elites_competencia"]
    foco_out = {}
    for tk in foco:
        t = next(x for x in toks if x["token"] == tk)
        hits = [(n, cid, sorted(t["words"] & set(o))) for n, cs in casos for cid, o in cs if t["words"] & set(o)]
        foco_out[tk] = {"D": t["D"], "escala": t["E"], "palabras_puente": sorted(t["words"]), "cortes_encendido": len(hits), "donde": hits[:12]}
    lente = None
    if Path(a.patterns).exists() and hashlib.sha256(Path(a.patterns).read_bytes()).hexdigest() == SHA_PATTERNS:
        lente = lente_constancia(casos, toks, json.load(open(a.patterns)))
    out = {"version": "COACTIVACION_ESCALAS_20260927", "can_decide_H": False, "feeds_H": False, "toca_ranking": False,
           "tiers": tiers, "casos": [n for n, _ in casos], "n_cortes": n_cortes, "prefix_check": prefix_check,
           "resumen_estados_por_dinamica": {D: dict(v) for D, v in resumen.items()},
           "coactivacion_total": {"independiente": obs_ind, "trivial": obs_triv, "celdas_corte_x_dinamica": n_cortes * len(DS)},
           "nulos": perms, "tabla_dinamica_x_caso": tabla, "combinaciones_escalas": combos, "foco_mj": foco_out,
           "constancia_lente_por_candidato": lente, "por_corte": por_corte}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("tiers", "n_cortes", "coactivacion_total", "nulos", "resumen_estados_por_dinamica")}, ensure_ascii=False, indent=1))
if __name__ == "__main__": main()
