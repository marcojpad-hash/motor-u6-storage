#!/usr/bin/env python3
"""test_cableado_sombrero_blanco.py — Sombrero blanco v2 cableado a la puerta de entrada.

Contrato: orquestador-central `docs/filtros_operativos/SOMBRERO_BLANCO.md`
v1.1. El filtro admite solo lo objetivamente medible; el juicio es ruido
tipado; no decide la hipótesis.

Cobertura:
- Ejemplo de la spec (2 hechos + 2 ruidos tipados, con traza).
- Un texto que dice literalmente "juicio estético" no se tira entero
  (nada se descarta; el nombre del método nunca es ruido).
- Separación Lamborghini V2/V3 (dichos y figuras = ruido; hechos
  observables se conservan).
- compuerta: traza no modifica, activo admite y anota, off no ejecuta,
  idempotente (re-aplicar al texto admitido da el mismo texto).
- El runner UNICO aplica el filtro al entrar (red de seguridad).
- Cableado estático: la puerta existe en `correr_estandar.py` y en
  `MOTOR_V15_3_UNICO_20260927.py`.
- Un bypass se marca en el recibo (SOMBRERO_BLANCO=off -> NO_CONFIGURADO),
  no pasa en silencio.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

MOTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOTOR))
sys.path.insert(0, str(MOTOR / "capa_llm"))

from sombrero_blanco_filtro_v2 import compuerta, filtrar  # noqa: E402

CORRER = MOTOR / "correr_estandar.py"
UNICO = MOTOR / "motor" / "MOTOR_V15_3_UNICO_20260927.py"
FIXTURE = MOTOR / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

EJEMPLO_SPEC = "el niño era cruel y el sombrero estaba muy bonito"

V2_HECHO = (
    "ACTOR_A ocupa el paso con su bicicleta azul y su mochila roja y "
    "VICTIMA vende periódicos en el mismo paso, y la narración del "
    'NARRADOR dice que VICTIMA es inmundo, "que los pobres huelen mal y '
    'que son crueles y peligrosos" y que "no debían existir"'
)

V3_HECHO = (
    'NARRADOR compara "palacios multicolores" con un "joyero sin tapa", '
    '"un espacio en blanco" y una "espada espejeante". NARRADOR sostiene '
    'que "el silencio entre las casas era un espacio en blanco" y que '
    '"el hambre era una cuchilla de hierro y de marfil". NARRADOR usa los '
    'calificativos "execrable" y "joyesca". ACTOR_A ocupa el paso con su '
    "bicicleta azul y su mochila roja y VICTIMA vende periódicos en el "
    "mismo paso."
)


def _caso_base():
    return {
        "case_id": "TEST_SOMBRERO_BLANCO",
        "question": EJEMPLO_SPEC,
        "cuts": [
            {"id": "c1", "hecho": V2_HECHO, "P": "x", "A": "y", "C": "z"},
            {"id": "c2", "hecho": V3_HECHO, "P": "x", "A": "y", "C": "z"},
        ],
    }


# ---------------------------------------------------------------- ejemplo spec
def test_filtrar_ejemplo_spec_dos_hechos_dos_ruidos_tipados():
    res = filtrar(EJEMPLO_SPEC)
    unidades = [(h["unidad"], h["clase"]) for h in res["hechos"]]
    assert ("niño", "quién (actor)") in unidades
    assert ("sombrero", "qué (objeto)") in unidades
    assert len(res["hechos"]) == 2
    tipos = [(r["fragmento"], r["tipo"]) for r in res["ruido"]]
    assert ("era cruel", "juicio moral") in tipos
    assert ("estaba muy bonito", "juicio estético") in tipos
    assert len(res["ruido"]) == 2
    # Cada hecho y cada ruido llevan su traza al fragmento fuente.
    for h in res["hechos"]:
        assert h["traza"] in EJEMPLO_SPEC and isinstance(h["offset"], int)
    for r in res["ruido"]:
        assert r["traza"] in EJEMPLO_SPEC and isinstance(r["offset"], int)
    # El texto admitido conserva lo observable y nada más.
    assert res["texto_admitido"] == "el niño y el sombrero"
    assert "cruel" not in res["texto_admitido"]
    assert "bonito" not in res["texto_admitido"]
    # No decide veredicto.
    assert res["can_decide_H"] is False
    assert res["feeds_predictor"] is False
    assert res["llamadas_llm"] == 0


def test_filtrar_juicio_estetico_literal_no_se_tira():
    # Criterio de aceptación 2: un texto que dice literalmente
    # "juicio estético" no se tira entero por coincidir con una cadena.
    texto = "esto es un juicio estético sobre el sombrero blanco"
    res = filtrar(texto)
    assert res["ruido"] == []
    # El nombre del método ("sombrero blanco") es un hecho, no ruido.
    unidades = [(h["unidad"], h["clase"]) for h in res["hechos"]]
    assert ("sombrero", "qué (objeto)") in unidades
    assert ("blanco", "cualidad observable") in unidades
    # Nada se descarta: el texto admitido es el original.
    assert res["texto_admitido"] == texto


# ------------------------------------------------------- Lamborghini V2 / V3
def test_lamborghini_v2_dichos_no_son_hechos():
    res = filtrar(V2_HECHO)
    tipos = [r["tipo"] for r in res["ruido"]]
    assert "dicho atribuido" in tipos
    assert "juicio moral" in tipos
    # Los dichos del narrador no entran como hechos del mundo.
    fragmentos_ruido = " ".join(r["fragmento"] for r in res["ruido"])
    assert "huelen mal" in fragmentos_ruido
    assert "no debían existir" in fragmentos_ruido
    # Los hechos observables se conservan.
    unidades = [(h["unidad"], h["clase"]) for h in res["hechos"]]
    assert ("ACTOR_A", "quién (actor)") in unidades
    assert ("VICTIMA", "quién (actor)") in unidades
    assert ("vende", "qué (acción)") in unidades
    assert ("paso", "qué (objeto)") in unidades
    assert "inmundo" not in res["texto_admitido"]


def test_lamborghini_v3_figuras_son_ruido():
    res = filtrar(V3_HECHO)
    tipos = [r["tipo"] for r in res["ruido"]]
    assert "figura retórica" in tipos
    assert "dicho atribuido" in tipos
    fragmentos_ruido = " ".join(r["fragmento"] for r in res["ruido"])
    for figura in ("palacios multicolores", "joyero sin tapa", "espada espejeante"):
        assert figura in fragmentos_ruido
    # Las figuras no quedan en el texto admitido.
    for figura in ("palacios multicolores", "joyero sin tapa", "espada espejeante"):
        assert figura not in res["texto_admitido"]
    # Los hechos observables se conservan.
    unidades = [(h["unidad"], h["clase"]) for h in res["hechos"]]
    assert ("ACTOR_A", "quién (actor)") in unidades
    assert ("VICTIMA", "quién (actor)") in unidades
    assert ("vende", "qué (acción)") in unidades


# ------------------------------------------------------------------ compuerta
def test_compuerta_traza_no_modifica():
    caso = _caso_base()
    out, traza = compuerta(caso, "traza")
    assert out == caso
    assert traza["status"] == "TRAZA_SIN_MODIFICACION"
    assert traza["n_ruido"] > 0
    assert traza["can_decide_H"] is False
    assert traza["feeds_predictor"] is False


def test_compuerta_activo_admite_y_anota_ruido():
    caso = _caso_base()
    out, traza = compuerta(caso, "activo")
    assert traza["status"] == "EXECUTED"
    assert traza["n_hechos"] > 0 and traza["n_ruido"] > 0
    # El caso que sigue lleva solo lo admitido.
    assert out["question"] == "el niño y el sombrero"
    assert "inmundo" not in out["cuts"][0]["hecho"]
    assert "palacios multicolores" not in out["cuts"][1]["hecho"]
    # P/A/C y el resto del caso no se tocan.
    assert out["cuts"][0]["P"] == "x" and out["cuts"][0]["A"] == "y"
    # El texto original y el ruido quedan en la traza (no se borran).
    campos = traza["campos"]
    assert any(c["texto_original"] == EJEMPLO_SPEC for c in campos)
    assert any(c["ruido"] for c in campos)


def test_compuerta_off_no_ejecuta():
    caso = _caso_base()
    out, traza = compuerta(caso, "off")
    assert out == caso
    assert traza["status"] == "NO_CONFIGURADO"


def test_compuerta_idempotente():
    caso = _caso_base()
    una, _ = compuerta(caso, "activo")
    dos, traza_dos = compuerta(una, "activo")
    assert dos == una
    assert traza_dos["status"] == "EXECUTED"


# ------------------------------------------------------- runner UNICO (red)
def test_runner_aplica_sombrero_blanco_al_entrar():
    import importlib.util as _iu

    spec = _iu.spec_from_file_location("MOTOR_V15_3_UNICO_20260927", str(UNICO))
    mod = _iu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    caso = _caso_base()
    out, traza = mod._aplicar_sombrero_blanco(caso)
    assert traza["status"] == "EXECUTED"
    assert traza["can_decide_H"] is False
    assert "cruel" not in out["question"]
    assert "bonito" not in out["question"]


def test_runner_sombrero_blanco_off_se_marca():
    import importlib.util as _iu

    spec = _iu.spec_from_file_location("MOTOR_V15_3_UNICO_20260927", str(UNICO))
    mod = _iu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    caso = _caso_base()
    os.environ["SOMBRERO_BLANCO"] = "off"
    try:
        out, traza = mod._aplicar_sombrero_blanco(caso)
    finally:
        del os.environ["SOMBRERO_BLANCO"]
    assert out == caso
    assert traza["status"] == "NO_CONFIGURADO"


# ------------------------------------------------------------ cableado estático
def test_cableado_presente_en_runner_y_correr_estandar():
    src_unico = UNICO.read_text(encoding="utf-8")
    assert "_aplicar_sombrero_blanco" in src_unico
    assert "_cargar_sombrero_blanco" in src_unico
    assert "result[\"sombrero_blanco\"]" in src_unico
    src_correr = CORRER.read_text(encoding="utf-8")
    assert "sombrero_blanco_filtro_v2" in src_correr
    assert "SOMBRERO_BLANCO" in src_correr
    assert '"stage": "sombrero_blanco"' in src_correr
    assert 'result["sombrero_blanco"]' in src_correr


# ------------------------------------------------- bypass se marca en el recibo
def _corrida_fixture(modo_sb, tmpdir):
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture["question"] = EJEMPLO_SPEC
    fixture["cuts"][0]["hecho"] = V2_HECHO
    entrada = Path(tmpdir) / "entrada_sombrero.json"
    entrada.write_text(json.dumps(fixture, ensure_ascii=False), encoding="utf-8")
    salida = Path(tmpdir) / "salida_sombrero.json"
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["U6_HARNESS_BUSCADOR_MOCK"] = "1"
    env["PYTHONPATH"] = str(MOTOR / "harness_site")
    env["SOMBRERO_BLANCO"] = modo_sb
    proc = subprocess.run(
        [
            sys.executable,
            str(CORRER),
            str(entrada),
            "--out",
            str(salida),
        ],
        cwd=str(MOTOR),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode in (0, 5), proc.stdout[-2000:] + proc.stderr[-2000:]
    resultado = json.loads(salida.read_text(encoding="utf-8"))
    recibo = json.loads(
        salida.with_name(salida.stem + "_RECIBO_EJECUCION.json").read_text(encoding="utf-8")
    )
    return resultado, recibo


def test_corrida_puerta_activo_ejecuta_y_registra():
    with tempfile.TemporaryDirectory() as tmp:
        resultado, recibo = _corrida_fixture("activo", tmp)
        assert "sombrero_blanco" in resultado
        traza = resultado["sombrero_blanco"]
        assert traza["status"] == "EXECUTED"
        # La traza del resultado es la de run(): re-aplica el filtro al caso
        # ya admitido por la puerta, así que no encuentra ruido que quitar
        # (idempotencia). Lo que la puerta quitó está en la etapa del recibo.
        etapas = {e["stage"]: e for e in recibo.get("stages", [])}
        assert "sombrero_blanco" in etapas
        assert etapas["sombrero_blanco"]["status"] == "EXECUTED"
        assert etapas["sombrero_blanco"]["modo"] == "activo"
        assert etapas["sombrero_blanco"]["n_ruido"] > 0


def test_corrida_puerta_off_se_marca_no_pasa_en_silencio():
    with tempfile.TemporaryDirectory() as tmp:
        resultado, recibo = _corrida_fixture("off", tmp)
        etapas = {e["stage"]: e for e in recibo.get("stages", [])}
        assert "sombrero_blanco" in etapas
        assert etapas["sombrero_blanco"]["status"] == "NO_CONFIGURADO"
        assert etapas["sombrero_blanco"]["modo"] == "off"
        assert resultado.get("sombrero_blanco", {}).get("status") == "NO_CONFIGURADO"
