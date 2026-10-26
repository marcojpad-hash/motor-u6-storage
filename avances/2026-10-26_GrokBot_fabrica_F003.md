# 2026-10-26 — GrokBot — fábrica de casos, lote F003

## Qué cambió
- Lote F003: 10 sujetos históricos nuevos (ninguno repetido de calibracion_acumulada.csv, Lote 01, los 15 ciegos sellados, Mozart, Musk, Papa Pío ni Casanova). 6 caídas/rupturas y 4 auges.
- Semillas en `casos/fabrica/semillas_lote_F003.py` (formato de F002; toda afirmación con su enlace de Wikipedia en inglés, consultado 2026-10-26). Preparado con `fabrica.py preparar-z` (el README obliga a `preparar-z`; `preparar` a secas quedó solo para F001) → compuerta GATE_Z_TRABAJO_20261024 OK.
- Destinos, familias y lista negra del custodio: `/workspace/FABRICA_CUSTODIA/F003/destinos_lote_F003.py` (fuera del repo); lo sellado vive en `cola/CAL_F003_*/desenlace_sellado.json` y `destino_sellado.json`.
- **Aviso de ceguera:** a diferencia de lo que declaró F002, en F003 las semillas (`GrokBot-preparador-ciego-F003`) y los destinos (`GrokBot-custodio-rutina-F003`) los escribió **el mismo ejecutor en la misma sesión**. La ceguera es solo de procedimiento: las semillas usan únicamente hechos ≤ Z, pasan la compuerta Z (sin años posteriores, sin lenguaje de futuro) y la lista negra del custodio. Los sujetos se eligieron sabiendo su desenlace (lo pide el encargo).
- Ajustes hechos solo al texto de las semillas para pasar la compuerta (sin tocar protocolo): se quitó "probablemente" (Caravaggio); se reemplazó "sería su propio primer ministro" (Fouquet); se quitó una afirmación de Trotski fechada solo "1923-10" (cae después de Z=1923-10-15); Z de Lavoisier/Faraday/Carnegie/Pedro II pasó al primer día del periodo siguiente (1790-01-01, 1822-01-01, 1873-01-01, 1888-09-01) porque la compuerta toma una fecha parcial como "último instante del periodo"; Sketches by Boz fechado febrero 1836 (fuente: página Sketches_by_Boz).
- `lotes/F003_PRECOMPROMISO_REGLA.json` escrito ANTES de correr (regla 022 congelada por sha256).

## Antes → ahora
- casos/fabrica/cola/CAL_F003_01…10/ — antes: no existían → ahora: entrada.json, desenlace_sellado.json, destino_sellado.json.
- casos/fabrica/lotes/F003_PRECOMPROMISO_REGLA.json, F003_COMPROMISO.json, F003_RESUMEN.json — antes: no existían → ahora: creados.
- casos/fabrica/calibracion_acumulada.csv — antes: 20 filas → ahora: 30 filas.
- casos/fabrica/CALIBRACION_ACUMULADA.md — regenerado.
- stinkbox/tokens.jsonl y casos/resultados/resultados.jsonl — sincronizados por el propio `correr` (commit automático 15ad68c, "corrida F003: resumen + 22651 observaciones StinkBox", igual que pasó con F002 en 1df3cb9).

## Hashes canónicos verificados (antes y después: iguales)
- motor/motor/Engine_V5_CANONICO_SOLO.py `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`
- motor/motor/patterns_final_v14.json (244) `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`
- motor/motor/apuesta_destino_personal_022.py `4252fd4564877183fd8be86f579fdde59635eb547c139a04dd79acedc349b302`
- Candados de `correr` antes/después y en la copia temporal: todos true. `git diff HEAD -- motor/` vacío.

## Pruebas
motor/tests/test_arnes_calibracion.py 7/7. Corrida F003: 10 casos, 9 sellados, 1 NO_SELLADO (Faraday: exit 6, TORTUGAS_REQUIERE_CONTINUACION, pausa reanudable; las dos primeras hipótesis quedaron a 0.027 de distancia y la medida de relleno/tortugas que desempata no estuvo disponible — comportamiento previsto por el README, no cuenta). Compuerta Caldero: OK (11/11 EJECUTADO). Compuerta piezas: OK (0 FALLO_EJECUCION, 0 REQUIERE_CONTRATO). Registro sellado sha256 8bcf80ae2c7f2663734898ae6abded9f1c659d11ec6f22a8de1dd39f6d036575.

## Resultados F003
| Caso (Z) | Real | H1 | Set | Apuesta | Destino apostado | Destino |
|---|---|---|---|---|---|---|
| Caravaggio 1605-12-31 | ruptura | no | no | no | ruptura | sí |
| Dickens 1836-04-02 | auge | sí | sí | sí | auge | sí |
| Lavoisier 1790-01-01 | ruptura | no | no | no | auge | no |
| Faraday 1822-01-01 | auge | NO_SELLADO | — | — | — | — |
| Fouquet 1661-08-17 | ruptura | no | sí | sí | caida | no (polaridad sí) |
| Trotski 1923-10-15 | caida | no | no | no | caida | sí |
| Lincoln 1858-10-15 | auge | no | sí | sí | caida | no |
| John Law 1720-01-31 | ruptura | no | sí | no | caida | no (polaridad sí) |
| Carnegie 1873-01-01 | auge | sí | sí | sí | auge | sí |
| Pedro II 1888-09-01 | ruptura | no | no | no | caida | no (polaridad sí) |

F003: H1 2/9, H2 3/9, set 5/9, apuesta 4/9, destino exacto 4/9, polaridad 7/9.

## Acumulado (30 filas, 27 evaluados, 3 no sellados; F001 y F001_D022 son los mismos 5 sujetos contados dos veces)
H1 6/27, H2 3/27, set 9/27, apuesta 6/27, destino exacto 9/22, polaridad 14/22.

## Patrón visible
- Sesgo de continuidad intacto: el escenario principal salió CONTINUIDAD_ASCENDENTE en los 9 sellados, incluidas las 6 caídas/rupturas. Las familias de H1/H2 siguen siendo de logro/obtención/ambición (schwartz_07_logro, 12_obtencion, 30_ambicion) aunque la persona vaya a caer.
- En cambio, la apuesta de destino 022 sí leyó la bajada: polaridad correcta en 5 de 6 caídas/rupturas (falló Lavoisier, que apostó auge). Pero confunde "caída" con "ruptura" (Fouquet, Law, Pedro II) y en Lincoln apostó caída cuando vino un auge.
- Los aciertos de H1 llegan cuando el desenlace es un auge de logro (Dickens, Carnegie), igual que Pasteur/Rockefeller en F002.

## Fuentes flojas
- Todas las afirmaciones vienen de Wikipedia en inglés en vivo (secundaria, consultada 2026-10-26), igual que F002; no hay copias congeladas ni fuentes primarias.
- Dickens: el dato "seis chelines" del trabajo en Warren's está en el texto del hecho, pero la evidencia citada solo respalda las jornadas de diez horas.
- Caravaggio C1: "se supone que por influencia de del Monte" (Wikipedia dice "presumably").
