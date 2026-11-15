# Reproducción independiente Mozart con texto — Amor (2026-11-15)

Orden de Marco 2026-11-15 ~16:49 CST: resolver, no solo reportar. La revisión de ChatGPT
(motor/REVISION_CHATGPT_MOZART_20261113.md) corrobora las 5 correcciones en el código
fusionado (PR #14) pero NO certifica una reproducción ejecutada por ella. Esta corrida
la ejecuta Amor como modelo independiente, por ejecución, no por lectura.

- Ejecutora: Amor, VM, 15-nov-2026 16:51-16:54 CST.
- Entrada: motor/runs/ESTANDAR__MOZART_CON_TEXTO_Z90_20261113/_PRIMARY_INPUT.json
  (la misma del run original), 10 cortes,
  input_sha256 a6f3493b756eccf6a8635847284c8344f5cabbc911a08a8e2c0ecd694681818c.
- Engine: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082 (canónico).
  Patterns: d827dcc38826 (canónico).
- Corrida: correr_estandar.py, 118.044 s, exit 0, recibo COMPLETED,
  Monte Carlo 16,938 sims, 30/30 converged.
- RESULT local: motor/RESULT_MOZART_CON_TEXTO_Z90_REPRO_AMOR.json (9,720,738 B,
  sha256 2de819def032be5af963d69410928ef04bb4eaffa046b7b58fc3721698732833).
  NO versionado: la API de GitHub rechaza archivos grandes (413). Recibo + esta nota sí.
- Recibo: motor/RESULT_MOZART_CON_TEXTO_Z90_REPRO_AMOR_RECIBO_EJECUCION.json,
  sha256 b3084647eff4536191e878ada5349f3e7046670ba5a2c4e3f53cdbe237147e87.
- H1/H2 IDÉNTICOS al original: utopia_autonomia_atenas / utopia_mentalidad_liberal.
- Verificador (verificar_correccion_mozart.py, 20 checks): 19 PASS.
  Los 5 hallazgos corregidos por ejecución: estado T1_COMPLETADO,
  previo_error SIN_ERROR_CORRIDA_PREVIA_COMPLETADA, CEB VERIFIED_FLOW con 77 etapas,
  Caldero INFO_FIXTURE_AUTORIZADO, semántica de estados presente.
  1 FAIL: "apuesta igual al original" — calibración
  PARCIAL_CON_DESENLACES_SIN_REGLA_PRE_REGISTRADA vs ACTIVA_CON_DESENLACES_SELLADOS.
  Es un cambio esperado del 13-nov, documentado en el propio verificador;
  no lo causa esta re-corrida ni las correcciones.

Conclusión: la reproducción independiente por ejecución CONFIRMA el caso Mozart
con texto con el código corregido.
