# Contrato para guardar corridas — motor U6

Para modelos que guardan o revisan corridas. Lee esto antes de entregar una corrida. Si algo aquí contradice otro archivo, este contrato manda sobre la forma de guardar corridas, porque recoge la forma adoptada por Marco el 2026-11-11; los tres archivos viejos que dicen lo contrario están pendientes de actualizar (ver §6).

## 1. Dos cosas diferentes, no las confundas

Guardar una corrida son DOS entregas distintas, en DOS lugares distintos, con DOS motivos distintos:

1. **Resumen de una línea por corrida** en `casos/resultados/resultados.jsonl` (una línea JSON por corrida): hash del caso (sha256 de la entrada), fecha, H1/H2/apuesta, grado, margen, métricas clave y hashes de entrada/salida. Lo genera `scripts/sincronizar_storage.py despues` (`casos/REGLAS.md` regla 6). Motivo: no saturar el motor. El motor no carga corridas completas.
2. **Corrida completa** en el apartado separado `motor/runs/<LOTE>_<FECHA>/` para el historial, para que otros modelos la puedan revisar. Ejemplo: `motor/runs/F001_F002_20261111/` (15 corridas F001/F002, commit 393038e9). Motivo: que la corrida se pueda repetir y auditar.

No sustituyas una por la otra. El resumen no es la corrida, y la carpeta de corridas no es el resumen.

## 2. El StinkBox NO es para las corridas

El StinkBox (`stinkbox/`) es el repositorio del motor para los **TOKENS** (tokens deduplicados en `tokens.jsonl`, procedencia y reportes de brechas), no para las corridas. Las corridas NO van al StinkBox.

Los tokens que salen de las corridas sí van al StinkBox: dan idea de qué tokens o familias de tokens se han introducido y cuáles habría que meter. Por eso se metió, por ejemplo, Cameo (su matriz de tokens salió de las corridas). Si de una corrida sale un token o una familia nueva, va al StinkBox; la corrida en sí va a `motor/runs/`.

## 3. Formato de entrega

### Por caso (en `motor/runs/<LOTE>_<FECHA>/`)

- `<CASO>_INTERPRETABLE.json` — resultado interpretable completo, sin recortes: `salida_interpretable` íntegra (H1/H2 con desglose, mezcla, grado, conjunto abierto con trazabilidad geométrica, apuesta), `monte_carlo`, `predictive_validation` y la entrada.
- `<CASO>_RECIBO_EJECUCION.json` — recibo de ejecución (PROTOCOLO §3: estado, runner/commit, hashes de entrada/salida, exit code, preflight, integridad; lo que falta se anota NO REGISTRADO, no se inventa).
- `<CASO>_entrada.json` — el input en prosa (pregunta, cortes con fecha y hecho) y los tokens P/A/C, para repetir la corrida. No solo tokens: la prosa va incluida.

### Por lote (en la misma carpeta)

- `README.md` — qué es el lote, qué contiene, bajo qué regla/excepción se entrega (declara su base).
- `TABLA_VALORES_COMPLETA.md` — TODOS los valores por caso, sin recortes: H1/H2 (desglose por grupo, predictibilidad, peso), trazabilidad geométrica de cada hipótesis del conjunto abierto (régimen, señal multiescala, micro, meso, macro, aceleración, divergencia), grado, mezcla, apuesta, Monte Carlo, validación y el input en prosa. Regla «Todo dato es un dato» (PROTOCOLO §4): se conservan picos, mesetas, valles y descensos; no se borra nada por estar fuera del top, abajo o por contradecir la hipótesis preferida.
- `MANIFIESTO.json` — SHA-256 de cada RESULT completo y de cada entrada, con estado y segundos.
- `REVISION.md` — revisión de los casos: hallazgos sistemáticos y por caso.
- `LECTURA.json` — evidencia de lectura (ver §5).

Nota de tamaño: los RESULT crudos suman ~90 MB por lote de 15 y el snapshot de push-files admite 16 MiB en total, así que los RESULT crudos no se suben. Se sube el interpretable completo (lo revisable) + recibo + entrada, y el SHA-256 de cada RESULT completo queda en `MANIFIESTO.json`. Los RESULT crudos quedan en la copia de trabajo.

## 4. El candado: nada se guarda si no cumple

`scripts/candado_entrega.py` valida el paquete ANTES de aceptarlo/guardarlo en el repo. Si un criterio no se cumple, el paquete **NO se guarda** y el candado dice **exactamente** qué criterio falló (qué archivo falta, qué regla no se siguió, qué lectura no se demostró). La única razón para no guardar es no cumplir los criterios; nunca es un vago «no se pudo guardar».

Cómo se corre:

```bash
python3 scripts/candado_entrega.py motor/runs/<LOTE>_<FECHA>/ [--repo RUTA_REPO]
```

- `exit 0` — `CANDADO_ENTREGA: PASA`. Se puede guardar.
- `exit 1` — `CANDADO_ENTREGA: BLOQUEADO — NO SE GUARDA`, con la lista exacta de criterios incumplidos.
- `exit 2` — error de uso.

Qué verifica (detalle en `scripts/CANDADO_ENTREGA.md`):

- **A. Estructura:** `MANIFIESTO.json`, `README.md`, `TABLA_VALORES_COMPLETA.md` y `LECTURA.json` presentes; manifiesto con `lote` y `casos` (cada caso con `case_id`, SHA-256 de resultado/entrada/recibo, sin duplicados); por cada caso los tres archivos; sin huérfanos; README menciona el protocolo.
- **B. Contenido:** INTERPRETABLE con H1/H2, conjunto abierto con trazabilidad geométrica completa por hipótesis; `monte_carlo` y `predictive_validation`; SHA-256 coinciden con el MANIFIESTO. RECIBO con `status` declarado. Entrada con `question` en prosa y `cuts` con `hecho` en prosa.
- **C. Tabla:** la tabla menciona cada `case_id` del manifiesto.
- **D. Lectura demostrada:** ver §5.

El candado no decide la política: valida el paquete de `motor/runs/`. No toca `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`.

## 5. LECTURA.json: la evidencia de lectura

`LECTURA.json` es la prueba de que se leyó el protocolo, no solo decirlo. Es una lista de los archivos de protocolo/especificación leídos para hacer la entrega. Por cada uno trae su `ruta` y su `sha256` (la huella del archivo tal como se leyó) o `fecha`:

```json
{
  "entrega": "F001_F002_20261111",
  "fecha_lectura": "2026-11-11",
  "lecturas": [
    {"ruta": "casos/REGLAS.md", "sha256": "<64 hex>", "reglas": ["regla 6"]},
    {"ruta": "CONTRATO_CARPETAS.md", "sha256": "<64 hex>", "reglas": ["casos/: nunca corridas completas"]},
    {"ruta": "PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md", "sha256": "<64 hex>", "reglas": ["§3 recibo mínimo", "§4 todo dato es un dato"]}
  ]
}
```

El candado comprueba: cada `ruta` existe en el repo; si trae `sha256`, coincide con el archivo actual (si el archivo cambió desde la lectura, lo reporta como no coincidente); y README.md o REVISION.md menciona el nombre de cada archivo leído (la entrega cita lo que leyó). Sin `LECTURA.json`, la entrega no pasa: es el criterio [A4].

## 6. Conflicto explícito con el protocolo viejo

Tres archivos todavía dicen que nunca se sube la corrida completa:

- `casos/REGLAS.md` regla 6: «nunca subir la corrida completa».
- `CONTRATO_CARPETAS.md`: `casos/` — «Nunca corridas completas».
- `casos/fabrica/README.md`: «Corridas completas quedan fuera del repo, en `/workspace/FABRICA_CORRIDAS/<lote>/`».

La forma adoptada por Marco (2026-11-11 ~18:07 CST) es: resumen de una línea en `resultados.jsonl` **y** corridas completas en el apartado separado `motor/runs/<LOTE>_<FECHA>/` para el historial. Este contrato recoge esa forma. Esos tres archivos siguen pendientes de actualizar para que la regla quede escrita. Mientras tanto, si un modelo se encuentra con la contradicción, manda la forma adoptada por Marco y este contrato, no la prohibición vieja.

## 7. Lo que no cambia

- Rama de trabajo vigente: `alterno/cameo-pesos` (`CONTRATO_OPERATIVO_RAMA_VIGENTE.md`). Los PR van contra ella, no contra `main`.
- Engine `motor/Engine_V5_CANONICO_SOLO.py` (sha256 `665c39a2…`) y catálogo 244 `motor/patterns_final_v14.json` (sha256 `d827dcc3…`) son canónicos. No se tocan.
- Leer archivo por archivo con la API de GitHub o el conector, o `git clone`. Prohibido depender de ZIP/zipball. Sin binarios ni ZIPs en el repo.
- Nada se borra ni sobrescribe en silencio; cambios = versiones nuevas + entrada en `avances/`.
