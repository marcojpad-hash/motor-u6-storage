# NAPOLEON_CON_TEXTO_Z90_20261115 — comparación con FINAL27 (sin texto)

Corrida: 2026-11-15, `motor/correr_estandar.py` sobre
`motor/corridas_ciegas_20261113/entrada_NAPOLEON_CON_TEXTO_Z90_20261115.json`
(construida por `build_napoleon_con_texto.py` desde el input congelado de FINAL27).
Recibo: `motor/RESULT_NAPOLEON_CON_TEXTO_Z90_20261115_RECIBO_EJECUCION.json`
(status COMPLETED, 148.484 s, Monte Carlo true; engine 665c39a2…, patterns d827dcc3…).
RESULT: `motor/RESULT_NAPOLEON_CON_TEXTO_Z90_20261115.json` (10,646,454 B);
copia en `motor/runs/ESTANDAR__NAPOLEON_CON_TEXTO_Z90_20261115/_PRIMARY_RESULT.json`
(solo en la copia local de la VM).

NOTA 2026-11-15: el RESULT (10,646,454 B) NO está en el repo. La API de
GitHub lo rechazó al subirlo a
`motor/runs/ESTANDAR__NAPOLEON_CON_TEXTO_Z90_20261115/_PRIMARY_RESULT.json`
(HTTP 413, request body too large; el RESULT de Mozart de 8.4 MB ya había
sido rechazado por lo mismo). La entrada y el recibo SÍ están en el repo;
el RESULT se reproduce corriendo `motor/correr_estandar.py` sobre la entrada
(mismo random_seed 20261111, Engine 665c39a2…, patterns d827dcc3…).
Primer intento: TIMEOUT interno 90 s (exit=3, sin RESULT); segundo intento: OK
(exit=124 por el colgado posterior, RESULT+RECIBO completos — comportamiento conocido).

## Diferencia con FINAL27: solo el texto
- Mismo P/A/C y mismos pesos (verificado por assert en el constructor).
- Mismo random_seed (20261111) para aislar el efecto del texto.
- 10 cortes con `hecho` + `narracion` (prosa verificada con las 4 fuentes
  Wikipedia ya citadas en FINAL27), `fuentes_por_corte`, `caldero_search_sources`
  y fixture reescritos por corte (formato Mozart con texto).

## Resultado
| Medida | FINAL27 (sin texto) | CON_TEXTO | Delta |
|---|---|---|---|
| H1 | arquetipo_el_gobernante (FRAGIL) | arquetipo_el_gobernante (FRAGIL) | sin cambio |
| H2 | 30_ambicion (FRAGIL) | 30_ambicion (FRAGIL) | sin cambio |
| margen rank_fusion | 0.914454 | 0.476954 | −0.437 (se achica) |
| giro (sonda v1) | 236.6° | 236.6° | 0.0° |
| Sol (gravedad post-meseta) | 0.79–0.80 (serie) | 0.7813 | en rango |
| cometa | C9 | C9 (3 nudos, salto 0.32) | mismo corte |
| en_meseta | sí | sí (MESeta_O_ESTABILIZACION) | igual |

Lectura post-meseta + traductor:
`motor/runs/ESTANDAR__NAPOLEON_CON_TEXTO_Z90_20261115/LECTURA_NAPOLEON_CON_TEXTO.json`
- `leer_resultado()`: en_meseta=True, 7 nudos, proporcionalidad 0.568 NO CONCLUYENTE
  (BAJA_MUESTRA); `proyectar_gravedad()`: cometa_previsto=null.
- `traducir()` v2.8: `violaciones=['heroe']` → lectura reemplazada por la frase
  genérica segura. Colisión conocida (familia suelta `heroe` vs palabra común
  "héroe"; `arquetipos_luces` trae `arquetipo_heroe`). El anexo sale completo
  y correcto; solo la lectura se pierde. Pendiente: distinguir en
  `_verificar_lectura` el ID de familia de la palabra común.

## Conclusión
El texto NO mueve H1/H2 ni el giro ni el cometa; solo achica el margen
(0.914 → 0.477). La geometría es la misma; el texto solo mueve los márgenes
del ranking. El par gobernante+ambición sigue empatado en banda (< 1.0),
como en FINAL27.
