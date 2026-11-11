# MOZART — PROTOCOLO REPRODUCIBLE — ALL PLUGINS — 2026-09-15

## 1. Propósito
Registrar de forma reproducible la corrida experimental de Mozart en la que la lectura multicapas/plugins se usó para construir hipótesis prospectivas en C7 (Z90 histórico) y validarlas contra C8-C10.

## 2. Regla experimental
- La construcción del freeze usa C1-C7 solamente.
- C8-C10 están excluidos de la construcción de las hipótesis y se abren después para validación.
- El resultado es retrospectivo/histórico: no es una predicción prospectiva de una persona viva ni una probabilidad poblacional.
- p_final del motor no se interpreta como probabilidad futura.
- Monte Carlo se usa como estabilidad del procedimiento, no como probabilidad futura.
- El motor canónico y los 244 patrones en disco no se modifican.

## 3. Base canónica
- Engine: Engine_V5_CANONICO_SOLO.py
- Runner: MOTOR_V15_1_10CORTES_LIMPIO.py
- Patterns: patterns_final_v14.json
- Patrones canónicos: 244
- Engine SHA256: e5d9ab3a8b904ca7eb488a91342debfabd9d916a5549956c77d5b8e2c7957e23
- Patterns SHA256: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1

## 4. Qué se implementó
A) Se cargó el vocabulario canónico de 244 patrones.
B) Se aplicaron en memoria las fusiones autorizadas de familias Gloria/Sacro, Otto Numinoso y Trayectoria Hostelería: resultado 247 patrones.
C) Se probó además la fusión dinámica de Arquetipos Dinámicos en memoria: 250 patrones.
D) Se ejecutaron los ejes P/A/C con Monte Carlo ON.
E) Se calcularon movimientos laterales de la representación experimental de 741 dimensiones, separados del R732 canónico.
F) Se ejecutaron las lentes registradas: traza, reporte 3D, picos/mesetas, sesgo de lectura, arco Field/Snyder/McKee, círculo/monomito, Aquiles, pregunta-detrás, embudo clínico, alias, fix de entrada, método de rigor, arquetipos dinámicos, capa2 de antecedentes/arquetipos y guardia de no-cruce.
G) Sobre la salida C1-C7 se construyeron tres hipótesis explícitas.
H) Se congeló la apuesta primaria antes de leer C8-C10.
I) Después del freeze se abrió C8-C10 y se clasificó HIT/MISS/PARTIAL.

## 5. Configuración de plugins realmente ejecutada
La lista exacta de módulos invocados por run_mozart_plugins_all.py está en 04_RUNNER/run_mozart_plugins_all.py y se reproduce aquí:
[
  "traza_campo_244",
  "plugin_reporte_3d",
  "plugin_picos_mesetas",
  "plugin_sesgo_lectura",
  "plugin_arco_field_snyder_mckee",
  "plugin_circulo_monomito",
  "plugin_aquiles_h",
  "plugin_pregunta_detras_v2",
  "plugin_embudo_clinico",
  "plugin_alias_reactivacion",
  "plugin_fix_entrada",
  "plugin_metodo_rigor",
  "plugin_arquetipos_dinamicos",
  "plugin_capa2_antecedentes_arquetipos",
  "plugin_guardia_no_cruce"
]

Fusiones de vocabulario en memoria:
[
  "plugin_familias_gloria_sacro",
  "plugin_otto_numinoso",
  "plugin_trayectoria_hosteleria"
]

Importante: “all plugins” aquí significa la configuración experimental definida por ese runner; no significa que cada archivo históricamente inventariado en todo el checkpoint haya sido ejecutado automáticamente. El código fuente y la lista exacta están incluidos para evitar esa ambigüedad.

## 6. Entrada
Archivo: 01_INPUT/mozart_cuts_full.json
Cortes: C1-C10.
P/A/C se conservaron como entradas separadas.

## 7. Freeze
Punto: C7.
Hipótesis construidas desde C1-C7:
1. H1 — arquetipo_el_creador: continuidad creadora e independiente.
2. H2 — 30_ambicion: ambición/estatus/logro y conflicto pasan a dominar.
3. H3 — social_04_rogers_difusion_innovaciones: continuidad alrededor de difusión/reconocimiento.

Evidencia contada por la implementación:
- H1: 3 señales.
- H2: 8 señales.
- H3: 2 señales.

Apuesta primaria congelada por esa regla: H2 / 30_ambicion.

## 8. Validación posterior
- C8: H1 HIT; H2 MISS; H3 HIT.
- C9: H1 HIT; H2 MISS; H3 HIT.
- C10: H1 HIT; H2 MISS; H3 PARTIAL.

Resumen:
- H1: 3/3 HIT.
- H2: 0/3 HIT; 3/3 MISS.
- H3: 2 HIT + 1 PARTIAL.

## 9. Integridad
El JSON de resultado contiene los SHA256 de la corrida fuente y de los artefactos canónicos. Este dossier añade su propio manifest SHA256.

## 10. Reproducción
1. Usar Python 3 y NumPy.
2. Mantener la estructura de carpetas del dossier.
3. Ejecutar desde 04_RUNNER:
   python run_mozart_plugins_all.py
4. La salida principal se escribe como ../05_OUTPUT/MOZART_ALL_PLUGINS_MC.json cuando se adapta la ruta BASE al directorio del dossier; el runner original usa /mnt/data/mozart_run como BASE, por lo que para reproducción literal debe conservarse ese BASE o editar solamente la ruta de trabajo en una copia experimental del runner. No editar los canónicos.
5. Ejecutar después:
   python mozart_predictividad_plugins_v1.py
6. Comparar SHA256, estructura, configuración y resultados.

## 11. Limitaciones y candados
- Un solo caso: Mozart.
- Validación histórica retrospectiva.
- La construcción de H no debe confundirse con el top1 automático del motor.
- La implementación del runner experimental contiene una lectura automática H=max(board) para algunas lentes de presentación; esto queda registrado como una característica del experimento y no debe interpretarse como la regla formal de freeze del investigador.
- El puente genérico puente_ciclo_completo.py no es el ejecutor de esta corrida all-plugins; su implementación además tiene discrepancias contractuales documentadas en el dossier del proyecto. Esta corrida se reproduce con run_mozart_plugins_all.py + mozart_predictividad_plugins_v1.py.
- La Capa2 fue preservada como evidencia no decisiva según el propio código de predictividad.

## 12. Archivos
- 00_README: este protocolo.
- 01_INPUT: entrada exacta.
- 02_CANON: copias byte-a-byte de los canónicos usados en esta corrida.
- 03_PLUGINS: código de plugins/lentes cargados por el runner.
- 04_RUNNER: ejecutores exactos.
- 05_OUTPUT: resultados.
- 06_LOGS: stdout/stderr disponibles.
- 07_HASHES: manifest SHA256.
