#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dialectica.py — Lateral: DIALÉCTICA HEGELIANA (A + B = C, C es una nueva A).

Pedido de Mj (2026-11-13 ~02:41 CST): generar el elemento que es el
equivalente de la dialéctica hegeliana — A más B igual a C, lo cual es
una nueva A que podría ser otra vez A más B igual a C. Y la forma de
uso: que el que no haya algo no significa que no se pueda conseguir a
través de un proceso dialéctico. Tenemos esto (A), tenemos esto en
contra (B), ¿cómo hacemos su síntesis (C)? Es el "cómo hacemos que sí
se pueda": no lo tengo directamente calibrado ni cableado para esto,
pero puedo usar su análogo para que se resuelva.

EL CONTRATO (V1_20261113) — en palabras y en fórmula:

Vocabulario (ya está en el catálogo 244, no se inventa nada):
  dialectica_01_tesis_estabilidad_hegemonica
    favor: autoridad, tradicionalismo, rutina, control
    contra: disrupción, insubordinación
  dialectica_02_antitesis_contradiccion_y_conflicto
    favor: conflictividad, ira_institucional, opresión, insubordinación,
           confrontación, oposición
    contra: paz_interior, reconciliación, estabilidad_absoluta, consenso
  dialectica_03_sintesis_superacion_estructural
    favor: comprensión_nueva, resolución, transformación, paz_interior
    contra: estancamiento, monotonía

El catálogo ya entrelaza las tres: "insubordinación" es contra de la
tesis y favor de la antítesis (el mismo token cambia de bando);
"paz_interior" es contra de la antítesis y favor de la síntesis (lo
que resuelve el conflicto es la síntesis). La dialéctica ya vive en
el vocabulario; lo que faltaba era el MECANISMO que la corre.

Sea t un token, c un corte, T(c) sus tokens (P/A/C), F(t) sus familias
favor, y S = favor(dialectica_03) los tokens de síntesis.

1. TRIADA en un corte c:
   A(c) = T(c) ∩ favor(dialectica_01)   (la tesis: lo que sostiene)
   B(c) = T(c) ∩ favor(dialectica_02)   (la antítesis: lo que se opone)
   C(c) = T(c) ∩ favor(dialectica_03)   (la síntesis ya presente)
   Hay triada completa ⇔ A(c) y B(c) no vacíos.

2. SÍNTESIS desde A y B (cuando C(c) está vacía o hay que resolver):
   Un token de síntesis s es ALCANZABLE desde A∪B por dos rutas del
   catálogo: (a) comparte una familia (que no sea una dialectica) con
   algún token de A∪B, o es vecino de Caldero de A∪B; (b) s está en
   contra(dialectica_02) y hay antítesis real — la única intersección
   contra(antítesis) ∩ favor(síntesis) es paz_interior: la resolución
   estructural del conflicto.
   C = {s ∈ S : s alcanzable desde A∪B}, en orden del catálogo.
   Vía "alcance_directo" si C no vacío.
   Si C vacío: C = la SÍNTESIS POR ANÁLOGO — la familia activa que
   más tokens favor comparte con la familia que falta (ver 4), y sus
   tokens de síntesis si los tiene. Vía "analogo".

3. CICLO entre cortes (C es una nueva A):
   A(c+1) = triada(c+1).tesis ∪ C(c)   (la síntesis del corte anterior
   entra como tesis del siguiente: la síntesis se vuelve tesis).
   Punto fijo: si C(c+1) == C(c), el ciclo se estabiliza (la síntesis
   ya no cambia: la dialéctica llegó a su síntesis).
   El ciclo corre hasta 3 vueltas por corte o hasta punto fijo.

4. RESOLVER LO QUE FALTA (el "cómo hacemos que sí se pueda"):
   resolver_falta(falta, estado): falta es una familia o un token que
   no está activo/calibrado/cableado para esto. El análogo es la
   familia ACTIVA (presente en el estado: el conjunto de hipótesis
   del RESULT o las familias de los tokens del corte) que más tokens
   favor comparte con falta (solape de favor). El análogo es lo que
   se usa para que se resuelva: no es la cosa misma, es su equivalente
   funcional — lo que se le parece y hace la función.

QUÉ MIDE ESTE LATERAL QUE NADA EXISTENTE MIDA (navaja de Ockham):
la vinculación mide transiciones (hacia dónde se desplaza la
trayectoria); la rueda mide mezcla (dos cosas en una); el décimo
hombre mide supervivencia adversarial; analogos_fase mide fase→
arquetipo. Ninguno mide LA RESOLUCIÓN DE UNA CONTRADICCIÓN EN UNA
SÍNTESIS QUE SE VUELVE NUEVA TESIS, ni el análogo que resuelve lo
que falta. Eso mide este lateral.

No decide H. No toca Engine ni catálogo. Solo lee el catálogo y la
entrada/RESULT. can_decide_H = False.
"""

import json
from pathlib import Path

DIALECTICA_FAMS = (
    "dialectica_01_tesis_estabilidad_hegemonica",
    "dialectica_02_antitesis_contradiccion_y_conflicto",
    "dialectica_03_sintesis_superacion_estructural",
)
MAX_VUELTAS = 3


def _norm(t):
    return str(t or "").strip().casefold()


def cargar_patrones(ruta=None):
    """Lee el catálogo (patterns_final_v14.json) como lo lee el motor."""
    if ruta is None:
        here = Path(__file__).resolve()
        # El módulo vive en <root>/motor/laterales/dialectica_hegeliana/;
        # el catálogo está en <root>/motor/motor/patterns_final_v14.json.
        # No usar cwd: el corredor cambia de directorio durante la corrida.
        for cand in (
            here.parent.parent.parent / "motor" / "patterns_final_v14.json",
            here.parent.parent / "motor" / "patterns_final_v14.json",
            here.parent.parent.parent / "patterns_final_v14.json",
        ):
            if cand.exists():
                ruta = cand
                break
    if ruta is None:
        raise FileNotFoundError("patterns_final_v14.json no encontrado")
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def _favor(patrones, fam):
    spec = patrones.get(fam) or {}
    return {_norm(t) for t in (spec.get("tokens_favor") or {}).keys()}


def _contra(patrones, fam):
    spec = patrones.get(fam) or {}
    return {_norm(t) for t in (spec.get("tokens_contra") or {}).keys()}


def _familias_de_token(patrones, token):
    """Familias (favor y contra) que contienen al token."""
    t = _norm(token)
    fav, con = set(), set()
    for fam, spec in patrones.items():
        if not isinstance(spec, dict):
            continue
        if t in {_norm(x) for x in (spec.get("tokens_favor") or {}).keys()}:
            fav.add(fam)
        if t in {_norm(x) for x in (spec.get("tokens_contra") or {}).keys()}:
            con.add(fam)
    return fav, con


def triada(tokens_corte, patrones):
    """Clasifica los tokens de un corte en tesis / antítesis / síntesis."""
    toks = {_norm(t) for t in (tokens_corte or []) if str(t).strip()}
    a = sorted(toks & _favor(patrones, DIALECTICA_FAMS[0]))
    b = sorted(toks & _favor(patrones, DIALECTICA_FAMS[1]))
    c = sorted(toks & _favor(patrones, DIALECTICA_FAMS[2]))
    return {
        "tesis": a,
        "antitesis": b,
        "sintesis_presente": c,
        "triada_completa": bool(a and b),
    }


def _alcanzables(desde, patrones, vecinos=None):
    """Tokens de síntesis alcanzables desde un conjunto de tokens.

    Dos rutas (las dos están en el catálogo, no se inventan):
    (a) familia_compartida: s comparte una familia (que no sea una
        dialectica) con algún token de `desde`.
    (b) resolucion_contra: s está en contra(dialectica_02) — es lo que
        la antítesis niega — y `desde` trae antítesis real. La única
        intersección contra(antítesis) ∩ favor(síntesis) es
        paz_interior: la resolución estructural del conflicto.
    """
    sintesis_favor = _favor(patrones, DIALECTICA_FAMS[2])
    # familias (favor) de cada token de `desde`, sin las dialectica
    fams_desde = set()
    for t in desde:
        fav, _ = _familias_de_token(patrones, t)
        fams_desde |= {f for f in fav if f not in DIALECTICA_FAMS}
    out = set()
    for s in sintesis_favor:
        fav_s, _ = _familias_de_token(patrones, s)
        if (fav_s & fams_desde) - set(DIALECTICA_FAMS):
            out.add(s)
    # (b) la antítesis trae su propia resolución: lo que niega es la síntesis
    antitesis_favor = _favor(patrones, DIALECTICA_FAMS[1])
    if set(desde) & antitesis_favor:
        out |= (sintesis_favor & _contra(patrones, DIALECTICA_FAMS[1]))
    if vecinos:
        vec = {_norm(v) for v in vecinos}
        out |= (sintesis_favor & vec)
    return sorted(out)


def sintesis_desde(a_tokens, b_tokens, patrones, vecinos=None, estado_familias=None):
    """A + B = C. Devuelve la síntesis y por qué vía llegó."""
    a = {_norm(t) for t in (a_tokens or []) if str(t).strip()}
    b = {_norm(t) for t in (b_tokens or []) if str(t).strip()}
    desde = a | b
    c = _alcanzables(desde, patrones, vecinos=vecinos)
    if c:
        return {"sintesis": c, "via": "alcance_directo", "analogo": None}
    # Sin alcance directo: síntesis por análogo (la familia activa que
    # más se le parece a lo que falta: ver resolver_falta).
    if estado_familias:
        analog = resolver_falta(
            DIALECTICA_FAMS[2], estado_familias, patrones,
            activas=set(estado_familias),
        )
        if analog.get("analogo"):
            s_fav = sorted(_favor(patrones, analog["analogo"]) & _favor(patrones, DIALECTICA_FAMS[2]))
            return {"sintesis": s_fav, "via": "analogo", "analogo": analog["analogo"]}
    return {"sintesis": [], "via": "sin_sintesis", "analogo": None}


def resolver_falta(falta, estado, patrones, activas=None):
    """El 'cómo hacemos que sí se pueda' para algo que falta.

    falta: familia o token que no está activo/calibrado/cableado.
    estado: familias activas (conjunto de hipótesis del RESULT) o, si
    no hay RESULT, las familias de los tokens del corte.
    Devuelve el análogo: la familia activa que más tokens favor
    comparte con falta, y con qué tokens se parece.
    """
    f = _norm(falta)
    # favor de lo que falta: si es familia, sus favor; si es token,
    # el favor de las familias que lo contienen como favor.
    if f in {_norm(k) for k in patrones.keys()}:
        fam_real = next(k for k in patrones.keys() if _norm(k) == f)
        favor_falta = _favor(patrones, fam_real)
    else:
        fav_fams, _ = _familias_de_token(patrones, f)
        favor_falta = set()
        for fam in fav_fams:
            favor_falta |= _favor(patrones, fam)
    if not favor_falta:
        return {"falta": str(falta), "analogo": None, "solape": 0,
                "tokens_compartidos": [], "como_se_puede": ""}
    activas = set(activas) if activas is not None else set(estado or [])
    mejor, mejor_solape, mejor_tokens = None, 0, []
    for g in sorted(activas):
        if _norm(g) == f:
            continue
        fav_g = _favor(patrones, g)
        if not fav_g:
            continue
        compartidos = sorted(favor_falta & fav_g)
        if len(compartidos) > mejor_solape:
            mejor, mejor_solape, mejor_tokens = g, len(compartidos), compartidos
    if not mejor:
        return {"falta": str(falta), "analogo": None, "solape": 0,
                "tokens_compartidos": [], "como_se_puede": ""}
    return {
        "falta": str(falta),
        "analogo": mejor,
        "solape": mejor_solape,
        "tokens_compartidos": mejor_tokens,
        "como_se_puede": (
            f"se resuelve con {mejor} porque comparte "
            f"{', '.join(mejor_tokens)}"
        ),
    }


def ciclo(cortes, patrones, vecinos_por_corte=None, max_vueltas=MAX_VUELTAS):
    """Corre A+B=C corte a corte; la síntesis de un corte es tesis del siguiente.

    cortes: lista de (id, tokens) en orden. Devuelve la cadena por corte
    y si el ciclo llegó a punto fijo (la síntesis ya no cambia).
    """
    vecinos_por_corte = vecinos_por_corte or {}
    cadena = []
    acarreada = []  # síntesis del corte anterior -> tesis del siguiente
    for cid, toks in cortes:
        tr = triada(list(toks) + acarreada, patrones)
        a = tr["tesis"]
        b = tr["antitesis"]
        if tr["sintesis_presente"]:
            sint = {"sintesis": tr["sintesis_presente"], "via": "presente_en_corte", "analogo": None}
        else:
            sint = sintesis_desde(a, b, patrones, vecinos=vecinos_por_corte.get(cid))
        cadena.append({
            "corte": cid,
            "tesis": a,
            "antitesis": b,
            "sintesis": sint["sintesis"],
            "via_sintesis": sint["via"],
            "analogo": sint["analogo"],
            "triada_completa": tr["triada_completa"],
            "tesis_acarreada_de_anterior": list(acarreada),
        })
        acarreada = list(sint["sintesis"])
    # punto fijo: la síntesis se repite en dos cortes seguidos
    punto_fijo = None
    for i in range(1, len(cadena)):
        if cadena[i]["sintesis"] and cadena[i]["sintesis"] == cadena[i - 1]["sintesis"]:
            punto_fijo = cadena[i]["corte"]
            break
    return {
        "cadena": cadena,
        "punto_fijo_en": punto_fijo,
        "vueltas": min(len(cadena), max_vueltas) if cadena else 0,
        "can_decide_H": False,
    }


def sobre_entrada(entrada, patrones, vecinos_por_corte=None):
    """Corre el ciclo sobre una entrada (P/A/C por corte)."""
    cortes = []
    for raw in (entrada.get("cuts") or []):
        cid = str(raw.get("id") or raw.get("corte") or "")
        toks = []
        for axis in ("P", "A", "C"):
            toks.extend([
                str(p[0]) for p in (raw.get(axis) or [])
                if isinstance(p, (list, tuple)) and p and str(p[0]).strip()
            ])
        cortes.append((cid, toks))
    return ciclo(cortes, patrones, vecinos_por_corte=vecinos_por_corte)


def sobre_result(ruta_result, patrones=None):
    """Corre el ciclo sobre un RESULT sellado (busca su entrada por case_id)."""
    patrones = patrones or cargar_patrones()
    ruta = Path(ruta_result)
    r = json.loads(ruta.read_text(encoding="utf-8"))
    case_id = r.get("case_id")
    entrada = None
    if case_id:
        cand = ruta.parent.parent / "casos" / "precedentes" / str(case_id) / "entrada.json"
        if cand.is_file():
            entrada = json.loads(cand.read_text(encoding="utf-8"))
    if entrada is None:
        raise ValueError("no se encontró la entrada del RESULT (case_id=%s)" % (case_id,))
    res = sobre_entrada(entrada, patrones)
    # familias activas del RESULT (conjunto de hipótesis abiertas)
    hipotesis = (
        (r.get("salida_interpretable") or {})
        .get("conjunto_hipotesis_abiertas", {})
        .get("hipotesis", [])
    )
    res["familias_activas"] = [h.get("familia") for h in hipotesis if h.get("familia")]
    res["case_id"] = case_id
    res["can_decide_H"] = False
    return res


def run(ruta_result, out_dir):
    """Punto de entrada post-corrida (como teoria_color.run).

    Lee el RESULT y su entrada, corre el ciclo y escribe
    DIALECTICA_<nombre>.json y .md junto al RESULT. No decide H.
    """
    ruta = Path(ruta_result)
    out_dir = Path(out_dir)
    res = sobre_result(ruta)
    nombre = ruta.name.replace(".json", "")
    triadas = sum(1 for p in res["cadena"] if p["triada_completa"])
    sintesis_tot = sum(1 for p in res["cadena"] if p["sintesis"])
    artefacto = {
        "lateral": "dialectica_hegeliana",
        "contrato": "V1_20261113",
        "case_id": res.get("case_id"),
        "can_decide_H": False,
        "triadas_completas": triadas,
        "cortes_con_sintesis": sintesis_tot,
        "cortes": len(res["cadena"]),
        "punto_fijo_en": res.get("punto_fijo_en"),
        "cadena": res["cadena"],
    }
    out_json = out_dir / f"DIALECTICA_{nombre}.json"
    out_json.write_text(json.dumps(artefacto, ensure_ascii=False, indent=2), encoding="utf-8")
    lineas = [
        f"# Dialéctica hegeliana — {res.get('case_id')}",
        "",
        f"Triadas completas: {triadas} de {len(res['cadena'])} cortes. "
        f"Cortes con síntesis: {sintesis_tot}. "
        f"Punto fijo: {res.get('punto_fijo_en') or 'no llegó'}.",
        "",
    ]
    for p in res["cadena"]:
        lineas.append(
            f"- {p['corte']}: tesis {p['tesis'] or '—'}; "
            f"antítesis {p['antitesis'] or '—'}; "
            f"síntesis {p['sintesis'] or '—'} ({p['via_sintesis']})."
        )
    out_md = out_dir / f"DIALECTICA_{nombre}.md"
    out_md.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return {
        "triadas_completas": triadas,
        "cortes_con_sintesis": sintesis_tot,
        "cortes": len(res["cadena"]),
        "punto_fijo_en": res.get("punto_fijo_en"),
        "json": str(out_json),
        "md": str(out_md),
        "can_decide_H": False,
    }


__all__ = [
    "DIALECTICA_FAMS", "cargar_patrones", "triada", "sintesis_desde",
    "resolver_falta", "ciclo", "sobre_entrada", "sobre_result", "run",
]
