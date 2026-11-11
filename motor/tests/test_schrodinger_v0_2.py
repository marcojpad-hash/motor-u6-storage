#!/usr/bin/env python3
"""Test del puente de Schrödinger V0_2 (sintético, sin datos externos).

Verifica: sinkhorn_no_balanceado devuelve un plan con masa transportada
M <= 1 (destruye masa, no la crea) y converge; con rho grande recupera el
V0_1 (marginales duras); memento_inversa() es el mismo del V0_1;
transportar_trayectoria_v02() sobre cortes sintéticos con oscilación
transversal mueve la media hacia el eje (media|y| baja y TV baja más que el
V0_1); con <3 cortes devuelve SIN_TRAYECTORIA sin romper.
Uso: python3 motor/tests/test_schrodinger_v0_2.py  (exit 0 = PASS)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "motor"))
import schrodinger_transport_v0_1 as v01
import schrodinger_transport_v0_2 as v02


def test_sinkhorn_no_balanceado():
    import numpy as np
    mu = np.array([0.5, 0.3, 0.2])
    nu = np.array([0.2, 0.5, 0.3])
    C = np.array([[0.0, 0.1, 0.2], [0.1, 0.0, 0.1], [0.2, 0.1, 0.0]])
    # rho chico: el plan destruye masa (M < 1) y converge.
    P, info = v02.sinkhorn_no_balanceado(mu, nu, C, 0.05, 0.1)
    assert info["convergio"], info
    assert (P >= 0).all()
    assert 0.0 < info["masa_transportada"] <= 1.0 + 1e-9, info
    assert info["masa_transportada"] < 1.0, "con rho=0.1 el plan debe destruir algo de masa"
    assert info["penalizacion_kl"] >= 0.0
    print("sinkhorn_no_balanceado rho=0.1 OK (M=%.4f KL=%.4f it=%d)" % (
        info["masa_transportada"], info["penalizacion_kl"], info["iteraciones"]))
    # rho grande: recupera el balanceado (M -> 1, marginales -> mu/nu).
    P2, info2 = v02.sinkhorn_no_balanceado(mu, nu, C, 0.05, 100.0)
    assert info2["convergio"], info2
    assert abs(info2["masa_transportada"] - 1.0) < 1e-3, info2
    assert max(abs(P2.sum(axis=1) - mu).max(), abs(P2.sum(axis=0) - nu).max()) < 1e-3
    print("sinkhorn_no_balanceado rho=100 OK (M=%.4f, marginales casi exactas)" % info2["masa_transportada"])
    # rho chico destruye más masa que rho grande (monótono).
    P3, info3 = v02.sinkhorn_no_balanceado(mu, nu, C, 0.05, 0.02)
    assert info3["masa_transportada"] < info["masa_transportada"], (info3, info)
    print("monotonía rho OK (M rho=0.02 %.4f < M rho=0.1 %.4f)" % (
        info3["masa_transportada"], info["masa_transportada"]))


def test_memento():
    r = v02.memento_inversa({"P": 3, "A": 0, "C": 0})
    assert r["orden"] == ["P", "A", "C"] and r["recuperado"] == {"P": 3, "A": 0, "C": 0}, r
    print("memento_inversa OK (mismo que V0_1)")


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


def test_transporte_v02():
    cortes = cortes_sinteticos()
    tr1 = v01.transportar_trayectoria(cortes)
    assert tr1["estado"] == "TRANSPORTE_OK", tr1
    tr2 = v02.transportar_trayectoria_v02(cortes)
    assert tr2["estado"] == "TRANSPORTE_OK", tr2
    y_antes = [p["y_transversal"] for p in tr2["trayectoria_cruda"]]
    y_v01 = [p["y_transversal"] for p in tr1["trayectoria_regularizada"]]
    y_v02 = [p["y_transversal"] for p in tr2["trayectoria_transformada"]]
    osc_antes = v01.medir_oscilacion(y_antes)
    osc_v01 = v01.medir_oscilacion(y_v01)
    osc_v02 = v01.medir_oscilacion(y_v02)
    # La media se mueve hacia el eje: media|y| del V0_2 < media|y| del V0_1.
    may_v01 = sum(abs(v) for v in y_v01) / len(y_v01)
    may_v02 = sum(abs(v) for v in y_v02) / len(y_v02)
    assert may_v02 < may_v01, (may_v01, may_v02)
    # TV del V0_2 < TV del V0_1 (el costo mueve la media, no solo interpola).
    assert osc_v02["variacion_total"] < osc_v01["variacion_total"], (osc_v02, osc_v01)
    # Extremos anclados.
    assert y_v02[0] == y_antes[0] and y_v02[-1] == y_antes[-1], (y_v02, y_antes)
    # Se destruye masa (M < 1) y converge en todas las transiciones.
    for t in tr2["transiciones"]:
        for lado, pl in t["planes"].items():
            assert pl["info"]["convergio"], (t, lado, pl["info"])
            assert 0.0 < pl["info"]["masa_transportada"] <= 1.0 + 1e-9, pl["info"]
    ct = tr2["costo_transformacion"]
    assert ct["masa_destruida_media"] > 0.0, ct
    print("transporte_v02 OK (TV %.4f -> V0_1 %.4f -> V0_2 %.4f; media|y| V0_1 %.4f -> V0_2 %.4f; M=%.3f)" % (
        osc_antes["variacion_total"], osc_v01["variacion_total"], osc_v02["variacion_total"],
        may_v01, may_v02, ct["masa_transportada_media"]))


def test_pocos_cortes():
    tr = v02.transportar_trayectoria_v02(cortes_sinteticos()[:2])
    assert tr["estado"] == "SIN_TRAYECTORIA", tr
    print("pocos cortes OK (SIN_TRAYECTORIA, no rompe)")


if __name__ == "__main__":
    test_sinkhorn_no_balanceado()
    test_memento()
    test_transporte_v02()
    test_pocos_cortes()
    print("PASS test_schrodinger_v0_2")
