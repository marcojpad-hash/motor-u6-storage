# Revisión Grok — Mozart con texto Z90 (2026-11-13)

Reproducción independiente del RESULT `motor/RESULT_MOZART_CON_TEXTO_Z90_20261113.json` (commit a57e2c3, rama alterno/reconexion-2a1). Misma lógica que la revisión de Gemini sobre Napoleón: reconstruir rank_fusion cifra por cifra desde las features publicadas y contrastar contra el valor reportado.

**Actualización:** la revisión anterior (SHA 7a93aae) se bloqueó porque el RESULT no estaba en la rama. Ahora sí está (commit a57e2c3). Esta versión lo usa.

## Identidad de la corrida

- case_id: MOZART_CON_TEXTO_Z90_U6_20261113
- motor: V15.3_NATIVO (hash_candado 48333cd11b9234f1)
- patterns_sha256: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1 (244 patrones, verificado)
- sidecar: false
- predictor method: rank_fusion_fractional_ties_constant_guard_plus_bounded_lateral_plus_resolution_rescan

## Cierre reportado

| | H1 | H2 |
|---|---|---|
| familia | utopia_autonomia_atenas | utopia_mentalidad_liberal |
| rank_fusion | 32.140733 | 31.572873 |
| margen | 0.567860 | — |
| grado | FRAGIL | FRAGIL |
| peso_relativo | 0.229 | 0.224954 |
| % relleno | 59.95 | 65.43 |

Método de cierre: MOTOR_RANK_FUSION_DESEMPATA_SOLO_EN_BANDA_020. Compuerta: LATENCIA_INFORMACIONAL, cierre_propuesto=false, feeds_H=false.

## Reproducción cifra por cifra

Fórmula aplicada (de MOTOR_V15_3_UNICO_20260927.py, `_frac_scores` + lateral aditivo + resolución):

1. 40 dimensiones base (las 43 de `predictor.dimensions` menos las 3 de resolución).
2. Rank fraccional por dimensión: valores iguales comparten el rango promedio; score = 1 - avg_rank / (N-1), N=5 candidatas.
3. Suma de señales laterales crudas (`lateral_signal_contributions`, 10 señales).
4. Suma de ranks fraccionales de resolution_micro / meso / macro.

Resultado:

| candidata | reportado | reconstruido | diff |
|---|---|---|---|
| utopia_autonomia_atenas | 32.140733 | 32.140733 | -8e-8 |
| utopia_mentalidad_liberal | 31.572873 | 31.572873 | -3.3e-7 |
| 30_ambicion | 28.113657 | 28.113657 | -4.6e-7 |
| schwartz_10_autodireccion | 24.865760 | 24.865760 | +2e-8 |
| arquetipo_el_creador | 23.659369 | 23.659369 | +1.7e-7 |

Diff dentro de error de punto flotante. techo_rank = 53 (43 dims + 10 laterales). índice_fusion_relativo_0_1 H1 = 32.140733/53 = 0.606429, coincide con el publicado.

## Qué sostiene a H1 vs H2

H1 (utopia_autonomia_atenas) toma rango 1.0 en: relational_alignment, stinkbox_support, lateral_shared_evidence, trajectory_meso_support, propp_signal, propp_transgression, structural_shared_evidence, structural_contribution.

H2 (utopia_mentalidad_liberal) toma rango 1.0 en: delta, axis_convergence, geometric_inertia_alignment, geometric_direction_change, trajectory_micro_support, trajectory_acceleration_support, trajectory_inertia_alignment, trajectory_curvature_response.

Features propias H1: own_pattern_evidence 0.71, propp_signal 0.945, booker_signal 0.746, frye_support 0.693, greimas_support 0.661, structural_shared_evidence 0.761, dynamis_tokens_active = competencia + creatividad + desafio_autoridad.

Laterales H1 (crudos): traza_campo_244 0.911, plugin_reporte_3d 0.812, billar_circular_v0_2 0.667, ricci_forman_v0_1 0.638, lateral_metrics_v1_1 1.0, acero_zoomout 0.613, plugin_picos_mesetas 1.0, negativo_ricci_vs_billar 1.0, familias_tokens_puente 1.0, polti_caldero 0.0.

## Estado de componentes

Ejecutados y alimentan H: polti_caldero, traza_campo_244, plugin_reporte_3d, billar_circular_v0_2, ricci_forman_v0_1, lateral_metrics_v1_1, acero_zoomout, plugin_picos_mesetas, motor_interrelacion_extensible, sujetos_014, dynamis_dramatica_sistemica, stinkbox_transport, filtro_relleno_013, stinkbox_to_light_bus, laterales_unico_v1 (pre), hub:negativo_ricci_vs_billar, hub:familias_tokens_puente, hipotesis_trayectoria_abierta.

Ejecutados sin alimentar H (TRAZA_SOLO o ACTIVA_MUDA): geometria, otto_numinoso, embudo_clinico, trayectoria_hosteleria (SIN_SENAL), estabilidad_vectorial, aquiles_h, capa2_antecedentes, plugin_arquetipos_dinamicos (SIN_SENAL), predictor_vecinos_prefijo_v1 (SIN_PREFIJO_EN_INPUT), cameo_*, sidecar_caldero (FIXTURE), pre_h_analogical_search (FIXTURE), compuerta_cierre, guardianes, ruta_cierre_latente, predictibilidad_set_021.

Dimensiones excluidas por constante (23): relational_activity, caldero_neighbor_*, cameo_*, geometric_*_context/latest_movement, propp_damage, greimas_opponent_friction, coupling_opponent, dynamis_* (varios buckets en 0), analog_alignment. Motivo documentado en dimension_guard.

## Lectura

El motor cerró H1/H2 por rank_fusion con margen 0.56786 (banda FRAGIL). La reproducción independiente confirma que el número es la suma exacta de ranks fraccionales de 40 dimensiones + 10 laterales crudos + 3 ranks de resolución. No hay señal lateral dominante única; H1 gana por convergencia de Propp, estructura y laterales de traza/reporte_3d, mientras H2 gana en geometría e inercia. Caldero de vecinos no aportó (SIN_PREFIJO_EN_INPUT). La compuerta no detuvo la ejecución ni cambió el orden.

Revisión hecha sobre el RESULT sellado. No se reejecutó el motor.
