# Inventario de casos biográficos vs protocolo Z90

Generado: 2026-11-11T03:14:00 (America/Mexico_City).

## Regla

En biografías de personas muertas, la Z de trabajo es la Z90: el 90% del intervalo entre nacimiento y muerte. Los cortes son acumulativos desde el nacimiento y su número lo pide la biografía (nunca un número fijo; 3 cortes no bastan). El último corte pre-Z termina en la Z90. Todo lo posterior queda sellado y solo sirve para validar (como en el Mozart original: C1–C7 hasta 1788-05-04, C8–C10 post-Z). En preguntas vivas, Z = hoy.

Nacimiento y muerte se leen de los campos del input o de los markers del mismo paquete. Si no están y la identidad es clara, se anotan fechas de fuente pública, marcadas como tales. No se inventaron cortes ni fechas dentro de los archivos copiados: las copias están sin modificar.

Veredictos: **CONFORME** (Z = Z90 ±6 meses y ≥5 cortes pre-Z); **Z_MAL_PUESTA**; **POCOS_CORTES**; **SIN_FECHAS**; **VIVO_Z_HOY**. Puede haber dos banderas juntas.

Deduplicación por SHA-256 del archivo. Se descartan copias en `runs/` a la hora de elegir la fuente, aunque se cuenta cuántas había. Se prefiere el paquete más antiguo o sellado.

Inputs únicos: **108**.

## Resumen de veredictos

- `Z_MAL_PUESTA;POCOS_CORTES`: 52
- `SIN_FECHAS;POCOS_CORTES`: 24
- `Z_MAL_PUESTA`: 10
- `CONFORME`: 9
- `SIN_FECHAS`: 7
- `VIVO_Z_HOY`: 4
- `POCOS_CORTES`: 2

## Mejores candidatos para recalibrar (CONFORME)

Candidatos preferidos (Z bien puesta, ≥5 cortes pre-Z, y no son el Mozart rearmado de octubre):

- **Ernesto Che Guevara** (``): 9 pre-Z / 0 post-Z; Z declarada 1963-11-03 vs Z90 1963-11-03; fuente `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/MARTIRES_Z90/_cuts_che_run.json` (`9f3baec1110e`). Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública (marcadas).
- **Galileo Galilei** (`GALILEO_NUEVO_EJERCICIO_20260924`): 10 pre-Z / 0 post-Z; Z declarada 1634-03-25 vs Z90 1634-03-26; fuente `/workspace/pred_hist_bio_in/inbox_20260926_zips/012bddf1/GALILEO_NUEVO_EJERCICIO_20260924.json` (`878f8a6d3088`). Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública (marcadas).
- **Giordano Bruno** (`GIORDANO_BRUNO_V15_3_PATCH09_20261010`): 8 pre-Z / 0 post-Z; Z declarada 1594-12-31 vs Z90 1594-12-01; fuente `/workspace/MOTOR_1019/U6_UNIFICADO_20261020/inputs/GIORDANO_BRUNO_PATCH19_COMPACTO.json` (`56daf3601390`). Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública (marcadas).
- **Martin Luther King Jr.** (``): 8 pre-Z / 0 post-Z; Z declarada 1964-05-03 vs Z90 1964-05-03; fuente `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/MARTIRES_Z90/_cuts_mlk_run.json` (`7e42cc4c7c7c`). Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública (marcadas).
- **Stephen Hawking** (``): 7 pre-Z / 0 post-Z; Z declarada 2010-12-30 vs Z90 2010-08-01; fuente `/workspace/HAWKING_Z90_INFORME_COMPLETO_20260919/02_datos_corrida/_cuts_hawking_Z90_run.json` (`7083daa2c46f`). Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Nota: el último corte pre-Z (2011-12-31) dista más de 12 meses de la Z de referencia.
- **Wolfgang Amadeus Mozart** (`MOZART_NOCTURNA_20261005`): 7 pre-Z / 3 post-Z; Z declarada — vs Z90 1788-05-04; fuente `/workspace/CORRIDA_NOCTURNA_20261005/CORRIDA_0547_20261006/inputs/INPUT_CAPA2_MOZART.json` (`b51131a713e1`). Sin Z declarada en campo, pero el último corte pre-Z cae a ±6 meses de la Z90 calculada y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública.
- **Wolfgang Amadeus Mozart** (`MOZART_NOCTURNA_20261005`): 7 pre-Z / 3 post-Z; Z declarada — vs Z90 1788-05-04; fuente `/workspace/CORRIDA_NOCTURNA_20261005/inputs/INPUT_ESTANDAR_MOZART.json` (`cc51218bbdc3`). Sin Z declarada en campo, pero el último corte pre-Z cae a ±6 meses de la Z90 calculada y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública.
- **Wolfgang Amadeus Mozart** (``): 7 pre-Z / 3 post-Z; Z declarada — vs Z90 1788-05-04; fuente `/workspace/alt_cameo/fuentes_originales/202609/MOZART_PROTOCOLO_REPRODUCIBLE_ALL_PLUGINS_20260915/01_INPUT/mozart_cuts_full.json` (`a86ab3e48c23`). Sin Z declarada en campo, pero el último corte pre-Z cae a ±6 meses de la Z90 calculada y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública.

También salen CONFORME en números, pero no se recomiendan como molde: el Mozart `MOZART_FRESH_Z90_U6_20261014` tiene la Z90 bien calculada y 10 cortes pre-Z, pero no es el original (en el de septiembre C8–C10 son post-Z).

- **Wolfgang Amadeus Mozart** (`MOZART_FRESH_Z90_U6_20261014`): 10 pre-Z / 0 post-Z; fuente `/workspace/IN_t860/INPUT_FROZEN.json` (`a2e2158bab9d`).

## Tabla

| # | Persona / id | Fuente (sha12, fecha) | Nacimiento | Muerte | Z90 calc. | Z declarada | Pre/post | Último corte pre-Z | Veredicto |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Ernesto Che Guevara | `_cuts_che_run.json` `9f3baec1110e` 2026-11-07 | 1928-06-14 | 1967-10-09 * | 1963-11-03 * | 1963-11-03 | 9/0 (n=9) | C9: 1963-11-15 | `CONFORME` |
| 2 | Galileo Galilei | `GALILEO_NUEVO_EJERCICIO_20260924.json` `878f8a6d3088` 2026-09-26 | 1564-02-15 * | 1642-01-08 * | 1634-03-26 * | 1634-03-25 | 10/0 (n=10) | G_C10_Z90: 1634-03-25 | `CONFORME` |
| 3 | Giordano Bruno | `GIORDANO_BRUNO_PATCH19_COMPACTO.json` `56daf3601390` 2026-10-20 | 1548-01-01 * | 1600-02-17 * | 1594-12-01 * | 1594-12-31 | 8/0 (n=8) | C8: 1594-12-01 | `CONFORME` |
| 4 | Martin Luther King Jr. | `_cuts_mlk_run.json` `7e42cc4c7c7c` 2026-11-07 | 1929-01-15 | 1968-04-04 * | 1964-05-03 * | 1964-05-03 | 8/0 (n=8) | C8: 1964-05-03 | `CONFORME` |
| 5 | Stephen Hawking | `_cuts_hawking_Z90_run.json` `7083daa2c46f` 2026-09-19 | 1942-01-08 | 2018-03-14 | 2010-08-01 | 2010-12-30 | 7/0 (n=7) | C7: 2011-12-31 | `CONFORME` |
| 6 | Wolfgang Amadeus Mozart | `INPUT_CAPA2_MOZART.json` `b51131a713e1` 2026-10-05 | 1756-01-27 * | 1791-12-05 * | 1788-05-04 * | — | 7/3 (n=10) | C7: 1788-05-04 | `CONFORME` |
| 7 | Wolfgang Amadeus Mozart | `INPUT_ESTANDAR_MOZART.json` `cc51218bbdc3` 2026-10-05 | 1756-01-27 * | 1791-12-05 * | 1788-05-04 * | — | 7/3 (n=10) | C7: 1788-05-04 | `CONFORME` |
| 8 | Wolfgang Amadeus Mozart | `INPUT_FROZEN.json` `a2e2158bab9d` 2026-11-07 | 1756-01-27 | 1791-12-05 | 1788-05-04 | 1788-05-04 | 10/0 (n=10) | C10: 1788-05-04 | `CONFORME` |
| 9 | Wolfgang Amadeus Mozart | `mozart_cuts_full.json` `a86ab3e48c23` 2026-09-15 | 1756-01-27 * | 1791-12-05 * | 1788-05-04 * | — | 7/3 (n=10) | C7: 1788-05-04 | `CONFORME` |
| 10 | Abraham Lincoln | `entrada.json` `8633e12924db` 2026-11-11 | 1809-02-12 * | 1865-04-15 * | 1859-09-02 * | 1858-10-15 | 3/0 (n=3) | C3_1858: 1858-10-15 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 11 | Alan Turing | `entrada.json` `1ac923395579` 2026-11-11 | 1912-06-23 * | 1954-06-07 * | 1950-03-28 * | 1952-01-01 | 2/1 (n=3) | C2_1950: 1950-10-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 12 | Albert Einstein | `entrada.json` `0965b7ae2e69` 2026-11-11 | 1904-01-01 | 1955-04-18 * | 1950-03-02 * | 1904-01-01 | 3/0 (n=3) | C3_1904: 1904-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 13 | Andrew Carnegie | `entrada.json` `2f292231c6a4` 2026-11-11 | 1835-11-25 * | 1919-08-11 * | 1911-03-29 * | 1872-01-01 | 3/0 (n=3) | C3_1872: 1872-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 14 | Antoine Lavoisier | `entrada.json` `33e508f4b5b2` 2026-11-11 | 1743-08-26 * | 1794-05-08 * | 1789-04-12 * | 1789-01-01 | 3/0 (n=3) | C3_1789: 1789-01-01 | `POCOS_CORTES` |
| 15 | Benito Mussolini | `entrada.json` `ad61bff24f8e` 2026-11-11 | 1883-07-29 * | 1945-04-28 * | 1939-02-24 * | 1942-11-08 | 3/0 (n=3) | C3_1942: 1942-11-08 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 16 | C01 | `entrada.json` `767c9710672e` 2026-11-11 | — | — | — | 1781-01-01 | 2/1 (n=3) | C2_1777: 1777-09-23 | `SIN_FECHAS;POCOS_CORTES` |
| 17 | C02 | `entrada.json` `5601543947d2` 2026-11-11 | — | — | — | 1859-01-01 | 2/1 (n=3) | C2_1844: 1844-07-01 | `SIN_FECHAS;POCOS_CORTES` |
| 18 | C03 | `entrada.json` `8ba09c5eee0b` 2026-11-11 | — | — | — | 1687-01-01 | 2/1 (n=3) | C2_1672: 1672-01-11 | `SIN_FECHAS;POCOS_CORTES` |
| 19 | C04 | `entrada.json` `1fbeec7becfe` 2026-11-11 | — | — | — | 1879-01-01 | 2/1 (n=3) | C2_1878: 1878-09-01 | `SIN_FECHAS;POCOS_CORTES` |
| 20 | C05 | `entrada.json` `064f64f29dd0` 2026-11-11 | — | — | — | 1599-01-01 | 3/0 (n=3) | C3_1599: 1599-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 21 | C06 | `entrada.json` `8a3727f8a58d` 2026-11-11 | — | — | — | 1605-01-01 | 2/1 (n=3) | C2_1580: 1580-09-19 | `SIN_FECHAS;POCOS_CORTES` |
| 22 | C07 | `entrada.json` `cfb95e0abbed` 2026-11-11 | — | — | — | 1609-01-01 | 3/0 (n=3) | C3_1609: 1609-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 23 | C08 | `entrada.json` `ffe195b1fbec` 2026-11-11 | — | — | — | 1854-01-01 | 2/1 (n=3) | C2_1853: 1853-08-12 | `SIN_FECHAS;POCOS_CORTES` |
| 24 | C09 | `entrada.json` `f9b6d0cf6807` 2026-11-11 | — | — | — | 1429-01-01 | 1/2 (n=3) | C1_1428: 1428-05-01 | `SIN_FECHAS;POCOS_CORTES` |
| 25 | C10 | `entrada.json` `cbd75d94450c` 2026-11-11 | — | — | — | C3_0800 | 3/0 (n=3) | C3_0800: 0800-12-25 | `SIN_FECHAS;POCOS_CORTES` |
| 26 | C11 | `entrada.json` `c05ab0c81640` 2026-11-11 | — | — | — | 1520-01-01 | 2/1 (n=3) | C2_1514: 1514-08-23 | `SIN_FECHAS;POCOS_CORTES` |
| 27 | C12 | `entrada.json` `598b32b0df62` 2026-11-11 | — | — | — | 1547-01-01 | 2/1 (n=3) | C2_1545: 1545-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 28 | C13 | `entrada.json` `58e13aa87788` 2026-11-11 | — | — | — | 1206-01-01 | 3/0 (n=3) | C3_1206: 1206-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 29 | C14 | `entrada.json` `d19b345f912d` 2026-11-11 | — | — | — | 1492-01-01 | 2/1 (n=3) | C2_1491: 1491-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 30 | C15 | `entrada.json` `9b669466fa1f` 2026-11-11 | — | — | — | 1519-01-01 | 2/1 (n=3) | C2_1517: 1517-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 31 | C16 | `entrada.json` `e0986541ef21` 2026-11-11 | — | — | — | 1275-01-01 | 2/1 (n=3) | C2_1273: 1273-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 32 | C17 | `entrada.json` `7502f1a7ad2d` 2026-11-11 | — | — | — | 1302-01-01 | 2/1 (n=3) | C2_1301: 1301-11-01 | `SIN_FECHAS;POCOS_CORTES` |
| 33 | C18 | `entrada.json` `47f160eea05f` 2026-11-11 | — | — | — | 1508-01-01 | 3/0 (n=3) | C3_1508: 1508-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 34 | C19 | `entrada.json` `d834a155a0b6` 2026-11-11 | — | — | — | 1642-01-01 | 3/0 (n=3) | C3_1642: 1642-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 35 | C20 | `entrada.json` `356b25ecc848` 2026-11-11 | — | — | — | 1514-01-01 | 3/0 (n=3) | C3_1514: 1514-01-01 | `SIN_FECHAS;POCOS_CORTES` |
| 36 | Calvin Coolidge | `entrada.json` `ce093eb238f1` 2026-11-11 | 1872-07-04 * | 1933-01-05 * | 1926-12-18 * | 1925-03-04 | 3/0 (n=3) | C3_1925: 1925-03-04 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 37 | Catalina Alexéievna (nacida Sofía de Anhalt-Zerbst) | `entrada.json` `267264ce6425` 2026-11-11 | 1729-05-02 * | 1796-11-17 * | 1790-02-15 * | 1762-05-05 | 3/0 (n=3) | C3_1762: 1762-05-05 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 38 | Charles Dickens | `entrada.json` `2715f0870655` 2026-11-11 | 1812-02-07 * | 1870-06-09 * | 1864-08-08 * | 1836-04-02 | 3/0 (n=3) | C3_1836: 1836-04-02 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 39 | Coco Chanel | `entrada.json` `a6cac4f38bb7` 2026-11-11 | 1883-08-19 * | 1971-01-10 * | 1962-04-15 * | 1919-12-22 | 3/0 (n=3) | C3_1919_12: 1919-12-22 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 40 | Elizabeth Holmes | `CAL_LOTE01_08_HOLMES.json` `d6ec5dae5082` 2026-11-07 | — | — | — | 2015-01-01 | 2/1 (n=3) | C2_2014: 2014-06-12 | `SIN_FECHAS;POCOS_CORTES` |
| 41 | Emmy Noether | `_cuts_ciego_Z90_run.json` `db82da5c23aa` 2026-09-14 | 1882-07-01 | 1935-04-14 * | 1930-01-02 * | 1932-07-01 | 6/1 (n=7) | C7: 1932-12-31 | `Z_MAL_PUESTA` |
| 42 | Ferdinand de Lesseps | `entrada.json` `8f9e1695fdba` 2026-11-11 | 1805-11-19 * | 1894-12-07 * | 1886-01-10 * | 1886-01-01 | 3/0 (n=3) | C3_1886: 1886-01-01 | `POCOS_CORTES` |
| 43 | Fritz Haber | `entrada.json` `578a5e3b85e5` 2026-11-11 | 1868-12-09 * | 1934-01-29 * | 1927-07-26 * | 1932-01-01 | 3/0 (n=3) | C3_1932: 1932-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 44 | Galileo Galilei | `entrada.json` `7774f41d9de1` 2026-11-11 | 1564-02-15 * | 1642-01-08 * | 1634-03-26 * | 1632-02-22 | 3/0 (n=3) | C3_1632: 1632-02-22 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 45 | Giacomo Casanova | `INPUT_CASANOVA_SEARCH_MC_OFF.json` `bc3b9b6e2fc1` 2026-10-20 | 1725-04-02 | 1798-06-04 | 1791-02-08 | 1791-12-31 | 10/0 (n=10) | C10: 1791-12-31 | `Z_MAL_PUESTA` |
| 46 | Giacomo Casanova | `INPUT_CASANOVA_SEARCH_MC_ON.json` `c938aeeeda10` 2026-10-20 | 1725-04-02 | 1798-06-04 | 1791-02-08 | 1791-12-31 | 10/0 (n=10) | C10: 1791-12-31 | `Z_MAL_PUESTA` |
| 47 | Giacomo Casanova | `INPUT_ESTANDAR_CASANOVA.json` `76e3cf190024` 2026-11-07 | 1725-04-02 | 1798-06-04 | 1791-02-08 | 1791-12-31 | 10/0 (n=10) | C10: 1791-12-31 | `Z_MAL_PUESTA` |
| 48 | Gregor Mendel | `entrada.json` `8ba5c5ee7295` 2026-11-11 | 1822-07-20 * | 1884-01-06 * | 1877-11-13 * | 1866-01-01 | 3/0 (n=3) | C3_1866: 1866-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 49 | Gustave Courbet | `entrada.json` `a81708648e0f` 2026-11-11 | 1819-06-10 * | 1877-12-31 * | 1872-02-22 * | 1871-04-27 | 3/0 (n=3) | C3_1871_04: 1871-04-27 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 50 | Harry S. Truman | `entrada.json` `1691fb7f5844` 2026-11-11 | 1884-05-08 * | 1972-12-26 * | 1964-02-15 * | 1948-01-01 | 3/0 (n=3) | C3_1948_07: 1948-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 51 | Henry Ford | `CAL_LOTE01_07_FORD.json` `a9ebf27e65fe` 2026-11-07 | 1863-07-30 * | 1947-04-07 * | 1938-11-23 * | 1903-01-01 | 2/1 (n=3) | C2_1901: 1901-11-30 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 52 | Herbert Hoover | `entrada.json` `2dad1342091f` 2026-11-11 | 1874-08-10 * | 1964-10-20 * | 1955-10-14 * | 1928-01-01 | 3/0 (n=3) | C3_1928: 1928-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 53 | Herman Melville | `entrada.json` `14cf75067e75` 2026-11-11 | 1819-08-01 * | 1891-09-28 * | 1884-07-10 * | 1851-01-01 | 3/0 (n=3) | C3_1851: 1851-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 54 | Ignaz Semmelweis | `CAL_LOTE01_03_SEMMELWEIS.json` `9cc748fb17f2` 2026-11-07 | 1818-07-01 * | 1865-08-13 * | 1860-11-26 * | 1849-01-01 | 2/1 (n=3) | C2_1847: 1847-05-15 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 55 | Isabel Tudor (Isabel I de Inglaterra) | `entrada.json` `678978f96d93` 2026-11-11 | 1533-09-07 * | 1603-03-24 * | 1596-04-09 * | 1558-01-01 | 3/0 (n=3) | C3_1558_10: 1558-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 56 | Ivar Kreuger | `entrada.json` `9b3f8cd9326c` 2026-11-11 | 1880-03-20 * | 1932-03-12 * | 1926-12-31 * | 1931-01-01 | 3/0 (n=3) | C3_1931: 1931-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 57 | J. Robert Oppenheimer | `entrada.json` `b51580b50f6b` 2026-11-11 | 1904-04-22 * | 1967-02-18 * | 1960-11-06 * | 1953-01-01 | 3/0 (n=3) | C3_1953_06: 1953-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 58 | Jacques-Louis David | `entrada.json` `da23e1a1cfad` 2026-11-11 | 1748-08-30 * | 1825-12-29 * | 1818-04-06 * | 1794-06-08 | 3/0 (n=3) | C3_1794_06: 1794-06-08 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 59 | Johann Sebastian Bach | `entrada.json` `805d719d412f` 2026-11-11 | 1685-03-31 * | 1750-07-28 * | 1744-01-15 * | 1723-05-30 | 3/0 (n=3) | C3_1723: 1723-05-30 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 60 | John D. Rockefeller | `entrada.json` `8d817fffc938` 2026-11-11 | 1839-07-08 * | 1937-05-23 * | 1927-08-09 * | 1870-01-10 | 3/0 (n=3) | C3_1870: 1870-01-10 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 61 | John Law | `entrada.json` `6e7ac5463956` 2026-11-11 | 1671-04-21 * | 1729-03-21 * | 1723-06-06 * | 1720-01-05 | 3/0 (n=3) | C3_1720: 1720-01-05 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 62 | Joseph McCarthy | `entrada.json` `a84c20ef8b32` 2026-11-11 | 1908-11-14 * | 1957-05-02 * | 1952-06-27 * | 1954-02-18 | 3/0 (n=3) | C3_1954: 1954-02-18 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 63 | Juan Pablo II | `IN_JPII_Z1995.json` `3e2d9db98968` 2026-10-11 | 1920-05-18 * | 2005-04-02 * | 1996-10-06 * | 1995-12-31 | 9/0 (n=9) | — | `Z_MAL_PUESTA` |
| 64 | Kenneth Lay | `entrada.json` `8f31b2115721` 2026-11-11 | 1942-04-15 * | 2006-07-05 * | 2000-02-01 * | 2001-01-01 | 3/0 (n=3) | C3_2001_07: 2001-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 65 | Kurt Cobain | `IN_COBAIN_Z1990.json` `988b59bfc482` 2026-10-11 | 1967-02-20 * | 1994-04-05 * | 1991-07-19 * | 1990-01-01 | 9/0 (n=9) | C9: 1990-01-01 | `Z_MAL_PUESTA` |
| 66 | Kurt Cobain | `COBAIN_Z1990_EJERCICIO_CIEGO_COMPLETO.json` `90ff9cf09ea5` 2026-11-07 | 1967-02-20 * | 1994-04-05 * | 1991-07-19 * | 1990-01-01 | 9/0 (n=9) | C9: 1990-01-01 | `Z_MAL_PUESTA` |
| 67 | León Trotski | `entrada.json` `e92fd2825725` 2026-11-11 | 1879-11-07 * | 1940-08-21 * | 1934-07-24 * | 1923-10-15 | 3/0 (n=3) | C3_1923: 1923-10-15 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 68 | Louis Pasteur | `entrada.json` `53fc65d239ad` 2026-11-11 | 1822-12-27 * | 1895-09-28 * | 1888-06-19 * | 1884-06-15 | 3/0 (n=3) | C3_1884: 1884-06-15 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 69 | Ludwig van Beethoven | `CAL_LOTE01_06_BEETHOVEN.json` `432c9dfa85e9` 2026-11-07 | 1770-12-17 * | 1827-03-26 * | 1821-08-09 * | 1802-01-01 | 2/1 (n=3) | C2_1800: 1800-04-02 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 70 | Luis II de Baviera | `entrada.json` `c834c0bf3fab` 2026-11-11 | 1845-08-25 * | 1886-06-13 * | 1882-05-15 * | 1885-01-01 | 3/0 (n=3) | C3_1885: 1885-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 71 | Luis XVI de Francia | `entrada.json` `905cd94e3734` 2026-11-11 | 1754-08-23 * | 1793-01-21 * | 1789-03-20 * | 1791-01-01 | 3/0 (n=3) | C3_1791: 1791-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 72 | Lázaro Cárdenas | `CAL_LOTE01_10_CARDENAS.json` `744f7be3d03c` 2026-11-07 | 1895-05-21 * | 1970-10-19 * | 1963-04-05 * | 1936-01-01 | 2/1 (n=3) | C2_1935: 1935-06-15 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 73 | Marie Curie | `CAL_LOTE01_04_CURIE.json` `034a133f493c` 2026-11-07 | 1867-11-07 * | 1934-07-04 * | 1927-11-03 * | 1906-01-01 | 2/1 (n=3) | C2_1903: 1903-12-10 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 74 | Michael Faraday | `entrada.json` `7dad402f8256` 2026-11-11 | 1791-09-22 * | 1867-08-25 * | 1860-01-21 * | 1821-01-01 | 3/0 (n=3) | C3_1821: 1821-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 75 | Michelangelo Merisi da Caravaggio | `entrada.json` `953aadc15725` 2026-11-11 | 1571-09-29 * | 1610-07-18 * | 1606-08-31 * | 1605-01-01 | 3/0 (n=3) | C3_1605: 1605-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 76 | Mijaíl Gorbachov | `CAL_LOTE01_09_GORBACHEV.json` `4132e6ce0147` 2026-11-07 | 1931-03-02 * | 2022-08-30 * | 2013-07-06 * | 1988-01-01 | 2/1 (n=3) | C2_1986: 1986-04-26 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 77 | Napoleón Bonaparte | `entrada.json` `e05645ddb3ea` 2026-11-11 | 1769-08-15 * | 1821-05-05 * | 1816-03-03 * | 1812-01-01 | 2/1 (n=3) | C2_1805: 1805-12-02 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 78 | Nicolas Fouquet | `entrada.json` `2c7af97e3fe8` 2026-11-11 | 1615-01-01 * | 1680-03-23 * | 1673-09-14 * | 1661-08-17 | 3/0 (n=3) | C3_1661: 1661-08-17 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 79 | Nicolás II de Rusia | `entrada.json` `f9d43876d181` 2026-11-11 | 1868-05-18 * | 1918-07-17 * | 1913-07-11 * | 1916-12-30 | 3/0 (n=3) | C3_1916_12: 1916-12-30 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 80 | Nikita Jrushchov | `entrada.json` `91988e3a6342` 2026-11-11 | 1894-04-15 * | 1971-09-11 * | 1963-12-15 * | 1963-01-01 | 3/0 (n=3) | C3_1963: 1963-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 81 | Nikola Tesla | `entrada.json` `be89b315b99b` 2026-11-11 | 1856-07-10 * | 1943-01-07 * | 1934-05-15 * | 1901-01-01 | 2/1 (n=3) | C2_1893: 1893-05-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 82 | Oscar Wilde | `entrada.json` `54247ffa2a4f` 2026-11-11 | 1854-10-16 * | 1900-11-30 * | 1896-04-19 * | 1895-01-01 | 1/2 (n=3) | C1_1891: 1891-06-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 83 | Pedro II de Brasil | `entrada.json` `1668c4dff7d7` 2026-11-11 | 1825-12-02 * | 1891-12-05 * | 1885-04-29 * | 1888-01-01 | 3/0 (n=3) | C3_1888: 1888-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 84 | Pío II / Enea Silvio Piccolomini | `INPUT_CAPA2_PAPA_PIO.json` `3e9261fafa58` 2026-10-05 | 1405-10-18 | 1464-08-14 | 1458-09-26 | 1464-08-14 | 10/0 (n=10) | C10: 1464-08-01 | `Z_MAL_PUESTA` |
| 85 | Pío II / Enea Silvio Piccolomini | `INPUT_ESTANDAR_PAPA_PIO.json` `942c593d3fb5` 2026-10-05 | 1405-10-18 | 1464-08-14 | 1458-09-26 | 1464-08-14 | 10/0 (n=10) | C10: 1464-08-01 | `Z_MAL_PUESTA` |
| 86 | Richard Nixon | `CAL_LOTE01_01_NIXON.json` `ad6f139dda32` 2026-11-07 | 1913-01-09 * | 1994-04-22 * | 1986-03-06 * | 1973-01-01 | 2/1 (n=3) | C2_1972: 1972-11-07 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 87 | Richard Wagner | `entrada.json` `ff8e2bf77851` 2026-11-11 | 1813-05-22 * | 1883-02-13 * | 1876-02-23 * | 1863-01-01 | 3/0 (n=3) | C3_1863: 1863-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 88 | Roscoe 'Fatty' Arbuckle | `entrada.json` `f737feea7743` 2026-11-11 | 1887-03-24 * | 1933-06-29 * | 1928-11-12 * | 1920-01-01 | 3/0 (n=3) | C3_1920: 1920-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 89 | Steve Jobs | `jobs_corrected_backend.json` `31ea1efd9d30` 2026-11-07 | 1955-02-24 * | 2011-10-05 * | 2006-02-05 * | — | 5/0 (n=5) | 1989-1991: 1991-12-31 | `Z_MAL_PUESTA` |
| 90 | Steve Jobs | `entrada.json` `c556241e0491` 2026-11-11 | 1955-02-24 * | 2011-10-05 * | 2006-02-05 * | 1996-01-01 | 3/0 (n=3) | C3_1996: 1996-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 91 | Themistocles | `THEMISTOCLES_FREEZE_480BC.json` `dce6f796a42a` 2026-10-20 | — | — | — | — | 3/0 (n=3) | — | `SIN_FECHAS;POCOS_CORTES` |
| 92 | Themistocles | `THEMISTOCLES_FREEZE_480BC_WITH_SEARCH_BRIDGE.json` `ee524314dfc6` 2026-10-20 | — | — | — | — | 3/0 (n=3) | — | `SIN_FECHAS;POCOS_CORTES` |
| 93 | Themistocles | `THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json` `6067686f138e` 2026-10-20 | — | — | — | C3_480BC | 3/0 (n=3) | — | `SIN_FECHAS;POCOS_CORTES` |
| 94 | Vincent van Gogh | `CAL_LOTE01_05_VANGOGH.json` `628b24529fd8` 2026-11-07 | 1853-03-30 * | 1890-07-29 * | 1886-11-04 * | 1888-01-01 | 1/2 (n=3) | C1_1880: 1880-08-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 95 | Walt Disney | `entrada.json` `d546c10647b2` 2026-11-11 | 1901-12-05 * | 1966-12-15 * | 1960-06-14 * | 1928-01-01 | 2/1 (n=3) | C2_1927: 1927-09-05 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 96 | William C. Durant | `entrada.json` `e3d8254732e6` 2026-11-11 | 1861-12-08 * | 1947-03-18 * | 1938-09-06 * | 1919-01-01 | 3/0 (n=3) | C3_1919: 1919-01-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 97 | Winston Churchill | `CAL_LOTE01_02_CHURCHILL.json` `5858c5deedea` 2026-11-07 | 1874-11-30 * | 1965-01-24 * | 1956-01-19 * | 1939-01-01 | 2/1 (n=3) | C2_1933: 1933-06-01 | `Z_MAL_PUESTA;POCOS_CORTES` |
| 98 | CIEGO_09 | `IN_CIEGO_09.json` `a64d7d3e2343` 2026-10-11 | — | — | — | — | 5/0 (n=5) | — | `SIN_FECHAS` |
| 99 | CIEGO_10 | `IN_CIEGO_10.json` `98480f5c3b22` 2026-10-11 | — | — | — | — | 6/0 (n=6) | — | `SIN_FECHAS` |
| 100 | CIEGO_11 | `IN_CIEGO_11.json` `80ed20a73046` 2026-10-11 | — | — | — | — | 7/0 (n=7) | — | `SIN_FECHAS` |
| 101 | CIEGO_12 | `IN_CIEGO_12.json` `51990be562ed` 2026-10-11 | — | — | — | — | 6/0 (n=6) | — | `SIN_FECHAS` |
| 102 | CIEGO_14 | `IN_CIEGO_14.json` `af1ccd887e61` 2026-10-11 | — | — | — | — | 6/0 (n=6) | — | `SIN_FECHAS` |
| 103 | CIEGO_15_ANTECEDENTES_C | `IN_CIEGO_15.json` `dd79011441dc` 2026-10-11 | — | — | — | — | 6/0 (n=6) | — | `SIN_FECHAS` |
| 104 | Elon Musk | `CASO_CIEGO_MUSK_RETROSPECTIVA.json` `728eba2554d1` 2026-11-07 | — | — | — | — | 2/0 (n=2) | — | `VIVO_Z_HOY` |
| 105 | Elon Musk | `INPUT_CAPA2_MUSK.json` `d19acb7a1485` 2026-10-05 | 1971-06-28 | — | — | 2026-09-24 | 10/0 (n=10) | C10: 2026-09-24 | `VIVO_Z_HOY` |
| 106 | Elon Musk | `INPUT_ESTANDAR_MUSK.json` `dd8f06e02423` 2026-10-05 | 1971-06-28 | — | — | 2026-09-24 | 10/0 (n=10) | C10: 2026-09-24 | `VIVO_Z_HOY` |
| 107 | Elon Musk | `IN_CIEGO_13_MUSK.json` `9f48f196b371` 2026-10-11 | — | — | — | — | 6/0 (n=6) | — | `VIVO_Z_HOY` |
| 108 | Rachel Carson | `_cuts_ciego_Z90_B_run.json` `3804069c8652` 2026-09-14 | 1907-05-27 * | 1964-04-14 * | 1958-08-06 * | Z≈90% lifespan | 7/0 (n=7) | — | `SIN_FECHAS` |

\* = fecha o Z90 calculada con fuente pública, no con un campo del input. El archivo copiado no se alteró.

## Detalle por caso

### 1. Ernesto Che Guevara — ``

- Fuente original: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/MARTIRES_Z90/_cuts_che_run.json`
- SHA-256: `9f3baec1110ea3b8c4971697ea985597e9b04701bc79603fc2e2e129309fc12a` (corto `9f3baec1110e`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:55
- Copia en repo: `inputs/001_Ernesto_Che_Guevara_9f3baec1110e/_cuts_che_run.json`
- Markers del mismo paquete: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/MARTIRES_Z90/markers_che_Z1963.json` (`02305b0ac1a5`)
- Nacimiento (input): 1928-06-14 (markers.born=1928-06-14)
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Ernesto Che Guevara): muerte=1967-10-09
- Z90 calculada (90% nacimiento→muerte): 1963-11-03
- Z declarada en el input: 1963-11-03 (normalizada: 1963-11-03)
- Cortes: 9 total; pre-Z 9 / post-Z 0; vs Z90 calculada: pre 9 / post 0
- Último corte pre-Z: C9 1963-11-15
- Veredicto: `CONFORME` — Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1` 1928-01-01→1940-12-31: 1928-1940s Rosario/Córdoba: infancia clase media, asma, entorno familiar estable; rutina de estudios previos a medicina
  - `C2` 1948-01-01→1953-12-31: c.1948-1953 Córdoba: estudios de medicina; conciencia social creciente; aún no salto político armado
  - `C3` 1951-01-01→1952-12-31: 1951-1952 viaje en motocicleta por América del Sur: contacto con pobreza e injusticia; incidente detonante de vocación política
  - `C4` ?→1954-12-31: 1954 Guatemala: caída de Árbenz / intervención; radicalización; hostilidad del orden regional
  - `C5` 1955-01-01→1956-12-31: 1955-1956 México: encuentro con Castro (mentor); compromiso con Granma; partida hacia Cuba
  - `C6` 1956-01-01→1958-12-31: 1956-1958 Granma/Sierra Maestra: guerra de guerrillas; pruebas, aliados y enemigos; audacia y riesgo
  - `C7` ?→1959-12-31: 1959 triunfo revolucionario / entrada a La Habana: victoria colectiva; celebración; nuevo poder
  - `C8` 1959-01-01→1962-12-31: 1959-1962 cargos ministeriales / industria / diplomacia revolucionaria: organización del Estado; tensión ideal vs pragmatismo
  - `C9` ?→1963-11-15 [Z_foto]: Z≈1963-11 (90% vida): aún vivo en órbita cubana; idealismo internacionalista alto; inquietud de nueva lucha; Bolivia/muerte sellados

### 2. Galileo Galilei — `GALILEO_NUEVO_EJERCICIO_20260924`

- Fuente original: `/workspace/pred_hist_bio_in/inbox_20260926_zips/012bddf1/GALILEO_NUEVO_EJERCICIO_20260924.json`
- SHA-256: `878f8a6d3088dbad3744e4fe85aa6ad9f74b3935f8169afdabf71852f3b305ca` (corto `878f8a6d3088`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:52; paquete: 2026-09-26
- Copia en repo: `inputs/002_GALILEO_NUEVO_EJERCICIO_20260924_878f8a6d3088/GALILEO_NUEVO_EJERCICIO_20260924.json`
- Otras copias con el mismo hash: 35 (ej. `/workspace/pred_hist_bio_in/TRANSFER_V15_1/IN_20260926_REBUILD/v15_rebuild/test/GALILEO_NUEVO_EJERCICIO_20260924.json`)
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Galileo Galilei): nacimiento=1564-02-15; fuente pública (Galileo Galilei): muerte=1642-01-08
- Z90 calculada (90% nacimiento→muerte): 1634-03-26
- Z declarada en el input: 1634-03-25 (normalizada: 1634-03-25)
- Cortes: 10 total; pre-Z 10 / post-Z 0; vs Z90 calculada: pre 10 / post 0
- Último corte pre-Z: G_C10_Z90 1634-03-25
- Veredicto: `CONFORME` — Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `G_C1` ?→1573-01-01: 1573-01-01
  - `G_C2` ?→1580-01-01: 1580-01-01
  - `G_C3` ?→1590-01-01: 1590-01-01
  - `G_C4` ?→1600-01-01: 1600-01-01
  - `G_C5` ?→1610-01-01: 1610-01-01
  - `G_C6` ?→1620-01-01: 1620-01-01
  - `G_C7` ?→1625-01-01: 1625-01-01
  - `G_C8` ?→1630-01-01: 1630-01-01
  - `G_C9` ?→1632-01-01: 1632-01-01
  - `G_C10_Z90` ?→1634-03-25: 1634-03-25

### 3. Giordano Bruno — `GIORDANO_BRUNO_V15_3_PATCH09_20261010`

- Fuente original: `/workspace/MOTOR_1019/U6_UNIFICADO_20261020/inputs/GIORDANO_BRUNO_PATCH19_COMPACTO.json`
- SHA-256: `56daf3601390af5115fe159f223516e03589247b59c44d9f2ff5ba90e52b64a3` (corto `56daf3601390`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:37; paquete: 2026-10-20
- Copia en repo: `inputs/003_GIORDANO_BRUNO_V15_3_PATCH09_20261010_56daf3601390/GIORDANO_BRUNO_PATCH19_COMPACTO.json`
- Otras copias con el mismo hash: 13 (ej. `/workspace/UNIFICADO_20261011/TRABAJO/entrega/PACK_U1_CONSULTA_DIRIGIDA/inputs/GIORDANO_BRUNO_PATCH19_COMPACTO.json`)
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Giordano Bruno): nacimiento=1548 (año; el día exacto no es seguro), se toma 1548-01-01; fuente pública (Giordano Bruno): muerte=1600-02-17
- Z90 calculada (90% nacimiento→muerte): 1594-12-01
- Z declarada en el input: 1594-12-31 (normalizada: 1594-12-31)
- Cortes: 8 total; pre-Z 8 / post-Z 0; vs Z90 calculada: pre 8 / post 0
- Último corte pre-Z: C8 1594-12-01
- Veredicto: `CONFORME` — Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1` ?→1565-01-01: 1565-01-01
  - `C2` ?→1575-07-01: 1575-07-01
  - `C3` ?→1576-10-01: 1576-10-01
  - `C4` ?→1579-09-01: 1579-09-01
  - `C5` ?→1582-12-01: 1582-12-01
  - `C6` ?→1585-12-01: 1585-12-01
  - `C7` ?→1588-12-01: 1588-12-01
  - `C8` ?→1594-12-01: 1594-12-01

### 4. Martin Luther King Jr. — ``

- Fuente original: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/MARTIRES_Z90/_cuts_mlk_run.json`
- SHA-256: `7e42cc4c7c7c08b2639f63d88144b0c5c7e22cb8a2f1c996bf4178251b973361` (corto `7e42cc4c7c7c`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:50
- Copia en repo: `inputs/004_Martin_Luther_King_Jr_7e42cc4c7c7c/_cuts_mlk_run.json`
- Markers del mismo paquete: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/MARTIRES_Z90/markers_mlk_Z1964.json` (`d4eab2a95e0b`)
- Nacimiento (input): 1929-01-15 (markers.born=1929-01-15)
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Martin Luther King Jr.): muerte=1968-04-04
- Z90 calculada (90% nacimiento→muerte): 1964-05-03
- Z declarada en el input: 1964-05-03 (normalizada: 1964-05-03)
- Cortes: 8 total; pre-Z 8 / post-Z 0; vs Z90 calculada: pre 8 / post 0
- Último corte pre-Z: C8 1964-05-03
- Veredicto: `CONFORME` — Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1` 1929-01-01→1940-12-31: 1929-1940s Atlanta: infancia en hogar pastor; segregación cotidiana; mundo ordinario bajo opresión racial
  - `C2` 1948-01-01→1954-12-31: c.1948-1954 seminario / Boston / Coretta: formación, mentoría, matrimonio; herramientas de liderazgo moral
  - `C3` 1955-01-01→1956-12-31: 1955-1956 Montgomery: boicot de autobuses; llamado público; liderazgo improvisado ante injusticia
  - `C4` ?→1957-12-31: 1957+ SCLC: organización del movimiento; alianzas; planificaciones nacionales
  - `C5` ?→1963-12-31: 1963 Birmingham + Carta desde la cárcel: confrontación directa; privación de libertad; prueba suprema moral
  - `C6`: Agosto 1963 March on Washington / discurso: recompensa simbólica; persuasión masiva; celebración parcial
  - `C7`: Finales 1963–primavera 1964: presión legislativa derechos civiles; amenaza persistente; Nobel aún no otorgado en la foto Z
  - `C8` ?→1964-05-03 [Z_foto]: Z≈1964-05-03 (90% vida): movimiento en auge; sacrificio por ideal civil visible como trayectoria; asesinato post-Z sellado

### 5. Stephen Hawking — ``

- Fuente original: `/workspace/HAWKING_Z90_INFORME_COMPLETO_20260919/02_datos_corrida/_cuts_hawking_Z90_run.json`
- SHA-256: `7083daa2c46ff1c41704ec9e3ed209b20a8c1cf0b42bde2f3a7af8e054d319d2` (corto `7083daa2c46f`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:48; paquete: 2026-09-19
- Copia en repo: `inputs/005_Stephen_Hawking_7083daa2c46f/_cuts_hawking_Z90_run.json`
- Markers del mismo paquete: `/workspace/HAWKING_Z90_INFORME_COMPLETO_20260919/02_datos_corrida/markers_hawking_Z90.json` (`fc0e8505c9f2`)
- Otras copias con el mismo hash: 2 (ej. `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_Z90_HAWKING.json`)
- Nacimiento (input): 1942-01-08 (markers.born=1942-01-08)
- Muerte (input): 2018-03-14 (markers.died=2018-03-14)
- Z90 calculada (90% nacimiento→muerte): 2010-08-01
- Z declarada en el input: ~2010-2011 (normalizada: 2010-12-30)
- Cortes: 7 total; pre-Z 7 / post-Z 0; vs Z90 calculada: pre 7 / post 0
- Último corte pre-Z: C7 2011-12-31
- Veredicto: `CONFORME` — Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z. Nota: el último corte pre-Z (2011-12-31) dista más de 12 meses de la Z de referencia.
- Cortes:
  - `C1` 1942-01-01→1959-12-31: ~1942-1959: nace Oxford 1942-01-08; infancia St Albans; estudiante brillante; interes temprano por matematicas y fisica; trayectoria escolar
  - `C2` 1959-01-01→1962-12-31: ~1959-1962: Oxford; grado en fisica; rema en equipo universitario; aparecen torpezas motoras que mas tarde resultan clinicamente relevantes
  - `C3` 1962-01-01→1966-12-31: ~1962-1966: Cambridge; doctorado en cosmologia; diagnostico ELA/MND ~1963 a edad 21; continua el doctorado pese al pronostico; matrimonio
  - `C4` 1966-01-01→1974-12-31: ~1966-1974: investigacion en agujeros negros y singularidades con Penrose; radiacion de Hawking ~1974; reconocimiento cientifico creciente p
  - `C5` 1975-01-01→1988-12-31: ~1975-1988: Catedra Lucasiana 1979; papers mayores; perdida progresiva de habla y movilidad; A Brief History of Time 1988 abre popularizacio
  - `C6` 1989-01-01→2000-12-31: ~1989-2000: fama global como comunicador de ciencia; voz por sintetizador; continua trabajo teorico; figura publica internacional
  - `C7` 2010-01-01→2011-12-31 [Z_foto]: ~2010-2011: Z_foto STOP. Ultimo ~10% de vida sellado. Estado observable: sigue activo como cientifico e intelectual publico; discapacidad se

### 6. Wolfgang Amadeus Mozart — `MOZART_NOCTURNA_20261005`

- Fuente original: `/workspace/CORRIDA_NOCTURNA_20261005/CORRIDA_0547_20261006/inputs/INPUT_CAPA2_MOZART.json`
- SHA-256: `b51131a713e1da51be430981d48f40bf256dbd573f4ff1dd6e5fba1a8b9a9b56` (corto `b51131a713e1`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:08; paquete: 2026-10-05
- Copia en repo: `inputs/006_MOZART_NOCTURNA_20261005_b51131a713e1/INPUT_CAPA2_MOZART.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Wolfgang Amadeus Mozart): nacimiento=1756-01-27; fuente pública (Wolfgang Amadeus Mozart): muerte=1791-12-05
- Z90 calculada (90% nacimiento→muerte): 1788-05-04
- Z declarada en el input: — (normalizada: —)
- Cortes: 10 total; pre-Z 7 / post-Z 3; vs Z90 calculada: pre 7 / post 3
- Último corte pre-Z: C7 1788-05-04
- Veredicto: `CONFORME` — Sin Z declarada en campo, pero el último corte pre-Z cae a ±6 meses de la Z90 calculada y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública.
- Cortes:
  - `C1` 1756-01-01→1762-12-31: 1756-1762: nace en Salzburg en una familia musical; recibe formación musical temprana de Leopold; muestra capacidades extraordinarias desde 
  - `C2` 1763-01-01→1766-12-31: 1763-1766: gran viaje europeo con la familia; actuaciones en París, Londres, La Haya y territorios alemanes y suizos; aumenta la composición
  - `C3` 1769-01-01→1772-12-31: 1769-1772: viajes italianos; encargos y estrenos operísticos; actividad compositiva intensiva y consolidación temprana como compositor.
  - `C4` 1773-01-01→1777-12-31: 1773-1777: regreso y trabajo en Salzburg; producción musical continua; relación de servicio con la corte y búsqueda de oportunidades profesi
  - `C5` 1777-01-01→1778-12-31: 1777-1778: viaje por Mannheim y París buscando oportunidades; muerte de Anna Maria Mozart en París; regreso posterior a Salzburg.
  - `C6` 1779-01-01→1781-12-31: 1779-1781: regreso a Salzburg; compone Idomeneo y se estrena en Munich en enero de 1781; conflicto creciente con el servicio arzobispal.
  - `C7` 1781-01-01→1788-05-04: 1781-1788-05-04: rompe con el servicio del arzobispo y se establece en Viena; Die Entführung aus dem Serail; matrimonio con Constanze; Figar
  - `C8` 1788-01-01→1789-12-31 [post-Z decl., post-Z90]: 1788-1789: tras el punto Z90 continúa componiendo; trabaja en la producción vienesa de Don Giovanni y realiza nuevas obras; Figaro vuelve a 
  - `C9` ?→1790-12-31 [post-Z90]: 1790: compone Così fan tutte; mantiene actividad compositiva y teatral en Viena.
  - `C10` ?→1791-12-31 [post-Z90]: 1791: compone y estrena La clemenza di Tito y Die Zauberflöte; continúa trabajando hasta enfermar gravemente a mediados de noviembre; muere 

### 7. Wolfgang Amadeus Mozart — `MOZART_NOCTURNA_20261005`

- Fuente original: `/workspace/CORRIDA_NOCTURNA_20261005/inputs/INPUT_ESTANDAR_MOZART.json`
- SHA-256: `cc51218bbdc33c4e8c158f3a199731c2f22f950367e21a9f7707fd56c11d6b24` (corto `cc51218bbdc3`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:08; paquete: 2026-10-05
- Copia en repo: `inputs/007_MOZART_NOCTURNA_20261005_cc51218bbdc3/INPUT_ESTANDAR_MOZART.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Wolfgang Amadeus Mozart): nacimiento=1756-01-27; fuente pública (Wolfgang Amadeus Mozart): muerte=1791-12-05
- Z90 calculada (90% nacimiento→muerte): 1788-05-04
- Z declarada en el input: — (normalizada: —)
- Cortes: 10 total; pre-Z 7 / post-Z 3; vs Z90 calculada: pre 7 / post 3
- Último corte pre-Z: C7 1788-05-04
- Veredicto: `CONFORME` — Sin Z declarada en campo, pero el último corte pre-Z cae a ±6 meses de la Z90 calculada y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública.
- Cortes:
  - `C1` 1756-01-01→1762-12-31: 1756-1762: nace en Salzburg en una familia musical; recibe formación musical temprana de Leopold; muestra capacidades extraordinarias desde 
  - `C2` 1763-01-01→1766-12-31: 1763-1766: gran viaje europeo con la familia; actuaciones en París, Londres, La Haya y territorios alemanes y suizos; aumenta la composición
  - `C3` 1769-01-01→1772-12-31: 1769-1772: viajes italianos; encargos y estrenos operísticos; actividad compositiva intensiva y consolidación temprana como compositor.
  - `C4` 1773-01-01→1777-12-31: 1773-1777: regreso y trabajo en Salzburg; producción musical continua; relación de servicio con la corte y búsqueda de oportunidades profesi
  - `C5` 1777-01-01→1778-12-31: 1777-1778: viaje por Mannheim y París buscando oportunidades; muerte de Anna Maria Mozart en París; regreso posterior a Salzburg.
  - `C6` 1779-01-01→1781-12-31: 1779-1781: regreso a Salzburg; compone Idomeneo y se estrena en Munich en enero de 1781; conflicto creciente con el servicio arzobispal.
  - `C7` 1781-01-01→1788-05-04: 1781-1788-05-04: rompe con el servicio del arzobispo y se establece en Viena; Die Entführung aus dem Serail; matrimonio con Constanze; Figar
  - `C8` 1788-01-01→1789-12-31 [post-Z decl., post-Z90]: 1788-1789: tras el punto Z90 continúa componiendo; trabaja en la producción vienesa de Don Giovanni y realiza nuevas obras; Figaro vuelve a 
  - `C9` ?→1790-12-31 [post-Z90]: 1790: compone Così fan tutte; mantiene actividad compositiva y teatral en Viena.
  - `C10` ?→1791-12-31 [post-Z90]: 1791: compone y estrena La clemenza di Tito y Die Zauberflöte; continúa trabajando hasta enfermar gravemente a mediados de noviembre; muere 

### 8. Wolfgang Amadeus Mozart — `MOZART_FRESH_Z90_U6_20261014`

- Fuente original: `/workspace/IN_t860/INPUT_FROZEN.json`
- SHA-256: `a2e2158bab9d5cbeaf58d4e8ab2ce409743a29bb404925cbb62970cb8a200ecc` (corto `a2e2158bab9d`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:13
- Copia en repo: `inputs/008_MOZART_FRESH_Z90_U6_20261014_a2e2158bab9d/INPUT_FROZEN.json`
- Otras copias con el mismo hash: 1 (ej. `/workspace/alt_cameo/casos/precedentes/MOZART_10_CORTES/INPUT_FROZEN.json`)
- Nacimiento (input): 1756-01-27 (input.birth_date=1756-01-27)
- Muerte (input): 1791-12-05 (input.death_date=1791-12-05)
- Z90 calculada (90% nacimiento→muerte): 1788-05-04
- Z declarada en el input: 1788-05-04 (normalizada: 1788-05-04)
- Cortes: 10 total; pre-Z 10 / post-Z 0; vs Z90 calculada: pre 10 / post 0
- Último corte pre-Z: C10 1788-05-04
- Veredicto: `CONFORME` — Z declarada (o último corte pre-Z) = Z90 ±6 meses y hay ≥5 cortes pre-Z.
- Cortes:
  - `C1` ?→1761-12-31: 1761-12-31
  - `C2` ?→1762-10-13: 1762-10-13
  - `C3` ?→1763-06-01: 1763-06-01
  - `C4` ?→1769-12-11: 1769-12-11
  - `C5` ?→1773-03-13: 1773-03-13
  - `C6` ?→1777-09-23: 1777-09-23
  - `C7` ?→1778-07-03: 1778-07-03
  - `C8` ?→1779-01-17: 1779-01-17
  - `C9` ?→1781-06-08: 1781-06-08
  - `C10` ?→1788-05-04: 1788-05-04

### 9. Wolfgang Amadeus Mozart — ``

- Fuente original: `/workspace/alt_cameo/fuentes_originales/202609/MOZART_PROTOCOLO_REPRODUCIBLE_ALL_PLUGINS_20260915/01_INPUT/mozart_cuts_full.json`
- SHA-256: `a86ab3e48c235e2d50d9da4cde305ae3eb2b2b105f5122e71ad24443d9b44858` (corto `a86ab3e48c23`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T02:55:15; paquete: 2026-09-15
- Copia en repo: `inputs/009_Wolfgang_Amadeus_Mozart_a86ab3e48c23/mozart_cuts_full.json`
- Otras copias con el mismo hash: 1 (ej. `/workspace/pred_hist_bio_in/TRANSFER_V15_1/IN_20260926_UNIF0923/MOZART_CUTS_FULL_CANON_TOKENS.json`)
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Wolfgang Amadeus Mozart): nacimiento=1756-01-27; fuente pública (Wolfgang Amadeus Mozart): muerte=1791-12-05
- Z90 calculada (90% nacimiento→muerte): 1788-05-04
- Z declarada en el input: — (normalizada: —)
- Cortes: 10 total; pre-Z 7 / post-Z 3; vs Z90 calculada: pre 7 / post 3
- Último corte pre-Z: C7 1788-05-04
- Veredicto: `CONFORME` — Sin Z declarada en campo, pero el último corte pre-Z cae a ±6 meses de la Z90 calculada y hay ≥5 cortes pre-Z. Z90 calculada con fechas de fuente pública.
- Cortes:
  - `C1` 1756-01-01→1762-12-31: 1756-1762: nace en Salzburg en una familia musical; recibe formación musical temprana de Leopold; muestra capacidades extraordinarias desde 
  - `C2` 1763-01-01→1766-12-31: 1763-1766: gran viaje europeo con la familia; actuaciones en París, Londres, La Haya y territorios alemanes y suizos; aumenta la composición
  - `C3` 1769-01-01→1772-12-31: 1769-1772: viajes italianos; encargos y estrenos operísticos; actividad compositiva intensiva y consolidación temprana como compositor.
  - `C4` 1773-01-01→1777-12-31: 1773-1777: regreso y trabajo en Salzburg; producción musical continua; relación de servicio con la corte y búsqueda de oportunidades profesi
  - `C5` 1777-01-01→1778-12-31: 1777-1778: viaje por Mannheim y París buscando oportunidades; muerte de Anna Maria Mozart en París; regreso posterior a Salzburg.
  - `C6` 1779-01-01→1781-12-31: 1779-1781: regreso a Salzburg; compone Idomeneo y se estrena en Munich en enero de 1781; conflicto creciente con el servicio arzobispal.
  - `C7` 1781-01-01→1788-05-04: 1781-1788-05-04: rompe con el servicio del arzobispo y se establece en Viena; Die Entführung aus dem Serail; matrimonio con Constanze; Figar
  - `C8` 1788-01-01→1789-12-31 [post-Z decl., post-Z90]: 1788-1789: tras el punto Z90 continúa componiendo; trabaja en la producción vienesa de Don Giovanni y realiza nuevas obras; Figaro vuelve a 
  - `C9` ?→1790-12-31 [post-Z90]: 1790: compone Così fan tutte; mantiene actividad compositiva y teatral en Viena.
  - `C10` ?→1791-12-31 [post-Z90]: 1791: compone y estrena La clemenza di Tito y Die Zauberflöte; continúa trabajando hasta enfermar gravemente a mediados de noviembre; muere 

### 10. Abraham Lincoln — `CAL_F003_07_LINCOLN`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_07_LINCOLN/entrada.json`
- SHA-256: `8633e12924db622171f8af0b908ded1b93b7df07c6d64cdfcf16ddc68cff7af5` (corto `8633e12924db`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/010_CAL_F003_07_LINCOLN_8633e12924db/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Abraham Lincoln): nacimiento=1809-02-12; fuente pública (Abraham Lincoln): muerte=1865-04-15
- Z90 calculada (90% nacimiento→muerte): 1859-09-02
- Z declarada en el input: 1858-10-15 (normalizada: 1858-10-15)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1858 1858-10-15
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1858-10-15 vs Z90 1859-09-02 (Δ 10.6 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1846` ?→1846-01-01: Autodidacta criado en la frontera, perdió su primera candidatura a la legislatura de Illinois en 1832; en 1834, como whig seguidor de Henry 
  - `C2_1856` ?→1856-01-01: Indignado por la Ley Kansas-Nebraska de 1854, que abría los territorios a la esclavitud, dejó el partido whig en crisis; en 1856 se unió a l
  - `C3_1858` ?→1858-10-15: En junio de 1858 los republicanos de Illinois lo nominaron al Senado contra el titular Stephen A. Douglas y el 16 de junio pronunció el disc

### 11. Alan Turing — `CAL_F001_05_TURING`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F001_05_TURING/entrada.json`
- SHA-256: `1ac92339557934c04d1be9827344a1bc0f06e9d4299a05646890ae941cdd314a` (corto `1ac923395579`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/011_CAL_F001_05_TURING_1ac923395579/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Alan Turing): nacimiento=1912-06-23; fuente pública (Alan Turing): muerte=1954-06-07
- Z90 calculada (90% nacimiento→muerte): 1950-03-28
- Z declarada en el input: C3_1952 (normalizada: 1952-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 1 / post 2
- Último corte pre-Z: C2_1950 1950-10-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1952-01-01 vs Z90 1950-03-28 (Δ 21.2 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1936` ?→1936-11-12: Publica 'On Computable Numbers', base de la teoría de la computación. \| 1936-11-12 \| 1936-11-12
  - `C2_1950` ?→1950-10-01 [post-Z90]: Tras su trabajo secreto en Bletchley Park (OBE 1946), publica 'Computing Machinery and Intelligence'. \| 1950-10-01 \| 1950-10-01
  - `C3_1952` ?→1952-03-31 [post-Z decl., post-Z90]: Condenado por 'indecencia grave'; acepta tratamiento hormonal en vez de prisión y pierde su acceso al trabajo criptográfico con GCHQ. \| 1952

### 12. Albert Einstein — `CAL_F005_03_EINSTEIN`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_03_EINSTEIN/entrada.json`
- SHA-256: `0965b7ae2e693b3f6dcc2c06b87f6ee33478df36686ca3ee3c7f499bc0ac996d` (corto `0965b7ae2e69`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/012_CAL_F005_03_EINSTEIN_0965b7ae2e69/entrada.json`
- Nacimiento (input): 1904-01-01 (hecho del corte (nace 1904)) Nota: solo año, se toma 01-01
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Albert Einstein): muerte=1955-04-18
- Z90 calculada (90% nacimiento→muerte): 1950-03-02
- Z declarada en el input: 1904-05 (normalizada: 1904-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1904 1904-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1904-01-01 vs Z90 1950-03-02 (Δ 554.0 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1901` ?→1901-01-01: Se gradúa en el Politécnico de Zúrich (1900) como profesor de matemáticas y física, pero durante casi dos años ninguna escuela suiza le da p
  - `C2_1902` ?→1902-01-01: Con ayuda del padre de Marcel Grossmann entra a la Oficina de Patentes de Berna como examinador asistente de tercera clase; con Habicht y So
  - `C3_1904` ?→1904-01-01: Su puesto en la oficina se vuelve permanente (1903), sin ascenso hasta 'dominar la tecnología de máquinas'; se casa con Mileva Marić (enero 

### 13. Andrew Carnegie — `CAL_F003_09_CARNEGIE`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_09_CARNEGIE/entrada.json`
- SHA-256: `2f292231c6a45be26e9412385e70b98d1b603b849e7d76429aa5b1995c008926` (corto `2f292231c6a4`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/013_CAL_F003_09_CARNEGIE_2f292231c6a4/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Andrew Carnegie): nacimiento=1835-11-25; fuente pública (Andrew Carnegie): muerte=1919-08-11
- Z90 calculada (90% nacimiento→muerte): 1911-03-29
- Z declarada en el input: 1872 (normalizada: 1872-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1872 1872-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1872-01-01 vs Z90 1911-03-29 (Δ 470.8 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1859` ?→1859-12-01: Hijo de un tejedor escocés empobrecido que emigró a Pittsburgh en 1848, empezó como bobinador de algodón por 1.20 dólares semanales y luego 
  - `C2_1865` ?→1865-01-01: Con ayuda de Scott hizo sus primeras inversiones; en 1864 invirtió en la Columbia Oil Company, que en un año pagó más de un millón de dólare
  - `C3_1872` ?→1872-01-01: En 1868, a los 33 años, escribió un memorando proponiéndose limitar su ingreso a 50,000 dólares anuales y retirarse de los negocios; en el v

### 14. Antoine Lavoisier — `CAL_F003_03_LAVOISIER`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_03_LAVOISIER/entrada.json`
- SHA-256: `33e508f4b5b2c55d7e0f052f31dfd8118f442fe999febf56c6340e3afca60091` (corto `33e508f4b5b2`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/014_CAL_F003_03_LAVOISIER_33e508f4b5b2/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Antoine Lavoisier): nacimiento=1743-08-26; fuente pública (Antoine Lavoisier): muerte=1794-05-08
- Z90 calculada (90% nacimiento→muerte): 1789-04-12
- Z declarada en el input: 1789 (normalizada: 1789-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1789 1789-01-01
- Veredicto: `POCOS_CORTES` — Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1771` ?→1771-01-01: En 1768 recibió un nombramiento provisional en la Academia de Ciencias y, hacia esa fecha, compró una participación en la Ferme générale, la
  - `C2_1783` ?→1783-01-01: En 1775 fue nombrado uno de los cuatro comisarios de la pólvora y mejoró la cantidad y calidad de la pólvora francesa; en 1783 leyó en la Ac
  - `C3_1789` ?→1789-01-01: En 1787 presentó con Guyton de Morveau, Berthollet y Fourcroy la Méthode de nomenclature chimique, ligada a su teoría del oxígeno, y en 1789

### 15. Benito Mussolini — `CAL_F005_05_MUSSOLINI`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_05_MUSSOLINI/entrada.json`
- SHA-256: `ad61bff24f8e322957fc3cbe0459dfe5d79d1d31f8bd82704bf6a95896b8dbac` (corto `ad61bff24f8e`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/015_CAL_F005_05_MUSSOLINI_ad61bff24f8e/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Benito Mussolini): nacimiento=1883-07-29; fuente pública (Benito Mussolini): muerte=1945-04-28
- Z90 calculada (90% nacimiento→muerte): 1939-02-24
- Z declarada en el input: 1942-11-08 (normalizada: 1942-11-08)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 2 / post 1
- Último corte pre-Z: C3_1942 1942-11-08
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1942-11-08 vs Z90 1939-02-24 (Δ 44.5 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1922` ?→1922-10-31: Con la Marcha sobre Roma (28–31 de octubre de 1922), en la que participan casi 30 000 fascistas, llega al poder. \| 1922-10-31 \| 1922-10-31
  - `C2_1936` ?→1936-01-01: Declara la guerra a Etiopía (octubre de 1935) y proclama el imperio en mayo de 1936, en la cima de su popularidad; la condena de la Sociedad
  - `C3_1942` ?→1942-11-08 [post-Z90]: Entra a la guerra en junio de 1940 creyendo inminente la victoria alemana, sin planes de largo plazo; la guerra con Grecia es un desastre; e

### 16. C01 — `C01`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C01/entrada.json`
- SHA-256: `767c9710672e48f2d93e9816795f54d58d1a02d5fed09ea862f418dbdc835cd0` (corto `767c9710672e`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/016_C01_767c9710672e/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1781 (normalizada: 1781-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1777 1777-09-23
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1756` ?→1756-01-27: Nace en Salzburgo; niño prodigio, gira por las cortes de Europa con su padre. \| 1756-01-27 \| 1756-01-27
  - `C2_1777` ?→1777-09-23: Viaja a París con su madre (muere en 1778); busca un empleo estable sin conseguirlo. \| 1777-09-23 \| 1777-09-23
  - `C3_1781` ?→1781-03-16 [post-Z decl.]: Rompe con el arzobispo de Salzburgo; se establece en Viena como músico independiente. \| 1781-03-16 \| 1781-03-16

### 17. C02 — `C02`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C02/entrada.json`
- SHA-256: `5601543947d26f9faaab7a476bbaa35835986ed7b91578c5a2a74e6f8b40fd95` (corto `5601543947d2`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/017_C02_5601543947d2/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1859 (normalizada: 1859-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1844 1844-07-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1836` ?→1836-10-02: Regresa del viaje del Beagle (1831-1836) con observaciones y especímenes de Galápagos y Sudamérica. \| 1836-10-02 \| 1836-10-02
  - `C2_1844` ?→1844-07-01: Escribe el 'Ensayo de 1844' con su teoría de selección natural; lo guarda sin publicar por temor a la reacción. \| 1844-07-01 \| 1844-07-01
  - `C3_1859` ?→1859-11-24 [post-Z decl.]: Publica El origen de las especies; la primera edición se agota el día de su salida. \| 1859-11-24 \| 1859-11-24

### 18. C03 — `C03`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C03/entrada.json`
- SHA-256: `8ba09c5eee0bd362e3e55e71221bfc432f1ab98239b61517f4cf20660f3c0606` (corto `8ba09c5eee0b`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/018_C03_8ba09c5eee0b/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1687 (normalizada: 1687-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1672 1672-01-11
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1665` ?→1665-08-01: Annus mirabilis durante la peste: cálculo, óptica y gravitación en Woolsthorpe. \| 1665-08-01 \| 1665-08-01
  - `C2_1672` ?→1672-01-11: Elegido miembro de la Royal Society; presenta su telescopio reflector y su teoría de la luz y el color. \| 1672-01-11 \| 1672-01-11
  - `C3_1687` ?→1687-07-05 [post-Z decl.]: Publica Philosophiæ Naturalis Principia Mathematica con las leyes del movimiento y la gravitación universal. \| 1687-07-05 \| 1687-07-05

### 19. C04 — `C04`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C04/entrada.json`
- SHA-256: `1fbeec7becfedc9d2693dec10b650624d37c55e970642acf1f9a3ba8edf8fe1e` (corto `1fbeec7becfe`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/019_C04_1fbeec7becfe/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1879 (normalizada: 1879-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1878 1878-09-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1877` ?→1877-11-21: Presenta el fonógrafo, su primera gran invención; lo apodan 'el mago de Menlo Park'. \| 1877-11-21 \| 1877-11-21
  - `C2_1878` ?→1878-09-01: Funda una compañía de luz eléctrica para desarrollar la iluminación; compite por financiación. \| 1878-09-01 \| 1878-09-01
  - `C3_1879` ?→1879-10-21 [post-Z decl.]: Logra una bombilla incandescente que dura 13,5 horas; patenta el sistema de luz eléctrica. \| 1879-10-21 \| 1879-10-21

### 20. C05 — `C05`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C05/entrada.json`
- SHA-256: `064f64f29dd09ce9c1f207f2da8fa00c1319ea58a98129a7a2f7f9cacf751439` (corto `064f64f29dd0`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/020_C05_064f64f29dd0/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1599 (normalizada: 1599-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: C3_1599 1599-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1590` ?→1590-01-01: Llega a Londres; escribe sus primeras obras y se hace un nombre en el teatro. \| 1590-01-01 \| 1590-01-01
  - `C2_1594` ?→1594-01-01: Se une a los Lord Chamberlain's Men; escribe Romeo y Julieta y El sueño de una noche de verano. \| 1594-01-01 \| 1594-01-01
  - `C3_1599` ?→1599-01-01: Se construye el Globe Theatre; el sujeto es copropietario y dramaturgo principal de la compañía. \| 1599-01-01 \| 1599-01-01

### 21. C06 — `C06`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C06/entrada.json`
- SHA-256: `8a3727f8a58df62542f3befdef22f33fdb8accd0f4c14a793caf018eab916a35` (corto `8a3727f8a58d`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/021_C06_8a3727f8a58d/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1605 (normalizada: 1605-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1580 1580-09-19
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1571` ?→1571-10-07: Combate en Lepanto; pierde el uso de la mano izquierda. \| 1571-10-07 \| 1571-10-07
  - `C2_1580` ?→1580-09-19: Liberado tras cinco años cautivo en Argel; regresa a España arruinado y busca empleo. \| 1580-09-19 \| 1580-09-19
  - `C3_1605` ?→1605-01-16 [post-Z decl.]: Publica la primera parte de Don Quijote de la Mancha; éxito inmediato en España y Europa. \| 1605-01-16 \| 1605-01-16

### 22. C07 — `C07`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C07/entrada.json`
- SHA-256: `cfb95e0abbed2ff65eb4dd960c4e353aee5214773013ddb42ceadc7751b4f0cc` (corto `cfb95e0abbed`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/022_C07_cfb95e0abbed/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1609 (normalizada: 1609-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: C3_1609 1609-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1600` ?→1600-01-01: Llega a Praga como asistente de Tycho Brahe; hereda sus observaciones planetarias precisas. \| 1600-01-01 \| 1600-01-01
  - `C2_1601` ?→1601-10-24: Muere Tycho Brahe; el sujeto lo sucede como matemático imperial de Rodolfo II. \| 1601-10-24 \| 1601-10-24
  - `C3_1609` ?→1609-01-01: Publica Astronomia Nova con las dos primeras leyes del movimiento planetario (órbitas elípticas). \| 1609-01-01 \| 1609-01-01

### 23. C08 — `C08`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C08/entrada.json`
- SHA-256: `ffe195b1fbec71a435022bce1157acb69924ce844b82e77b69f37ee0c92fde9a` (corto `ffe195b1fbec`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/023_C08_ffe195b1fbec/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1854 (normalizada: 1854-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1853 1853-08-12
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1850` ?→1850-01-01: Estudia enfermería en Kaiserswerth (Alemania); rechaza el papel tradicional asignado a las mujeres de su época. \| 1850-01-01 \| 1850-01-01
  - `C2_1853` ?→1853-08-12: Dirige el Instituto para el Cuidado de Damas Enfermas en Londres; reforma su gestión y sus registros. \| 1853-08-12 \| 1853-08-12
  - `C3_1854` ?→1854-11-04 [post-Z decl.]: Llega a Scutari (Crimea) con 38 enfermeras; encuentra un hospital con mortalidad altísima y condiciones insalubres. \| 1854-11-04 \| 1854-11-0

### 24. C09 — `C09`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C09/entrada.json`
- SHA-256: `f9b6d0cf680733f2d333990d48c1d1b60ea4b89c2375cb84141c3f5d3624e27c` (corto `f9b6d0cf6807`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/024_C09_f9b6d0cf6807/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1429 (normalizada: 1429-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 1 / post-Z 2
- Último corte pre-Z: C1_1428 1428-05-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1428` ?→1428-05-01: Llega a Chinon y convence al delfín de que es enviada a liberar el reino. \| 1428-05-01 \| 1428-05-01
  - `C2_1429` ?→1429-04-01 [post-Z decl.]: Recibe el mando de un ejército y marcha a Orléans con estandarte propio. \| 1429-04-01 \| 1429-04-01
  - `C3_1429` ?→1429-07-17 [post-Z decl.]: Libera Orléans en nueve días; el delfín es coronado rey en Reims con el sujeto a su lado con el estandarte. \| 1429-07-17 \| 1429-07-17

### 25. C10 — `C10`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C10/entrada.json`
- SHA-256: `cbd75d94450c0014acef322c312ea08a8cea0026ab5c5e1f1487509d8da37906` (corto `cbd75d94450c`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/025_C10_cbd75d94450c/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_0800 (normalizada: —)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: C3_0800 0800-12-25
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_0768` ?→0768-09-24: Hereda el reino franco junto a su hermano; tras la muerte de este (771) queda como único rey. \| 0768-09-24 \| 0768-09-24
  - `C2_0782` ?→0782-01-01: Campañas contra los sajones; masacre de Verden y sumisión de los territorios del norte. \| 0782-01-01 \| 0782-01-01
  - `C3_0800` ?→0800-12-25: Coronado emperador en Roma por el papa León III; une gran parte de Europa occidental bajo su corona. \| 0800-12-25 \| 0800-12-25

### 26. C11 — `C11`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C11/entrada.json`
- SHA-256: `c05ab0c816409d472b54847c6142d33a66e7a4ae9d1c467337b9b7bd6ae30e3e` (corto `c05ab0c81640`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/026_C11_c05ab0c81640/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1520 (normalizada: 1520-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1514 1514-08-23
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1512` ?→1512-01-01: Gobierna como príncipe en Manisa; se forma en administración, leyes y estrategia militar. \| 1512-01-01 \| 1512-01-01
  - `C2_1514` ?→1514-08-23: Participa en la campaña de Chaldiran contra Persia; el imperio se expande hacia el este. \| 1514-08-23 \| 1514-08-23
  - `C3_1520` ?→1520-09-30 [post-Z decl.]: Accede al trono tras la muerte de su padre; hereda un imperio en expansión y un ejército temido. \| 1520-09-30 \| 1520-09-30

### 27. C12 — `C12`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C12/entrada.json`
- SHA-256: `598b32b0df629725cbd4d8546e1aecaf22e7c9831608d720a684f2759c143c96` (corto `598b32b0df62`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/027_C12_598b32b0df62/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1547 (normalizada: 1547-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1545 1545-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1533` ?→1533-12-03: Accede al trono con tres años; el poder queda en manos de regentes y facciones de boyardos. \| 1533-12-03 \| 1533-12-03
  - `C2_1545` ?→1545-01-01: Toma el poder personal a los 15 años; impone su autoridad sobre los boyardos. \| 1545-01-01 \| 1545-01-01
  - `C3_1547` ?→1547-01-16 [post-Z decl.]: Coronado primer zar en Moscú; inicia conquistas (Kazán 1552, Astracán 1556). \| 1547-01-16 \| 1547-01-16

### 28. C13 — `C13`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C13/entrada.json`
- SHA-256: `58e13aa87788645b98c1e005519be1c02df0db63ae479e1994bc8e79189956ce` (corto `58e13aa87788`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/028_C13_58e13aa87788/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1206 (normalizada: 1206-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: C3_1206 1206-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1189` ?→1189-01-01: Elegido kan de una confederación de clanes; sobrevive a traiciones y derrotas tempranas. \| 1189-01-01 \| 1189-01-01
  - `C2_1203` ?→1203-01-01: Derrota a sus rivales (Jamukha y los naimanes); incorpora sus guerreros y su organización. \| 1203-01-01 \| 1203-01-01
  - `C3_1206` ?→1206-01-01: Proclamado gobernante universal en el kuriltai; unifica las tribus mongolas. \| 1206-01-01 \| 1206-01-01

### 29. C14 — `C14`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C14/entrada.json`
- SHA-256: `d19b345f912d8e86b9fe6442086b99e3e8a5557b5b50a38a634d18a3506f8fd5` (corto `d19b345f912d`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/029_C14_d19b345f912d/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1492 (normalizada: 1492-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1491 1491-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1484` ?→1484-01-01: Presenta su proyecto a la corte de Portugal; es rechazado y se traslada a Castilla. \| 1484-01-01 \| 1484-01-01
  - `C2_1491` ?→1491-01-01: Tras años de espera, los Reyes Católicos aceptan financiar la expedición (Capitulaciones de Santa Fe, abr-1492). \| 1491-01-01 \| 1491-01-01
  - `C3_1492` ?→1492-08-03 [post-Z decl.]: Zarpa de Palos con tres naves hacia el oeste, buscando una ruta marítima a las Indias. \| 1492-08-03 \| 1492-08-03

### 30. C15 — `C15`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C15/entrada.json`
- SHA-256: `9b669466fa1f7af805bccbd00b677f0874c24380f8c9b9290103cdb73aa8e951` (corto `9b669466fa1f`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/030_C15_9b669466fa1f/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1519 (normalizada: 1519-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1517 1517-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1505` ?→1505-01-01: Sirve a Portugal en la India y Malaca; aprende navegación oceánica y rutas de especias. \| 1505-01-01 \| 1505-01-01
  - `C2_1517` ?→1517-01-01: Rechazado por el rey de Portugal, ofrece su proyecto a Castilla; Carlos I lo acepta. \| 1517-01-01 \| 1517-01-01
  - `C3_1519` ?→1519-09-20 [post-Z decl.]: Zarpa de Sanlúcar con cinco naves hacia el oeste, buscando un paso por el sur del nuevo continente. \| 1519-09-20 \| 1519-09-20

### 31. C16 — `C16`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C16/entrada.json`
- SHA-256: `e0986541ef212647b6caf66a86f40360673306e6a54cc7a14a6d2f3e9115cf28` (corto `e0986541ef21`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/031_C16_e0986541ef21/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1275 (normalizada: 1275-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1273 1273-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1271` ?→1271-01-01: Sale de Venecia con su padre y su tío rumbo a Oriente por la ruta terrestre. \| 1271-01-01 \| 1271-01-01
  - `C2_1273` ?→1273-01-01: Travesía por Persia y Asia Central; la ruta es larga, peligrosa y exige negociar con gobernantes locales. \| 1273-01-01 \| 1273-01-01
  - `C3_1275` ?→1275-06-01 [post-Z decl.]: Llega a China (c. 1275) y entra al servicio de la corte del gran kan. \| 1275-06-01 \| 1275-06-01

### 32. C17 — `C17`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C17/entrada.json`
- SHA-256: `7502f1a7ad2dc3295fe0f3ec59c110d43dbc340b40dab1f18c1f393d6fd4d13e` (corto `7502f1a7ad2d`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/032_C17_7502f1a7ad2d/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1302 (normalizada: 1302-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_1301 1301-11-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1295` ?→1295-01-01: Entra en la política florentina; se alinea con los güelfos blancos en la lucha de facciones. \| 1295-01-01 \| 1295-01-01
  - `C2_1301` ?→1301-11-01: Los güelfos negros toman Florencia con ayuda papal; el sujeto está fuera de la ciudad en misión diplomática. \| 1301-11-01 \| 1301-11-01
  - `C3_1302` ?→1302-01-27 [post-Z decl.]: Condenado al exilio y a muerte si regresa; pierde sus bienes y su posición en Florencia. \| 1302-01-27 \| 1302-01-27

### 33. C18 — `C18`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C18/entrada.json`
- SHA-256: `47f160eea05f8768bb54693bc592ee0a0a911c2b044cbd5aa41f13dda0f61027` (corto `47f160eea05f`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/033_C18_47f160eea05f/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1508 (normalizada: 1508-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: C3_1508 1508-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1501` ?→1501-08-16: Recibe el encargo del David en Florencia; trabaja un bloque de mármol abandonado por otros escultores. \| 1501-08-16 \| 1501-08-16
  - `C2_1505` ?→1505-01-01: Llamado a Roma por el papa Julio II para su tumba; el proyecto se interrumpe y el sujeto se siente humillado. \| 1505-01-01 \| 1505-01-01
  - `C3_1508` ?→1508-01-01: Julio II le encarga pintar la bóveda de la Capilla Sixtina, un trabajo que el sujeto considera ajeno a su oficio de escultor. \| 1508-01-01 \|

### 34. C19 — `C19`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C19/entrada.json`
- SHA-256: `d834a155a0b65807efc1c691c669247dd0f837fc84b63d9b53a798505cb1f27e` (corto `d834a155a0b6`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/034_C19_d834a155a0b6/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1642 (normalizada: 1642-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: C3_1642 1642-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1631` ?→1631-01-01: Se traslada a Ámsterdam; se convierte en el retratista más solicitado de la burguesía. \| 1631-01-01 \| 1631-01-01
  - `C2_1634` ?→1634-06-22: Se casa en 1634; compra una casa grande y colecciona arte y objetos. \| 1634-06-22 \| 1634-06-22
  - `C3_1642` ?→1642-01-01: Termina La ronda de noche; su esposa Saskia muere ese año y su fortuna empieza a declinar. \| 1642-01-01 \| 1642-01-01

### 35. C20 — `C20`

- Fuente original: `/workspace/alt_cameo/casos/ciegos/lote_20/C20/entrada.json`
- SHA-256: `356b25ecc84837520e1b50c9d6d39dc97494b1c24746183361339b594cad4e21` (corto `356b25ecc848`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/035_C20_356b25ecc848/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_1514 (normalizada: 1514-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: C3_1514 1514-01-01
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_1503` ?→1503-01-01: Doctor en derecho canónico en Ferrara; regresa a Polonia como canónigo de Frombork. \| 1503-01-01 \| 1503-01-01
  - `C2_1510` ?→1510-01-01: Se instala en Frombork; observa el cielo y anota discrepancias con el modelo geocéntrico. \| 1510-01-01 \| 1510-01-01
  - `C3_1514` ?→1514-01-01: Circula entre amigos el Commentariolus (c. 1514), breve tratado que propone el Sol en el centro. \| 1514-01-01 \| 1514-01-01

### 36. Calvin Coolidge — `CAL_F002_06_COOLIDGE`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_06_COOLIDGE/entrada.json`
- SHA-256: `ce093eb238f160061a8c9d7e9f427c930d45a15b057ca0fbaee5665cdec446f1` (corto `ce093eb238f1`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/036_CAL_F002_06_COOLIDGE_ce093eb238f1/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Calvin Coolidge): nacimiento=1872-07-04; fuente pública (Calvin Coolidge): muerte=1933-01-05
- Z90 calculada (90% nacimiento→muerte): 1926-12-18
- Z declarada en el input: 1925-03-04 (normalizada: 1925-03-04)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1925 1925-03-04
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1925-03-04 vs Z90 1926-12-18 (Δ 21.5 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1919` ?→1919-01-01: Como gobernador de Massachusetts enfrentó la huelga de la policía de Boston iniciada el 9 de septiembre de 1919 y respondió por telegrama a 
  - `C2_1923` ?→1923-08-03: Vicepresidente de Warren Harding desde 1921, al quedar vacante la presidencia juró el cargo a las 2:47 de la madrugada del 3 de agosto de 19
  - `C3_1925` ?→1925-03-04: En julio de 1924 perdió a su hijo Calvin Jr., de 16 años, por una septicemia originada en una ampolla; en la elección de noviembre de 1924 o

### 37. Catalina Alexéievna (nacida Sofía de Anhalt-Zerbst) — `CAL_F002_07_CATALINA`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_07_CATALINA/entrada.json`
- SHA-256: `267264ce64257c224f7d68041ee924cb519a72de3959cb3a9a141f976a2d5ec5` (corto `267264ce6425`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/037_CAL_F002_07_CATALINA_267264ce6425/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Catalina la Grande): nacimiento=1729-05-02; fuente pública (Catalina la Grande): muerte=1796-11-17
- Z90 calculada (90% nacimiento→muerte): 1790-02-15
- Z declarada en el input: 1762-05-05 (normalizada: 1762-05-05)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1762 1762-05-05
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1762-05-05 vs Z90 1790-02-15 (Δ 333.4 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1745` ?→1745-08-21: Princesa alemana llegada a Rusia en 1744 a los 15 años, se empeñó en aprender ruso y ganarse a la emperatriz Isabel; el 28 de junio de 1744 
  - `C2_1754` ?→1754-01-01: El matrimonio resultó infeliz; Pedro tomó una amante y ella se relacionó con otras figuras de la corte, se ganó el favor de grupos políticos
  - `C3_1762` ?→1762-05-05: Pedro subió al trono el 5 de enero de 1762 y ella pasó a ser emperatriz consorte; admirador de Federico II, Pedro firmó el 5 de mayo de 1762

### 38. Charles Dickens — `CAL_F003_02_DICKENS`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_02_DICKENS/entrada.json`
- SHA-256: `2715f0870655a2a8986a65fdfcd8b4dceec1b27793232b8a702ce8975ae7c1ce` (corto `2715f0870655`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/038_CAL_F003_02_DICKENS_2715f0870655/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Charles Dickens): nacimiento=1812-02-07; fuente pública (Charles Dickens): muerte=1870-06-09
- Z90 calculada (90% nacimiento→muerte): 1864-08-08
- Z declarada en el input: 1836-04-02 (normalizada: 1836-04-02)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1836 1836-04-02
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1836-04-02 vs Z90 1864-08-08 (Δ 340.2 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1824` ?→1824-01-01: Su padre, John Dickens, entró en la prisión de deudores de Marshalsea en 1824; Charles, de 12 años, tuvo que dejar la escuela y trabajar jor
  - `C2_1834` ?→1834-01-01: En diciembre de 1833 publicó su primer relato en The Monthly Magazine; trabajaba como periodista parlamentario y para el Morning Chronicle, 
  - `C3_1836` ?→1836-04-02: En febrero de 1836 se publicaron en libro sus Sketches by Boz; por su éxito, la editorial Chapman and Hall le propuso escribir el texto para

### 39. Coco Chanel — `CAL_F004_07_CHANEL`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_07_CHANEL/entrada.json`
- SHA-256: `a6cac4f38bb7bb651d74743b0cbf0761ec6cb3811cd78d3f494ef3af1b493a86` (corto `a6cac4f38bb7`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/039_CAL_F004_07_CHANEL_a6cac4f38bb7/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Coco Chanel): nacimiento=1883-08-19; fuente pública (Coco Chanel): muerte=1971-01-10
- Z90 calculada (90% nacimiento→muerte): 1962-04-15
- Z declarada en el input: 1919-12-22 (normalizada: 1919-12-22)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1919_12 1919-12-22
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1919-12-22 vs Z90 1962-04-15 (Δ 507.8 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1906` ?→1906-01-01: Nacida en un hospicio de pobres, huérfana de madre a los 11 años y criada en el orfanato de Aubazine, donde aprendió a coser; intenta una ca
  - `C2_1916` ?→1916-01-01: Con financiación de Arthur 'Boy' Capel abre tienda de sombreros en París (1910), boutique en Deauville (1913) y casa en Biarritz (1915), con
  - `C3_1919_12` ?→1919-12-22: Compra el edificio del 31 de la rue Cambon (1918) y se registra como couturière con su maison de couture (1919); Capel, casado en 1918 con o

### 40. Elizabeth Holmes — `CAL_LOTE01_08_HOLMES`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_08_HOLMES.json`
- SHA-256: `d6ec5dae5082710b40c274b4d324ed6bd10611a3927da4f3c9862365de3216c7` (corto `d6ec5dae5082`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/040_CAL_LOTE01_08_HOLMES_d6ec5dae5082/CAL_LOTE01_08_HOLMES.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_2015 (normalizada: 2015-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1
- Último corte pre-Z: C2_2014 2014-06-12
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_2004` ?→2004-03-01: Deja Stanford para fundar Theranos con promesa de análisis con gota de sangre. \| 2004-03-01 \| 2004-03-01
  - `C2_2014` ?→2014-06-12: Valuación de 9 mil millones; alianza con Walgreens; portada de Forbes. \| 2014-06-12 \| 2014-06-12
  - `C3_2015` ?→2015-10-16 [post-Z decl.]: WSJ (Carreyrou) revela que la tecnología Edison no funciona como se dice; la empresa lo niega. \| 2015-10-16 \| 2015-10-16

### 41. Emmy Noether — ``

- Fuente original: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/CHECKPOINT_MOTOR_CLONABLE_20260914/09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_NOETHER_Z90_20260914/SELLADO_PRE_REVELACION/_cuts_ciego_Z90_run.json`
- SHA-256: `db82da5c23aa1b5b0f07b259a3a935dd7b238728b5c1596e33e94930ee6d35e9` (corto `db82da5c23aa`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:00; paquete: 2026-09-14
- Copia en repo: `inputs/041_Emmy_Noether_db82da5c23aa/_cuts_ciego_Z90_run.json`
- Markers del mismo paquete: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/CHECKPOINT_MOTOR_CLONABLE_20260914/09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_NOETHER_Z90_20260914/SELLADO_PRE_REVELACION/markers_ciego_Z90.json` (`b6360f5bb7d7`)
- Otras copias con el mismo hash: 8 (ej. `/tmp/ck_CHECKPOINT_MOTOR_CLONABLE_20260914/CHECKPOINT_MOTOR_CLONABLE_20260914/09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_NOETHER_Z90_20260914/SELLADO_PRE_REVELACION/_cuts_ciego_Z90_run.json`)
- Nacimiento (input): 1882-07-01 (markers.born_approx=~1882) Nota: año aproximado ~1882, se toma 07-01
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Emmy Noether): muerte=1935-04-14
- Z90 calculada (90% nacimiento→muerte): 1930-01-02
- Z declarada en el input: ~1932 (normalizada: 1932-07-01)
- Cortes: 7 total; pre-Z 6 / post-Z 1; vs Z90 calculada: pre 6 / post 1
- Último corte pre-Z: C7 1932-12-31
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1932-07-01 vs Z90 1930-01-02 (Δ 29.9 meses). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1` 1882-01-01→1900-12-31: ~1882-1900: nace en ciudad universitaria mediana; familia academica; padre profesor; hogar intelectual; escuela local
  - `C2` 1900-01-01→1907-12-31: ~1900-1907: universidad local; no puede matricularse oficialmente por barrera de genero; asiste como oyente; un semestre en otra universidad
  - `C3` 1907-01-01→1915-12-31: ~1907-1915: trabaja en institucion donde enseña el padre; sin sueldo; sin titulo oficial; publica bajo nombres de colegas; aportes reconocid
  - `C4` 1915-01-01→1919-12-31: ~1915-1919: dos academicos renombrados invitan a centro de elite; resistencia institucional a aceptarle como docente; enseña bajo nombre de 
  - `C5` 1920-01-01→1927-12-31: ~1920-1927: figura central de campo emergente; forma escuela; atrae estudiantes de varios paises; publica obra que reorganiza el campo; reco
  - `C6` 1928-01-01→1932-12-31 [post-Z decl., post-Z90]: ~1928-1932: invitado a congresos internacionales; reconocimiento internacional; pico de influencia teorica
  - `C7` ?→1932-12-31 [Z_foto]: ~1932: Z_foto STOP. Ultimo 10% de vida sellado. Estado observable: influencia teorica alta, reconocimiento internacional, escuela formada; f

### 42. Ferdinand de Lesseps — `CAL_F004_08_LESSEPS`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_08_LESSEPS/entrada.json`
- SHA-256: `8f9e1695fdbad046ee3c84220b4d3bee530c81b6a813816b465d30b9bd11e87d` (corto `8f9e1695fdba`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/042_CAL_F004_08_LESSEPS_8f9e1695fdba/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Ferdinand de Lesseps): nacimiento=1805-11-19; fuente pública (Ferdinand de Lesseps): muerte=1894-12-07
- Z90 calculada (90% nacimiento→muerte): 1886-01-10
- Z declarada en el input: 1886 (normalizada: 1886-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1886 1886-01-01
- Veredicto: `POCOS_CORTES` — Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1869` ?→1869-11-17: Obtiene la concesión de Suez (1854), reúne capital con suscripciones patrióticas francesas, resiste la oposición británica sin escuchar crít
  - `C2_1880` ?→1880-01-01: Un congreso en París vota un canal de Panamá a nivel del mar, sin esclusas, como Suez; con 74 años lo nombran presidente de la compañía y Ga
  - `C3_1886` ?→1886-01-01: La obra empezó en 1882; las dificultades técnicas del trópico húmedo la acosan: deslizamientos recurrentes de cerros saturados dentro de las

### 43. Fritz Haber — `CAL_F005_02_HABER`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_02_HABER/entrada.json`
- SHA-256: `578a5e3b85e5c16634104c89da122c7be432c2c06689bcf4160c263067f84338` (corto `578a5e3b85e5`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/043_CAL_F005_02_HABER_578a5e3b85e5/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Fritz Haber): nacimiento=1868-12-09; fuente pública (Fritz Haber): muerte=1934-01-29
- Z90 calculada (90% nacimiento→muerte): 1927-07-26
- Z declarada en el input: 1932 (normalizada: 1932-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 2 / post 1
- Último corte pre-Z: C3_1932 1932-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1932-01-01 vs Z90 1927-07-26 (Δ 53.2 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1909` ?→1909-01-01: Es el primer químico en sintetizar amoníaco; con Carl Bosch en BASF el proceso se escala a producción industrial. Converso del judaísmo al l
  - `C2_1915` ?→1915-05-02: Nacionalista, dirige el desarrollo del cloro como arma y está presente en su primer uso en la segunda batalla de Ypres; días después su espo
  - `C3_1932` ?→1932-01-01 [post-Z90]: Premio Nobel de Química (1918), director del Instituto Kaiser Wilhelm de Fisicoquímica en Berlín-Dahlem; su búsqueda de oro en el agua de ma

### 44. Galileo Galilei — `CAL_F002_01_GALILEI`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_01_GALILEI/entrada.json`
- SHA-256: `7774f41d9de12c7130c70919fa93422d73b68acec3071b71916c20db2d37e799` (corto `7774f41d9de1`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/044_CAL_F002_01_GALILEI_7774f41d9de1/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Galileo Galilei): nacimiento=1564-02-15; fuente pública (Galileo Galilei): muerte=1642-01-08
- Z90 calculada (90% nacimiento→muerte): 1634-03-26
- Z declarada en el input: 1632-02-22 (normalizada: 1632-02-22)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1632 1632-02-22
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1632-02-22 vs Z90 1634-03-26 (Δ 25.1 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1610` ?→1610-03-13: Publicó el Sidereus Nuncius con sus observaciones telescópicas, dedicado a Cosme II de Médici; llamó estrellas mediceas a las lunas de Júpit
  - `C2_1623` ?→1623-01-01: Tras un decreto eclesiástico de 1616 que suspendió el libro de Copérnico hasta su corrección, el cardenal Maffeo Barberini, amigo y admirado
  - `C3_1632` ?→1632-02-22: Publicó el Diálogo sobre los dos máximos sistemas del mundo, que comparaba el sistema copernicano con el ptolemaico, con autorización formal

### 45. Giacomo Casanova — `CASANOVA_INTERIOR_20261014_SEARCH_MC_ON`

- Fuente original: `/workspace/MOTOR_1019/U6_UNIFICADO_20261020/audit/INTEGRACION_U6_R2_SEARCH_MC_MARCADOR_MORTALIDAD_V0_2/INPUT_CASANOVA_SEARCH_MC_OFF.json`
- SHA-256: `bc3b9b6e2fc1865dee2a45f42a253eae2f56ce87fd212e8d0142d6a5ee9da729` (corto `bc3b9b6e2fc1`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:02; paquete: 2026-10-20
- Copia en repo: `inputs/045_CASANOVA_INTERIOR_20261014_SEARCH_MC_ON_bc3b9b6e2fc1/INPUT_CASANOVA_SEARCH_MC_OFF.json`
- Nacimiento (input): 1725-04-02 (input.birth_date=1725-04-02)
- Muerte (input): 1798-06-04 (input.death_date=1798-06-04)
- Z90 calculada (90% nacimiento→muerte): 1791-02-08
- Z declarada en el input: 1791-12-31 (normalizada: 1791-12-31)
- Cortes: 10 total; pre-Z 10 / post-Z 0; vs Z90 calculada: pre 10 / post 0
- Último corte pre-Z: C10 1791-12-31
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1791-12-31 vs Z90 1791-02-08 (Δ 10.7 meses).
- Cortes:
  - `C1` 1725-01-01→1734-12-31: 1725-1734: nace en Venecia, hijo de actores; niño enfermizo; a los nueve años lo envían a una pensión en Padua; en su autobiografía recuerda
  - `C2` 1737-01-01→1742-12-31: 1737-1742: entra a la Universidad de Padua a los 12 y se gradúa en derecho a los 17; luego dirá que no tenía vocación por el derecho; recibe
  - `C3` 1743-01-01→1745-12-31: 1743-1745: expulsado del seminario de San Cipriano por conducta escandalosa; escribano del cardenal Acquaviva en Roma; despedido tras cargar
  - `C4` ?→1746-01-01: 1746: violinista de oficio en el teatro San Samuele, insatisfecho con su suerte; salva la vida del senador Bragadin tras un ataque en una gó
  - `C5` 1750-01-01→1755-12-31: 1750-1755: viaja; se hace masón en Lyon; París, Dresde, Praga, Viena; vuelve a Venecia; en 1755 es denunciado como mago y condenado a cinco 
  - `C6` ?→1756-10-31: 1756: tras meses de encierro, que en su relato vive con desesperación y planes obsesivos, logra una fuga espectacular de los Plomos el 31 de
  - `C7` 1757-01-01→1759-12-31: 1757-1759: en París ayuda a crear la lotería estatal y es uno de sus administradores; gana fortuna y nombre ante la aristocracia; vive de su
  - `C8` 1760-01-01→1774-12-31: 1760-1774: huye de acreedores, adopta el nombre de Caballero de Seingalt; recorre Suiza (conoce a Voltaire), Italia, Londres, Berlín, Rusia 
  - `C9` 1774-01-01→1785-12-31: 1774-1785: se le permite volver a Venecia y trabaja como informante de los inquisidores de Estado; sus empresas fracasan por falta de capita
  - `C10` 1789-01-01→1791-12-31 [Z_foto]: ~1789-1791: Z_foto STOP. Último 10% de vida sellado. Estado observable: en Dux, aislado, se dedica a escribir sus memorias; el texto narra s

### 46. Giacomo Casanova — `CASANOVA_INTERIOR_20261014_SEARCH_MC_ON`

- Fuente original: `/workspace/MOTOR_1019/U6_UNIFICADO_20261020/audit/INTEGRACION_U6_R2_SEARCH_MC_MARCADOR_MORTALIDAD_V0_2/INPUT_CASANOVA_SEARCH_MC_ON.json`
- SHA-256: `c938aeeeda1078fa179bb396ba94aa87ee488b9d2363997e88a11cf63653dd4a` (corto `c938aeeeda10`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:02; paquete: 2026-10-20
- Copia en repo: `inputs/046_CASANOVA_INTERIOR_20261014_SEARCH_MC_ON_c938aeeeda10/INPUT_CASANOVA_SEARCH_MC_ON.json`
- Nacimiento (input): 1725-04-02 (input.birth_date=1725-04-02)
- Muerte (input): 1798-06-04 (input.death_date=1798-06-04)
- Z90 calculada (90% nacimiento→muerte): 1791-02-08
- Z declarada en el input: 1791-12-31 (normalizada: 1791-12-31)
- Cortes: 10 total; pre-Z 10 / post-Z 0; vs Z90 calculada: pre 10 / post 0
- Último corte pre-Z: C10 1791-12-31
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1791-12-31 vs Z90 1791-02-08 (Δ 10.7 meses).
- Cortes:
  - `C1` 1725-01-01→1734-12-31: 1725-1734: nace en Venecia, hijo de actores; niño enfermizo; a los nueve años lo envían a una pensión en Padua; en su autobiografía recuerda
  - `C2` 1737-01-01→1742-12-31: 1737-1742: entra a la Universidad de Padua a los 12 y se gradúa en derecho a los 17; luego dirá que no tenía vocación por el derecho; recibe
  - `C3` 1743-01-01→1745-12-31: 1743-1745: expulsado del seminario de San Cipriano por conducta escandalosa; escribano del cardenal Acquaviva en Roma; despedido tras cargar
  - `C4` ?→1746-01-01: 1746: violinista de oficio en el teatro San Samuele, insatisfecho con su suerte; salva la vida del senador Bragadin tras un ataque en una gó
  - `C5` 1750-01-01→1755-12-31: 1750-1755: viaja; se hace masón en Lyon; París, Dresde, Praga, Viena; vuelve a Venecia; en 1755 es denunciado como mago y condenado a cinco 
  - `C6` ?→1756-10-31: 1756: tras meses de encierro, que en su relato vive con desesperación y planes obsesivos, logra una fuga espectacular de los Plomos el 31 de
  - `C7` 1757-01-01→1759-12-31: 1757-1759: en París ayuda a crear la lotería estatal y es uno de sus administradores; gana fortuna y nombre ante la aristocracia; vive de su
  - `C8` 1760-01-01→1774-12-31: 1760-1774: huye de acreedores, adopta el nombre de Caballero de Seingalt; recorre Suiza (conoce a Voltaire), Italia, Londres, Berlín, Rusia 
  - `C9` 1774-01-01→1785-12-31: 1774-1785: se le permite volver a Venecia y trabaja como informante de los inquisidores de Estado; sus empresas fracasan por falta de capita
  - `C10` 1789-01-01→1791-12-31 [Z_foto]: ~1789-1791: Z_foto STOP. Último 10% de vida sellado. Estado observable: en Dux, aislado, se dedica a escribir sus memorias; el texto narra s

### 47. Giacomo Casanova — `CASANOVA_INTERIOR_20261014`

- Fuente original: `/workspace/MOTOR_FINAL/HANDOFF_GROK/CASOS/INPUT_ESTANDAR_CASANOVA.json`
- SHA-256: `76e3cf1900244f07d67258c2177eaa23f96515bc12d7a8c6c1bc91f6d2b0da34` (corto `76e3cf190024`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:01
- Copia en repo: `inputs/047_CASANOVA_INTERIOR_20261014_76e3cf190024/INPUT_ESTANDAR_CASANOVA.json`
- Nacimiento (input): 1725-04-02 (input.birth_date=1725-04-02)
- Muerte (input): 1798-06-04 (input.death_date=1798-06-04)
- Z90 calculada (90% nacimiento→muerte): 1791-02-08
- Z declarada en el input: 1791-12-31 (normalizada: 1791-12-31)
- Cortes: 10 total; pre-Z 10 / post-Z 0; vs Z90 calculada: pre 10 / post 0
- Último corte pre-Z: C10 1791-12-31
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1791-12-31 vs Z90 1791-02-08 (Δ 10.7 meses).
- Cortes:
  - `C1` 1725-01-01→1734-12-31: 1725-1734: nace en Venecia, hijo de actores; niño enfermizo; a los nueve años lo envían a una pensión en Padua; en su autobiografía recuerda
  - `C2` 1737-01-01→1742-12-31: 1737-1742: entra a la Universidad de Padua a los 12 y se gradúa en derecho a los 17; luego dirá que no tenía vocación por el derecho; recibe
  - `C3` 1743-01-01→1745-12-31: 1743-1745: expulsado del seminario de San Cipriano por conducta escandalosa; escribano del cardenal Acquaviva en Roma; despedido tras cargar
  - `C4` ?→1746-01-01: 1746: violinista de oficio en el teatro San Samuele, insatisfecho con su suerte; salva la vida del senador Bragadin tras un ataque en una gó
  - `C5` 1750-01-01→1755-12-31: 1750-1755: viaja; se hace masón en Lyon; París, Dresde, Praga, Viena; vuelve a Venecia; en 1755 es denunciado como mago y condenado a cinco 
  - `C6` ?→1756-10-31: 1756: tras meses de encierro, que en su relato vive con desesperación y planes obsesivos, logra una fuga espectacular de los Plomos el 31 de
  - `C7` 1757-01-01→1759-12-31: 1757-1759: en París ayuda a crear la lotería estatal y es uno de sus administradores; gana fortuna y nombre ante la aristocracia; vive de su
  - `C8` 1760-01-01→1774-12-31: 1760-1774: huye de acreedores, adopta el nombre de Caballero de Seingalt; recorre Suiza (conoce a Voltaire), Italia, Londres, Berlín, Rusia 
  - `C9` 1774-01-01→1785-12-31: 1774-1785: se le permite volver a Venecia y trabaja como informante de los inquisidores de Estado; sus empresas fracasan por falta de capita
  - `C10` 1789-01-01→1791-12-31 [Z_foto]: ~1789-1791: Z_foto STOP. Último 10% de vida sellado. Estado observable: en Dux, aislado, se dedica a escribir sus memorias; el texto narra s

### 48. Gregor Mendel — `CAL_F004_04_MENDEL`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_04_MENDEL/entrada.json`
- SHA-256: `8ba5c5ee72952055c9a1891722b3f7414ee07727ff81582345b2f4a2138d3e63` (corto `8ba5c5ee7295`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/048_CAL_F004_04_MENDEL_8ba5c5ee7295/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Gregor Mendel): nacimiento=1822-07-20; fuente pública (Gregor Mendel): muerte=1884-01-06
- Z90 calculada (90% nacimiento→muerte): 1877-11-13
- Z declarada en el input: 1866 (normalizada: 1866-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1866 1866-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1866-01-01 vs Z90 1877-11-13 (Δ 142.4 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1850` ?→1850-01-01: Fraile agustino en Brno y maestro suplente; reprueba la parte oral del examen para maestro certificado. \| 1850 \| 1850
  - `C2_1856` ?→1856-01-01: Estudia en Viena (física con Doppler) patrocinado por su superior Cyril Napp; vuelve a Brno como maestro; en 1856 reprueba otra vez el oral;
  - `C3_1866` ?→1866-01-01: Tras cultivar unas 28 000 plantas de guisante (1856–1863) presenta sus experimentos de hibridación en dos sesiones de la Sociedad de Histori

### 49. Gustave Courbet — `CAL_F005_01_COURBET`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_01_COURBET/entrada.json`
- SHA-256: `a81708648e0fe77f5a12ef24eb3a26553fa82cb427068de9b3530fe0dd638b5c` (corto `a81708648e0f`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/049_CAL_F005_01_COURBET_a81708648e0f/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Gustave Courbet): nacimiento=1819-06-10; fuente pública (Gustave Courbet): muerte=1877-12-31
- Z90 calculada (90% nacimiento→muerte): 1872-02-22
- Z declarada en el input: 1871-04-27 (normalizada: 1871-04-27)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1871_04 1871-04-27
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1871-04-27 vs Z90 1872-02-22 (Δ 9.9 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1855` ?→1855-01-01: Le rechazan obras en la Exposición Universal (entre ellas Entierro en Ornans y El taller del pintor) y él levanta por su cuenta el Pabellón 
  - `C2_1870` ?→1870-09-04: Rechaza la Legión de Honor que le ofrece Napoleón III, lo que enoja al poder y lo vuelve muy popular entre la oposición; en septiembre pide 
  - `C3_1871_04` ?→1871-04-27: Con la Comuna de París organiza la Federación de Artistas; es elegido delegado del 6.º distrito y Delegado de Bellas Artes; el 27 de abril p

### 50. Harry S. Truman — `CAL_F004_06_TRUMAN`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_06_TRUMAN/entrada.json`
- SHA-256: `1691fb7f5844d4c75dffacfdb86bb8edc28d5a8101c5af26151769b6d3f5fc65` (corto `1691fb7f5844`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/050_CAL_F004_06_TRUMAN_1691fb7f5844/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Harry S. Truman): nacimiento=1884-05-08; fuente pública (Harry S. Truman): muerte=1972-12-26
- Z90 calculada (90% nacimiento→muerte): 1964-02-15
- Z declarada en el input: 1948-07 (normalizada: 1948-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1948_07 1948-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1948-01-01 vs Z90 1964-02-15 (Δ 193.5 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1945` ?→1945-04-12: Vicepresidente desde hace 82 días, poco consultado por Roosevelt; a la muerte de este jura como presidente y dice sentir que se le vinieron 
  - `C2_1946` ?→1946-01-01: Su aprobación cae del 82 % (enero) al 52 % (junio) y luego al 32 %; los republicanos ganan el Congreso en las elecciones de mitad de periodo
  - `C3_1948_07` ?→1948-01-01: En primavera tiene 36 % de aprobación y casi nadie lo cree capaz de ganar; en la convención ataca al 'Congreso que no hace nada'; firma la O

### 51. Henry Ford — `CAL_LOTE01_07_FORD`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_07_FORD.json`
- SHA-256: `a9ebf27e65fe3d3624cf1321db523e6e71e9209991a4179338a98cd24b92d78f` (corto `a9ebf27e65fe`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/051_CAL_LOTE01_07_FORD_a9ebf27e65fe/CAL_LOTE01_07_FORD.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Henry Ford): nacimiento=1863-07-30; fuente pública (Henry Ford): muerte=1947-04-07
- Z90 calculada (90% nacimiento→muerte): 1938-11-23
- Z declarada en el input: C3_1903 (normalizada: 1903-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1901 1901-11-30
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1903-01-01 vs Z90 1938-11-23 (Δ 430.7 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1896` ?→1896-06-04: Construye el Quadricycle mientras trabaja en Edison Illuminating Company. \| 1896-06-04 \| 1896-06-04
  - `C2_1901` ?→1901-11-30: Detroit Automobile Co. fracasa; deja Henry Ford Company por choques con inversores. \| 1901-11-30 \| 1901-11-30
  - `C3_1903` ?→1903-06-16 [post-Z decl.]: Funda Ford Motor Company con Malcomson y otros inversores. \| 1903-06-16 \| 1903-06-16

### 52. Herbert Hoover — `CAL_F005_04_HOOVER`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_04_HOOVER/entrada.json`
- SHA-256: `2dad1342091f9424f44247eb38c579d657dde63c7fe476586eafa4cbb852f466` (corto `2dad1342091f`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/052_CAL_F005_04_HOOVER_2dad1342091f/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Herbert Hoover): nacimiento=1874-08-10; fuente pública (Herbert Hoover): muerte=1964-10-20
- Z90 calculada (90% nacimiento→muerte): 1955-10-14
- Z declarada en el input: 1928-11 (normalizada: 1928-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1928 1928-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1928-01-01 vs Z90 1955-10-14 (Δ 333.4 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1917` ?→1917-01-01: Ingeniero de minas enriquecido; en 1914 organiza y dirige la Comisión de Ayuda a Bélgica; en 1917 Wilson lo pone al frente de la Administrac
  - `C2_1927` ?→1927-01-01: Tras buscar sin éxito la candidatura republicana en 1920, es secretario de Comercio con Harding y Coolidge (1921–1928), muy activo y visible
  - `C3_1928` ?→1928-01-01: Gana la candidatura republicana y vence a Al Smith por amplio margen en la elección presidencial de 1928, apoyado en su reputación nacional 

### 53. Herman Melville — `CAL_F005_10_MELVILLE`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_10_MELVILLE/entrada.json`
- SHA-256: `14cf75067e7501339246be3c3391980411f819dc83df2b223fe57538fcd33ba1` (corto `14cf75067e75`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/053_CAL_F005_10_MELVILLE_14cf75067e75/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Herman Melville): nacimiento=1819-08-01; fuente pública (Herman Melville): muerte=1891-09-28
- Z90 calculada (90% nacimiento→muerte): 1884-07-10
- Z declarada en el input: 1851-09 (normalizada: 1851-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1851 1851-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1851-01-01 vs Z90 1884-07-10 (Δ 402.3 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1847` ?→1847-01-01: Marinero que desertó de un ballenero en las Marquesas; su primer libro Typee (1846) y la secuela Omoo (1847) tienen éxito y le dan seguridad
  - `C2_1850` ?→1850-01-01: Mardi (1849), su primer libro no basado en su experiencia, no es bien recibido; Redburn (1849) y White-Jacket (1850) reciben reseñas respeta
  - `C3_1851` ?→1851-01-01: Pide prestados 3 000 dólares a su suegro para comprar la granja Arrowhead en Pittsfield (septiembre de 1850); traba amistad intensa con Hawt

### 54. Ignaz Semmelweis — `CAL_LOTE01_03_SEMMELWEIS`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_03_SEMMELWEIS.json`
- SHA-256: `9cc748fb17f278ace264c2f4a7ea07f31f764a9b614f437e1473cd8dd77ba604` (corto `9cc748fb17f2`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/054_CAL_LOTE01_03_SEMMELWEIS_9cc748fb17f2/CAL_LOTE01_03_SEMMELWEIS.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Ignaz Semmelweis): nacimiento=1818-07-01; fuente pública (Ignaz Semmelweis): muerte=1865-08-13
- Z90 calculada (90% nacimiento→muerte): 1860-11-26
- Z declarada en el input: C3_1849 (normalizada: 1849-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1847 1847-05-15
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1849-01-01 vs Z90 1860-11-26 (Δ 142.8 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1846` ?→1846-07-01: Asistente en la Primera Clínica obstétrica de Viena con mortalidad materna alta frente a la Segunda. \| 1846-07-01 \| 1846-07-01
  - `C2_1847` ?→1847-05-15: Tras la muerte de Kolletschka instaura el lavado con cloruro de cal; la mortalidad cae drásticamente. \| 1847-05-15 \| 1847-05-15
  - `C3_1849` ?→1849-03-20 [post-Z decl.]: No le renuevan el puesto; choca con su jefe Klein y casi no publica. \| 1849-03-20 \| 1849-03-20

### 55. Isabel Tudor (Isabel I de Inglaterra) — `CAL_F005_09_ISABEL_I`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_09_ISABEL_I/entrada.json`
- SHA-256: `678978f96d93fb46e2bfffc7d390939c32a765b1dfd3057b4de6bd0a5ff67d93` (corto `678978f96d93`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/055_CAL_F005_09_ISABEL_I_678978f96d93/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Isabel I): nacimiento=1533-09-07; fuente pública (Isabel I): muerte=1603-03-24
- Z90 calculada (90% nacimiento→muerte): 1596-04-09
- Z declarada en el input: 1558-10 (normalizada: 1558-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1558_10 1558-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1558-01-01 vs Z90 1596-04-09 (Δ 459.2 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1536` ?→1536-05-19: Hija de Enrique VIII y Ana Bolena; a los dos años y ocho meses su madre es decapitada y ella es declarada ilegítima y apartada de la sucesió
  - `C2_1554` ?→1554-05-22: Educada como protestante y de las mujeres más instruidas de su generación; bajo su media hermana María, católica, se la interroga por la reb
  - `C3_1558_10` ?→1558-01-01: El supuesto embarazo de María (1555) resulta falso y la sucesión de Isabel parece asegurada; Felipe de España la cultiva como aliada; en 155

### 56. Ivar Kreuger — `CAL_F005_06_KREUGER`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_06_KREUGER/entrada.json`
- SHA-256: `9b3f8cd9326c2db5479c62521326a1db4c27ad63e0cb2883b4e3646d69bda93b` (corto `9b3f8cd9326c`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/056_CAL_F005_06_KREUGER_9b3f8cd9326c/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Ivar Kreuger): nacimiento=1880-03-20; fuente pública (Ivar Kreuger): muerte=1932-03-12
- Z90 calculada (90% nacimiento→muerte): 1926-12-31
- Z declarada en el input: 1931-07 (normalizada: 1931-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 0 / post 3
- Último corte pre-Z: C3_1931 1931-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1931-01-01 vs Z90 1926-12-31 (Δ 48.0 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1928` ?→1928-01-01 [post-Z90]: Ingeniero cofundador de Kreuger & Toll (1908); entre 1925 y 1928 presta a gobiernos europeos y latinoamericanos a cambio de monopolios de fó
  - `C2_1929` ?→1929-01-01 [post-Z90]: En 1929 toma la mayoría de Ericsson, la minera Boliden, parte de SKF y bancos en Suecia, Alemania y Francia, a menudo con el propio dinero d
  - `C3_1931` ?→1931-01-01 [post-Z90]: En la primavera de 1930 lo recibe el presidente de EE. UU. en la Casa Blanca y Syracuse lo hace doctor honoris causa; en marzo de 1931 el ba

### 57. J. Robert Oppenheimer — `CAL_F004_03_OPPENHEIMER`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_03_OPPENHEIMER/entrada.json`
- SHA-256: `b51580b50f6b349b29671444ac1b3d32bd538d8c7e35596c9c3f8b41c7b7d7ef` (corto `b51580b50f6b`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/057_CAL_F004_03_OPPENHEIMER_b51580b50f6b/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (J. Robert Oppenheimer): nacimiento=1904-04-22; fuente pública (J. Robert Oppenheimer): muerte=1967-02-18
- Z90 calculada (90% nacimiento→muerte): 1960-11-06
- Z declarada en el input: 1953-06 (normalizada: 1953-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1953_06 1953-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1953-01-01 vs Z90 1960-11-06 (Δ 94.2 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1947` ?→1947-01-01: Director del Instituto de Estudios Avanzados de Princeton y presidente del Comité Asesor General de la nueva Comisión de Energía Atómica; pr
  - `C2_1950` ?→1950-01-31: En 1949 testifica ante el Comité de Actividades Antiestadounidenses sobre sus vínculos comunistas de los años treinta y los de sus alumnos; 
  - `C3_1953_06` ?→1953-01-01: Sale del GAC en agosto de 1952 porque Truman no lo renueva (opositores pidieron su salida); preside el panel de desarme y publica en Foreign

### 58. Jacques-Louis David — `CAL_F004_02_DAVID`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_02_DAVID/entrada.json`
- SHA-256: `da23e1a1cfadd56f2a768c02694757930b3512231186577a3b6e3cb0ef82d104` (corto `da23e1a1cfad`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/058_CAL_F004_02_DAVID_da23e1a1cfad/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Jacques-Louis David): nacimiento=1748-08-30; fuente pública (Jacques-Louis David): muerte=1825-12-29
- Z90 calculada (90% nacimiento→muerte): 1818-04-06
- Z declarada en el input: 1794-06-08 (normalizada: 1794-06-08)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1794_06 1794-06-08
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1794-06-08 vs Z90 1818-04-06 (Δ 285.9 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1784` ?→1784-01-01: Tras tres intentos fallidos por el Premio de Roma (con huelga de hambre en 1772) lo gana en 1774; en Roma pinta El juramento de los Horacios
  - `C2_1793` ?→1793-01-01: Jacobino y amigo de Robespierre y de Marat; vota en la Convención por la ejecución de Luis XVI; tras el asesinato de Marat pinta La muerte d
  - `C3_1794_06` ?→1794-06-08: Miembro del Comité de Seguridad General, contribuye directamente al Terror; organiza la Fiesta del Ser Supremo de Robespierre (20 pradial de

### 59. Johann Sebastian Bach — `CAL_F002_04_BACH`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_04_BACH/entrada.json`
- SHA-256: `805d719d412f057b567efe41f969b93fc58ebf3e4aa49f9181346eabf6e8222f` (corto `805d719d412f`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/059_CAL_F002_04_BACH_805d719d412f/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Johann Sebastian Bach): nacimiento=1685-03-31; fuente pública (Johann Sebastian Bach): muerte=1750-07-28
- Z90 calculada (90% nacimiento→muerte): 1744-01-15
- Z declarada en el input: 1723-05-30 (normalizada: 1723-05-30)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1723 1723-05-30
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1723-05-30 vs Z90 1744-01-15 (Δ 247.6 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1717` ?→1717-12-02: Al insistir con terquedad en que la corte de Weimar lo dejara ir, fue detenido el 6 de noviembre de 1717 y liberado el 2 de diciembre con un
  - `C2_1721` ?→1721-12-03: En Köthen se dedicó sobre todo a la música instrumental; el 7 de julio de 1720 perdió de forma repentina a su esposa Maria Barbara; el 24 de
  - `C3_1723` ?→1723-05-30: El concejo de Leipzig le ofreció el puesto de cantor de Santo Tomás después de que Telemann y Graupner lo rechazaran; asumió en 1723 la prep

### 60. John D. Rockefeller — `CAL_F002_09_ROCKEFELLER`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_09_ROCKEFELLER/entrada.json`
- SHA-256: `8d817fffc938d0f56b280221eee35448556de19afa9e3623f78e0c080fd67151` (corto `8d817fffc938`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/060_CAL_F002_09_ROCKEFELLER_8d817fffc938/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (John D. Rockefeller): nacimiento=1839-07-08; fuente pública (John D. Rockefeller): muerte=1937-05-23
- Z90 calculada (90% nacimiento→muerte): 1927-08-09
- Z declarada en el input: 1870-01-10 (normalizada: 1870-01-10)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1870 1870-01-10
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1870-01-10 vs Z90 1927-08-09 (Δ 690.9 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1859` ?→1859-01-01: Con ahorros propios y 1000 dólares prestados por su padre fundó en Cleveland con Maurice Clark y George Gardner una casa de comisiones de pr
  - `C2_1868` ?→1868-01-01: En febrero de 1865 compró en subasta la parte de los hermanos Clark en la refinería por 72 500 dólares y formó Rockefeller & Andrews, día qu
  - `C3_1870` ?→1870-01-10: El 10 de enero de 1870 disolvió la sociedad Rockefeller, Andrews & Flagler y cofundó con sus socios la Standard Oil Company de Ohio. \| 1870-

### 61. John Law — `CAL_F003_08_LAW`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_08_LAW/entrada.json`
- SHA-256: `6e7ac546395609ad013e728c0c7ab032a684f1211957e1b7ede977252784a797` (corto `6e7ac5463956`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/061_CAL_F003_08_LAW_6e7ac5463956/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (John Law): nacimiento=1671-04-21; fuente pública (John Law): muerte=1729-03-21
- Z90 calculada (90% nacimiento→muerte): 1723-06-06
- Z declarada en el input: 1720-01-05 (normalizada: 1720-01-05)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1720 1720-01-05
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1720-01-05 vs Z90 1723-06-06 (Δ 41.0 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1705` ?→1705-01-01: Jugador hábil con el cálculo de probabilidades, en 1694 mató en duelo a Edward Wilson en Londres, fue condenado y escapó a Ámsterdam; en 170
  - `C2_1718` ?→1718-01-01: En mayo de 1716 el regente Felipe de Orleans aprobó su banco privado de billetes; en 1717 fundó la Compañía de Occidente (Mississippi) para 
  - `C3_1720` ?→1720-01-05: En 1719 su compañía absorbió otras compañías coloniales, la acuñación y el cobro de impuestos, y sus acciones pasaron de 500 a 3,000 libras 

### 62. Joseph McCarthy — `CAL_F002_05_MCCARTHY`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_05_MCCARTHY/entrada.json`
- SHA-256: `a84c20ef8b32c2c09b1ca351f95628f8db81b3670194518dd09f96682db42ecb` (corto `a84c20ef8b32`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/062_CAL_F002_05_MCCARTHY_a84c20ef8b32/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Joseph McCarthy): nacimiento=1908-11-14; fuente pública (Joseph McCarthy): muerte=1957-05-02
- Z90 calculada (90% nacimiento→muerte): 1952-06-27
- Z declarada en el input: 1954-02-18 (normalizada: 1954-02-18)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 1 / post 2
- Último corte pre-Z: C3_1954 1954-02-18
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1954-02-18 vs Z90 1952-06-27 (Δ 19.7 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1950` ?→1950-02-09: En un discurso en Wheeling, Virginia Occidental, mostró un papel que según dijo contenía una lista de comunistas conocidos que trabajaban en
  - `C2_1953` ?→1953-01-01 [post-Z90]: Al iniciar su segundo mandato en enero de 1953 pasó a presidir la Comisión de Operaciones Gubernamentales del Senado, que incluía el Subcomi
  - `C3_1954` ?→1954-02-18 [post-Z90]: El subcomité citó el 30 de enero de 1954 al mayor del Ejército Irving Peress, que se acogió a la Quinta Enmienda; el 18 de febrero de 1954 i

### 63. Juan Pablo II — ``

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_JPII_Z1995.json`
- SHA-256: `3e2d9db9896836acc8aec1817191c03d70d7ccfb626e462e5d91ad308f6f3d4c` (corto `3e2d9db98968`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:57; paquete: 2026-10-11
- Copia en repo: `inputs/063_Juan_Pablo_II_3e2d9db98968/IN_JPII_Z1995.json`
- Markers del mismo paquete: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/markers_juan_pablo_ii.json` (`86f2b4412816`)
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Juan Pablo II): nacimiento=1920-05-18; fuente pública (Juan Pablo II): muerte=2005-04-02
- Z90 calculada (90% nacimiento→muerte): 1996-10-06
- Z declarada en el input: sufijo de archivo/carpeta Z1995, se toma 1995-12-31 (normalizada: 1995-12-31)
- Cortes: 9 total; pre-Z 9 / post-Z 0; vs Z90 calculada: pre 9 / post 0
- Último corte pre-Z: — 
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1995-12-31 vs Z90 1996-10-06 (Δ 9.2 meses). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1`: Wadowice; muerte de Emilia (1929) y Edmund
  - `C2`: Ocupación nazi; cantera/fábrica; teatro rapsódico clandestino
  - `C3`: Seminario clandestino; ordenación 1946
  - `C4`: Cátedra; Amor y responsabilidad; Vaticano II
  - `C5`: Arzobispo/cardenal de Cracovia frente al Estado
  - `C6`: Cónclave 1978; primer papa eslavo
  - `C7`: Viaje 1979 a Polonia; atentado 1981
  - `C8`: Solidaridad; desmonte del bloque 1989
  - `C9`: Parkinson; papado tardío visible

### 64. Kenneth Lay — `CAL_F004_09_LAY`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_09_LAY/entrada.json`
- SHA-256: `8f31b211572116733d883a6a9a4184a8f6004f1e3c7cc18a7857518c502f8aa5` (corto `8f31b2115721`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/064_CAL_F004_09_LAY_8f31b2115721/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Kenneth Lay): nacimiento=1942-04-15; fuente pública (Kenneth Lay): muerte=2006-07-05
- Z90 calculada (90% nacimiento→muerte): 2000-02-01
- Z declarada en el input: 2001-07 (normalizada: 2001-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 2 / post 1
- Último corte pre-Z: C3_2001_07 2001-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 2001-01-01 vs Z90 2000-02-01 (Δ 11.0 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1985` ?→1985-01-01: Hijo de un predicador bautista, crecido en la pobreza tras el fracaso de la tienda familiar; doctor en economía; preside Houston Natural Gas
  - `C2_2000` ?→2000-01-01: Los ingresos de Enron pasan de 13 300 a 100 700 millones de dólares (1996–2000); la acción cierra 2000 en 83,13 dólares con capitalización d
  - `C3_2001_07` ?→2001-01-01 [post-Z90]: Lay preside el consejo y Skilling es director general; un artículo de Fortune (marzo) pregunta si Enron está sobrevalorada y no explica cómo

### 65. Kurt Cobain — ``

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_COBAIN_Z1990.json`
- SHA-256: `988b59bfc4829c6ecd100bfab1491feeb1beaa69eeb26cd477b234dcc37162ab` (corto `988b59bfc482`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:57; paquete: 2026-10-11
- Copia en repo: `inputs/065_Kurt_Cobain_988b59bfc482/IN_COBAIN_Z1990.json`
- Markers del mismo paquete: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/markers_kurt_cobain_Z1990.json` (`4e042ce61186`)
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Kurt Cobain): nacimiento=1967-02-20; fuente pública (Kurt Cobain): muerte=1994-04-05
- Z90 calculada (90% nacimiento→muerte): 1991-07-19
- Z declarada en el input: 1990 (normalizada: 1990-01-01)
- Cortes: 9 total; pre-Z 9 / post-Z 0; vs Z90 calculada: pre 9 / post 0
- Último corte pre-Z: C9 1990-01-01
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1990-01-01 vs Z90 1991-07-19 (Δ 18.5 meses). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1`: Aberdeen; infancia con Wendy y Don; entorno rough working-class
  - `C2`: Divorcio de los padres (c.1979); Kurt shuttled; sentimiento de abandono
  - `C3`: Adolescencia; rechazo escolar; arte/dibujo; isolation
  - `C4`: Primera bandas / Fecal Matter; guitarra como escape
  - `C5`: Inestabilidad de vivienda; periodos sin casa fija; amigos/sofás
  - `C6`: Forma Nirvana con Krist; escena Olympia/Aberdeen-Tacoma
  - `C7`: Bleach (1989) Sub Pop; gira underground; identidad de banda
  - `C8` ?→1989-12-31: 1989-90: ritmo de gira indie; tension creativa; cuerpo/habitos ya frágiles (sin diagnosticar fama global)
  - `C9` ?→1990-01-01 [Z_foto]: Z=1990: banda consolidada en circuito indie; al borde de un salto mayor aún no ocurrido en la foto

### 66. Kurt Cobain — ``

- Fuente original: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/COBAIN_Z1990_EJERCICIO_CIEGO_COMPLETO.json`
- SHA-256: `90ff9cf09ea548413a17d23c64a8b214aa1ead9716739e3f00e71e0d3720aab6` (corto `90ff9cf09ea5`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:53
- Copia en repo: `inputs/066_Kurt_Cobain_90ff9cf09ea5/COBAIN_Z1990_EJERCICIO_CIEGO_COMPLETO.json.gz` (gzip)
- Markers del mismo paquete: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/5x3_RESEARCH/markers_kurt_cobain_Z1990.json` (`4e042ce61186`)
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Kurt Cobain): nacimiento=1967-02-20; fuente pública (Kurt Cobain): muerte=1994-04-05
- Z90 calculada (90% nacimiento→muerte): 1991-07-19
- Z declarada en el input: 1990 = C9 (normalizada: 1990-01-01)
- Cortes: 9 total; pre-Z 9 / post-Z 0; vs Z90 calculada: pre 9 / post 0
- Último corte pre-Z: C9 1990-01-01
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1990-01-01 vs Z90 1991-07-19 (Δ 18.5 meses). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1`: Aberdeen; infancia con Wendy y Don; entorno rough working-class
  - `C2`: Divorcio de los padres (c.1979); Kurt shuttled; sentimiento de abandono
  - `C3`: Adolescencia; rechazo escolar; arte/dibujo; isolation
  - `C4`: Primera bandas / Fecal Matter; guitarra como escape
  - `C5`: Inestabilidad de vivienda; periodos sin casa fija; amigos/sofás
  - `C6`: Forma Nirvana con Krist; escena Olympia/Aberdeen-Tacoma
  - `C7`: Bleach (1989) Sub Pop; gira underground; identidad de banda
  - `C8` ?→1989-12-31: 1989-90: ritmo de gira indie; tension creativa; cuerpo/habitos ya frágiles (sin diagnosticar fama global)
  - `C9` ?→1990-01-01 [Z_foto]: Z=1990: banda consolidada en circuito indie; al borde de un salto mayor aún no ocurrido en la foto

### 67. León Trotski — `CAL_F003_06_TROTSKY`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_06_TROTSKY/entrada.json`
- SHA-256: `e92fd2825725c0359480c89c6896b76e3fca0b622c4fa9c480ffdccbe7668f47` (corto `e92fd2825725`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/067_CAL_F003_06_TROTSKY_e92fd2825725/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (León Trotsky): nacimiento=1879-11-07; fuente pública (León Trotsky): muerte=1940-08-21
- Z90 calculada (90% nacimiento→muerte): 1934-07-24
- Z declarada en el input: 1923-10-15 (normalizada: 1923-10-15)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1923 1923-10-15
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1923-10-15 vs Z90 1934-07-24 (Δ 129.3 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1918` ?→1918-03-13: Presidente del Sóviet de Petrogrado, dirigió la organización práctica de la Revolución de Octubre de 1917; fue comisario de Asuntos Exterior
  - `C2_1922` ?→1922-09-11: Con Lenin enfermo tras su primer infarto cerebral de mayo de 1922, Stalin fue nombrado secretario general del Comité Central en abril de 192
  - `C3_1923` ?→1923-10-15: En el XII Congreso de abril de 1923 habló de democracia interna sin enfrentar a la troika y recibió una ovación; el 8 de octubre de 1923 esc

### 68. Louis Pasteur — `CAL_F002_02_PASTEUR`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_02_PASTEUR/entrada.json`
- SHA-256: `53fc65d239ad4c25dae1c7e70c8abf6099a7bfe04f4e5a2824a0d37c400eb59b` (corto `53fc65d239ad`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/068_CAL_F002_02_PASTEUR_53fc65d239ad/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Louis Pasteur): nacimiento=1822-12-27; fuente pública (Louis Pasteur): muerte=1895-09-28
- Z90 calculada (90% nacimiento→muerte): 1888-06-19
- Z declarada en el input: 1884-06-15 (normalizada: 1884-06-15)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1884 1884-06-15
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1884-06-15 vs Z90 1888-06-19 (Δ 48.1 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1862` ?→1862-01-01: Sus experimentos contra la generación espontánea, repetidos con Claude Bernard el 20 de abril de 1862, le valieron ese año el premio Alhumbe
  - `C2_1881` ?→1881-06-02: En Pouilly-le-Fort inoculó ovejas y cabras con cultivos atenuados de carbunco el 5 y el 17 de mayo de 1881, expuso a todos los animales al a
  - `C3_1884` ?→1884-06-15: En notas a la Academia de Ciencias de febrero y mayo de 1884 informó que la virulencia del agente de la rabia cambiaba al pasar por distinto

### 69. Ludwig van Beethoven — `CAL_LOTE01_06_BEETHOVEN`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_06_BEETHOVEN.json`
- SHA-256: `432c9dfa85e913930dc4c65ce24c5a41151e1ad1c6151a6e601f363390b14b14` (corto `432c9dfa85e9`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/069_CAL_LOTE01_06_BEETHOVEN_432c9dfa85e9/CAL_LOTE01_06_BEETHOVEN.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Ludwig van Beethoven): nacimiento=1770-12-17; fuente pública (Ludwig van Beethoven): muerte=1827-03-26
- Z90 calculada (90% nacimiento→muerte): 1821-08-09
- Z declarada en el input: C3_1802 (normalizada: 1802-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1800 1800-04-02
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1802-01-01 vs Z90 1821-08-09 (Δ 235.2 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1792` ?→1792-11-01: Llega a Viena a estudiar con Haydn. \| 1792-11-01 \| 1792-11-01
  - `C2_1800` ?→1800-04-02: Primera sinfonía; reconocimiento como pianista; oculta problemas de audición. \| 1800-04-02 \| 1800-04-02
  - `C3_1802` ?→1802-10-10 [post-Z decl.]: Testamento de Heiligenstadt: desesperación por la sordera, renuncia al suicidio por su arte. \| 1802-10-10 \| 1802-10-10

### 70. Luis II de Baviera — `CAL_F004_10_LUDWIG_II`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_10_LUDWIG_II/entrada.json`
- SHA-256: `c834c0bf3fab948fc87b52d514094ac0cb91a257165e82716b15fc090d2e4530` (corto `c834c0bf3fab`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/070_CAL_F004_10_LUDWIG_II_c834c0bf3fab/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Ludwig II de Baviera): nacimiento=1845-08-25; fuente pública (Ludwig II de Baviera): muerte=1886-06-13
- Z90 calculada (90% nacimiento→muerte): 1882-05-15
- Z declarada en el input: 1885 (normalizada: 1885-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 2 / post 1
- Último corte pre-Z: C3_1885 1885-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1885-01-01 vs Z90 1882-05-15 (Δ 31.6 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1864` ?→1864-01-01: Sube al trono de Baviera con 18 años, sin preparación pero muy popular; sus intereses reales son el arte, la música y la arquitectura; coloc
  - `C2_1871` ?→1871-01-18: Baviera pierde con Austria en 1866 y queda atada a Prusia; él se retira de la vida pública; en 1870 Bismarck le compra con concesiones finan
  - `C3_1885` ?→1885-01-01 [post-Z90]: Vive casi aislado en sus castillos (último desfile en 1875, último banquete en 1876); en 1885 debe 14 millones de marcos, ha pedido mucho pr

### 71. Luis XVI de Francia — `CAL_F002_08_LUISXVI`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_08_LUISXVI/entrada.json`
- SHA-256: `905cd94e3734ef2c44f6368c1e415adab41287e2208dc950be0511eac2a8ed27` (corto `905cd94e3734`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/071_CAL_F002_08_LUISXVI_905cd94e3734/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Luis XVI): nacimiento=1754-08-23; fuente pública (Luis XVI): muerte=1793-01-21
- Z90 calculada (90% nacimiento→muerte): 1789-03-20
- Z declarada en el input: 1791-04 (normalizada: 1791-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 0 / post 3
- Último corte pre-Z: C3_1791 1791-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1791-01-01 vs Z90 1789-03-20 (Δ 21.4 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1789A` ?→1789-05-05 [post-Z90]: Ante una grave crisis fiscal convocó los Estados Generales, que se abrieron en Versalles el 5 de mayo de 1789, la primera reunión desde 1614
  - `C2_1789B` ?→1789-10-06 [post-Z90]: Tras la marcha de las mujeres sobre Versalles, la multitud, con la Guardia Nacional al frente, llevó a la familia real a París el 6 de octub
  - `C3_1791` ?→1791-01-01 [post-Z90]: En Semana Santa de 1791 quiso salir de las Tullerías hacia Saint-Cloud para recibir los servicios de un sacerdote no juramentado, contrario 

### 72. Lázaro Cárdenas — `CAL_LOTE01_10_CARDENAS`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_10_CARDENAS.json`
- SHA-256: `744f7be3d03c354c59ae10fefa6a5617bc20488f845127295f179a1de2a89052` (corto `744f7be3d03c`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/072_CAL_LOTE01_10_CARDENAS_744f7be3d03c/CAL_LOTE01_10_CARDENAS.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Lázaro Cárdenas): nacimiento=1895-05-21; fuente pública (Lázaro Cárdenas): muerte=1970-10-19
- Z90 calculada (90% nacimiento→muerte): 1963-04-05
- Z declarada en el input: C3_1936 (normalizada: 1936-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1935 1935-06-15
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1936-01-01 vs Z90 1963-04-05 (Δ 327.1 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1934` ?→1934-12-01: Asume la presidencia como candidato de Calles (Maximato). \| 1934-12-01 \| 1934-12-01
  - `C2_1935` ?→1935-06-15: Ruptura con Calles tras sus críticas; Cárdenas remueve callistas del gabinete. \| 1935-06-15 \| 1935-06-15
  - `C3_1936` ?→1936-04-10 [post-Z decl.]: Calles es expulsado a EE. UU.; reparto agrario y apoyo obrero crecen. \| 1936-04-10 \| 1936-04-10

### 73. Marie Curie — `CAL_LOTE01_04_CURIE`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_04_CURIE.json`
- SHA-256: `034a133f493cc989723cbb023675c380f4ff12c63542b59c44c52e8b0b1a12ea` (corto `034a133f493c`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/073_CAL_LOTE01_04_CURIE_034a133f493c/CAL_LOTE01_04_CURIE.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Marie Curie): nacimiento=1867-11-07; fuente pública (Marie Curie): muerte=1934-07-04
- Z90 calculada (90% nacimiento→muerte): 1927-11-03
- Z declarada en el input: C3_1906 (normalizada: 1906-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1903 1903-12-10
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1906-01-01 vs Z90 1927-11-03 (Δ 262.0 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1891` ?→1891-11-01: Llega a París desde Varsovia para estudiar en la Sorbona con recursos escasos. \| 1891-11-01 \| 1891-11-01
  - `C2_1903` ?→1903-12-10: Doctorado y Premio Nobel de Física compartido por la radiactividad. \| 1903-12-10 \| 1903-12-10
  - `C3_1906` ?→1906-04-19 [post-Z decl.]: Pierre muere atropellado; ella hereda su cátedra en la Sorbona. \| 1906-04-19 \| 1906-04-19

### 74. Michael Faraday — `CAL_F003_04_FARADAY`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_04_FARADAY/entrada.json`
- SHA-256: `7dad402f8256312c61d451bdbe4da3cbc5c2acb1b664dfdd97b70a6d9ff46dfe` (corto `7dad402f8256`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/074_CAL_F003_04_FARADAY_7dad402f8256/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Michael Faraday): nacimiento=1791-09-22; fuente pública (Michael Faraday): muerte=1867-08-25
- Z90 calculada (90% nacimiento→muerte): 1860-01-21
- Z declarada en el input: 1821 (normalizada: 1821-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1821 1821-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1821-01-01 vs Z90 1860-01-21 (Δ 468.6 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1813` ?→1813-03-01: Aprendiz de encuadernador sin estudios formales, en 1812 asistió a las conferencias de Humphry Davy y le envió un libro de 300 páginas con s
  - `C2_1820` ?→1820-01-01: Entre 1813 y 1815 viajó por Europa con Davy; como su asistente estudió el cloro y en 1820 informó la primera síntesis de compuestos de carbo
  - `C3_1821` ?→1821-01-01: En 1821 fue nombrado superintendente asistente de la casa de la Royal Institution y el 12 de junio se casó con Sarah Barnard; ese año, tras 

### 75. Michelangelo Merisi da Caravaggio — `CAL_F003_01_CARAVAGGIO`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_01_CARAVAGGIO/entrada.json`
- SHA-256: `953aadc15725c4c40bbd231fc9391f90c6fe0bad619fb01c545dc04c273bd2ae` (corto `953aadc15725`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/075_CAL_F003_01_CARAVAGGIO_953aadc15725/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Caravaggio): nacimiento=1571-09-29; fuente pública (Caravaggio): muerte=1610-07-18
- Z90 calculada (90% nacimiento→muerte): 1606-08-31
- Z declarada en el input: 1605-08 (normalizada: 1605-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1605 1605-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1605-01-01 vs Z90 1606-08-31 (Δ 19.9 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1600` ?→1600-01-01: Con el apoyo del cardenal Francesco Maria del Monte, entregó en 1600 los dos lienzos de San Mateo para la capilla Contarelli de San Luigi de
  - `C2_1603` ?→1603-01-01: El 28 de noviembre de 1600 golpeó con un garrote al noble Girolamo Stampa, huésped de del Monte, y las riñas se hicieron frecuentes; en 1603
  - `C3_1605` ?→1605-01-01: Entre mayo y octubre de 1604 fue arrestado varias veces por portar armas ilegales e insultar a los guardias, y un mesero lo demandó por arro

### 76. Mijaíl Gorbachov — `CAL_LOTE01_09_GORBACHEV`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_09_GORBACHEV.json`
- SHA-256: `4132e6ce014749a2746a42d6f78e4bdba1a3e74f477f879e603875a6e23721e9` (corto `4132e6ce0147`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/076_CAL_LOTE01_09_GORBACHEV_4132e6ce0147/CAL_LOTE01_09_GORBACHEV.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Mijaíl Gorbachov): nacimiento=1931-03-02; fuente pública (Mijaíl Gorbachov): muerte=2022-08-30
- Z90 calculada (90% nacimiento→muerte): 2013-07-06
- Z declarada en el input: C3_1988 (normalizada: 1988-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1986 1986-04-26
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1988-01-01 vs Z90 2013-07-06 (Δ 306.1 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1985` ?→1985-03-11: Elegido secretario general del PCUS en una economía estancada. \| 1985-03-11 \| 1985-03-11
  - `C2_1986` ?→1986-04-26: Chernóbil; impulsa glásnost. \| 1986-04-26 \| 1986-04-26
  - `C3_1988` ?→1988-06-28 [post-Z decl.]: XIX Conferencia del Partido: reforma política; tensiones nacionalistas (Karabaj, Bálticos). \| 1988-06-28 \| 1988-06-28

### 77. Napoleón Bonaparte — `CAL_F001_01_NAPOLEON`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F001_01_NAPOLEON/entrada.json`
- SHA-256: `e05645ddb3eab1601992b86037b8ef530c6b27413575241b6bf0e3860e66b046` (corto `e05645ddb3ea`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/077_CAL_F001_01_NAPOLEON_e05645ddb3ea/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Napoleón Bonaparte): nacimiento=1769-08-15; fuente pública (Napoleón Bonaparte): muerte=1821-05-05
- Z90 calculada (90% nacimiento→muerte): 1816-03-03
- Z declarada en el input: C3_1812 (normalizada: 1812-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1805 1805-12-02
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1812-01-01 vs Z90 1816-03-03 (Δ 50.0 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1799` ?→1799-11-09: Golpe del 18 de brumario; se convierte en Primer Cónsul. \| 1799-11-09 \| 1799-11-09
  - `C2_1805` ?→1805-12-02: Emperador desde 1804; victoria en Austerlitz sobre Austria y Rusia. \| 1805-12-02 \| 1805-12-02
  - `C3_1812` ?→1812-06-24 [post-Z decl.]: Rusia abandona el Bloqueo Continental; Napoleón cruza el Niemen con unos 600 000 hombres. \| 1812-06-24 \| 1812-06-24

### 78. Nicolas Fouquet — `CAL_F003_05_FOUQUET`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_05_FOUQUET/entrada.json`
- SHA-256: `2c7af97e3fe816e3c69390d0b58cc4f39056e13bfcf763921281e6a9b368a2e5` (corto `2c7af97e3fe8`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/078_CAL_F003_05_FOUQUET_2c7af97e3fe8/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Nicolas Fouquet): nacimiento=1615-01-01; fuente pública (Nicolas Fouquet): muerte=1680-03-23
- Z90 calculada (90% nacimiento→muerte): 1673-09-14
- Z declarada en el input: 1661-08-17 (normalizada: 1661-08-17)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1661 1661-08-17
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1661-08-17 vs Z90 1673-09-14 (Δ 144.9 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1653` ?→1653-02-07: Durante la Fronda se mantuvo leal al cardenal Mazarino y a la regente Ana de Austria; como recompensa obtuvo el 7 de febrero de 1653 la supe
  - `C2_1658` ?→1658-01-01: Las finanzas reales estaban en desorden y él cubría a veces los pagos con su propio crédito; en 1658 compró Belle-Île y fortificó la isla co
  - `C3_1661` ?→1661-08-17: Al morir Mazarino el 9 de marzo de 1661 esperaba ser primer ministro, pero Luis XIV declaró que gobernaría sin primer ministro y Colbert le 

### 79. Nicolás II de Rusia — `CAL_F005_08_NICOLAS_II`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_08_NICOLAS_II/entrada.json`
- SHA-256: `f9d43876d181f8608a8c5996a9375a67428627aa8cc2a0c1ed62a320e622c55f` (corto `f9d43876d181`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/079_CAL_F005_08_NICOLAS_II_f9d43876d181/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Nicolás II): nacimiento=1868-05-18; fuente pública (Nicolás II): muerte=1918-07-17
- Z90 calculada (90% nacimiento→muerte): 1913-07-11
- Z declarada en el input: 1916-12-30 (normalizada: 1916-12-30)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 1 / post 2
- Último corte pre-Z: C3_1916_12 1916-12-30
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1916-12-30 vs Z90 1913-07-11 (Δ 41.7 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1905` ?→1905-01-01: Tras el Domingo Sangriento (enero de 1905), la derrota naval de Tsushima y la revolución de 1905 tiene que firmar el Manifiesto de Octubre: 
  - `C2_1915` ?→1915-01-01 [post-Z90]: Tras la Gran Retirada y la pérdida de Polonia destituye a su primo el gran duque Nicolás y asume el mando supremo del ejército en septiembre
  - `C3_1916_12` ?→1916-12-30 [post-Z90]: A fines de 1916 rechaza con firmeza la petición familiar de conceder una constitución y un gobierno responsable ante la Duma; el 2 de diciem

### 80. Nikita Jrushchov — `CAL_F004_05_KHRUSHCHEV`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_05_KHRUSHCHEV/entrada.json`
- SHA-256: `91988e3a63427efae031a6cbbf2050a90484ac65d130c3511326b535d0f6994c` (corto `91988e3a6342`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/080_CAL_F004_05_KHRUSHCHEV_91988e3a6342/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Nikita Jrushchov): nacimiento=1894-04-15; fuente pública (Nikita Jrushchov): muerte=1971-09-11
- Z90 calculada (90% nacimiento→muerte): 1963-12-15
- Z declarada en el input: 1963 (normalizada: 1963-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1963 1963-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1963-01-01 vs Z90 1963-12-15 (Δ 11.4 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1956` ?→1956-02-25: Tras imponerse en la lucha por el poder posterior a Stalin, pronuncia el 'Discurso secreto' en el XX Congreso, que demuele la reputación de 
  - `C2_1962` ?→1962-01-01: Sube los precios de carne y mantequilla (revuelta de Novocherkask reprimida); en la crisis de los misiles retira los misiles de Cuba, arregl
  - `C3_1963` ?→1963-01-01: Sequía y cosecha de grano muy por debajo del pico de 1958; colas por pan; agota las reservas de divisas y parte del oro para comprar grano; 

### 81. Nikola Tesla — `CAL_F001_02_TESLA`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F001_02_TESLA/entrada.json`
- SHA-256: `be89b315b99b09cb06f0cd46a5eb823aefd4e1b9681fea0279d8803128137635` (corto `be89b315b99b`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/081_CAL_F001_02_TESLA_be89b315b99b/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Nikola Tesla): nacimiento=1856-07-10; fuente pública (Nikola Tesla): muerte=1943-01-07
- Z90 calculada (90% nacimiento→muerte): 1934-05-15
- Z declarada en el input: C3_1901 (normalizada: 1901-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1893 1893-05-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1901-01-01 vs Z90 1934-05-15 (Δ 400.4 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1884` ?→1884-06-06: Llega a Nueva York, trabaja para Edison y renuncia al poco tiempo por un desacuerdo de pago. \| 1884-06-06 \| 1884-06-06
  - `C2_1893` ?→1893-05-01: Sus patentes de corriente alterna, licenciadas a Westinghouse (1888), iluminan la Exposición de Chicago. \| 1893-05-01 \| 1893-05-01
  - `C3_1901` ?→1901-03-01 [post-Z decl.]: Morgan acepta financiar con 150 000 dólares una torre de transmisión inalámbrica (Wardenclyffe). \| 1901-03-01 \| 1901-03-01

### 82. Oscar Wilde — `CAL_F001_03_WILDE`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F001_03_WILDE/entrada.json`
- SHA-256: `54247ffa2a4f5f1478ed253f5ae6f7c73fa947a3f991a979e12dc7a8ba4e9df8` (corto `54247ffa2a4f`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/082_CAL_F001_03_WILDE_54247ffa2a4f/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Oscar Wilde): nacimiento=1854-10-16; fuente pública (Oscar Wilde): muerte=1900-11-30
- Z90 calculada (90% nacimiento→muerte): 1896-04-19
- Z declarada en el input: C3_1895B (normalizada: 1895-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 1 / post-Z 2; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C1_1891 1891-06-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1895-01-01 vs Z90 1896-04-19 (Δ 15.6 meses). Cortes pre-Z: 1 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1891` ?→1891-06-01: Publica El retrato de Dorian Gray en libro y conoce a Lord Alfred Douglas. \| 1891-06-01 \| 1891-06-01
  - `C2_1895A` ?→1895-02-14 [post-Z decl.]: Estreno triunfal de La importancia de llamarse Ernesto en Londres. \| 1895-02-14 \| 1895-02-14
  - `C3_1895B` ?→1895-03-01 [post-Z decl.]: Queensberry le deja una tarjeta insultante en su club; Wilde obtiene orden de arresto contra él por difamación. \| 1895-03-01 \| 1895-03-01

### 83. Pedro II de Brasil — `CAL_F003_10_PEDRO_II`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F003_10_PEDRO_II/entrada.json`
- SHA-256: `1668c4dff7d71ac2ac6851bf60006d92ac7ce581bd113362b07436800d235bc5` (corto `1668c4dff7d7`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/083_CAL_F003_10_PEDRO_II_1668c4dff7d7/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Pedro II de Brasil): nacimiento=1825-12-02; fuente pública (Pedro II de Brasil): muerte=1891-12-05
- Z90 calculada (90% nacimiento→muerte): 1885-04-29
- Z declarada en el input: 1888-08 (normalizada: 1888-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 2 / post 1
- Último corte pre-Z: C3_1888 1888-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1888-01-01 vs Z90 1885-04-29 (Δ 32.1 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1840` ?→1840-07-23: Emperador desde los cinco años por la abdicación de su padre en 1831, tras una regencia inestable la Asamblea General lo declaró mayor de ed
  - `C2_1871` ?→1871-09-28: Dirigió con tenacidad la guerra contra Paraguay hasta la victoria del 1 de marzo de 1870 y rechazó una estatua ecuestre para construir escue
  - `C3_1888` ?→1888-01-01 [post-Z90]: Con la salud muy deteriorada desde junio de 1887, viajó a Europa y en Milán pasó dos semanas entre la vida y la muerte; el 13 de mayo de 188

### 84. Pío II / Enea Silvio Piccolomini — `PAPA_PIO_NOCTURNA_20261005`

- Fuente original: `/workspace/CORRIDA_NOCTURNA_20261005/CORRIDA_0547_20261006/inputs/INPUT_CAPA2_PAPA_PIO.json`
- SHA-256: `3e9261fafa58079de79110a450577c111498b6c2f3d980b0a09ed9dc1fd2b701` (corto `3e9261fafa58`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:08; paquete: 2026-10-05
- Copia en repo: `inputs/084_PAPA_PIO_NOCTURNA_20261005_3e9261fafa58/INPUT_CAPA2_PAPA_PIO.json`
- Nacimiento (input): 1405-10-18 (input.birth_date=1405-10-18)
- Muerte (input): 1464-08-14 (input.death_date=1464-08-14)
- Z90 calculada (90% nacimiento→muerte): 1458-09-26
- Z declarada en el input: 1464-08-14 (normalizada: 1464-08-14)
- Tipo/nota de Z: z90_date=fecha de muerte (no 90%)
- Cortes: 10 total; pre-Z 10 / post-Z 0; vs Z90 calculada: pre 7 / post 3
- Último corte pre-Z: C10 1464-08-01
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1464-08-14 vs Z90 1458-09-26 (Δ 70.6 meses).
- Cortes:
  - `C1` 1405-01-01→1429-12-31: 1405-1429: nace en Corsignano (Siena) en familia noble empobrecida; estudios en Siena y Florencia; formación humanista y jurídica temprana. 
  - `C2` 1431-01-01→1436-12-31: 1431-1436: entra al servicio diplomático en el Concilio de Basilea; oratoria y secretariado conciliar; exposición internacional. \| 1432-01-0
  - `C3` 1439-01-01→1442-12-31: 1439-1442: secretario del antipapa Félix V; luego pasa a la corte del emperador Federico III; cambio de lealtad institucional. \| 1440-01-01
  - `C4` 1445-01-01→1447-12-31: 1445-1447: reconciliación con Roma; toma órdenes; obispo de Trieste bajo Nicolás V; mediación entre estados alemanes y la Santa Sede. \| 1446
  - `C5` 1450-01-01→1455-12-31: 1450-1455: obispo de Siena; continúa mediación imperial-papal; consolidación eclesiástica y diplomática. \| 1450-01-01
  - `C6` 1456-01-01→1457-12-31: 1456-1457: creado cardenal; titular Santa Sabina; adquiere Warmia; presión por cruzada antiturca tras 1453. \| 1456-12-01
  - `C7` ?→1458-08-19: 1458: elegido papa (Pío II) tras Calixtus III; coronación; prioridad diplomática y recuperación de autoridad papal. \| 1458-08-19
  - `C8` 1459-01-01→1460-12-31 [post-Z90]: 1459-1460: Congreso de Mantua para coalición antiturca; respuesta limitada de príncipes; fricción diplomática. \| 1459-01-01
  - `C9` 1461-01-01→1463-12-31 [post-Z90]: 1461-1463: presión sobre Francia (Pragmática Sanción); proclama cruzada (1463); movilización papal pese a adhesión incompleta. \| 1462-01-01
  - `C10` ?→1464-08-01 [post-Z90]: 1464: viaja a Ancona para embarcar la cruzada; enfermedad; muerte el 14 ago 1464; la empresa se desvanece. \| 1464-08-01

### 85. Pío II / Enea Silvio Piccolomini — `PAPA_PIO_NOCTURNA_20261005`

- Fuente original: `/workspace/CORRIDA_NOCTURNA_20261005/inputs/INPUT_ESTANDAR_PAPA_PIO.json`
- SHA-256: `942c593d3fb55d5727526065b722add16def2292cf8e9d056accea0e96be5278` (corto `942c593d3fb5`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:07; paquete: 2026-10-05
- Copia en repo: `inputs/085_PAPA_PIO_NOCTURNA_20261005_942c593d3fb5/INPUT_ESTANDAR_PAPA_PIO.json`
- Nacimiento (input): 1405-10-18 (input.birth_date=1405-10-18)
- Muerte (input): 1464-08-14 (input.death_date=1464-08-14)
- Z90 calculada (90% nacimiento→muerte): 1458-09-26
- Z declarada en el input: 1464-08-14 (normalizada: 1464-08-14)
- Tipo/nota de Z: z90_date=fecha de muerte (no 90%)
- Cortes: 10 total; pre-Z 10 / post-Z 0; vs Z90 calculada: pre 7 / post 3
- Último corte pre-Z: C10 1464-08-01
- Veredicto: `Z_MAL_PUESTA` — Z declarada 1464-08-14 vs Z90 1458-09-26 (Δ 70.6 meses).
- Cortes:
  - `C1` 1405-01-01→1429-12-31: 1405-1429: nace en Corsignano (Siena) en familia noble empobrecida; estudios en Siena y Florencia; formación humanista y jurídica temprana. 
  - `C2` 1431-01-01→1436-12-31: 1431-1436: entra al servicio diplomático en el Concilio de Basilea; oratoria y secretariado conciliar; exposición internacional. \| 1432-01-0
  - `C3` 1439-01-01→1442-12-31: 1439-1442: secretario del antipapa Félix V; luego pasa a la corte del emperador Federico III; cambio de lealtad institucional. \| 1440-01-01
  - `C4` 1445-01-01→1447-12-31: 1445-1447: reconciliación con Roma; toma órdenes; obispo de Trieste bajo Nicolás V; mediación entre estados alemanes y la Santa Sede. \| 1446
  - `C5` 1450-01-01→1455-12-31: 1450-1455: obispo de Siena; continúa mediación imperial-papal; consolidación eclesiástica y diplomática. \| 1450-01-01
  - `C6` 1456-01-01→1457-12-31: 1456-1457: creado cardenal; titular Santa Sabina; adquiere Warmia; presión por cruzada antiturca tras 1453. \| 1456-12-01
  - `C7` ?→1458-08-19: 1458: elegido papa (Pío II) tras Calixtus III; coronación; prioridad diplomática y recuperación de autoridad papal. \| 1458-08-19
  - `C8` 1459-01-01→1460-12-31 [post-Z90]: 1459-1460: Congreso de Mantua para coalición antiturca; respuesta limitada de príncipes; fricción diplomática. \| 1459-01-01
  - `C9` 1461-01-01→1463-12-31 [post-Z90]: 1461-1463: presión sobre Francia (Pragmática Sanción); proclama cruzada (1463); movilización papal pese a adhesión incompleta. \| 1462-01-01
  - `C10` ?→1464-08-01 [post-Z90]: 1464: viaja a Ancona para embarcar la cruzada; enfermedad; muerte el 14 ago 1464; la empresa se desvanece. \| 1464-08-01

### 86. Richard Nixon — `CAL_LOTE01_01_NIXON`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_01_NIXON.json`
- SHA-256: `ad6f139dda3243515c67accd57b25f59bd7a7935a95e0bfa79ed508c3a0d22e1` (corto `ad6f139dda32`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/086_CAL_LOTE01_01_NIXON_ad6f139dda32/CAL_LOTE01_01_NIXON.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Richard Nixon): nacimiento=1913-01-09; fuente pública (Richard Nixon): muerte=1994-04-22
- Z90 calculada (90% nacimiento→muerte): 1986-03-06
- Z declarada en el input: C3_1973 (normalizada: 1973-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1972 1972-11-07
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1973-01-01 vs Z90 1986-03-06 (Δ 158.1 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1968` ?→1968-11-05: Gana la elección presidencial de 1968 tras derrotas en 1960 y 1962. \| 1968-11-05 \| 1968-11-05
  - `C2_1972` ?→1972-11-07: Reelección aplastante; en junio de 1972 ocurre el allanamiento del Watergate y su campaña lo encubre. \| 1972-11-07 \| 1972-11-07
  - `C3_1973` ?→1973-06-30 [post-Z decl.]: Audiencias del Senado; renuncian Haldeman y Ehrlichman (abril); John Dean testifica contra el presidente (junio). \| 1973-06-30 \| 1973-06-30

### 87. Richard Wagner — `CAL_F004_01_WAGNER`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F004_01_WAGNER/entrada.json`
- SHA-256: `ff8e2bf77851d9dcde1c4f4a269178b58b1fc62a8ab0a24cd4d49f839eaf352c` (corto `ff8e2bf77851`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/087_CAL_F004_01_WAGNER_ff8e2bf77851/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Richard Wagner): nacimiento=1813-05-22; fuente pública (Richard Wagner): muerte=1883-02-13
- Z90 calculada (90% nacimiento→muerte): 1876-02-23
- Z declarada en el input: 1863 (normalizada: 1863-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1863 1863-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1863-01-01 vs Z90 1876-02-23 (Δ 157.7 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1849` ?→1849-01-01: Participa en el fallido Levantamiento de Mayo de Dresde; se emiten órdenes de arresto, huye a París y se instala en Zúrich; comienza un exil
  - `C2_1861` ?→1861-01-01: El Tannhäuser de París es un fiasco notable: protestas organizadas por el Jockey Club y retirada de la obra tras pocas funciones. \| 1861 \| 1
  - `C3_1863` ?→1863-01-01: Levantada la prohibición política (1862), vive en Biebrich, se separa de forma irrevocable de su esposa Minna y empieza Los maestros cantore

### 88. Roscoe 'Fatty' Arbuckle — `CAL_F002_03_ARBUCKLE`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_03_ARBUCKLE/entrada.json`
- SHA-256: `f737feea7743992fcf2e3a7b2ae0855c88070faee55e08de44093f00848f8e78` (corto `f737feea7743`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/088_CAL_F002_03_ARBUCKLE_f737feea7743/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Roscoe Arbuckle): nacimiento=1887-03-24; fuente pública (Roscoe Arbuckle): muerte=1933-06-29
- Z90 calculada (90% nacimiento→muerte): 1928-11-12
- Z declarada en el input: 1920 (normalizada: 1920-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1920 1920-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1920-01-01 vs Z90 1928-11-12 (Δ 106.4 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1913` ?→1913-01-01: Tras empezar en el cine con Selig Polyscope en julio de 1909, entró en 1913 en Keystone, el estudio de Mack Sennett, donde se volvió figura 
  - `C2_1917` ?→1917-04-23: Fundó con Joseph Schenck la productora Comique, con control creativo propio; su primer corto ahí, The Butcher Boy, estrenado el 23 de abril 
  - `C3_1920` ?→1920-01-01: En 1918 cedió a Keaton su participación en Comique y aceptó la oferta de Paramount de 3 millones de dólares por hasta 18 largometrajes en tr

### 89. Steve Jobs — ``

- Fuente original: `/workspace/JOBS_FUENTES_Y_STACK_PARA_REPRO_INDEPENDIENTE_V1/01_FUENTES_MATRIZ/jobs_corrected_backend.json`
- SHA-256: `31ea1efd9d304d5c8961754b175989e5bc8ef0dc0a857ec2e94d0222bad4f03f` (corto `31ea1efd9d30`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:42
- Copia en repo: `inputs/089_Steve_Jobs_31ea1efd9d30/jobs_corrected_backend.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Steve Jobs): nacimiento=1955-02-24; fuente pública (Steve Jobs): muerte=2011-10-05
- Z90 calculada (90% nacimiento→muerte): 2006-02-05
- Z declarada en el input: — (normalizada: —)
- Cortes: 5 total; pre-Z 5 / post-Z 0; vs Z90 calculada: pre 5 / post 0
- Último corte pre-Z: 1989-1991 1991-12-31
- Veredicto: `Z_MAL_PUESTA` — Último corte no alinea con Z90 2006-02-05. Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `1971-1975` 1971-01-01→1975-12-31: 
  - `1976-1980` 1976-01-01→1980-12-31: 
  - `1981-1984` 1981-01-01→1984-12-31: 
  - `1985-1988` 1985-01-01→1988-12-31: 
  - `1989-1991` 1989-01-01→1991-12-31: 

### 90. Steve Jobs — `CAL_F005_07_JOBS`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F005_07_JOBS/entrada.json`
- SHA-256: `c556241e0491a0e6fa2f909978d8a62c40b38e02f348a99c0ced12cffe8be749` (corto `c556241e0491`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/090_CAL_F005_07_JOBS_c556241e0491/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Steve Jobs): nacimiento=1955-02-24; fuente pública (Steve Jobs): muerte=2011-10-05
- Z90 calculada (90% nacimiento→muerte): 2006-02-05
- Z declarada en el input: 1996-10 (normalizada: 1996-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1996 1996-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1996-01-01 vs Z90 2006-02-05 (Δ 121.2 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1984` ?→1984-01-01: Cofundador de Apple (1976); tras el poco exitoso Lisa (1983) lanza el Macintosh 128K (1984), primer ordenador con interfaz gráfica de produc
  - `C2_1985` ?→1985-01-01: Sale de Apple tras una larga lucha de poder con el consejo y con Sculley; ese mismo año funda NeXT con empleados de Apple y en 1986 compra l
  - `C3_1996` ?→1996-01-01: NeXT vende solo 50 000 máquinas y en 1993 abandona el hardware para hacer software; da su primera ganancia anual en 1994 y lanza WebObjects 

### 91. Themistocles — `CASO_NUEVO_20261013_01`

- Fuente original: `/workspace/MOTOR_1019/U6_UNIFICADO_20261020/THEMISTOCLES_FREEZE_480BC.json`
- SHA-256: `dce6f796a42afcfdb2b9e32ae0813d3063cd3f212d96a74a4319fde45d9a85f5` (corto `dce6f796a42a`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:02; paquete: 2026-10-20
- Copia en repo: `inputs/091_CASO_NUEVO_20261013_01_dce6f796a42a/THEMISTOCLES_FREEZE_480BC.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_490BC`: Tras la batalla de Maratón, el conflicto con Persia sigue siendo una amenaza estratégica para las ciudades griegas. \| 490 a. C.
  - `C2_483BC`: La política ateniense impulsa una expansión naval; se aprueba construir una gran flota y se intensifica la rivalidad política interna. \| 483
  - `C3_480BC`: Durante la invasión persa, el dirigente persuade a los aliados para combatir en el estrecho de Salamina; la flota griega obtiene una victori

### 92. Themistocles — `CASO_NUEVO_20261013_01`

- Fuente original: `/workspace/MOTOR_1019/U6_UNIFICADO_20261020/THEMISTOCLES_FREEZE_480BC_WITH_SEARCH_BRIDGE.json`
- SHA-256: `ee524314dfc60173cd9a72d7c374858b0834c9f949ee856df74b5cba5a63ada2` (corto `ee524314dfc6`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:02; paquete: 2026-10-20
- Copia en repo: `inputs/092_CASO_NUEVO_20261013_01_ee524314dfc6/THEMISTOCLES_FREEZE_480BC_WITH_SEARCH_BRIDGE.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_490BC`: Tras la batalla de Maratón, el conflicto con Persia sigue siendo una amenaza estratégica para las ciudades griegas. \| 490 a. C.
  - `C2_483BC`: La política ateniense impulsa una expansión naval; se aprueba construir una gran flota y se intensifica la rivalidad política interna. \| 483
  - `C3_480BC`: Durante la invasión persa, el dirigente persuade a los aliados para combatir en el estrecho de Salamina; la flota griega obtiene una victori

### 93. Themistocles — `CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2`

- Fuente original: `/workspace/MOTOR_1019/U6_UNIFICADO_20261020/inputs/THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json`
- SHA-256: `6067686f138e3a54760e0ae1406c0a7a1eb0dd441a04ac8d92aecb81ad8aed7c` (corto `6067686f138e`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:02; paquete: 2026-10-20
- Copia en repo: `inputs/093_CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2_6067686f138e/THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: C3_480BC (normalizada: —)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS;POCOS_CORTES` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90. Además solo hay 3 cortes.
- Cortes:
  - `C1_490BC`: Tras la batalla de Maratón, el conflicto con Persia sigue siendo una amenaza estratégica para las ciudades griegas. \| amenaza externa defens
  - `C2_483BC`: La política ateniense impulsa una expansión naval; se aprueba construir una gran flota y se intensifica la rivalidad política interna. \| riv
  - `C3_480BC`: Durante la invasión persa, el dirigente persuade a los aliados para combatir en el estrecho de Salamina; la flota griega obtiene una victori

### 94. Vincent van Gogh — `CAL_LOTE01_05_VANGOGH`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_05_VANGOGH.json`
- SHA-256: `628b24529fd80b01735739e4a9935caf63c3df30b16286b8a34627a19b6d7308` (corto `628b24529fd8`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/094_CAL_LOTE01_05_VANGOGH_628b24529fd8/CAL_LOTE01_05_VANGOGH.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Vincent van Gogh): nacimiento=1853-03-30; fuente pública (Vincent van Gogh): muerte=1890-07-29
- Z90 calculada (90% nacimiento→muerte): 1886-11-04
- Z declarada en el input: C3_1888B (normalizada: 1888-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 1 / post-Z 2; vs Z90 calculada: pre 1 / post 2
- Último corte pre-Z: C1_1880 1880-08-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1888-01-01 vs Z90 1886-11-04 (Δ 13.9 meses). Cortes pre-Z: 1 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1880` ?→1880-08-01: Tras fracasar como predicador decide ser artista; depende de su hermano Theo. \| 1880-08-01 \| 1880-08-01
  - `C2_1888A` ?→1888-02-20 [post-Z decl., post-Z90]: Se muda a Arlés; producción intensa; sueña con un taller del sur. \| 1888-02-20 \| 1888-02-20
  - `C3_1888B` ?→1888-12-24 [post-Z decl., post-Z90]: Tras disputa con Gauguin se corta la oreja y es hospitalizado. \| 1888-12-24 \| 1888-12-24

### 95. Walt Disney — `CAL_F001_04_DISNEY`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F001_04_DISNEY/entrada.json`
- SHA-256: `d546c10647b235bfffdc1d309ffcef91de4e2050302eff86614ad4938e61b014` (corto `d546c10647b2`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/095_CAL_F001_04_DISNEY_d546c10647b2/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Walt Disney): nacimiento=1901-12-05; fuente pública (Walt Disney): muerte=1966-12-15
- Z90 calculada (90% nacimiento→muerte): 1960-06-14
- Z declarada en el input: C3_1928 (normalizada: 1928-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1927 1927-09-05
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1928-01-01 vs Z90 1960-06-14 (Δ 389.4 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1923` ?→1923-10-16: Tras la quiebra de Laugh-O-Gram en Kansas City funda con su hermano Roy el estudio Disney Brothers en Los Ángeles. \| 1923-10-16 \| 1923-10-16
  - `C2_1927` ?→1927-09-05: Oswald the Lucky Rabbit, producido para Universal vía Charles Mintz, tiene éxito. \| 1927-09-05 \| 1927-09-05
  - `C3_1928` ?→1928-03-01 [post-Z decl.]: En Nueva York, Mintz se queda con Oswald (los derechos eran de Universal) y contrata a casi todos sus animadores. \| 1928-03-01 \| 1928-03-01

### 96. William C. Durant — `CAL_F002_10_DURANT`

- Fuente original: `/workspace/alt_cameo/casos/fabrica/cola/CAL_F002_10_DURANT/entrada.json`
- SHA-256: `e3d8254732e64439841bdbdde8950f2d315d91f38c4bebd242c2168e4aa9b22b` (corto `e3d8254732e6`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-11T01:36:20
- Copia en repo: `inputs/096_CAL_F002_10_DURANT_e3d8254732e6/entrada.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (William C. Durant): nacimiento=1861-12-08; fuente pública (William C. Durant): muerte=1947-03-18
- Z90 calculada (90% nacimiento→muerte): 1938-09-06
- Z declarada en el input: 1919 (normalizada: 1919-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 3 / post-Z 0; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C3_1919 1919-01-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1919-01-01 vs Z90 1938-09-06 (Δ 236.2 meses). Cortes pre-Z: 3 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1908` ?→1908-11-12: Tomó el control de Buick el 1 de noviembre de 1904; el 16 de septiembre de 1908 fundó General Motors como sociedad de cartera y el 12 de nov
  - `C2_1911` ?→1911-11-03: Sobreendeudado tras sumar Cadillac, Oakland y otras compañías, perdió en 1910 el control de General Motors a manos de los banqueros; el 3 de
  - `C3_1919` ?→1919-01-01: Apoyado en las ventas de Chevrolet recuperó en 1916 el control de General Motors; en febrero de 1918 se anunció el plan para que GM absorbie

### 97. Winston Churchill — `CAL_LOTE01_02_CHURCHILL`

- Fuente original: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/casos_cal/CAL_LOTE01_02_CHURCHILL.json`
- SHA-256: `5858c5deedeaa3159c3b41dc5a4e1042ca4c678f68d242b8c81471fc5c55aa79` (corto `5858c5deedea`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:49:18
- Copia en repo: `inputs/097_CAL_LOTE01_02_CHURCHILL_5858c5deedea/CAL_LOTE01_02_CHURCHILL.json`
- Otras copias con el mismo hash: 1 (ej. `/workspace/alt_cameo/casos/corridas_alterno/CHURCHILL_CAMEO_ALTERNO/entrada.json`)
- Nacimiento (input): — 
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Winston Churchill): nacimiento=1874-11-30; fuente pública (Winston Churchill): muerte=1965-01-24
- Z90 calculada (90% nacimiento→muerte): 1956-01-19
- Z declarada en el input: C3_1939 (normalizada: 1939-01-01)
- Tipo/nota de Z: CASE_CUTOFF
- Cortes: 3 total; pre-Z 2 / post-Z 1; vs Z90 calculada: pre 3 / post 0
- Último corte pre-Z: C2_1933 1933-06-01
- Veredicto: `Z_MAL_PUESTA;POCOS_CORTES` — Z declarada 1939-01-01 vs Z90 1956-01-19 (Δ 204.6 meses). Cortes pre-Z: 2 (hace falta ≥5). Z90 calculada con fechas de fuente pública (marcadas).
- Cortes:
  - `C1_1915` ?→1915-05-25: Desastre de Gallípoli; deja el Almirantazgo. \| 1915-05-25 \| 1915-05-25
  - `C2_1933` ?→1933-06-01: 'Años del desierto': fuera del gobierno, advierte contra el rearme alemán. \| 1933-06-01 \| 1933-06-01
  - `C3_1939` ?→1939-09-03 [post-Z decl.]: Gran Bretaña declara la guerra; Churchill vuelve como Primer Lord del Almirantazgo. \| 1939-09-03 \| 1939-09-03

### 98. CIEGO_09 — `CIEGO_09`

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_CIEGO_09.json`
- SHA-256: `a64d7d3e2343498aa273cad607656c5da1f2712a8119bc03d82fd41699a99255` (corto `a64d7d3e2343`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:57; paquete: 2026-10-11
- Copia en repo: `inputs/098_CIEGO_09_a64d7d3e2343/IN_CIEGO_09.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 5 total; pre-Z 5 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90.
- Cortes:
  - `A`: 
  - `B`: 
  - `C`: 
  - `D`: 
  - `E`: 

### 99. CIEGO_10 — `CIEGO_10`

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_CIEGO_10.json`
- SHA-256: `98480f5c3b2243e14fbf738f191db4db3c2f0acf10ddfe9e0825dc0e4db50402` (corto `98480f5c3b22`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:57; paquete: 2026-10-11
- Copia en repo: `inputs/099_CIEGO_10_98480f5c3b22/IN_CIEGO_10.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 6 total; pre-Z 6 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90.
- Cortes:
  - `A`: 
  - `B`: 
  - `C`: 
  - `D`: 
  - `E`: 
  - `F`: 

### 100. CIEGO_11 — `CIEGO_11`

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_CIEGO_11.json`
- SHA-256: `80ed20a730463d39aec17c49917039db2d26288f4c4a1f26493eb5aa0e430251` (corto `80ed20a73046`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:57; paquete: 2026-10-11
- Copia en repo: `inputs/100_CIEGO_11_80ed20a73046/IN_CIEGO_11.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 7 total; pre-Z 7 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90.
- Cortes:
  - `A`: 
  - `B`: 
  - `C`: 
  - `D`: 
  - `E`: 
  - `F`: 
  - `G`: 

### 101. CIEGO_12 — `CIEGO_12`

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_CIEGO_12.json`
- SHA-256: `51990be562ed3be08b791e5115f57474a479f0bbd24b21e056aa2f0d83c8f5c1` (corto `51990be562ed`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:57; paquete: 2026-10-11
- Copia en repo: `inputs/101_CIEGO_12_51990be562ed/IN_CIEGO_12.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 6 total; pre-Z 6 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90.
- Cortes:
  - `A`: 
  - `B`: 
  - `C`: 
  - `D`: 
  - `E`: 
  - `F`: 

### 102. CIEGO_14 — `CIEGO_14`

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_CIEGO_14.json`
- SHA-256: `af1ccd887e615b3185ef1cbc0ad3798f2a7b13ee3616b6997fdac2e7a18991e2` (corto `af1ccd887e61`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:57; paquete: 2026-10-11
- Copia en repo: `inputs/102_CIEGO_14_af1ccd887e61/IN_CIEGO_14.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 6 total; pre-Z 6 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90.
- Cortes:
  - `A`: 
  - `B`: 
  - `C`: 
  - `D`: 
  - `E`: 
  - `F`: 

### 103. CIEGO_15_ANTECEDENTES_C — `CIEGO_15_ANTECEDENTES_C`

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_CIEGO_15.json`
- SHA-256: `dd79011441dcf76e884289472e138eb7c276676f133aeecd60e4d92cca2d0b4e` (corto `dd79011441dc`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:08; paquete: 2026-10-11
- Copia en repo: `inputs/103_CIEGO_15_ANTECEDENTES_C_dd79011441dc/IN_CIEGO_15.json`
- Otras copias con el mismo hash: 2 (ej. `/workspace/CORRIDA_NOCTURNA_20261005/ciegos/15_CASO_CIEGO_ANTECEDENTES_C_FREEZE/INPUT_ESTANDAR_A_F.json`)
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 6 total; pre-Z 6 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS` — No hay nacimiento y muerte en el input (ni fechas públicas aplicables con identidad clara) para calcular Z90.
- Cortes:
  - `A`: Durante generaciones la vida política se organiza alrededor de cargos reconocidos, rangos heredados y normas que todos entienden aunque no t
  - `B`: Ese orden se encuentra de pronto con potencias y mercados que no cabían en su mapa mental. Llegan barcos, tratados, técnicas, deudas y preci
  - `C`: La presión externa se vuelve fisura interna. Las lealtades se parten: unos quieren cerrar la puerta y restaurar el orden tal como era; otros
  - `D`: Empiezan los remedios extraordinarios. Se crean mandos de crisis, alianzas de excepción, decretos que saltan el ritmo ordinario de los cargo
  - `E`: En ese punto el nudo ya no es ganar una escaramuza. Es reubicar el centro de autoridad. Un arreglo nuevo empieza a desplazarse sobre el viej
  - `F`: Al cerrar la transición, el orden que queda se presenta como recuperación de lo esencial y, al mismo tiempo, como fundación. Se recentraliza

### 104. Elon Musk — `CASO_CIEGO_MUSK_FREEZE_1997_2000`

- Fuente original: `/workspace/CASO_CIEGO_MUSK_RETROSPECTIVA.json`
- SHA-256: `728eba2554d11015c98950a4542b293b3d74689d11de9d6eef2e4cbf9e48b08f` (corto `728eba2554d1`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:48
- Copia en repo: `inputs/104_CASO_CIEGO_MUSK_FREEZE_1997_2000_728eba2554d1/CASO_CIEGO_MUSK_RETROSPECTIVA.json`
- Otras copias con el mismo hash: 2 (ej. `/workspace/pred_hist_bio_in/TRANSFER_V15_1/DATOS_CASO/13_MUSK_1997_2000/CASO_CIEGO_MUSK_RETROSPECTIVA.json`)
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 2 total; pre-Z 2 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `VIVO_Z_HOY` — Persona viva o sin fecha de muerte; Z de trabajo = hoy / fecha del caso.
- Cortes:
  - `corte_freeze_A_F`: 
  - `corte_completo_post_2000_solo_para_inversa`: 

### 105. Elon Musk — `CALIBRACION_ELON_MUSK_DESDE_CERO_20260924`

- Fuente original: `/workspace/CORRIDA_NOCTURNA_20261005/CORRIDA_0547_20261006/inputs/INPUT_CAPA2_MUSK.json`
- SHA-256: `d19acb7a1485a3b1f28eed6c9b70c3ba40bb800113ef4fb032741b24baed61d9` (corto `d19acb7a1485`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:08; paquete: 2026-10-05
- Copia en repo: `inputs/105_CALIBRACION_ELON_MUSK_DESDE_CERO_20260924_d19acb7a1485/INPUT_CAPA2_MUSK.json`
- Nacimiento (input): 1971-06-28 (input.birth_date=1971-06-28)
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: 2026-09-24 (normalizada: 2026-09-24)
- Tipo/nota de Z: hoy
- Cortes: 10 total; pre-Z 10 / post-Z 0
- Último corte pre-Z: C10 2026-09-24
- Veredicto: `VIVO_Z_HOY` — Persona viva o sin fecha de muerte; Z de trabajo = hoy / fecha del caso.
- Cortes:
  - `C01` ?→1984-01-01: 1984-01-01
  - `C02` ?→1995-01-01: 1995-01-01
  - `C03` ?→1999-01-01: 1999-01-01
  - `C04` ?→2002-01-01: 2002-01-01
  - `C05` ?→2008-01-01: 2008-01-01
  - `C06` ?→2012-01-01: 2012-01-01
  - `C07` ?→2015-01-01: 2015-01-01
  - `C08` ?→2020-01-01: 2020-01-01
  - `C09` ?→2022-01-01: 2022-01-01
  - `C10` ?→2026-09-24: 2026-09-24

### 106. Elon Musk — `CALIBRACION_ELON_MUSK_DESDE_CERO_20260924`

- Fuente original: `/workspace/CORRIDA_NOCTURNA_20261005/inputs/INPUT_ESTANDAR_MUSK.json`
- SHA-256: `dd8f06e02423defdabe2c3ff61750c377d0e29b1c76b12c89a02ec6df5d2ca35` (corto `dd8f06e02423`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:59; paquete: 2026-10-05
- Copia en repo: `inputs/106_CALIBRACION_ELON_MUSK_DESDE_CERO_20260924_dd8f06e02423/INPUT_ESTANDAR_MUSK.json`
- Nacimiento (input): 1971-06-28 (input.birth_date=1971-06-28)
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: 2026-09-24 (normalizada: 2026-09-24)
- Tipo/nota de Z: hoy
- Cortes: 10 total; pre-Z 10 / post-Z 0
- Último corte pre-Z: C10 2026-09-24
- Veredicto: `VIVO_Z_HOY` — Persona viva o sin fecha de muerte; Z de trabajo = hoy / fecha del caso.
- Cortes:
  - `C01` ?→1984-01-01: 1984-01-01
  - `C02` ?→1995-01-01: 1995-01-01
  - `C03` ?→1999-01-01: 1999-01-01
  - `C04` ?→2002-01-01: 2002-01-01
  - `C05` ?→2008-01-01: 2008-01-01
  - `C06` ?→2012-01-01: 2012-01-01
  - `C07` ?→2015-01-01: 2015-01-01
  - `C08` ?→2020-01-01: 2020-01-01
  - `C09` ?→2022-01-01: 2022-01-01
  - `C10` ?→2026-09-24: 2026-09-24

### 107. Elon Musk — `CIEGO_13`

- Fuente original: `/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_CIEGO_13_MUSK.json`
- SHA-256: `9f48f196b371a3a3ec160b8d544aba47681bc668b886b4b1817be0cf012788fd` (corto `9f48f196b371`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:47:57; paquete: 2026-10-11
- Copia en repo: `inputs/107_CIEGO_13_9f48f196b371/IN_CIEGO_13_MUSK.json`
- Nacimiento (input): — 
- Muerte (input): — 
- Z90 calculada (90% nacimiento→muerte): —
- Z declarada en el input: — (normalizada: —)
- Cortes: 6 total; pre-Z 6 / post-Z 0
- Último corte pre-Z: — 
- Veredicto: `VIVO_Z_HOY` — Persona viva o sin fecha de muerte; Z de trabajo = hoy / fecha del caso.
- Cortes:
  - `A`: 
  - `B`: 
  - `C`: 
  - `D`: 
  - `E`: 
  - `F`: 

### 108. Rachel Carson — ``

- Fuente original: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/CHECKPOINT_MOTOR_CLONABLE_20260914/09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_CARSON_Z90_20260914/SELLADO_PRE_REVELACION/_cuts_ciego_Z90_B_run.json`
- SHA-256: `3804069c86528ca57d4f80bcafbe49fc88ee3c52876fca2c60fad54efd4f1d4a` (corto `3804069c8652`)
- Fecha del archivo (mtime, America/Mexico_City): 2026-11-07T10:46:43; paquete: 2026-09-14
- Copia en repo: `inputs/108_Rachel_Carson_3804069c8652/_cuts_ciego_Z90_B_run.json`
- Markers del mismo paquete: `/workspace/pred_hist_bio_in/TRANSFER_V15_1/CHECKPOINT_MOTOR_CLONABLE_20260914/09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_CARSON_Z90_20260914/SELLADO_PRE_REVELACION/markers_ciego_Z90_B.json` (`2a0575244bcb`)
- Otras copias con el mismo hash: 8 (ej. `/tmp/ck_CHECKPOINT_MOTOR_CLONABLE_20260914/CHECKPOINT_MOTOR_CLONABLE_20260914/09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_CARSON_Z90_20260914/SELLADO_PRE_REVELACION/_cuts_ciego_Z90_B_run.json`)
- Nacimiento (input): — (markers.born_approx=SELLADO_EN_HECHOS) Nota: no parseable: SELLADO_EN_HECHOS
- Muerte (input): — 
- Fechas de fuente pública: fuente pública (Rachel Carson): nacimiento=1907-05-27; fuente pública (Rachel Carson): muerte=1964-04-14
- Z90 calculada (90% nacimiento→muerte): 1958-08-06
- Z declarada en el input: Z≈90% lifespan (normalizada: —)
- Cortes: 7 total; pre-Z 7 / post-Z 0; vs Z90 calculada: pre 7 / post 0
- Último corte pre-Z: — 
- Veredicto: `SIN_FECHAS` — Hay Z90 calculada, pero el input no declara Z y no se pudo fechar el último corte.
- Cortes:
  - `C1`: Origen: nace en entorno rural; familia modesta; interes materno por la naturaleza; lee y escribe de forma constante; hogar sin estudios form
  - `C2`: Formacion: estudia ciencias naturales en universidad publica; destaca; trabaja en laboratorio marino; publica primeros reportes tecnicos; ob
  - `C3`: Primer trabajo: agencia gubernamental; escribe reportes tecnicos; aprende a traducir ciencia a lenguaje comun; muere una hermana; cuida de l
  - `C4`: Primeros libros: publica libros de popularizacion de la naturaleza; exito moderado; entra a circulos literarios y cientificos; deja la agenc
  - `C5`: Consolidacion: publica libro de alto exito; escribe a tiempo completo; cuida sobrinas; estabilidad economica; entra a circulos de elite
  - `C6`: Investigacion polemica: investiga tema industrial controvertido (uso masivo de quimicos); escribe libro de denuncia; enfrenta ataques de ind
  - `C7` [Z_foto]: Z_foto STOP (~90% vida). Publica el libro; atencion mundial; continuan los ataques; diagnostico de enfermedad grave; sigue trabajando. Ultim

## Notas de alcance

- No se tocó `Engine_V5_CANONICO_SOLO.py` ni el catálogo 244.
- Los lotes de fábrica F001–F005 y CAL_LOTE01 entran porque son los casos de calibración (casi todos con 3 cortes y Z de evento, no Z90).
- El precedente `casos/precedentes/MOZART_10_CORTES` (y `IN_t860/INPUT_FROZEN.json` si coincide) no es el Mozart original de septiembre: el original tiene C1–C7 hasta Z90 y C8–C10 post-Z.
- Jobs del expediente independiente trae 5 cortes 1971–1991; no es una foto a Z90 (~2006).

