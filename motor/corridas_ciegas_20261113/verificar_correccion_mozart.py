#!/usr/bin/env python3
"""Verifica los 5 hallazgos de la auditoría de ChatGPT sobre Mozart en un RESULT.
Uso: python3 verificar_correccion_mozart.py <RESULT.json> [RESULT_ORIGINAL.json]
Sale 0 solo si los 5 hallazgos están corregidos (o documentados como por diseño).
Refuerzo 2026-11-14 (post-re-auditoría ChatGPT): comprobaciones expresas
1c (estado == T1_COMPLETADO) y 3e (exactamente 77 etapas CEB); 20 checks.
2a vuelta 2026-11-14: 3e exige cada etapa EXECUTED_AND_CONNECTED
(VERIFIED_FLOW es el status agregado, no por etapa); los invariantes
exigen H1/H2 presentes y apuesta dict antes de comparar; 20 checks.
3a vuelta 2026-11-14: 2 exige previo_error/visto_error str no vacío
(la 2 aceptaba ""); 2d coherencia: una corrida no completada nunca
puede clasificarse SIN_ERROR; 22 checks."""
import json, sys
from collections import Counter

def main():
    path = sys.argv[1]
    orig_path = sys.argv[2] if len(sys.argv) > 2 else None
    d = json.load(open(path))
    orig = json.load(open(orig_path)) if orig_path else None
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name + ((" :: " + str(detail)) if detail else ""))
        if not cond:
            ok = False

    # --- Hallazgo 1: efectividad_corte_retenido.estado != FAILED ---
    ecr = d.get("efectividad_corte_retenido") or {}
    check("1. efectividad_corte_retenido.estado != INTERNAL_T1_RUN_FAILED",
          ecr.get("estado") != "INTERNAL_T1_RUN_FAILED",
          f"estado={ecr.get('estado')} hit_H={ecr.get('hit_H')}")
    check("1b. visto_status es COMPLETED",
          ecr.get("visto_status") == "COMPLETED_ISOLATED_SUBPROCESS",
          f"visto_status={ecr.get('visto_status')}")
    # Refuerzo post-re-auditoría ChatGPT (2026-11-14): el contrato declara
    # estado=T1_COMPLETADO, no solo "no falló". Exigencia expresa.
    check("1c. efectividad_corte_retenido.estado == T1_COMPLETADO",
          ecr.get("estado") == "T1_COMPLETADO",
          f"estado={ecr.get('estado')} hit_H={ecr.get('hit_H')}")

    # --- Hallazgo 2: previo_error con clasificación real (no placeholder) ---
    # 3a vuelta (2026-11-14): la comprobación aceptaba la cadena vacía (""
    # no está en (None, "DATO_AUSENTE_REQUIERE_CLASIFICACION")) y no impedía
    # que una corrida fallida se clasificara SIN_ERROR. Ahora previo_error y
    # visto_error deben ser str no vacío, y una corrida no completada nunca
    # puede llevar el SIN_ERROR que corresponde solo a la corrida completada.
    pe = ecr.get("previo_error")
    ve = ecr.get("visto_error")
    check("2. previo_error es str no vacío y no es placeholder",
          isinstance(pe, str) and bool(pe.strip())
          and pe != "DATO_AUSENTE_REQUIERE_CLASIFICACION",
          f"previo_error={pe!r}")
    check("2c. visto_error es str no vacío y no es placeholder",
          isinstance(ve, str) and bool(ve.strip())
          and ve != "DATO_AUSENTE_REQUIERE_CLASIFICACION",
          f"visto_error={ve!r}")
    check("2d. una corrida fallida nunca se clasifica SIN_ERROR",
          (ecr.get("previo_status") == "COMPLETED_ISOLATED_SUBPROCESS"
           or pe != "SIN_ERROR_CORRIDA_PREVIA_COMPLETADA")
          and (ecr.get("visto_status") == "COMPLETED_ISOLATED_SUBPROCESS"
               or ve != "SIN_ERROR_CORRIDA_RETENIDA_COMPLETADA"),
          f"previo_status={ecr.get('previo_status')} previo_error={pe!r} "
          f"visto_status={ecr.get('visto_status')} visto_error={ve!r}")
    aud = d.get("auditoria_salida_json") or {}
    check("2b. auditoria_salida_json sin faltantes",
          aud.get("faltantes_detectados") == 0 and not aud.get("rutas_faltantes"),
          f"faltantes={aud.get('faltantes_detectados')} rutas={aud.get('rutas_faltantes')}")

    # --- Hallazgo 3: CEB ---
    ceb = d.get("ceb") or {}
    stages = ceb.get("stages") or {}
    dist = Counter(s.get("status") for s in stages.values())
    check("3. ceb.status es VERIFIED_FLOW",
          ceb.get("status") == "VERIFIED_FLOW",
          f"status={ceb.get('status')} dist={dict(dist)}")
    check("3b. sin anomalías CEB",
          not ceb.get("anomalies"),
          f"anomalies={ceb.get('anomalies')}")
    check("3c. sin etapas OUTPUT_NO_OBSERVED_CONSUMER (salvo documentadas)",
          dist.get("OUTPUT_NO_OBSERVED_CONSUMER", 0) == 0,
          f"no_consumer={dist.get('OUTPUT_NO_OBSERVED_CONSUMER', 0)}")
    # el aviso All-NaN ya no existe
    raw = open(path, encoding="utf-8").read()
    check("3d. sin aviso All-NaN slice",
          "All-NaN slice encountered" not in raw)
    # Refuerzo post-re-auditoría ChatGPT (2026-11-14): el contrato declara
    # exactamente 77 etapas CEB con VERIFIED_FLOW. Exigencia expresa del conteo.
    # 2a vuelta (2026-11-14): no basta el conteo; cada una de las 77 etapas
    # debe estar individualmente en el estado bueno. OJO vocabulario: la
    # reserva pedía literalmente status == "VERIFIED_FLOW" por etapa, pero
    # ese valor NO existe por etapa: ceb_runtime_v0_6_flow.py:456 asigna
    # por etapa EXECUTED_AND_CONNECTED / OUTPUT_NO_OBSERVED_CONSUMER /
    # OUTPUT_PERSISTED_WITHOUT_CONSUMER / EXECUTED_WITH_WARNINGS, y
    # VERIFIED_FLOW es solo el status AGREGADO del CEB (ibíd.:520), que se
    # pone justo cuando no hay etapas malas ni anomalías. El equivalente
    # por etapa del agregado VERIFIED_FLOW es EXECUTED_AND_CONNECTED en
    # las 77 (verificado por ejecución: el RESULT FIX5 reproducido trae
    # 77/77 EXECUTED_AND_CONNECTED y el original 62/77).
    check("3e. CEB tiene exactamente 77 etapas, cada una EXECUTED_AND_CONNECTED",
          len(stages) == 77 and all(s.get("status") == "EXECUTED_AND_CONNECTED" for s in stages.values()),
          f"n_stages={len(stages)} connected={sum(1 for s in stages.values() if s.get('status') == 'EXECUTED_AND_CONNECTED')} no_connected={sum(1 for s in stages.values() if s.get('status') != 'EXECUTED_AND_CONNECTED')} status={ceb.get('status')}")

    # --- Hallazgo 4: Caldero ---
    filas = (((d.get("laterales_unico") or {}).get("post") or {}).get("estado_verificado") or {}).get("filas") or []
    cal = [f for f in filas if f.get("componente") == "sidecar_caldero_busqueda_arquetipos.py"]
    check("4. fila Caldero presente", len(cal) == 1, f"n={len(cal)}")
    if cal:
        check("4b. Caldero NO es FALLO_EJECUCION",
              cal[0].get("severidad") != "FALLO_EJECUCION",
              f"severidad={cal[0].get('severidad')} alerta={cal[0].get('alerta')}")
        check("4c. Caldero es INFO_FIXTURE_AUTORIZADO",
              cal[0].get("severidad") == "INFO_FIXTURE_AUTORIZADO",
              f"severidad={cal[0].get('severidad')}")
    check("4d. sin 'FALLO DE EJECUCIÓN / A INVESTIGAR: SIMULADO_FIXTURE' en el RESULT",
          "FALLO DE EJECUCIÓN / A INVESTIGAR: SIMULADO_FIXTURE" not in raw)
    res = d.get("resolucion_operativa_final") or {}
    check("4e. llm_neighbor_hints_n sigue en 0 (no se inventan pistas)",
          res.get("llm_neighbor_hints_n") == 0,
          f"llm_neighbor_hints_n={res.get('llm_neighbor_hints_n')}")

    # --- Hallazgo 5: semántica de estados ---
    sem = d.get("semantica_estados") or {}
    check("5. existe semantica_estados",
          bool(sem) and sem.get("contrato") == "SEMANTICA_ESTADOS_TERMINALES_V1",
          f"keys={sorted(sem.keys())}")
    check("5b. estado_final y predictor y compuerta registrados con su significado",
          bool(sem.get("estado_final")) and bool(sem.get("predictor_status"))
          and bool(sem.get("compuerta_cierre_decision")) and bool(sem.get("regla_consistencia")),
          f"estado_final={sem.get('estado_final')} predictor={sem.get('predictor_status')} compuerta={sem.get('compuerta_cierre_decision')}")

    # --- Invariantes: H1/H2 no cambian respecto al original ---
    if orig is not None:
        def fam(h):
            return (h or {}).get("family") or (h or {}).get("familia") or h
        # 2a vuelta (2026-11-14): H1/H2 deben EXISTIR en ambos antes de
        # comparar; si faltan en los dos, fam(None)==fam(None) aprobaba
        # en vacío.
        check("INV. H1 igual al original",
              d.get("H1") is not None and orig.get("H1") is not None
              and fam(d.get("H1")) == fam(orig.get("H1")),
              f"{fam(d.get('H1'))} vs {fam(orig.get('H1'))}")
        check("INV. H2 igual al original",
              d.get("H2") is not None and orig.get("H2") is not None
              and fam(d.get("H2")) == fam(orig.get("H2")),
              f"{fam(d.get('H2'))} vs {fam(orig.get('H2'))}")
        def _esc(e):
            # Escenario/hisótesis/n exactos; el agregado de soporte con
            # tolerancia de flotante (0.99999999 vs 1.0 es el mismo valor
            # redondeado distinto, no un cambio). La etiqueta de calibración
            # NO se compara: el canónico la corrigió el 13-nov
            # (ACTIVA_CON_DESENLACES_SELLADOS →
            # PARCIAL_CON_DESENLACES_SIN_REGLA_PRE_REGISTRADA) y la
            # re-corrida la recoge correctamente; no es un cambio de la
            # corrección de la auditoría.
            return [(s.get("escenario"), tuple(s.get("hipotesis_que_convergen") or []),
                     s.get("n_hipotesis"), round(float(s.get("soporte_estructural_agregado") or 0), 6))
                    for s in (e or [])]
        # 2a vuelta (2026-11-14): apuesta debe SER un diccionario en ambos
        # antes de comparar su contenido; antes, si no era dict, el
        # ternario aprobaba en vacío (True). El detalle también es
        # a prueba de no-dict.
        def _cal(a):
            return a.get("calibracion") if isinstance(a, dict) else None
        check("INV. apuesta igual al original",
              isinstance(d.get("apuesta"), dict) and isinstance(orig.get("apuesta"), dict)
              and _esc(d["apuesta"].get("escenarios")) == _esc(orig["apuesta"].get("escenarios")),
              f"calibracion nueva={_cal(d.get('apuesta'))} vs vieja={_cal(orig.get('apuesta'))} (cambio esperado del 13-nov)")

    print()
    print("RESULTADO:", "TODOS LOS HALLAZGOS CORREGIDOS" if ok else "HAY FALLOS PENDIENTES")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
