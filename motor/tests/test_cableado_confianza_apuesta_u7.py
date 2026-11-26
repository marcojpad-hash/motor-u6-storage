"""Cableado del U7 (confianza de la apuesta) en el runner estándar (V7).

El U7 existía pero nadie lo ejecutaba: ningún archivo de motor/*.py lo llamaba.
La prueba que importa es la corrida completa: si el U7 no se ejecuta por
correr_estandar.main(), el RESULT no trae el puntaje y el recibo no trae la
etapa — y este test falla. No basta con probarlo en aislamiento.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

MOTOR = Path(__file__).resolve().parents[1]
CORRER = MOTOR / "correr_estandar.py"
FIXTURE = MOTOR / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

spec = importlib.util.spec_from_file_location("runner_cableado_u7_test", CORRER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_cableado_estatico_u7_en_correr_estandar():
    src = CORRER.read_text(encoding="utf-8")
    assert "def _confianza_apuesta_u7" in src
    assert 'result["confianza_apuesta_u7"]' in src
    assert '"stage": "confianza_apuesta_u7"' in src
    assert "U7_CONFIAZA_APUESTA" in src


def _fixture_u7_minimo():
    # Forma mínima del RESULT que calc() necesita (misma que el test U7).
    return {
        'case_id': 'SYNTH_U7_CABLEADO',
        'cierre_final': {'criterios_grado': {'separacion': 1.0, 'H1_en_banda': False},
                         'apuesta': {'familia_apostada': 'H1', 'frente_a': 'H2', 'margen': 1.0},
                         'prueba_acero': {'veredicto_top1': 'SOBREVIVE', 'rival_mas_fuerte': 'H2'},
                         'n_objeciones': 0, 'objeciones': [], 'grado': 'AJUSTADA'},
        'salida_interpretable': {'grado_inverso_set': 'SET_EXPLICA_TODOS_LOS_CORTES',
                                 'mezcla': {'lectura': 'H1_DOMINANTE'},
                                 'H1': {'predictibilidad_estructural_pct': 50}},
        'predictor': {'lateral_signal_registry': []},
        'cierre_guardianes': {},
        'decimo_hombre_esteroides': {'contador_supervivencia': {'H1': 1}, 'ataques': []},
        'efectividad_corte_retenido': {'H1_sellada_compatibilidad': 'H1',
                                       'tops_t1': [{'familia': 'H1'}] * 10, 'hit_H': True},
        'hipotesis_necesarias_suficientes': {'miembros': []},
        'lo_que_se_cocina_abajo': [],
        'predictibilidad_021': {'predictibilidad': {'base_pp': 40, 'techo_pp': 60}},
    }


def test_helper_u7_ejecuta_en_proceso_y_desactivado_queda_registrado(monkeypatch):
    monkeypatch.delenv("U7_CONFIAZA_APUESTA", raising=False)
    out = runner._confianza_apuesta_u7(_fixture_u7_minimo())
    assert out["status"] == "EJECUTADA"
    assert 0.0 <= out["S"] <= 1.0
    assert out["calibrada"] is False
    assert set(out["bloques"]) == {"B1_dominancia", "B2_set_mezcla", "B3_laterales",
                                    "B4_robustez_adversarial", "B5_estabilidad_sin_ultimo", "B6_fondo"}
    # Estado desactivado visible, nunca en silencio.
    monkeypatch.setenv("U7_CONFIAZA_APUESTA", "off")
    off = runner._confianza_apuesta_u7(_fixture_u7_minimo())
    assert off["status"] == "NO_EJECUTADO"
    assert "U7_CONFIAZA_APUESTA=off" in off["motivo"]


def _corrida_u7(tmpdir):
    entrada = Path(tmpdir) / "entrada_u7.json"
    entrada.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    salida = Path(tmpdir) / "salida_u7.json"
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["U6_HARNESS_BUSCADOR_MOCK"] = "1"
    env["PYTHONPATH"] = str(MOTOR / "harness_site")
    env.pop("U7_CONFIAZA_APUESTA", None)
    proc = subprocess.run(
        [sys.executable, str(CORRER), str(entrada), "--out", str(salida)],
        cwd=str(MOTOR), env=env, capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode in (0, 5), proc.stdout[-2000:] + proc.stderr[-2000:]
    resultado = json.loads(salida.read_text(encoding="utf-8"))
    recibo = json.loads(
        salida.with_name(salida.stem + "_RECIBO_EJECUCION.json").read_text(encoding="utf-8"))
    return resultado, recibo


def test_corrida_ejecuta_u7_y_registra_puntaje_en_resultado_y_recibo():
    with tempfile.TemporaryDirectory() as tmp:
        resultado, recibo = _corrida_u7(tmp)
        # El U7 corrió por run(): el RESULT trae el puntaje completo.
        u7 = resultado["confianza_apuesta_u7"]
        assert u7["status"] == "EJECUTADA"
        assert 0.0 <= u7["S"] <= 1.0
        assert u7["calibrada"] is False  # NOT_CALIBRATED: pesos iguales, placeholder
        assert set(u7["bloques"]) == {"B1_dominancia", "B2_set_mezcla", "B3_laterales",
                                       "B4_robustez_adversarial", "B5_estabilidad_sin_ultimo",
                                       "B6_fondo"}
        # B5 de punta a punta con datos reales: el productor escribió tops_t1
        # y H1_sellada_compatibilidad, y B5 puntuó con ellos (no por defecto).
        eff = resultado["efectividad_corte_retenido"]
        assert len(eff["tops_t1"]) == 10
        assert eff["H1_sellada_compatibilidad"] == "30_ambicion"
        b5 = u7["detalle"]["B5"]
        assert b5["retenido_usable"] is True
        assert b5["H1_sin_ultimo"] == "30_ambicion"
        assert u7["bloques"]["B5_estabilidad_sin_ultimo"] == 0.5  # hs en el set
        # El recibo trae la etapa con el puntaje.
        etapas = {e["stage"]: e for e in recibo.get("stages", [])}
        assert "confianza_apuesta_u7" in etapas
        etapa = etapas["confianza_apuesta_u7"]
        assert etapa["status"] == "EJECUTADA"
        assert etapa["S"] == u7["S"]
        assert etapa["confianza_apuesta_pct"] == u7["confianza_apuesta_pct"]
        assert etapa["calibrada"] is False
        # El cableado no movió H1/H2: el smoke sigue idéntico a la base.
        si = resultado["salida_interpretable"]
        assert si["H1"]["familia"] == "arquetipo_el_gobernante"
        assert si["H2"]["familia"] == "13_enemistad_de_parientes"
        ranks = {h["id"]: h["rank_fusion"]
                 for h in si["conjunto_hipotesis_abiertas"]["hipotesis"]}
        assert ranks["H_001"] == 32.986716
        assert ranks["H_002"] == 30.99436
