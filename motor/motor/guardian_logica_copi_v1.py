#!/usr/bin/env python3
"""guardian_logica_copi_v1.py — CANDADO DE CONSISTENCIA LÓGICA (Copi) · 2026-09-27

Por qué existe: se buscó código de Copi en disco, en todos los zips (también anidados),
en los transcripts del box y en Notion. Solo había especificación
(SPEC_SIDECARS_FALACIAS_Y_COPI.txt 20c48e5d, TABLERO_BERISTAIN_COPI_FALACIAS 5522cdad
"VIVO hoy: 0"; sidecar_trazabilidad_temporal devuelve copi=None). Este módulo es la
primera implementación en código, escrita desde la fuente (Copi, Introducción a la lógica):

  9 reglas de inferencia : MP, MT, SH, SD, DC, Abs, Simp, Conj, Ad   (+ DD como extra)
  10 reglas de reemplazo : De Morgan, Conm, Asoc, Dist, DN, Trans, Impl, Equiv, Exp, Taut

Nota sobre la lista de Mj ("MP, MT, SH, SD, DC, Simp, Conj, Ad, CD"): DC y CD son el mismo
Dilema Constructivo; la novena regla de Copi es la Absorción (Abs). Se implementan ambas
lecturas: Abs como novena y el Dilema Destructivo (DD) como extra.

Qué hace:
  - Núcleo proposicional exacto (tablas de verdad) para decidir validez y dar contraejemplo.
  - Identifica qué regla de Copi (inferencia o reemplazo) corresponde a un paso.
  - Falacias espejo: afirmar el consecuente, negar el antecedente, afirmar un disyunto,
    conversión ilícita, inversión ilícita, De Morgan mal aplicado, negar un conjunto.
  - Adaptadores: (a) afirmaciones condicionales/causales del texto de entrada;
    (b) la regla de cierre del motor (DETERMINADO / LATENCIA) sobre la corrida;
    (c) la cadena del top1 por corte (non sequitur, subdeterminación H1/H2).
  - NO_RESUELTO cuando no hay frontera clara (átomos que no se pueden emparejar).

Candados: control estructural siempre-on; can_decide_H=False; no escribe H ni patterns.
"""
from __future__ import annotations

import itertools
import re
import unicodedata
from typing import Any, Dict, List, Optional, Sequence, Tuple

VERSION = "1.0.1-20260927"
GUARDIAN = "LOGICA_COPI"

# ---------------------------------------------------------------- núcleo proposicional
F = tuple  # ('atom',name) | ('not',f) | ('and',f,g) | ('or',f,g) | ('imp',f,g) | ('iff',f,g)


def A(n): return ('atom', n)
def NOT(f): return ('not', f)
def AND(f, g): return ('and', f, g)
def OR(f, g): return ('or', f, g)
def IMP(f, g): return ('imp', f, g)
def IFF(f, g): return ('iff', f, g)


def atomos(f, acc=None):
    acc = set() if acc is None else acc
    if f[0] == 'atom':
        acc.add(f[1])
    else:
        for x in f[1:]:
            atomos(x, acc)
    return acc


def evaluar(f, env):
    op = f[0]
    if op == 'atom': return env[f[1]]
    if op == 'not': return not evaluar(f[1], env)
    a, b = evaluar(f[1], env), evaluar(f[2], env)
    if op == 'and': return a and b
    if op == 'or': return a or b
    if op == 'imp': return (not a) or b
    if op == 'iff': return a == b
    raise ValueError(op)


def valido(premisas: Sequence[F], conclusion: F) -> Tuple[bool, Optional[Dict[str, bool]]]:
    ats = set()
    for p in list(premisas) + [conclusion]:
        atomos(p, ats)
    ats = sorted(ats)
    if len(ats) > 14:
        raise ValueError("demasiados átomos para tabla de verdad")
    for vals in itertools.product([True, False], repeat=len(ats)):
        env = dict(zip(ats, vals))
        if all(evaluar(p, env) for p in premisas) and not evaluar(conclusion, env):
            return False, env
    return True, None


def equivalentes(f, g) -> bool:
    return valido([f], g)[0] and valido([g], f)[0]


def consistente(formulas: Sequence[F]) -> Tuple[bool, Optional[Dict[str, bool]]]:
    ats = sorted(set().union(*[atomos(f) for f in formulas])) if formulas else []
    for vals in itertools.product([True, False], repeat=len(ats)):
        env = dict(zip(ats, vals))
        if all(evaluar(f, env) for f in formulas):
            return True, env
    return False, None


def a_texto(f) -> str:
    op = f[0]
    if op == 'atom': return f[1]
    if op == 'not': return '¬' + a_texto(f[1])
    sym = {'and': '∧', 'or': '∨', 'imp': '→', 'iff': '↔'}[op]
    return f"({a_texto(f[1])} {sym} {a_texto(f[2])})"


# ---------------------------------------------------------------- esquemas (metavariables p,q,r,s)
p, q, r, s = A('?p'), A('?q'), A('?r'), A('?s')

REGLAS_INFERENCIA = {
    "MP":   ([IMP(p, q), p], q),
    "MT":   ([IMP(p, q), NOT(q)], NOT(p)),
    "SH":   ([IMP(p, q), IMP(q, r)], IMP(p, r)),
    "SD":   ([OR(p, q), NOT(p)], q),
    "DC":   ([AND(IMP(p, q), IMP(r, s)), OR(p, r)], OR(q, s)),
    "Abs":  ([IMP(p, q)], IMP(p, AND(p, q))),
    "Simp": ([AND(p, q)], p),
    "Conj": ([p, q], AND(p, q)),
    "Ad":   ([p], OR(p, q)),
    "DD_extra": ([AND(IMP(p, q), IMP(r, s)), OR(NOT(q), NOT(s))], OR(NOT(p), NOT(r))),
}
REGLAS_REEMPLAZO = {
    "DeMorgan": [(NOT(AND(p, q)), OR(NOT(p), NOT(q))), (NOT(OR(p, q)), AND(NOT(p), NOT(q)))],
    "Conm":     [(OR(p, q), OR(q, p)), (AND(p, q), AND(q, p))],
    "Asoc":     [(OR(p, OR(q, r)), OR(OR(p, q), r)), (AND(p, AND(q, r)), AND(AND(p, q), r))],
    "Dist":     [(AND(p, OR(q, r)), OR(AND(p, q), AND(p, r))), (OR(p, AND(q, r)), AND(OR(p, q), OR(p, r)))],
    "DN":       [(p, NOT(NOT(p)))],
    "Trans":    [(IMP(p, q), IMP(NOT(q), NOT(p)))],
    "Impl":     [(IMP(p, q), OR(NOT(p), q))],
    "Equiv":    [(IFF(p, q), AND(IMP(p, q), IMP(q, p))), (IFF(p, q), OR(AND(p, q), AND(NOT(p), NOT(q))))],
    "Exp":      [(IMP(AND(p, q), r), IMP(p, IMP(q, r)))],
    "Taut":     [(p, OR(p, p)), (p, AND(p, p))],
}
FALACIAS_ESPEJO = {
    "AFIRMAR_EL_CONSECUENTE":  ([IMP(p, q), q], p),
    "NEGAR_EL_ANTECEDENTE":    ([IMP(p, q), NOT(p)], NOT(q)),
    "AFIRMAR_UN_DISYUNTO":     ([OR(p, q), p], NOT(q)),
    "CONVERSION_ILICITA":      ([IMP(p, q)], IMP(q, p)),
    "INVERSION_ILICITA":       ([IMP(p, q)], IMP(NOT(p), NOT(q))),
    "DEMORGAN_MAL_APLICADO":   ([NOT(AND(p, q))], AND(NOT(p), NOT(q))),
    "NEGAR_UN_CONJUNTO":       ([NOT(AND(p, q))], NOT(p)),
}
ESPEJO_DE = {"AFIRMAR_EL_CONSECUENTE": "MP", "NEGAR_EL_ANTECEDENTE": "MT", "AFIRMAR_UN_DISYUNTO": "SD",
             "CONVERSION_ILICITA": "Trans", "INVERSION_ILICITA": "Trans", "DEMORGAN_MAL_APLICADO": "DeMorgan",
             "NEGAR_UN_CONJUNTO": "Simp"}


def _unificar(esq, f, b):
    if esq[0] == 'atom' and esq[1].startswith('?'):
        if esq[1] in b:
            return b if b[esq[1]] == f else None
        nb = dict(b); nb[esq[1]] = f
        return nb
    if esq[0] != f[0] or len(esq) != len(f):
        return None
    if esq[0] == 'atom':
        return b if esq[1] == f[1] else None
    for e, x in zip(esq[1:], f[1:]):
        b = _unificar(e, x, b)
        if b is None:
            return None
    return b


def _encaja(esq_prem, esq_concl, premisas, conclusion) -> bool:
    if len(esq_prem) != len(premisas):
        return False
    for perm in itertools.permutations(premisas):
        b: Optional[dict] = {}
        for e, x in zip(esq_prem, perm):
            b = _unificar(e, x, b)
            if b is None:
                break
        if b is not None and _unificar(esq_concl, conclusion, b) is not None:
            return True
    return False


def identificar(premisas: Sequence[F], conclusion: F) -> Dict[str, List[str]]:
    reglas = [n for n, (ep, ec) in REGLAS_INFERENCIA.items() if _encaja(ep, ec, list(premisas), conclusion)]
    reemplazo = []
    if len(premisas) == 1:
        for n, pares in REGLAS_REEMPLAZO.items():
            for x, y in pares:
                if _encaja([x], y, list(premisas), conclusion) or _encaja([y], x, list(premisas), conclusion):
                    reemplazo.append(n); break
    falacias = [n for n, (ep, ec) in FALACIAS_ESPEJO.items() if _encaja(ep, ec, list(premisas), conclusion)]
    return {"inferencia": reglas, "reemplazo": reemplazo, "falacia_espejo": falacias}


def evaluar_argumento(premisas: Sequence[F], conclusion: F) -> Dict[str, Any]:
    ok, contra = valido(premisas, conclusion)
    ids = identificar(premisas, conclusion)
    if ok:
        estado = "VALIDO"
    else:
        estado = "INVALIDO"
    return {"estado": estado, "premisas": [a_texto(x) for x in premisas], "conclusion": a_texto(conclusion),
            "regla_copi": ids["inferencia"] + ids["reemplazo"] if ok else [],
            "derivable_por_tabla": ok and not (ids["inferencia"] or ids["reemplazo"]),
            "falacia_espejo": ids["falacia_espejo"] if not ok else [],
            "espejo_de": [ESPEJO_DE[f] for f in ids["falacia_espejo"]] if not ok else [],
            "contraejemplo": contra}


# ---------------------------------------------------------------- (a) texto de entrada
_STOP = set("""el la los las un una unos unas de del al a en y o u que se su sus lo le les es son fue era ser
esta este esto eso ese esa con por para como mas muy ya tambien pero sino si no ni the a an of to in and or
is are was were be it he she they his her its that this so then if not""".split())
_NEG = re.compile(r"\b(?:no|nunca|jamas|tampoco|not|never|nadie|ningun\w*)\b")
_COND = re.compile(r"^\s*(?:si|if)\s+(?P<a>.+?)(?:\s*,\s*(?:entonces|then)?\s*|\s+(?:entonces|then)\s+)(?P<b>.+)$", re.I | re.S)
_CONCL = re.compile(r"(?:,|;|\.)?\s*\b(?:as[ií]\s+que|por\s+lo\s+tanto|por\s+tanto|luego|por\s+eso|en\s+consecuencia|"
                    r"de\s+modo\s+que|ergo|so|therefore|hence|thus)\b\s*,?\s*", re.I)
_CAUSAL = re.compile(r"(?P<efecto>[^.;]+?)\s+\b(?:porque|debido\s+a|a\s+causa\s+de|because(?:\s+of)?)\b\s+(?P<causa>[^.;]+)", re.I)
_CAUSAL2 = re.compile(r"(?P<causa>[^.;]+?)\s+\b(?:caus[oó]|provoc[oó]|llev[oó]\s+a|hizo\s+que|caused|led\s+to)\b\s+(?P<efecto>[^.;]+)", re.I)


def _norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c)).lower()).strip()


def _raices(t):
    return frozenset(w[:3] for w in re.findall(r"[a-zñ]+", _norm(t)) if len(w) >= 3 and w not in _STOP)


class _Atomizador:
    """Empareja frases con átomos por raíces compartidas. Si una frase queda a medio
    camino entre dos átomos, se marca como ambigua (frontera no clara → NO_RESUELTO)."""

    def __init__(self):
        self.atomos: List[Tuple[str, frozenset, str]] = []
        self.ambiguas: List[str] = []

    def lit(self, frase: str) -> F:
        neg = bool(_NEG.search(_norm(frase)))
        rs = _raices(frase)
        best, best_sc, second = None, 0.0, 0.0
        for nombre, r0, _ in self.atomos:
            if not rs or not r0:
                continue
            sc = len(rs & r0) / max(1, min(len(rs), len(r0)))
            if sc > best_sc:
                second, best_sc, best = best_sc, sc, nombre
            elif sc > second:
                second = sc
        if best is not None and best_sc >= 0.5:
            if second >= 0.5 and second == best_sc:
                self.ambiguas.append(frase)
            f = A(best)
        else:
            nombre = f"p{len(self.atomos) + 1}"
            self.atomos.append((nombre, rs, frase.strip()[:80]))
            f = A(nombre)
        return NOT(f) if neg else f

    def glosario(self):
        return {n: t for n, _, t in self.atomos}


def _oraciones(texto):
    return [x.strip() for x in re.split(r"(?<=[.?!])\s+|\n+", texto or "") if x.strip()]


def analizar_texto(textos: Sequence[str]) -> Dict[str, Any]:
    """Extrae condicionales y causales del texto y evalúa cada inferencia marcada."""
    argumentos, causales, marcas = [], [], []
    at = _Atomizador()
    afirmaciones: List[F] = []
    for texto in textos:
        ors = _oraciones(texto)
        for i, o in enumerate(ors):
            m = _COND.match(o.rstrip(".;"))
            if m:
                ante, cons = at.lit(m.group("a")), at.lit(m.group("b").strip(" .;"))
                prem_cond = IMP(ante, cons)
                afirmaciones.append(prem_cond)
                resto = " ".join(ors[i + 1:i + 3])
                mc = _CONCL.search(resto) if resto else None
                if mc:
                    menor = re.sub(r"^(?:como|dado\s+que|puesto\s+que|since|as)\s+", "", resto[:mc.start()].strip(" ,;."), flags=re.I)
                    concl = resto[mc.end():].strip(" ,;.")
                    if menor and concl:
                        fm, fc = at.lit(menor), at.lit(concl)
                        ev = evaluar_argumento([prem_cond, fm], fc)
                        ev["atomos_nuevos_en_conclusion"] = sorted(atomos(fc) - atomos(prem_cond) - atomos(fm))
                        ev["fragmento"] = (o + " " + resto)[:220]
                        argumentos.append(ev)
                continue
            for rx in (_CAUSAL, _CAUSAL2):
                mm = rx.search(o)
                if mm:
                    c, e = at.lit(mm.group("causa")), at.lit(mm.group("efecto"))
                    causales.append({"causa": a_texto(c), "efecto": a_texto(e), "forma": a_texto(IMP(c, e)), "fragmento": o[:200]})
                    afirmaciones.append(IMP(c, e))
                    break
    cons_ok, _ = consistente(afirmaciones) if afirmaciones else (True, None)
    for ev in argumentos:
        if ev["estado"] == "INVALIDO" and ev.get("atomos_nuevos_en_conclusion"):
            # la conclusión habla de algo que no está en las premisas: puede ser paráfrasis
            # (calle mojada / suelo húmedo) o salto real. Sin frontera clara → NO_RESUELTO.
            marcas.append({"tipo": "NO_RESUELTO_CONCLUSION_CON_ATOMO_NUEVO", "evidencia": ev["fragmento"], "estado": "NO_RESUELTO"})
            continue
        if ev["estado"] == "INVALIDO":
            marcas.append({"tipo": "FALACIA_ESPEJO:" + ("/".join(ev["falacia_espejo"]) or "FORMA_INVALIDA"),
                           "evidencia": ev["fragmento"], "estado": "DETECTADA"})
    if not cons_ok:
        marcas.append({"tipo": "AFIRMACIONES_INCONSISTENTES", "evidencia": [a_texto(x) for x in afirmaciones], "estado": "DETECTADA"})
    for fr in at.ambiguas:
        marcas.append({"tipo": "NO_RESUELTO_ATOMO_AMBIGUO", "evidencia": fr[:160], "estado": "NO_RESUELTO"})
    return {"argumentos": argumentos, "causales": causales, "consistentes": cons_ok,
            "glosario_atomos": at.glosario(), "marcas": marcas}


# ---------------------------------------------------------------- (b) regla de cierre del motor
def analizar_cierre(pred: Dict[str, Any], sep_umbral: float = 1.0) -> Dict[str, Any]:
    info = pred.get("information_state") or {}
    gate = pred.get("compuerta_cierre") or {}
    hechos = {
        "sig": bool(info.get("new_vector_signal")),
        "res": bool(info.get("resolution_exhausted")),
        "sep": float(info.get("top_margin") or 0.0) >= sep_umbral,
        "rep": int(info.get("top_neighbor_support") or 0) >= 2,
        "pos": float(info.get("top_margin") or 0.0) > 0.0,
        "blq": gate.get("decision") == "CIERRE_BLOQUEADO_LATENCIA",
    }
    ante = AND(AND(A("sig"), A("res")), OR(A("sep"), AND(A("rep"), A("pos"))))
    D = A("D")
    lits = [A(k) if v else NOT(A(k)) for k, v in hechos.items()]
    estado = info.get("state")
    reglas = {"suficiencia (código)": IMP(AND(ante, NOT(A("blq"))), D),
              "necesidad ('cerrar solo si')": IMP(D, ante),
              "compuerta": IMP(A("blq"), NOT(D))}
    prem = list(reglas.values()) + lits
    concl = D if estado == "DETERMINADO" else NOT(D)
    ev = evaluar_argumento(prem, concl)
    cons, _ = consistente(prem + [concl])
    # paso nombrado de Copi para explicar la derivación
    if estado == "DETERMINADO":
        paso = "Conj/Ad sobre hechos → antecedente; MP con la regla de suficiencia → D"
    elif hechos["blq"]:
        paso = "MP con la regla de la compuerta → ¬D"
    else:
        paso = "MT con la regla de necesidad ('cerrar solo si') y ¬antecedente → ¬D (sin 'solo si' sería negar el antecedente)"
    marcas = []
    if ev["estado"] != "VALIDO" or not cons:
        marcas.append({"tipo": "CIERRE_NO_SE_DERIVA_DE_SUS_PREMISAS", "evidencia": {"estado": estado, "hechos": hechos}, "estado": "DETECTADA"})
    return {"hechos": hechos, "estado_motor": estado, "conclusion": a_texto(concl),
            "reglas": {k: a_texto(v) for k, v in reglas.items()}, "evaluacion": ev, "paso_copi": paso,
            "bicondicional_completo": True, "marcas": marcas}


# ---------------------------------------------------------------- (c) cadena del top1
def analizar_cadena(motor: Dict[str, Any], pred: Dict[str, Any]) -> Dict[str, Any]:
    cuts = motor.get("cuts") or []
    cadena = [((c.get("P_top5_ANEXO") or [[None]])[0][0]) for c in cuts]
    cands = pred.get("candidates") or []
    top1 = cands[0]["family"] if cands else None
    rival = cands[1]["family"] if len(cands) > 1 else None
    margen = (cands[0]["rank_fusion"] - cands[1]["rank_fusion"]) if len(cands) > 1 else None
    vistos = lambda fam: sum(1 for c in cuts if fam in {x.get("familia") for x in (c.get("P_candidatos_0a3") or [])})
    v1, v2 = (vistos(top1) if top1 else 0), (vistos(rival) if rival else 0)
    marcas = []
    if top1 and top1 not in cadena:
        marcas.append({"tipo": "NO_RESUELTO_TOP1_NO_ES_TOP_DE_NINGUN_CORTE",
                       "evidencia": {"top1": top1, "cadena_top1": cadena}, "estado": "NO_RESUELTO"})
    if rival and margen is not None and margen < 1.0 and v2 >= v1:
        marcas.append({"tipo": "NO_RESUELTO_SUBDETERMINACION_H1_H2",
                       "evidencia": {"top1": top1, "rival": rival, "margen": round(margen, 6), "cortes_con_top1": v1, "cortes_con_rival": v2},
                       "estado": "NO_RESUELTO"})
    return {"cadena_top1": cadena, "top1_final": top1, "rival": rival,
            "tipo_inferencia_H": "ABDUCTIVA (mejor explicación): Copi no la valida ni la invalida; se revisan non sequitur y subdeterminación",
            "cortes_con_top1": v1, "cortes_con_rival": v2, "marcas": marcas}


def guardian(textos: Sequence[str], motor: Dict[str, Any], pred: Dict[str, Any]) -> Dict[str, Any]:
    t = analizar_texto(textos)
    c = analizar_cierre(pred)
    k = analizar_cadena(motor, pred)
    marcas = t["marcas"] + c["marcas"] + k["marcas"]
    bandera = "MARCA" if any(m["estado"] == "DETECTADA" for m in marcas) else ("NO_RESUELTO" if marcas else "LIMPIO")
    return {"texto": t, "cierre_motor": c, "cadena_top1": k, "marcas": marcas, "bandera": bandera,
            "n_revisados": {"textos": len(textos), "argumentos_texto": len(t["argumentos"]), "causales_texto": len(t["causales"]),
                            "cortes_cadena": len(k["cadena_top1"])}}
