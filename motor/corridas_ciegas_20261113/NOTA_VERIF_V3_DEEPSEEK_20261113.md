# Verificación v3 — Revisión de DeepSeek aplicada

**Fecha:** 2026-11-13 ~19:10 CST
**Origen:** revisión de DeepSeek al JSON de comparación + paper v2
(pasada por Marco 2026-11-13 ~19:02 CST)
**Veredicto de Pecas:** DeepSeek acertó en 9 de 10 puntos de su checklist.
Cada reclamo se verificó contra archivos, código y datos antes de corregirlo.

## Verificación de cada reclamo

| # | Reclamo | Veredicto | Evidencia |
|---|---------|-----------|-----------|
| a | Cometas Transición1/Mandela no separables del pulso | REAL | Medido: 18% y 19% de toda la masa_favor del run llega en el corte del cometa (Napoleón 16%, Mozart 11%). |
| b | Mozart -0.777 presentada como hallazgo | REAL | n=6, BAJA_MUESTRA. La lectura ahora dice NO CONCLUYENTE. |
| c | desv/spread mal etiquetados | REAL | Ahora desv_poblacional y spread_max_min (JSON y paper §10). |
| d | n_prop coincide con nudos | FALSA ALARMA | Coincide en todos los casos (DeepSeek mismo lo dice). |
| e | salida.version en v1 | FALSA ALARMA | El JSON ya estaba en v2 (cero strings v1). DeepSeek leyó copia vieja. El paper §13 sí estaba en v1 y se corrigió. |
| f | §13 ejemplo en v1 | REAL | Corregido a v3. |
| g | Fecha consistente | OK | Sin cambio. |
| h | Régimen con dos strings | REAL | Canónico definido (string largo); "MESETA" es display (§3, §12). |
| i | Tesla con tipos inconsistentes | REAL | Contrato añadido: si no hay meseta, gravedad no aparece; las listas son siempre listas (§13). Comparación usa n_* (conteos). |
| j | Sol como nudo | VERIFICADO | El Sol NUNCA es nudo (excluido por definición, bajo-top5). Salto propio de H1 en el cometa: Napoleón -0.003, Mozart -0.012, Bolívar +0.012, Transición1 +0.029, Mandela +0.108 (~10x menor que el salto de los nudos). |
| k | Distancia negativa | VERIFICADO | 0 distancias negativas en 5 casos + Bolívar. La regla la cubre (dist <= 0.01 → CAPTURADO). |
| l | Unidades heterogéneas | REAL | Pendiente = rango/corte, distancia = peso. La correlación es solo de signo, no de elasticidad (§8.4). |
| m | Punto por respaldo, no EMERGE | REAL | dumezil_f2_fuerza rango 23 > 20 → respaldo (§6, §11). |

## Cambios v3

- **Código** (`lateral_comportamiento_post_meseta_v1.py`, VERSION v3): la
  lectura degrada la proporcionalidad si es BAJA_MUESTRA ("NO CONCLUYENTE");
  documentados Sol-nunca-nudo, distancia negativa y cometa-pulso.
- **Paper y spec JSON** (v3): todas las correcciones del checklist.
- **Contrato** (`COMPORTAMIENTO_POST_MESETA_V1.md`): sección Gravedad
  actualizada a v3.

## Verificación v3 (números idénticos a v1/v2)

| Caso | Sol | Peso | Cometa | Prop | Confianza (n) |
|------|-----|------|--------|------|---------------|
| NAPOLEON_FINAL27 | gobernante | 0.7813 | C9 (3, 0.32) | +0.568 | NO CONCLUYENTE (7) |
| MOZART_Z90 | autonomia_atenas | 0.7985 | C6 (6, 0.482) | -0.777 | NO CONCLUYENTE (6) |
| TRANSICION1_Z90 | creador | 0.8006 | C7_1448 (8, 0.651) * | +0.295 | ALTA (20) |
| MANDELA_HEROE | kwml_01_rey | 0.8013 | C3_1961 (10, 1.077) * | +0.078 | ALTA (16) |
| BOLIVAR_Z90 | gobernante | 0.8155 | C5 (9, 1.045) | -0.232 | MEDIA (11) |

\* Salto no separable del pulso de input.

## Archivos cambiados (v3)

- `motor/motor/lateral_comportamiento_post_meseta_v1.py` (VERSION v3_20261113)
- `motor/COMPORTAMIENTO_POST_MESETA_V1.md`
- `motor/corridas_ciegas_20261113/PAPER_COMPORTAMIENTO_POST_MESETA_GRAVEDAD_V1.md`
- `motor/corridas_ciegas_20261113/SPEC_COMPORTAMIENTO_POST_MESETA_GRAVEDAD_V1.json`
