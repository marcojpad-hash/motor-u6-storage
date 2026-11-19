#!/usr/bin/env python3
"""test_coordinador_controles_generales.py — Tests del coordinador general
de controles operativos (paquete agnóstico ``controles_generales``).

Cada test falla si el control que cubre no se aplica: si el filtro
admitiera un juicio, si la secuencia dejara saltarse una fase, si la
salida pasara con un hueco o con una referencia inventada, si el cierre
se diera con pendientes vivos, o si la guardia no detectara una
mutación. Solo se prueba este paquete; no se corre la suite del motor.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

MOTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOTOR))

from controles_generales import (  # noqa: E402
    CompuertaCierre,
    ContextoContaminado,
    CoordinadorControles,
    CorteTemporal,
    FaseFueraDeOrden,
    FiltroAdmision,
    GuardiaSeparacion,
    ParadaDura,
    PiezaNoIntegra,
    SalidaNoConforme,
    SecuenciaFases,
    UnidadEntrada,
    VentanaSellada,
    VerificadorIntegridad,
    VerificadorSalida,
)


def unidad(contenido, marcas, procedencia="fuente, registro 1", ident="u1"):
    return UnidadEntrada(contenido, procedencia=procedencia, marcas=frozenset(marcas), identificador=ident)


# --- Filtro de admisión -------------------------------------------------

def test_filtro_admite_solo_lo_verificable():
    filtro = FiltroAdmision()
    admision = filtro.filtrar([
        unidad("llovió 12 mm", {"medible"}, ident="u1"),
        unidad("fue un día horrible", {"juicio"}, ident="u2"),
    ])
    assert [u.identificador for u in admision.admitidas] == ["u1"]
    assert len(admision.apartadas) == 1
    assert admision.apartadas[0]["tipo"] == "juicio"


def test_filtro_no_borra_lo_apartado():
    filtro = FiltroAdmision()
    admision = filtro.filtrar([unidad("qué bonito", {"opinion"}, ident="u2")])
    assert admision.apartadas[0]["unidad"].contenido == "qué bonito"
    assert any(r.accion == "apartado" for r in filtro.bitacora)


def test_filtro_sin_procedencia_no_se_admite():
    filtro = FiltroAdmision()
    admision = filtro.filtrar([unidad("dato sin fuente", {"observable"}, procedencia="")])
    assert admision.admitidas == []
    assert admision.apartadas[0]["tipo"] == "sin_procedencia"


def test_filtro_modo_traza_no_modifica_pero_anota():
    filtro = FiltroAdmision(modo="solo_traza")
    admision = filtro.filtrar([unidad("qué bonito", {"opinion"}, ident="u2")])
    assert [u.identificador for u in admision.admitidas] == ["u2"]
    assert admision.apartadas[0]["motivo"].startswith("solo_traza")


def test_filtro_apagado_es_bypass_registrado():
    coord = CoordinadorControles(fases=["a"], modo_filtro="apagado")
    assert coord.recibo()["bypass_filtro_apagado"] is True


# --- Secuencia de fases -------------------------------------------------

def test_secuencia_no_deja_saltarse_fases():
    sec = SecuenciaFases(["recoger", "revisar", "cerrar"])
    with pytest.raises(FaseFueraDeOrden):
        sec.completar("cerrar")


def test_secuencia_en_orden_completa():
    sec = SecuenciaFases(["recoger", "revisar", "cerrar"])
    sec.completar("recoger")
    sec.completar("revisar")
    assert sec.siguiente == "cerrar"
    sec.completar("cerrar")
    assert sec.terminada


def test_contorno_registra_y_sigue():
    sec = SecuenciaFases(["a", "b"])
    accion = sec.contornear("a", "falta_equivalente", "buscar equivalente por nombre")
    assert accion == "buscar equivalente por nombre"
    assert len(sec.contornos) == 1
    assert sec.completadas == []  # contornear no marca la fase como hecha


def test_parada_dura_si_para():
    sec = SecuenciaFases(["a", "b"], paradas_duras=["pieza_canonica_corrupta"])
    with pytest.raises(ParadaDura):
        sec.contornear("a", "pieza_canonica_corrupta", "seguir igual")


# --- Verificador de integridad ------------------------------------------

def test_integridad_acepta_pieza_que_compila():
    ver = VerificadorIntegridad()
    estado = ver.verificar("pieza1", "x = 1\n")
    assert estado["integra"] is True
    assert estado["cambio_huella"] is False


def test_integridad_rechaza_pieza_que_no_compila():
    ver = VerificadorIntegridad()
    with pytest.raises(PiezaNoIntegra):
        ver.verificar("rota", "def f(:\n")


def test_integridad_rechaza_corrupcion_tipica():
    ver = VerificadorIntegridad()
    with pytest.raises(PiezaNoIntegra):
        ver.verificar("curvas", "x = \u201c1\u201d\n")


def test_cambio_de_huella_avisa_y_no_bloquea():
    ver = VerificadorIntegridad(manifiesto={"p": VerificadorIntegridad().verificar("p", "x = 1\n")["huella"]})
    estado = ver.verificar("p", "x = 2\n")
    assert estado["integra"] is True
    assert estado["cambio_huella"] is True
    assert any(r.accion == "cambio_huella" for r in ver.bitacora)


# --- Verificador de salida ----------------------------------------------

def test_salida_conforme_pasa():
    ver = VerificadorSalida(["resumen", "referencias"], orden=["resumen", "referencias"],
                            referencias_permitidas=["u1"])
    res = ver.verificar({"resumen": "llovió", "referencias": ["u1"]})
    assert res.conforme


def test_salida_con_hueco_no_pasa():
    ver = VerificadorSalida(["resumen", "referencias"])
    res = ver.verificar({"resumen": "", "referencias": ["u1"]})
    assert not res.conforme
    assert "hueco:resumen" in res.violaciones


def test_salida_sin_campo_requerido_no_pasa():
    ver = VerificadorSalida(["resumen", "referencias"])
    with pytest.raises(SalidaNoConforme):
        ver.exigir({"resumen": "llovió"})


def test_salida_en_desorden_no_pasa():
    ver = VerificadorSalida(["a", "b"], orden=["a", "b"])
    res = ver.verificar({"b": "2", "a": "1"})
    assert not res.conforme
    assert "orden_incorrecto" in res.violaciones


def test_salida_con_referencia_inventada_no_pasa():
    ver = VerificadorSalida(["resumen", "referencias"], referencias_permitidas=["u1"])
    res = ver.verificar({"resumen": "x", "referencias": ["u99"]})
    assert not res.conforme
    assert "referencia_inventada:u99" in res.violaciones


# --- Compuerta de cierre -------------------------------------------------

def test_cierre_latente_con_pendientes_vivos():
    puerta = CompuertaCierre()
    decision = puerta.evaluar(pendientes_vivos=["revisar dato 3"])
    assert decision.decision == "LATENTE"
    assert not decision.cerrado


def test_cierre_latente_con_contradiccion():
    puerta = CompuertaCierre()
    decision = puerta.evaluar(contradicciones=["dos fuentes discrepan"])
    assert decision.decision == "LATENTE"


def test_cierre_solo_cuando_nada_queda_vivo():
    puerta = CompuertaCierre()
    decision = puerta.evaluar(secuencia_terminada=True, salida_verificada=True)
    assert decision.decision == "CERRADO"


# --- Guardia de separación ----------------------------------------------

def test_guardia_detecta_mutacion_del_contexto():
    contexto = {"a": 1}
    with pytest.raises(ContextoContaminado):
        with GuardiaSeparacion(contexto, corte_id="paso-1"):
            contexto["a"] = 2


def test_guardia_pasa_si_nadie_muta():
    contexto = {"a": 1}
    with GuardiaSeparacion(contexto, corte_id="paso-1"):
        copia = dict(contexto)
    assert copia == {"a": 1}


def test_guardia_rechaza_campos_prohibidos_en_salida():
    contexto = {"a": 1}
    with GuardiaSeparacion(contexto, corte_id="paso-1") as guardia:
        with pytest.raises(ContextoContaminado):
            guardia.validar_salida({"nota": "x", "peso": 0.9}, campos_prohibidos={"peso"})


# --- Corte temporal -------------------------------------------------------

def test_corte_temporal_aparta_lo_posterior():
    ventana = CorteTemporal(fecha_cierre="2026-11-19")
    assert ventana.admitir("dato viejo", "2026-11-18", "d1") is True
    assert ventana.admitir("dato futuro", "2026-11-20", "d2") is False
    assert len(ventana.fuera_de_ventana) == 1


def test_ventana_sellada_no_admite_mas():
    ventana = CorteTemporal(fecha_cierre="2026-11-19")
    ventana.sellar()
    with pytest.raises(VentanaSellada):
        ventana.admitir("dato", "2026-11-01", "d1")


# --- Coordinador completo -------------------------------------------------

def test_coordinador_flujo_completo_cierra():
    coord = CoordinadorControles(
        fases=["recoger", "revisar", "cerrar"],
        campos_requeridos_salida=["resumen", "referencias"],
        orden_salida=["resumen", "referencias"],
    )
    admision = coord.admitir_entrada([
        unidad("llovió 12 mm", {"medible"}, ident="u1"),
        unidad("día horrible", {"juicio"}, ident="u2"),
    ])
    assert len(admision.admitidas) == 1
    coord.completar_fase("recoger")
    coord.completar_fase("revisar")
    resultado = coord.verificar_salida(
        {"resumen": "llovió 12 mm", "referencias": ["u1"]},
        referencias_permitidas=["u1"],
    )
    assert resultado.conforme
    coord.completar_fase("cerrar")
    assert coord.evaluar_cierre().cerrado
    assert coord.recibo()["registros_bitacora"] > 0


def test_coordinador_no_cierra_con_fase_saltada():
    coord = CoordinadorControles(fases=["a", "b"])
    with pytest.raises(FaseFueraDeOrden):
        coord.completar_fase("b")
    assert not coord.evaluar_cierre().cerrado


def test_coordinador_no_cierra_con_salida_sin_verificar():
    coord = CoordinadorControles(
        fases=["a"], campos_requeridos_salida=["resumen"]
    )
    coord.completar_fase("a")
    decision = coord.evaluar_cierre()
    assert decision.decision == "LATENTE"
    assert "salida_sin_verificar" in decision.motivos
