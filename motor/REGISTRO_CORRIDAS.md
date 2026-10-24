# Registro resumido de corridas U6 — 2026-10-20

Este registro no sustituye los resultados completos archivados. Los hashes permiten identificar los originales en los ZIP de origen.

## Bruno unificado

- Caso: `GIORDANO_BRUNO_V15_3_PATCH09_20261010`
- H1: `arquetipo_el_sabio`
- H2: `spengler_02_verano_otono_racionalizacion`
- Cortes: 8
- Monte Carlo declarado: `True`
- R732 dX_norm: `[0.5611982626487719,0.5417329600458145,0.4968473206126808,0.4713095797880624,0.5909167792506826,0.3783846852080565,0.289558491500422]`
- SHA-256 del JSON original: `1b66e7e53ac3f895d37d342f63d0b62214a56b769cf23e70999f5b316d46ded6`

## Temístocles unificado

- Caso: `CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2`
- H1: `13_enemistad_de_parientes`
- H2: `social_08_girard_mimesis_y_chivo_expiatorio`
- Cortes: 3
- Monte Carlo declarado: `True`
- R732 dX_norm: `[0.7835499345925567,0.6702733024669862]`
- SHA-256 del JSON original: `c85e66cf6274c1baa430a2758264ec288c475505ebb55783067018d12a06a699`

## Bruno pre-unificación

- Caso: `GIORDANO_BRUNO_V15_3_PATCH09_20261010`
- H1: `arquetipo_el_sabio`
- H2: `spengler_02_verano_otono_racionalizacion`
- Cortes: 8
- Monte Carlo declarado: `True`
- R732 dX_norm: `[0.5611982626487719,0.5417329600458145,0.4968473206126808,0.4713095797880624,0.5909167792506826,0.3783846852080565,0.289558491500422]`
- SHA-256 del JSON original: `296b90dfa12102e5e05514e1d0997be04da2abd360ec8ba103554d44ef2b79de`

## Temístocles pre-unificación

- Caso: `CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2`
- H1: `13_enemistad_de_parientes`
- H2: `social_08_girard_mimesis_y_chivo_expiatorio`
- Cortes: 3
- Monte Carlo declarado: `True`
- R732 dX_norm: `[0.7835499345925567,0.6702733024669862]`
- SHA-256 del JSON original: `a6c360d83fb8c75177b26daf5961f14a72c8667ffc5a02fafea0f64f7acba029`

## Comparación antes/después de la unificación

El informe de unificación reporta igualdad de H1, H2, orden de candidatos, R732 y `rank_fusion` entre pre-unificación y unificado para Temístocles y Bruno. El manifiesto reportó `MATCH`, deriva 0, archivos ausentes 0 y archivos fuera de lista 0. Los laterales no alteraron la huella del resultado del motor.

### Geometría

- Temístocles: 3 cortes; insuficientes para validar hélice.
- Giordano Bruno: 8 cortes; 0 de 244 trayectorias con forma helicoidal según el criterio operativo de esa corrida.
- La jerarquía construida a partir de P/A/C es inferida, no una jerarquía recursiva nativa.
- Ricci sigue siendo un indicador de deriva temporal, no curvatura Ricci–Forman geométrica validada.

## Archivos originales omitidos de esta distribución

Los JSON completos, ledgers y outputs se retiraron de los paquetes operativos para evitar duplicarlos. Se registran sus hashes de origen en `HASHES_HISTORICOS_SHA256.json`; los ZIP originales recibidos conservan la evidencia bruta sin alteración.


## 2026-10-20 — SMOKE_STINKBOX_SINGLE_CUT (prueba de cableado; no calibración)

- Runner: `correr_estandar.py`; un corte; Monte Carlo ejecutado (2.592 simulaciones en tres observaciones internas).
- H1: `arquetipo_el_heroe`; H2: `crisis_vocacional`. Resultado técnico, no pronóstico calibrado.
- StinkBox: registro persistente OK; 7 eventos nuevos para el registro, 0 cadenas únicas nuevas porque ya figuraban en la línea base.
- Búsqueda externa obligatoria: `FAILED_REQUIRED_STAGE`; la corrida no es válida para evaluación predictiva.
- Se ejecutó también una prueba sintética de token fuera de catálogo. Detectó un falso equivalente por subcadena (`token_prueba_fuera_catalogo` → `prueba`); el defecto fue corregido y quedó cubierto por regresión.

- Segunda prueba sintética: `token_prueba_fuera_catalogo` quedó `PENDIENTE_REVISION`, sin equivalencia por subcadena; la importación automática quedó `OK`. Esta prueba solo verifica el cableado de descubrimiento.


## 2026-10-20 — Temístocles, puente de búsqueda ciega

- Caso variante: `CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2_CALDERO_BRIDGE_20261020`; 3 cortes; búsqueda conectada con 5 fuentes y `external_archetype_search_receipt.status=EXECUTED`.
- H1 `13_enemistad_de_parientes`; H2 `30_ambicion`; cierre `RESUELTO_OPERACIONALMENTE`; Monte Carlo: 7.273 simulaciones.
- La corrida produjo JSON de resultado y recibo, pero la invocación superó el límite de 200 s antes de la etapa automática de persistencia. Se importaron manualmente 188 eventos de evidencia; 54 tokens únicos nuevos quedaron en el registro, clasificados como vocabulario externo. La fuente, input, recibo y resumen compacto están en `STINKBOX_PERSISTENTE_20261020/imported_runs/`.
- Estado predictivo: `NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES`; no se cuenta como acierto/error por falta de reveal posterior.
