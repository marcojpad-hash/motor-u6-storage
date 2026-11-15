#!/usr/bin/env python3
"""Verifica los 5 hallazgos de la auditoría de ChatGPT sobre Mozart en un RESULT.
Uso: python3 verificar_correccion_mozart.py <RESULT.json> [RESULT_ORIGINAL.json]
Sale 0 solo si los 5 hallazgos están corregidos (o documentados como por diseño).
Refuerzo 2026-11-14 (post-re-auditoría ChatGPT): comprobaciones expresas
1c (estado == T1_COMPLETADO) y 3e (exactamente 77 etapas CEB); 20 checks."""
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
    check("2. previo_error no es placeholder",
          ecr.get("previo_error") not in (None, "DATO_AUSENTE_REQUIERE_CLASIFICACION"),
          f"previo_error={ecr.get('previo_error')}")
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
    check("3e. CEB tiene exactamente 77 etapas",
          len(stages) == 77,
          f"n_stages={len(stages)} status={ceb.get('status')}")

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
        check("INV. H1 igual al original",
              fam(d.get("H1")) == fam(orig.get("H1")),
              f"{fam(d.get('H1'))} vs {fam(orig.get('H1'))}")
        check("INV. H2 igual al original",
              fam(d.get("H2")) == fam(orig.get("H2")),
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
        check("INV. apuesta igual al original",
              _esc((d.get("apuesta") or {}).get("escenarios")) == _esc((orig.get("apuesta") or {}).get("escenarios")) if isinstance(d.get("apuesta"), dict) else True,
              f"calibracion nueva={ (d.get('apuesta') or {}).get('calibracion')} vs vieja={ (orig.get('apuesta') or {}).get('calibracion')} (cambio esperado del 13-nov)")

    print()
    print("RESULTADO:", "TODOS LOS HALLAZGOS CORREGIDOS" if ok else "HAY FALLOS PENDIENTES")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
