# Candado de entrega de corridas — motor U6

Script: `scripts/candado_entrega.py` (solo biblioteca estándar).

## Qué hace

Valida un paquete de entrega de corridas **antes** de aceptarlo/guardarlo en
el repo. Si un criterio no se cumple, el paquete **NO se guarda** y el candado
dice **exactamente** qué criterio falló (qué archivo falta, qué regla no se
siguió, qué lectura no se demostró). La única razón para no guardar es no
cumplir los criterios; nunca es un vago «no se pudo guardar».

## Cómo se corre

```bash
python3 scripts/candado_entrega.py motor/runs/<LOTE>_<FECHA>/ [--repo RUTA_REPO]
```

- `exit 0` — `CANDADO_ENTREGA: PASA`. La entrega cumple y se puede guardar.
- `exit 1` — `CANDADO_ENTREGA: BLOQUEADO — NO SE GUARDA`, con la lista
  exacta de criterios incumplidos.
- `exit 2` — error de uso.

`--repo` es la raíz del repo donde viven los archivos de protocolo que la
entrega dice haber leído. Si no se pasa, se detecta subiendo desde la carpeta
de entrega hasta encontrar `CONTRATO_CARPETAS.md`.

## Qué verifica

- **A. Estructura:** `MANIFIESTO.json`, `README.md`, `TABLA_VALORES_COMPLETA.md`
  y `LECTURA.json` presentes; manifiesto con `lote` y `casos` (cada caso con
  `case_id`, `result_sha256`, `result_bytes`, `entrada_sha256`,
  `receipt_sha256`, sin duplicados); por cada caso
  `<CASO>_INTERPRETABLE.json`, `<CASO>_RECIBO_EJECUCION.json` y
  `<CASO>_entrada.json`; sin archivos de caso huérfanos; README menciona el
  protocolo (declara bajo qué regla/excepción se entrega).
- **B. Contenido por caso:** INTERPRETABLE con H1/H2 (con `familia`),
  conjunto abierto con trazabilidad geométrica completa por hipótesis
  (régimen, señal multiescala, micro, meso, macro) — regla «Todo dato es un
  dato» (PROTOCOLO §4): picos, mesetas, valles y descensos se conservan;
  `monte_carlo` y `predictive_validation`; los SHA-256 del INTERPRETABLE
  coinciden con el MANIFIESTO. RECIBO con `status` declarado (PROTOCOLO §3:
  no inventar campos; lo que falta se anota NO REGISTRADO). Entrada con
  `question` en prosa y `cuts` con `hecho` en prosa, y su SHA-256 real
  coincide con el MANIFIESTO (igual para el RECIBO).
- **C. Tabla:** `TABLA_VALORES_COMPLETA.md` menciona cada `case_id` del
  manifiesto (ningún caso fuera de la tabla).
- **D. Lectura demostrada (`LECTURA.json`):** lista de archivos de
  protocolo/especificación leídos, cada uno con `ruta` y `sha256` o `fecha`;
  cada `ruta` existe en el repo; si trae `sha256`, coincide con el archivo
  actual; README.md o REVISION.md menciona el nombre de cada archivo leído
  (la entrega cita lo que leyó).

## Formato de `LECTURA.json`

```json
{
  "entrega": "F001_F002_20261111",
  "fecha_lectura": "2026-11-11",
  "lecturas": [
    {"ruta": "casos/REGLAS.md", "sha256": "<64 hex>", "reglas": ["regla 6"]},
    {"ruta": "CONTRATO_CARPETAS.md", "sha256": "<64 hex>",
     "reglas": ["casos/: nunca corridas completas"]},
    {"ruta": "PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md", "sha256": "<64 hex>",
     "reglas": ["§3 recibo mínimo", "§4 todo dato es un dato"]}
  ]
}
```

El `sha256` es el del archivo tal como se leyó; si el archivo cambió desde
entonces, el candado lo reporta como no coincidente.

## Regla de entrega que valida

Forma adoptada por Marco (2026-11-11 ~18:07 CST): resumen de una línea por
corrida en `casos/resultados/resultados.jsonl` (para no saturar el motor) **y**
corridas completas en el apartado separado `motor/runs/<LOTE>_<FECHA>/` para
el historial. Este candado valida el paquete de `motor/runs/`. Los archivos
`casos/REGLAS.md` (regla 6), `CONTRATO_CARPETAS.md` y
`casos/fabrica/README.md` todavía dicen que nunca se sube la corrida completa;
hay que actualizarlos para que la regla quede escrita.

## Prueba

```bash
python3 scripts/candado_entrega.py motor/runs/F001_F002_20261111/ --repo .
```

Contra la entrega F001/F002 (2026-11-11, commit 393038e9): el candado
**bloquea** por un solo criterio — falta `LECTURA.json` (la entrega no trae
evidencia explícita de lectura de protocolo). Todo lo demás pasa: 49 archivos
presentes, 15 casos con interpretable/recibo/entrada, manifiesto con SHA-256,
tabla completa con los 15 casos, trazabilidad geométrica y prosa en las
entradas (159 criterios pasados, 1 incumplido).

Prueba en positivo (copia local + `LECTURA.json` con los 3 archivos que el
README cita, con sus SHA-256 reales): el candado **pasa** (173 criterios,
0 incumplidos, exit 0). El candado distingue: si la `LECTURA.json` reclama un
archivo que README/REVISION no citan (p. ej. el PROTOCOLO), bloquea en D5 y
dice exactamente cuál falta citar. Para que la entrega F001/F002 pase, basta
agregar `LECTURA.json` con los archivos de protocolo leídos y sus SHA-256, y
que README/REVISION citen cada uno.

No toca `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`.
