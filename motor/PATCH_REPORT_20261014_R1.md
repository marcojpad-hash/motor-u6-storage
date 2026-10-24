# Informe de cierre verificado — U6 / V15.3

**Corte de auditoría:** 14 de octubre de 2026.  
**Alcance:** correcciones de U6/V15.3 sobre una copia de trabajo; ejecución real de dos casos; integridad del catálogo, contrato terminal, confianza de apuesta y pruebas.  
**Estado:** las correcciones descritas abajo están aplicadas y verificadas. No se declara cerrado aquello para lo que faltan artefactos históricos o desenlaces sellados.

## 1. Cambios aplicados y comprobados

1. **Integridad del catálogo.** El motor activo verifica el SHA-256 y el conteo del catálogo canónico por defecto. La estructura real del catálogo es un mapa con 244 entradas de familias/patrones y mapas `tokens_favor` / `tokens_contra`; no un vector numérico por patrón.
2. **Conservación del significado de estados.** La normalización terminal ya no transforma estados como `NO_RESUELTO`, `EMPATE` o `SIN_CANDIDATOS` en supuestos éxitos.
3. **Hombre de Acero y cierre.** La evidencia del acero solo se atribuye a la apuesta H1/H2 cuando el rival evaluado coincide con H2. La objeción global del guardián y C2 se deduplican cuando describen el mismo fallo; objeciones diferentes se conservan.
4. **Salida sin null/NaN/NAPIC.** La capa de presentación marca `TORTUGAS` cuando no existe una medida de relleno y deja explícito el motivo. El runner vuelve a comprobar el JSON final, reemplaza cualquier ausencia o valor no finito residual por un marcador `TORTUGAS` y registra las rutas en la auditoría; los recibos cuentan los valores reales, no ceros declarados de antemano.
5. **Runner.** `--no-mc` puede aparecer antes o después del nombre de salida sin convertirse accidentalmente en la ruta del archivo.
6. **Semiótica.** Los tokens de contra se restan del apoyo favorable; el módulo queda marcado como traza y no como predictor.
7. **Manifiesto.** Se actualizaron las huellas de los cuatro archivos fuente modificados y se añadieron las pruebas nuevas. Se recuperaron byte por byte 13 artefactos que sí estaban en los checkpoints disponibles.

## 2. Ejecuciones reales

### Temístocles — entrada congelada con puente de búsqueda ciega

- Caso: `CASO_NUEVO_20261013_01`.
- Runner: completado; Monte Carlo apagado; tiempo de motor registrado: **1.698 s**.
- H1: `arquetipo_heroe`.
- H2: `crisis_vocacional`.
- Grado: `FRAGIL`; margen top1–top2: `0.0`, por lo que no hay separación operativa.
- Búsqueda externa: recibo `EXECUTED`, 5 resultados conectados, 100 tokens tras el filtro. La ejecución técnica de la búsqueda quedó comprobada; **la relevancia de esos resultados como analogías históricas no queda certificada por el mero recibo**.
- Medición de relleno H1/H2: `TORTUGAS_SIN_MEDIDA_DE_RELLENO`; no se inventó un porcentaje.
- JSON de resultado y recibo: **0 null, 0 valores no finitos**.
- Resultado SHA-256: `a1d887afaca14696ddaa101c2dfa08519beef7552abd109af1a0be769b94e3a4`.

### Giordano Bruno — Patch19 compacto

- Caso: `GIORDANO_BRUNO_V15_3_PATCH09_20261010`.
- Runner: completado; Monte Carlo apagado; tiempo de motor registrado: **13.53 s**.
- H1: `arquetipo_el_sabio`.
- H2: `spengler_02_verano_otono_racionalizacion`.
- Grado: `FRAGIL`.
- Búsqueda externa: recibo `EXECUTED`, 3 resultados conectados, 70 tokens tras el filtro.
- Confianza de apuesta U7: **54.21**, explícitamente **no calibrada**. No es probabilidad validada ni tasa de acierto.
- El acero examinó `kwml_03_mago`, no H2; por ello su resultado no se atribuyó a la comparación H1/H2 y su aporte fue neutral (`0.5`). Se contabilizaron 2 objeciones únicas.
- JSON de resultado y recibo: **0 null, 0 valores no finitos**.
- Resultado SHA-256: `ce58e55182b6b8c561a4fc53c3e8c198224a631d35ca784430f4aaa1d138cd64`.

## 3. Pruebas ejecutadas

- `python -m pytest -q`: **56 passed, 2 skipped**.
- `python -m unittest discover -s tests -v`: **25 pruebas OK**; además, los chequeos U6 embebidos imprimieron `OK 13` y `U6: 10 PASS`.
- Los dos skips están identificados, no ocultos:
  1. comparación con el plugin original `0.5.0`: no se recuperó el archivo de origen exacto;
  2. contrato histórico de Bezos: no se recuperó el resultado/entrada original `RESULT_UNICO__BEZOS__PREFIX__r1.json`.
- Los módulos modificados y las pruebas nuevas compilan con `py_compile`.

## 4. Integridad y almacenamiento

- Engine canónico `motor/Engine_V5_CANONICO_SOLO.py`: 30,507 bytes; SHA-256 `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` — **sin modificación**.
- Catálogo canónico `motor/patterns_final_v14.json`: 123,937 bytes; SHA-256 `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` — **244 entradas; sin modificación**.
- Preflight de manifiesto: **0 hashes divergentes, 0 archivos de `motor/` fuera del manifiesto, 0 bloqueos de Engine/patrones**.
- El manifiesto sigue en `DRIFT_WARNED` por **15 rutas históricas/archivadas ausentes**. Se conservaron expresamente las referencias; no se borraron para aparentar integridad.

## 5. Límites que no se declaran resueltos

- No se recuperaron los originales Noether/CIEGO_12/CIEGO_15 ni los archivos exactos `confianza_apuesta.py` y `laterales_hub.py`. Las cifras históricas **65.19, 48.87, 46.75, 47.19 y 45.30→43.03** siguen sin reproducción independiente y no se validan en este informe.
- La confianza U7 no está calibrada con desenlaces sellados por caso.
- El cierre adversarial del Décimo Hombre no queda certificado como completo cuando el predictor no aporta dimensiones finitas o rankings contrafactuales utilizables.
- La métrica lateral Ricci activa sigue siendo un proxy de deriva temporal; no se presenta como curvatura exacta de Forman integrada al ranking.
- Souriau geométrico integrado (mapa de momento y órbita coadjunta) sigue sin implementación conectada a P/A/C.
- La búsqueda ciega de Temístocles se ejecutó con recibo verificable, pero sus fuentes no bastan por sí solas para certificar una analogía histórica de alta relevancia.

## Artefactos principales

- `RESULT_THEMISTOCLES_U6_MERGED_R1_BRIDGE_FINAL.json` y su `RECIBO_EJECUCION`.
- `RESULT_GIORDANO_BRUNO_U6_MERGED_R1_FINAL.json` y su `RECIBO_EJECUCION`.
- Los ledgers CEB y sus manifiestos para ambas corridas.
- `CONFIDENCE_GIORDANO_BRUNO_U6_MERGED_R1_FINAL.json`.
- `THEMISTOCLES_FREEZE_480BC.json` y la copia de entrada con el puente de búsqueda ciega.

**Veredicto:** las correcciones operativas descritas se aplicaron y se probaron con ejecuciones reales. El paquete no se declara históricamente completo ni predictivamente calibrado; esas dos cosas requieren los artefactos originales y los desenlaces sellados que se detallan arriba.
