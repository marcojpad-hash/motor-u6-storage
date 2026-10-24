#!/usr/bin/env python3
"""[COPIA ADAPTADA para MOTOR_UNICO_20260927: el contrato se verifica sobre las 28 corridas UNICO (raw/RESULT_UNICO__*),
con 9 bloques (8 guardianes + TROPOS_BERISTAIN) y catálogo = el registrado en cada corrida. Resto verbatim.]
Pruebas nuevas: Copi (19 reglas + falacias espejo + NO_RESUELTO + cierre), clasificador de falacias
(batería original de 11 casos + batería natural de 5 falacias con negativos), acero rival y
contrato de los guardianes (H intacto, can_decide_H=false, patterns sin escribir)."""
from __future__ import annotations
import copy, hashlib, importlib, importlib.util, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "guardianes"; sys.path.insert(0, str(G))
RES = []
def ok(nombre, cond, det=""):
    RES.append((nombre, bool(cond))); print(f"  [{'PASS' if cond else 'FAIL'}] {nombre}" + (f" — {det}" if det else ""))

# ------------------------------------------------------------------ COPI
def test_copi():
    print("\n=== LOGICA_COPI ===")
    import guardian_logica_copi_v1 as c
    A, NOT, AND, OR, IMP, IFF = c.A, c.NOT, c.AND, c.OR, c.IMP, c.IFF
    P, Q, R, S = A("p"), A("q"), A("r"), A("s")
    inf = {"MP": ([IMP(P, Q), P], Q), "MT": ([IMP(P, Q), NOT(Q)], NOT(P)), "SH": ([IMP(P, Q), IMP(Q, R)], IMP(P, R)),
           "SD": ([OR(P, Q), NOT(P)], Q), "DC": ([AND(IMP(P, Q), IMP(R, S)), OR(P, R)], OR(Q, S)),
           "Abs": ([IMP(P, Q)], IMP(P, AND(P, Q))), "Simp": ([AND(P, Q)], P), "Conj": ([P, Q], AND(P, Q)), "Ad": ([P], OR(P, Q))}
    for n, (pr, co) in inf.items():
        e = c.evaluar_argumento(pr, co); ok(f"inferencia {n} VALIDO y reconocida", e["estado"] == "VALIDO" and n in e["regla_copi"], str(e["regla_copi"]))
    rep = {"DeMorgan": (NOT(AND(P, Q)), OR(NOT(P), NOT(Q))), "Conm": (OR(P, Q), OR(Q, P)), "Asoc": (OR(P, OR(Q, R)), OR(OR(P, Q), R)),
           "Dist": (AND(P, OR(Q, R)), OR(AND(P, Q), AND(P, R))), "DN": (P, NOT(NOT(P))), "Trans": (IMP(P, Q), IMP(NOT(Q), NOT(P))),
           "Impl": (IMP(P, Q), OR(NOT(P), Q)), "Equiv": (IFF(P, Q), AND(IMP(P, Q), IMP(Q, P))), "Exp": (IMP(AND(P, Q), R), IMP(P, IMP(Q, R))),
           "Taut": (P, OR(P, P))}
    for n, (x, y) in rep.items():
        e1 = c.evaluar_argumento([x], y); e2 = c.evaluar_argumento([y], x)
        ok(f"reemplazo {n} equivalente en ambos sentidos y reconocido", c.equivalentes(x, y) and e1["estado"] == e2["estado"] == "VALIDO" and n in e1["regla_copi"], str(e1["regla_copi"]))
    fal = {"AFIRMAR_EL_CONSECUENTE": ([IMP(P, Q), Q], P), "NEGAR_EL_ANTECEDENTE": ([IMP(P, Q), NOT(P)], NOT(Q)),
           "AFIRMAR_UN_DISYUNTO": ([OR(P, Q), P], NOT(Q)), "CONVERSION_ILICITA": ([IMP(P, Q)], IMP(Q, P)),
           "INVERSION_ILICITA": ([IMP(P, Q)], IMP(NOT(P), NOT(Q))), "DEMORGAN_MAL_APLICADO": ([NOT(AND(P, Q))], AND(NOT(P), NOT(Q))),
           "NEGAR_UN_CONJUNTO": ([NOT(AND(P, Q))], NOT(P))}
    for n, (pr, co) in fal.items():
        e = c.evaluar_argumento(pr, co)
        ok(f"falacia espejo {n} INVALIDO con contraejemplo", e["estado"] == "INVALIDO" and n in e["falacia_espejo"] and e["contraejemplo"], f"espejo_de={e['espejo_de']}")
    t = c.analizar_texto(["Si alguien es un líder nato, entonces funda empresas. Fundó empresas, así que es un líder nato."])
    ok("texto: afirmar el consecuente detectado", any("AFIRMAR_EL_CONSECUENTE" in m["tipo"] for m in t["marcas"]), str([m["tipo"] for m in t["marcas"]]))
    t = c.analizar_texto(["Si invierte, entonces crece. Invirtió, así que crece."])
    ok("texto: modus ponens sin marca", not [m for m in t["marcas"] if m["estado"] == "DETECTADA"], str([m["tipo"] for m in t["marcas"]]))
    t = c.analizar_texto(["Si llueve, entonces la calle se moja. Llueve, así que el suelo está húmedo."])
    ok("texto: átomo sin frontera clara → NO_RESUELTO (no afirma falacia)", any(m["estado"] == "NO_RESUELTO" for m in t["marcas"]) and not any(m["estado"] == "DETECTADA" for m in t["marcas"]),
       str([(m["tipo"], m["estado"]) for m in t["marcas"]]))
    t = c.analizar_texto(["El proyecto fracasó porque faltó dinero.", "Faltó dinero porque el proyecto fracasó."])
    ok("texto: causales extraídas", len(t["causales"]) == 2, str([x["forma"] for x in t["causales"]]))
    # cierre del motor: estado DETERMINADO con hechos que no cumplen el antecedente debe marcarse
    pred = {"information_state": {"state": "DETERMINADO"}, "candidates": [{"family": "a", "rank_fusion": 10.0}, {"family": "b", "rank_fusion": 9.9}]}
    r = c.analizar_cierre(pred)
    ok("cierre: función devuelve evaluación Copi", "evaluacion" in r and r["evaluacion"]["estado"] in ("VALIDO", "INVALIDO"), r["evaluacion"]["estado"] if "evaluacion" in r else str(r)[:120])

# ------------------------------------------------------------------ FALACIAS
ORIG11 = [("AF+", "Si hay umbral, hay ruptura. Hubo ruptura; por tanto la causa era el umbral.", ["AF_AFIRMAR_CONSECUENTE"]),
          ("AF-", "Si hay umbral, hay ruptura. Hubo ruptura; eso NO prueba que la causa fuera el umbral.", []),
          ("AD+", "Si llueve, la calle se moja. Como no llovió, entonces no puede estar mojada.", ["AD_NEGAR_ANTECEDENTE"]),
          ("CS+", "Al mismo tiempo subió el índice; por eso provocó la crisis.", ["CS_CUM_HOC"]),
          ("BC1+", "El éxito equivale a ambición: si es ambicioso, entonces triunfa, si y solo si.", ["BC1_BICONDICIONAL_INCOMPLETO"]),
          ("BC2+", "El capital es necesario, o sea basta / es suficiente para ganar.", ["BC2_NECESARIO_SUFICIENTE"]),
          ("PQ+", "Sabemos que era un traidor. ¿Cuándo empezó a traicionar?", ["PQ_PETITIO"]),
          ("EQ+", "El pueblo quiere poder; por tanto el poder del pueblo demuestra la causa.", ["EQ_EQUIVOCACION"]),
          ("PH+", "κ cayó en C6, por eso ya sabíamos que iba a haber ruptura", ["POST_HOC_TEMPORAL"]),
          ("clean", "¿Qué papel tuvo la caída de kappa en C6?", []),
          ("ambicioso_attr", "El hombre ambicioso lideró el grupo.", [])]
# Batería natural de 5 falacias (+ negativos). Las frases originales de la batería del agente PERFIL
# no quedaron guardadas (solo su resultado: 1/5, BC1); se reconstruye con frases biográficas naturales.
NAT5 = [("AF", "Si alguien es un líder nato, funda empresas. Fundó una empresa, así que es un líder nato.", "AF_AFIRMAR_CONSECUENTE"),
        ("CS", "Cada vez que cambiaba de ciudad le iba mejor; mudarse causó su éxito.", "CS_CUM_HOC"),
        ("PQ", "¿Por qué siempre traicionaba a sus socios?", "PQ_PETITIO"),
        ("PH", "Después de que lo despidieron de Apple, eso provocó su regreso triunfal.", "POST_HOC_TEMPORAL"),
        ("BC1", "El éxito equivale a ambición: si es ambicioso, entonces triunfa, si y solo si.", "BC1_BICONDICIONAL_INCOMPLETO")]
EXTRA_POS = [("AD", "Si hubiera estudiado, habría triunfado. No estudió, por lo tanto no triunfó.", "AD_NEGAR_ANTECEDENTE"),
             ("CIRC", "Es confiable porque dice la verdad, y dice la verdad porque es confiable.", "PQ_PETITIO")]
NEG = [("NEG", "Lo despidieron en 1985 y después volvió, pero el despido no provocó su regreso."),
       ("MP", "Si invierte, crece. Invirtió, así que creció."), ("MT", "Si hubiera quebrado, habría cerrado. No cerró, por lo tanto no quebró."),
       ("HECHO", "Fundó la empresa en 1976 con dos socios."), ("PREG", "¿Por qué fundó la empresa en 1976?")]
PFX = ("AF_", "AD_", "CS_", "BC", "PQ_", "EQ_", "POST_")
def _tipos(m, t): return {h.tipo for h in m.detectar_falacias(t)} | {h.tipo for h in m.detectar_post_hoc(t)}
def test_falacias():
    baseline = ROOT / "rescate/plugin_pregunta_dirigida__SB_0_5_0_19f59a1d.py"
    if not baseline.is_file():
        import pytest
        pytest.skip("No se recuperó el código original 0.5.0; no se inventa la línea base de comparación")
    print("\n=== FALACIAS (clasificador 0.5.1 vs base 0.5.0) ===")
    new = importlib.import_module("plugin_pregunta_dirigida_v0_5_1")
    spec = importlib.util.spec_from_file_location("pd050", baseline)
    old = importlib.util.module_from_spec(spec); sys.modules["pd050"] = old; spec.loader.exec_module(old)
    for n, t, exp in ORIG11:
        ty = _tipos(new, t)
        good = all(e in ty for e in exp) if exp else not any(x.startswith(PFX) for x in ty)
        ok(f"batería original 11 · {n}", good, str(sorted(ty)))
    n_old = sum(1 for _, t, e in NAT5 if e in _tipos(old, t)); n_new = sum(1 for _, t, e in NAT5 if e in _tipos(new, t))
    print(f"  (batería natural 5: base 0.5.0 detecta {n_old}/5; 0.5.1 detecta {n_new}/5)")
    for n, t, e in NAT5 + EXTRA_POS:
        ok(f"natural · {n} detectada", e in _tipos(new, t), str(sorted(_tipos(new, t))))
    for n, t in NEG:
        ty = _tipos(new, t); ok(f"negativo · {n} sin falacia", not any(x.startswith(PFX) for x in ty), str(sorted(ty)))
    ok("batería natural 5/5 en 0.5.1", n_new == 5, f"0.5.0={n_old}/5")
    return n_old, n_new

# ------------------------------------------------------------------ ACERO
def _pred(vals):
    dims = ["d1", "d2", "d3", "d4"]
    cands = [{"family": f, "features": dict(zip(dims, v))} for f, v in vals]
    return {"dimensions": dims, "candidates": cands}
def test_acero():
    print("\n=== HOMBRE DE ACERO (rival) ===")
    import guardian_acero_rival_v1 as a
    base = [("c%d" % i, [0.1 * i, 0.05 * i, 0.02 * i, 0.3]) for i in range(1, 9)]
    fuerte = _pred([("top", [9, 9, 9, 9]), ("riv", [1, 1, 1, 1])] + base)
    r = a.acero_rival(fuerte, rivales_max=1); ok("top1 dominante SOBREVIVE", r["pruebas"][0]["veredicto_top1"] == "SOBREVIVE", str(r["pruebas"][0]["dif_acero"]))
    pegado = _pred([("top", [1.00, 1.00, 1.00, 1.00]), ("riv", [0.99, 0.99, 0.99, 0.99])] + base)
    r = a.acero_rival(pegado, rivales_max=1); ok("rival a menos de la banda de empate en todo → top1 no gana (NO_RESUELTO/CAE)", r["pruebas"][0]["veredicto_top1"] in ("NO_RESUELTO", "CAE"), str(r["pruebas"][0]))
    cae = _pred([("top", [1.0, 1.0, 1.0, 0.0]), ("riv", [0.99, 0.99, 0.99, 5.0])] + base)
    r = a.acero_rival(cae, rivales_max=1); ok("rival con empates a favor y ventaja propia → CAE", r["pruebas"][0]["veredicto_top1"] == "CAE", str(r["pruebas"][0]["dif_acero"]))
    ok("no reordena candidatos (solo mide)", [c["family"] for c in cae["candidates"]][:2] == ["top", "riv"])
    ok("sensibilidad de pilar reportada aparte", "sensibilidad_pilar" in r["pruebas"][0])
    ok("NO_APLICA con <2 candidatos", a.acero_rival({"dimensions": ["d1"], "candidates": [{"family": "x", "features": {"d1": 1}}]})["estado"] == "NO_APLICA")

# ------------------------------------------------------------------ CONTRATO
def test_contrato_sobre_corridas():
    print("\n=== CONTRATO DE GUARDIANES sobre las 28 corridas GUARDIANES ===")
    raws = sorted((ROOT / "raw").glob("RESULT_UNICO__*__r[12].json"))
    ok("hay 28 corridas", len(raws) == 28, str(len(raws)))
    pat = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"
    malos = []
    for f in raws:
        d = json.loads(f.read_text()); g = d["guardianes"]; v = g["verificacion_H_intacto"]
        c1 = g.get("can_decide_H") is False and all(b.get("can_decide_H") is False for b in g["bloques"])
        c2 = v["predictor_igual"] and v["H1_H2_igual"] and v["patterns_igual"] and v["patterns_sha256_despues"] == pat
        c3 = len(g["bloques"]) == 9 and all(b["bandera"] in ("LIMPIO", "MARCA", "NO_RESUELTO", "LATENTE") for b in g["bloques"])
        c4 = all(k in b for b in g["bloques"] for k in ("guardian", "reviso", "marcas", "bandera"))
        if not (c1 and c2 and c3 and c4): malos.append((f.name, c1, c2, c3, c4))
    ok("can_decide_H=false, H/predictor/patterns intactos, 9 bloques trazables sin ERROR", not malos, str(malos[:3]))

def test_contrato_sintetico():
    raw_fixture = ROOT / "raw" / "RESULT_UNICO__BEZOS__PREFIX__r1.json"
    input_fixture = ROOT / "runs" / "UNICO__BEZOS__PREFIX__r1" / "_INPUT.json"
    if not raw_fixture.is_file() or not input_fixture.is_file():
        import pytest
        pytest.skip("Fixture histórico Bezos no está en el paquete; no se sustituye por datos inventados")
    print("\n=== CONTRATO: el orquestador no muta sus entradas ===")
    import guardianes_control_v1 as gc
    run = ROOT / "runs" / "UNICO__BEZOS__PREFIX__r1"
    d = json.loads((ROOT / "raw" / "RESULT_UNICO__BEZOS__PREFIX__r1.json").read_text())
    case = json.loads((run / "_INPUT.json").read_text())
    motor, pred = d["motor"], d["predictor"]
    h = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True, default=str).encode()).hexdigest()
    before = (h(case), h(motor), h(pred))
    out = gc.correr_guardianes(case, motor, pred, run)
    ok("case/motor/pred iguales tras correr guardianes", before == (h(case), h(motor), h(pred)))
    ok("salida declara can_decide_H=false", out.get("can_decide_H") is False)
    ok("no escribe H1/H2 en su salida", "H1" not in out and "H2" not in out)

if __name__ == "__main__":
    test_copi(); nat = test_falacias(); test_acero(); test_contrato_sobre_corridas(); test_contrato_sintetico()
    n = sum(1 for _, x in RES if x); print(f"\n=== RESUMEN {n}/{len(RES)} PASS ===")
    (ROOT / "tests" / "RESULTADO_test_nuevos_guardianes.json").write_text(json.dumps({"pass": n, "total": len(RES), "falacias_natural5_base_050_vs_051": nat,
        "detalle": [{"prueba": a, "ok": b} for a, b in RES]}, ensure_ascii=False, indent=1))
    raise SystemExit(0 if n == len(RES) else 1)
