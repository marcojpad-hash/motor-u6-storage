# 2026-10-25 — Grok Bot — fábrica: lote F002 (primer lote ciego con compuerta Z_trabajo)
## Qué cambió
Lote F002: 10 sujetos nuevos, 3 cortes cada uno, preparados a ciegas y corridos con `preparar-z` + `correr` (sin cambios en motor/, Engine, catálogo 244, regla 022 ni protocolo).
- **Separación ciega:** semillas escritas por `GrokBot-preparador-ciego-F002` (no vio destinos); destinos, familias y lista negra por `GrokBot-custodio-rutina-F002`, en ejecutores separados. El archivo de destinos del custodio queda fuera del repo (`/workspace/FABRICA_CUSTODIA/F002/`); igual que F001, lo sellado vive en `cola/<ID>/desenlace_sellado.json` y `destino_sellado.json`.
- La lista de "los 15 casos sellados" se rehízo: los casos 01–06 de la serie ciega anterior no se pudieron identificar, así que F002 se armó con sujetos nuevos.
- Tipo nuevo de sujeto: `gobernante` (Catalina II, Luis XVI).
- Compuerta Z_trabajo (GATE_Z_TRABAJO_20261024, R1–R7): pasó a la primera; no se tocó el texto de ninguna semilla.
## Antes → ahora (por archivo)
- casos/fabrica/semillas_lote_F002.py — antes: sin seguimiento en git → ahora: incluido, contenido intacto.
- casos/fabrica/cola/CAL_F002_01…10/ — antes: no existían → ahora: entrada.json, desenlace_sellado.json, destino_sellado.json.
- casos/fabrica/lotes/F002_PRECOMPROMISO_REGLA.json — nuevo: regla 022 congelada (sha256 4252fd45…49b302) + hashes de entrada/desenlace/destino, escrito ANTES de correr y de abrir destinos (mismo esquema que F001_D022).
- casos/fabrica/lotes/F002_COMPROMISO.json, F002_RESUMEN.json — nuevos (los genera `correr`).
- casos/fabrica/calibracion_acumulada.csv, CALIBRACION_ACUMULADA.md — antes: 10 filas (F001 + F001_D022) → ahora: 20 filas.
- Nota: se corrió `--n 10` (no `--n 5`) para cerrar el lote completo bajo un solo nombre, F002.
## Hashes canónicos verificados (motor y catálogo)
Engine 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082 y patrones d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1: OK antes y después (repo y copia temporal). Regla 022 4252fd4564877183fd8be86f579fdde59635eb547c139a04dd79acedc349b302 sin cambios.
## Pruebas
motor/tests/test_arnes_calibracion.py 7/7. Corrida F002: 10 casos, 8 sellados, 2 NO_SELLADO (Coolidge y Luis XVI: exit 6, TORTUGAS_REQUIERE_CONTINUACION, pausa reanudable). Registro sellado sha256 388dc648b6aa2aa8287b8cbcceb9f4994635792ee81496d891d9e545fd36bee4.
## Resultados F002 (8 evaluados)
H1 2/8 · H2 1/8 · set 2/8 · apuesta temática 2/8 · destino exacto 2/8 · destino por polaridad 3/8.

| Caso | H1 | Escenario | Destino apostado | Destino real |
|---|---|---|---|---|
| Galileo 1632 | arquetipo_el_sabio | CONTINUIDAD_ASCENDENTE | auge | ruptura |
| Pasteur 1885 | arquetipo_el_sabio (acierta) | CONTINUIDAD_ASCENDENTE | auge | auge |
| Arbuckle 1921 | schwartz_07_logro | CONTINUIDAD_ASCENDENTE | auge | ruptura |
| Bach 1723 | 9_audaz_empresa | MESeta_O_ESTABILIZACION | auge | meseta |
| McCarthy 1954 | schwartz_07_logro | CONTINUIDAD_ASCENDENTE | meseta | caida |
| Coolidge 1925 | NO_SELLADO | — | — | — |
| Catalina 1762 | schwartz_07_logro | CONTINUIDAD_ASCENDENTE | caida | auge |
| Luis XVI 1791 | NO_SELLADO | — | — | — |
| Rockefeller 1870 | 30_ambicion (acierta) | CONTINUIDAD_ASCENDENTE | auge | auge |
| Durant 1920 | 12_obtencion | CONTINUIDAD_ASCENDENTE | auge | caida |

Acumulado (CALIBRACION_ACUMULADA.md, F001 cuenta dos veces por F001_D022): H1 4/18, H2 1/18, set 4/18, apuesta 2/18, destino exacto 5/13, polaridad 7/13. Sujetos únicos: 15 (13 evaluados).
**Patrón visible: sesgo de continuidad.** 7 de 8 escenarios dicen CONTINUIDAD_ASCENDENTE (1 MESETA); 4 de esos 7 terminaron en caída o ruptura (Galileo, Arbuckle, McCarthy, Durant). La regla 022 apostó a la baja una sola vez (Catalina, que en realidad subió) y no vio ninguna de las 4 bajadas reales.
## Fuentes flojas (aviso)
Arbuckle: Variety citado por el número completo (abril de 1917, archive.org), sin página. Pasteur: una sola fuente primaria (crónica veterinaria de 1884, Persée). Casi todo lo demás es Wikipedia secundaria (en Bach, el informe de la corte de Weimar llega a través de la biografía).
