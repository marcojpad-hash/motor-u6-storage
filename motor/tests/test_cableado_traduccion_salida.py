"""test_cableado_traduccion_salida.py — lateral_traduccion_salida_v1 v2.8 (021).

El test FALLA si el módulo no se ejecuta: cada test llama a traducir()
sobre un RESULT real (Napoleón, tercera persona; LIMBO, primera persona)
y exige la lectura calibrada con sus elementos (dirección, desempaque,
hallazgos con ancla, cierre) y 0 violaciones. El bypass apagado debe ser
visible (APAGADA_POR_FLAG), nunca silencioso. Una entrada neutra no debe
fabricar lectura (FALLO_SIN_RESULTADO). El módulo no muta el RESULT ni
decide H. El cableado en correr_estandar.py debe existir: si alguien quita
el enchufe, el test falla (el módulo quedaría como adorno: existiría pero
no se ejecutaría en la corrida).
"""
import copy
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
FIX = ROOT / "tests" / "fixtures"
NAP_RESULT = FIX / "napoleon_traduccion_result.json"
NAP_ENTRADA = ROOT.parent / "casos" / "fabrica" / "cola" / "CAL_F001_01_NAPOLEON" / "entrada.json"
LIM_RESULT = FIX / "limbo_traduccion_result.json"
LIM_ENTRADA = ROOT / "runs" / "TRADUCTOR_V28_20261113" / "LIMBO_6C_entrada.json"

NAPOLEON_LECTURA = (
    "Basado en lo que se cuenta, se perfila a que eso de que lucha contra "
    "el destino o lo divino se le haga más grande. Eso de que lucha contra "
    "el destino o lo divino creció: antes no estaba así de grande. A través "
    "de esta situación: eso de que busqueda de poder sin limites. Eso de "
    "que desafio a la autoridad no estaba antes: apareció apenas al final. "
    "Muy probablemente desafio a la autoridad se haga más grande, junto con "
    "todo eso. Y eso puede ir creciendo con el tiempo si las cosas siguen así."
)

LIMBO_LECTURA = (
    "Basado en lo que me contaste, te perfilas a quedarte en el limbo. "
    "Estás a la mitad, en el umbral: optaste por salirte, pero sigues en "
    "el limbo. El limbo creció: antes no estaba así de grande. A través "
    "de esta situación: eso de que ella estuvo mucho tiempo distante. El "
    "duelo no estaba antes: apareció apenas ahorita. Muy probablemente el "
    "duelo te pegue más fuerte, junto con todo eso. Y eso puede ir "
    "creciendo con el tiempo si las cosas siguen así."
)


def _load_tr():
    if str(MOTOR_DIR) not in sys.path:
        sys.path.insert(0, str(MOTOR_DIR))
    spec = importlib.util.spec_from_file_location(
        "lateral_traduccion_salida_v1", MOTOR_DIR / "lateral_traduccion_salida_v1.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _napoleon():
    result = json.loads(NAP_RESULT.read_text(encoding="utf-8"))
    ent = json.loads(NAP_ENTRADA.read_text(encoding="utf-8"))
    return result, ent


def _limbo():
    result = json.loads(LIM_RESULT.read_text(encoding="utf-8"))
    ent = json.loads(LIM_ENTRADA.read_text(encoding="utf-8"))
    return result, ent


def _sin_marcas_tecnicas(lectura):
    # La lectura no lleva etiquetas del catálogo ni vocabulario del motor.
    for marca in ("31_conflicto_con_un_dios", "30_ambicion",
                  "eterno_retorno_01_caos_primordial", "apego_03_evitativo",
                  "H1", "H2", "%", "token", "peso"):
        assert marca not in lectura, marca
    return True


def test_traduce_napoleon_tercera_persona():
    tr = _load_tr()
    result, ent = _napoleon()
    antes = copy.deepcopy(result)
    antes_ent = copy.deepcopy(ent)
    out = tr.traducir(result, ent)
    # El módulo ejecuta: lectura calibrada en tercera persona.
    assert out["anexo"]["status"] == "OK", out
    assert out["lectura"] == NAPOLEON_LECTURA, out["lectura"]
    assert out["violaciones"] == []
    assert out["anexo"]["H1"] == "31_conflicto_con_un_dios"
    assert out["anexo"]["H2"] == "30_ambicion"
    assert out["anexo"]["registro"] == "tercera"
    assert out["anexo"]["version"] == "v2.8_20261114"
    # El anexo no lleva nulls: el runner los marca como dato faltante y la
    # corrida quedaría INCOMPLETE_OUTPUT_DATA.
    assert all(v is not None for v in out["anexo"].values())
    _sin_marcas_tecnicas(out["lectura"])
    # No muta el RESULT ni la entrada, no cambia H.
    assert result == antes
    assert ent == antes_ent


def test_traduce_limbo_primera_persona():
    tr = _load_tr()
    result, ent = _limbo()
    antes = copy.deepcopy(result)
    out = tr.traducir(result, ent)
    # El módulo ejecuta: lectura en segunda persona, con las palabras
    # de la persona ("el limbo") y el hallazgo de lo nuevo ("el duelo").
    assert out["anexo"]["status"] == "OK", out
    assert out["lectura"] == LIMBO_LECTURA, out["lectura"]
    assert out["violaciones"] == []
    assert out["anexo"]["H1"] == "eterno_retorno_01_caos_primordial"
    assert out["anexo"]["H2"] == "apego_03_evitativo"
    assert out["anexo"]["registro"] == "primera"
    assert "te perfilas" in out["lectura"]
    assert "el limbo" in out["lectura"]
    assert "El duelo no estaba antes" in out["lectura"]
    # El anexo no lleva nulls: el runner los marca como dato faltante.
    assert all(v is not None for v in out["anexo"].values())
    _sin_marcas_tecnicas(out["lectura"])
    # No muta el RESULT ni cambia H.
    assert result == antes


def test_neutro_sin_resultado_no_fabrica():
    tr = _load_tr()
    # Entrada neutra fuera de U6: no debe fabricar lectura.
    out = tr.traducir({}, {})
    assert out["anexo"]["status"] == "FALLO_SIN_RESULTADO", out
    assert out["lectura"] == ""
    out2 = tr.traducir(None, None)
    assert out2["anexo"]["status"] == "FALLO_SIN_RESULTADO", out2
    assert out2["lectura"] == ""
    out3 = tr.traducir({"movimiento_de_fondo": {}}, {"cuts": []})
    assert out3["anexo"]["status"] == "FALLO_SIN_RESULTADO", out3
    assert out3["lectura"] == ""


def test_bypass_apagado_visible():
    tr = _load_tr()
    result, ent = _limbo()
    anterior = os.environ.get("TRADUCCION_SALIDA")
    try:
        os.environ["TRADUCCION_SALIDA"] = "0"
        assert tr.esta_activa() is False
        out = tr.traducir(result, ent)
        # Apagado VISIBLE, nunca en silencio: status y lectura vacía.
        assert out["anexo"]["status"] == "APAGADA_POR_FLAG", out
        assert out["lectura"] == ""
    finally:
        if anterior is None:
            os.environ.pop("TRADUCCION_SALIDA", None)
        else:
            os.environ["TRADUCCION_SALIDA"] = anterior
    # Al volver a encender, ejecuta.
    assert tr.esta_activa() is True
    out2 = tr.traducir(result, ent)
    assert out2["anexo"]["status"] == "OK"


def test_runner_enchufa_traduccion_salida():
    """El cableado: correr_estandar.py llama al módulo tras sellar el RESULT.

    Si alguien quita el enchufe, este test falla (el módulo quedaría como
    adorno: existiría pero no se ejecutaría en la corrida). El puente
    observar() es la vía por la que el runner lo invoca.
    """
    texto = (ROOT / "correr_estandar.py").read_text(encoding="utf-8")
    assert "lateral_traduccion_salida_v1" in texto
    assert "TRADUCCION_SALIDA" in texto
    assert 'result["traduccion_salida"]' in texto
    tr = _load_tr()
    result, ent = _limbo()
    out = tr.observar(ent, None, result)
    assert out["anexo"]["status"] == "OK", out
    assert out["anexo"]["H1"] == "eterno_retorno_01_caos_primordial"
    assert out["anexo"]["H2"] == "apego_03_evitativo"
    assert "te perfilas" in out["lectura"]
    assert out["lectura"] == LIMBO_LECTURA
