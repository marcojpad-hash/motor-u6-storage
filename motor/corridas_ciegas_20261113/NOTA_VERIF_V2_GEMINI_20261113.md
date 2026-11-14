# Verificación v2 — Revisión de Gemini aplicada

**Fecha:** 2026-11-13 ~19:15 CST
**Origen:** revisión de Gemini al paper/spec v1 (pasada por Marco 2026-11-13 ~18:54 CST)
**Veredicto de Pecas:** los 3 riesgos de Gemini son reales y se verificaron
contra el código antes de corregirlos.

## Los 3 riesgos y su corrección

1. **Pearson con pocos nudos es frágil.** El código calculaba la
   correlación con apenas 3 pares, sin etiqueta de confianza. Con n=3 o n=6
   un solo valor atípico puede invertir el signo y cambiar la lectura de
   convergencia a consolidación. Corrección: la proporcionalidad lleva ahora
   su n y su confianza (BAJA_MUESTRA si n<8, MEDIA si 8-11, ALTA si n>=12),
   en `leer_gravedad` y en `proyectar_gravedad`.

2. **EN_TRANSITO contradecía su definición.** La franja intermedia
   (0.2<=pendiente<0.5) caía en EN_TRANSITO sin importar la distancia,
   aunque el texto la definía como "cerca del Sol". Corrección: nuevo estado
   ACERCANDOSE para nudos lejos del Sol (dist>0.05) con pendiente media;
   EN_TRANSITO queda solo para nudos cerca del Sol (0.01<dist<=0.05).

3. **Reglas borde no estaban en el spec.** El desempate del cometa y la
   varianza cero ya estaban bien en el código (comparación estricta -> gana
   el corte más temprano; `sd>0 and sp>0` -> None), pero no estaban
   documentados. Corrección: documentados en el código, el contrato, el
   paper y el spec JSON.

## Verificación v2 en los 5 casos

| Caso | Sol | Peso | Nudos | Capt | Jal | Acer | Res | Cometa | Prop | Confianza (n) |
|------|-----|------|-------|------|-----|------|-----|--------|------|---------------|
| NAPOLEON_FINAL27 | gobernante | 0.7813 | 7 | 2 | 3 | 0 | 1 | C9 (3, 0.32) | +0.568 | BAJA_MUESTRA (7) |
| MOZART_Z90 | autonomia_atenas | 0.7985 | 6 | 0 | 1 | 2 | 1 | C6 (6, 0.482) | -0.777 | BAJA_MUESTRA (6) |
| TESLA_F001_02 | CONTINUIDAD_ASCENDENTE (muda) | — | 0 | 0 | 0 | 0 | 0 | — | — | — |
| TRANSICION1_Z90 | creador | 0.8006 | 20 | 0 | 12 | 0 | 2 | C7_1448 (8, 0.651) | +0.295 | ALTA (20) |
| MANDELA_HEROE | kwml_01_rey | 0.8013 | 16 | 1 | 9 | 0 | 1 | C3_1961 (10, 1.077) | +0.078 | ALTA (16) |

**Los números (sol, peso, cometa, proporcionalidad) son idénticos a v1.**
Solo Mozart reclasifica 2 nudos: `situacion_dramatica_ambicion`
(dist 0.072, pend 0.3571) y `dumezil_desequilibrio_f3_come_al_resto`
(dist 0.072, pend 0.3214) pasan de EN_TRANSITO a ACERCANDOSE — la
contradicción exacta que señaló Gemini.

**La confianza es honesta:** Napoleón (+0.568, n=7) y Mozart (-0.777, n=6)
quedan en BAJA_MUESTRA — el signo es frágil y hay que leerlo con esa
advertencia. Transición1 (n=20) y Mandela (n=16) son ALTA.

## Archivos cambiados (v2)

- `motor/motor/lateral_comportamiento_post_meseta_v1.py` (VERSION v2_20261113)
- `motor/COMPORTAMIENTO_POST_MESETA_V1.md`
- `motor/corridas_ciegas_20261113/PAPER_COMPORTAMIENTO_POST_MESETA_GRAVEDAD_V1.md`
- `motor/corridas_ciegas_20261113/SPEC_COMPORTAMIENTO_POST_MESETA_GRAVEDAD_V1.json`
