# FÓRMULA MASA-INERCIA v1 — lateral de observación

**Estado:** OBSERVACIÓN (no decide H, no toca ranking, no toca Engine ni catálogo 244).
**Origen:** analogía de sistemas helicoidales (tornado, tirabuzón solar) + mediciones en 6 casos
(Mozart, Napoleón, Galileo, Hawking, Che, MLK), 2026-11-13.
**Módulo:** `motor/motor/lateral_masa_inercia_v1.py` — `can_decide_H = False`.

## Definiciones (por caso, n cortes, vectores P_FULL_244 por corte)

1. **Masa por corte** `M_c` = suma del vector P_FULL_244 del corte c (244 pesos de familia).
   Base = 122 (244 × 0.5). Exceso `E_c = M_c − 122`.
2. **Radio por corte** `r_c` = distancia al origen en la proyección PCA a 2 componentes
   (centrada) de la matriz P_FULL_244 (n × 244): `r_c = √(PC1_c² + PC2_c²)`.
   El radio es invariante a rotación y a cambio de signo de los ejes PCA.
3. **Violencia radial** `V_c = |r_c − r_{c−1}|` para c = 2..n (salto radial por paso).
4. **Constante de amortiguamiento** `k = corr(V, M)` = correlación de Pearson entre la
   violencia V y la masa M (punto medio entre cortes) en los n−1 pasos.
   `k < 0` = la masa amortigua la violencia (inercia); `k ≈ 0` = no amortigua.

## Constante general y constante-función (dispersión por era)

- **Constante general:** `k_general = −0.46` (media de 6 casos, desv. 0.29).
- **Constante-función por era** (la constante es una función del contexto):
  - Era pre-s. XX (año de nacimiento < 1900): `k_esperada = −0.73`.
  - Era s. XX (año de nacimiento ≥ 1900): `k_esperada = −0.19`.
  - Dispersión: ±0.27 alrededor de la constante general.
- La era se toma del `birth_date` del caso.

## El "no" (la negación)

- `N_sup_c` = número de familias con peso < 0.5 en el corte c (familias suprimidas).
- `N_sup` = media de `N_sup_c` en los cortes.
- `D` (déficit) = media de la suma de `(0.5 − peso)` en las familias bajo 0.5.
- **Umbral:** `N_sup < 10` → se espera amortiguamiento fuerte (`k < −0.5`);
  `N_sup ≥ 10` → se espera amortiguamiento débil (`k ≥ −0.5`).
  (Medido: Mozart 5.0, Napoleón 8.6, Galileo 7.8 → fuerte; Hawking 10.7, Che 28.1,
  MLK 16.6 → débil/nulo. El "no" es el conflicto: mucha supresión = la figura
  conflictúa con el contexto y la masa no amortigua.)

## Veredicto (¿se sostiene?)

El caso **SOSTIENE** si se cumplen las dos:
- (a) Predicción por era: `|k_medido − k_esperada(era)| ≤ 0.30`.
- (b) Umbral del "no": (`N_sup < 10` y `k < −0.5`) o (`N_sup ≥ 10` y `k ≥ −0.5`).

Si no, **NO_SOSTIENE**.

## Lo que NO es esta fórmula

- No es Kepler (`μ = v²·r` no es constante: varía 80× en Mozart).
- No es balance ciclostrófico (`Vθ²/r` no es constante: varía 250×).
- No es espiral logarítmica (`r = a·e^(bθ)`: R²_log = 0.29 en Mozart).
- No es atracción `M/r²` (correlación con la violencia: −0.28 Mozart, −0.43 Napoleón, débil).
- No es la dirección de fase (consistencia suma/conflictúa no explica k: corr −0.30).
- La masa es INERCIA que amortigua, no jalón que acelera. Y solo en 3 de 6 casos
  es fuerte; en los otros 3 es débil. La fórmula describe esa dispersión, no la borra.

## Valores medidos (referencia, 2026-11-13)

| caso | k | N_sup | era | H1 |
|---|---|---|---|---|
| Mozart | −0.81 | 5.0 | pre-s.XX | autonomia_atenas |
| Napoleón | −0.745 | 8.6 | pre-s.XX | arquetipo_el_gobernante |
| Galileo | −0.628 | 7.8 | pre-s.XX | arquetipo_el_creador |
| Hawking | −0.016 | 10.7 | s.XX | arquetipo_el_sabio |
| Che | −0.193 | 28.1 | s.XX | dumezil_f2_fuerza |
| MLK | −0.361 | 16.6 | s.XX | eterno_retorno_02_cosmizacion_fundacion |
