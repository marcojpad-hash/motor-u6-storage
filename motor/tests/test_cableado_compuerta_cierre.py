#!/usr/bin/env python3
"""test_cableado_compuerta_cierre.py — compuerta de cierre: el camino de bloqueo.

V7 (C-F8): la compuerta corría siempre con 0 pendientes y sin test que
construyera el caso contradictorio; su función central (retener un cierre con
pendientes vivos contradictorios) era código leído, no hecho demostrado.
Estos tests ejercitan el camino CIERRE_BLOQUEADO_LATENCIA con una caja falsa
y documentan el límite real: el review_pending del StinkBox real es un stub
que nunca devuelve contradicciones (ver último test).
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"


def _load_unico():
    spec = importlib.util.spec_from_file_location("runner_u6_compuerta", UNICO)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class _CajaFalsa:
    """StinkBox mínimo para el test: review_pending devuelve lo que se le pide."""

    def __init__(self, contradicen):
        self.case_id = "TEST_COMPUERTA"
        self._contradicen = list(contradicen)

    def pendientes_vivos(self):
        return [{"front_id": f} for f in self._contradicen] or [{"front_id": "F1"}]

    def review_pending(self, rows=None, cut_id=None, closing_candidate=None, latest_dX=None,
                       separation=None, discard_gap=None, absent_limit=None, **_k):
        vivos = [v["front_id"] for v in self.pendientes_vivos()]
        return {"revisados": vivos, "resueltos_a_favor": [], "resueltos_en_contra": [],
                "siguen_latentes": vivos, "contradicen_cierre": list(self._contradicen),
                "detalle": []}


def _fused():
    return [("arquetipo_el_gobernante", {"rank_fusion": 32.98}),
            ("13_enemistad_de_parientes", {"rank_fusion": 30.99})]


def test_compuerta_bloquea_cierre_con_pendiente_contradictorio():
    u = _load_unico()
    gate_ctx = {"box": _CajaFalsa(["F1"]), "cut_id": "C3_480BC"}
    block = u._compuerta_cierre(_fused(), [], {},
                                {"evidence_sufficient": True, "state": "RESUELTO"},
                                gate_ctx)
    assert block["status"] == "EJECUTADA"
    assert block["contradice_cierre"] is True
    assert block["decision"] == "CIERRE_BLOQUEADO_LATENCIA"
    assert block["pendientes_que_contradicen"] == ["F1"]


def test_compuerta_permite_cierre_sin_contradiccion():
    u = _load_unico()
    gate_ctx = {"box": _CajaFalsa([]), "cut_id": "C3_480BC"}
    block = u._compuerta_cierre(_fused(), [], {},
                                {"evidence_sufficient": True, "state": "RESUELTO"},
                                gate_ctx)
    assert block["decision"] == "CIERRE_PERMITIDO"
    assert block["contradice_cierre"] is False


def test_review_pending_real_no_contradicta_nunca(tmp_path):
    # Documenta el límite real (V7, C-F8): el review_pending del StinkBox real
    # es un stub que siempre devuelve contradicen_cierre=[] — por eso el camino
    # CIERRE_BLOQUEADO_LATENCIA nunca se ejercita en una corrida real. Si alguien
    # implementa la evaluación real de contradicciones, este test debe cambiar.
    spec = importlib.util.spec_from_file_location(
        "stinkbox_transport_v0_2", MOTOR_DIR / "stinkbox_transport_v0_2.py")
    sb = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = sb
    spec.loader.exec_module(sb)
    box = sb.StinkBox("TEST_COMPUERTA", tmp_path / "stinkbox")
    box.record_pending(front_id="F1", cut_id="C1", reason="TEST")
    rep = box.review_pending([], "C3_480BC", closing_candidate="arquetipo_el_gobernante")
    assert rep["contradicen_cierre"] == []
    assert rep["siguen_latentes"] == ["F1"]
