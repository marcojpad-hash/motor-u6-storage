#!/usr/bin/env python3
"""Test del puente de Schrödinger V0_1 (sintético, sin datos externos).

Verifica: costo() no negativo y penaliza el cruce de eje; sinkhorn() devuelve
un plan con las marginales correctas y converge; memento_inversa() respeta el
orden y rechaza órdenes inválidos; transportar_trayectoria() sobre cortes
sintéticos con oscilación transversal reduce la oscilación (TV y amplitud);
con <3 cortes devuelve SIN_TRAYECTORIA sin romper.
Uso: python3 motor/tests/test_schrodinger_v0_1.py  (exit 0 = PASS)
"""
import math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "motor"))
import schrodinger_transport_v0_1 as sch


def test_costo():
    ctx = {"polaridad": {"a": 0.2, "b": -0.2, "c": 0.2},
           "tusi": {"a": 0.0, "b": 0.0, "c": 0.0},
           "exceso_t": {"a": 0.1, "b": 0.1, "c": 0.1},
           "exceso_t1": {"a": 0.1, "b": 0.1, "c": 0.1}}
    c_mismo = sch.costo("a", "c", ctx)   # misma polaridad (+,+)
    c_cruce = sch.costo("a", "b", ctx)   # cruce de eje (+,-)
    assert c_mismo >= 0.0 and c_cruce >= 0.0, (c_mismo, c_cruce)
    assert c_cruce > c_mismo, "el cruce de eje debe costar más que el mismo lado"
    assert sch.costo("a", "a", ctx) == 0.0, "costo(i,i) con igual activación debe ser 0"
    print("costo OK (mismo=%.4f cruce=%.4f)" % (c_mismo, c_cruce))


def test_sinkhorn():
    import numpy as np
    mu = np.array([0.5, 0.3, 0.2])
    nu = np.array([0.2, 0.5, 0.3])
    C = np.array([[0.0, 0.1, 0.2], [0.1, 0.0, 0.1], [0.2, 0.1, 0.0]])
    P, info = sch.sinkhorn(mu, nu, C, 0.05)
    assert info["convergio"], info
    assert abs(P.sum(axis=1).sum() - 1.0) < 1e-9
    assert max(abs(P.sum(axis=1) - mu).max(), abs(P.sum(axis=0) - nu).max()) < 1e-6
    assert (P >= 0).all()
    print("sinkhorn OK (it=%d err=%.2e costo=%.4f)" % (info["iteraciones"], info["error_marginal"], info["costo_total"]))


def test_memento():
    r = sch.memento_inversa({"P": 3, "A": 0, "C": 0})
    assert r["orden"] == ["P", "A", "C"] and r["recuperado"] == {"P": 3, "A": 0, "C": 0}, r
    r2 = sch.memento_inversa({"P": 3}, orden=("C", "P"))
    assert r2["orden"] == ["C", "P"] and r2["faltantes"] == ["C"], r2
    try:
        sch.memento_inversa({"P": 1}, orden=("P", "P"))
        raise AssertionError("orden duplicado debe levantar ValueError")
    except ValueError:
        pass
    try:
        sch.memento_inversa({"P": 1}, orden=("X",))
        raise AssertionError("orden inválido debe levantar ValueError")
    except ValueError:
        pass
    print("memento_inversa OK")


def cortes_sinteticos():
    """6 cortes, 10 familias. 'sube' y 'baja' oscilan en oposición (la onda
    transversal); 'prog' sube monótona (el eje Tusi); el resto planas."""
    fams = ["sube", "baja", "prog"] + [f"plana{i}" for i in range(7)]
    cortes = []
    for t in range(6):
        osc = 0.2 if t % 2 == 0 else -0.2
        p = {"sube": 0.5 + osc, "baja": 0.5 - osc, "prog": 0.5 + 0.04 * t}
        p.update({f: 0.5 for f in fams[3:]})
        cortes.append({"corte": f"C{t+1}", "P_FULL_244": p})
    return cortes


def test_transporte():
    cortes = cortes_sinteticos()
    tr = sch.transportar_trayectoria(cortes)
    assert tr["estado"] == "TRANSPORTE_OK", tr
    osc = tr["oscilacion"]
    ta, td = osc["transversal_antes"]["variacion_total"], osc["transversal_despues"]["variacion_total"]
    aa, ad = osc["transversal_antes"]["amplitud_pico_valle"], osc["transversal_despues"]["amplitud_pico_valle"]
    assert td <= ta + 1e-9, (ta, td)
    assert ad <= aa + 1e-9, (aa, ad)
    assert td < ta, "la regularizada debe oscilar menos (TV)"
    for t in tr["transiciones"]:
        for lado, pl in t["planes"].items():
            assert pl["info"]["convergio"], (t, lado, pl["info"])
    print("transporte OK (TV %.4f -> %.4f, amplitud %.4f -> %.4f)" % (ta, td, aa, ad))


def test_pocos_cortes():
    tr = sch.transportar_trayectoria(cortes_sinteticos()[:2])
    assert tr["estado"] == "SIN_TRAYECTORIA", tr
    print("pocos cortes OK (SIN_TRAYECTORIA, no rompe)")


if __name__ == "__main__":
    test_costo()
    test_sinkhorn()
    test_memento()
    test_transporte()
    test_pocos_cortes()
    print("PASS test_schrodinger_v0_1")
