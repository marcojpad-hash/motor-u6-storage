# Plan de 20 casos ciegos — Motor U6 / V15.3

## Estado al 2026-10-31

- La carpeta casos/ciegos/ ya existe.
- Se migraron cuatro entradas históricas pre-Z desde Notion: B-01, N-02, C-03 y H-01, junto con sus freezes de Grok y ChatGPT.
- Esos cuatro casos son pruebas históricas de modelos; las páginas de origen declaran que Motor V5+244 no se ejecutó en ellos. **No contarlos como casos de evaluación del motor.**
- El repositorio tiene una fábrica/calibración F separada (50 filas, 45 evaluadas en el informe acumulado). F006 R7 es una reevaluación de Courbet, no un caso independiente.
- No se encontró un paquete dedicado de 20 corridas ciegas independientes de Motor U6 con entrada Z, salida congelada y desenlace sellado. No se inventan casos para llenar la cuota.

## Objetivo

Construir 20 casos independientes que ejecuten el motor bajo el protocolo Z final y permitan evaluar por separado:
- H1 y H2.
- Set abierto.
- Escenario.
- Destino exacto y polaridad.
- Predictibilidad estructural previa.
- Integridad del freeze y hashes del motor/patrones.

## Qué significa CIEGO (definición, 2026-11-08)

**Ciego significa que el motor NO recibe ningún dato que pueda decirle QUIÉN es el sujeto.** Nada de nombre, nada que identifique a la persona. La identidad va sellada aparte junto con el desenlace y se revela solo al verificar.

Esto NO es el Z90 ni el freeze: el Z90 y el trabajo Z son la metodología (cómo se corta y se congela), no la ceguera. La ceguera es solo la identidad oculta.

Cómo se aplica en el lote_20 (concreto):
- El `entrada.json` NO lleva el nombre: sin campo `person`, sin nombre en
  el `case_id` (solo el slot, `C01`–`C20`), sin nombre en la `question`, sin
  nombre en los `hecho` de los cortes y sin URL que lo identifique (ni
  Wikipedia ni ninguna fuente con el nombre) en `source_notes`.
- Los cortes llevan hechos, fechas y probabilidades (P/A/C). Los hechos son
  el dato; la identidad no es dato del motor.
- La IDENTIDAD va sellada aparte (`IDENTIDAD_SELLADA.json` en
  `casos/ciegos/lote_20/custodia/CXX/`), junto con el desenlace y el destino
  sellados. No va en el `entrada.json` ni en ningún archivo que el motor lea.
- La identidad se revela solo al verificar (unblinding), después de que la
  salida está congelada y el recibo emitido. Quien verifica (Pecas) es quien
  abre la custodia, no el runner.

## Reglas de independencia

1. Un case_id único por sujeto/entrada (`C01`–`C20`, sin nombre del sujeto).
2. Ninguna reevaluación del mismo input_sha256 incrementa el n.
3. F006/Courbet queda como reevaluación histórica de F005.
4. Cada caso debe congelar Z antes de formular hipótesis.
5. El desenlace se sella por separado y no se consulta hasta que la salida esté congelada.
6. No ajustar pesos ni motor sobre un caso cuyo desenlace ya se conoce.
7. Registrar Engine V5 SHA-256 y catálogo de 244 patrones antes/después.
8. **Ceguera de identidad**: el `entrada.json` no lleva nombre ni dato que
   identifique al sujeto (ver la definición de CIEGO arriba). La identidad
   va sellada en custodia y se revela solo al verificar.

## Plantilla y estructura

Usar PLANTILLA_ENTRADA_CIEGA.md. Por caso crear:

Visible (lo que lee el motor y lo que se congela):
- casos/ciegos/lote_20/CXX/ENTRADA_CIEGA.md
- casos/ciegos/lote_20/CXX/entrada.json (sin `person`, sin nombre en
  `case_id`/`question`/`hecho`/`source_notes`)
- casos/ciegos/lote_20/CXX/COMPROMISO.json (hashes de entrada, identidad,
  desenlace, destino, Engine V5 y catálogo 244)
- casos/ciegos/lote_20/CXX/SALIDA_CONGELADA.json
- casos/ciegos/lote_20/CXX/RECIBO_EJECUCION.json

Custodia separada (no la lee el motor; se abre solo al verificar):
- casos/ciegos/lote_20/custodia/CXX/IDENTIDAD_SELLADA.json
- casos/ciegos/lote_20/custodia/CXX/DESENLACE_SELLADO.json
- casos/ciegos/lote_20/custodia/CXX/DESTINO_SELLADO.json

## Registro de slots

| Slot | Freeze Z | Estado | Nota |
|---|---|---|---|
| C01 | 1781-03-16 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C02 | 1859-11-24 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C03 | 1687-07-05 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C04 | 1879-10-21 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C05 | 1599-01-01 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C06 | 1605-01-16 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C07 | 1609-01-01 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C08 | 1854-11-04 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C09 | 1429-07-17 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C10 | 0800-12-25 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C11 | 1520-09-30 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C12 | 1547-01-16 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C13 | 1206-01-01 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C14 | 1492-08-03 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C15 | 1519-09-20 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C16 | 1275-06-01 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C17 | 1302-01-27 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C18 | 1508-01-01 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C19 | 1642-01-01 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |
| C20 | 1514-01-01 | CORRIDO | Entrada ciega, sin nombre. Custodia sellada. Salida congelada + recibo COMPLETED (lote_20, 2026-11-08). |

Los nombres de los sujetos NO van en este plan: están sellados en
`casos/ciegos/lote_20/custodia/CXX/IDENTIDAD_SELLADA.json` y se revelan solo
al verificar. No se crean entradas sintéticas ni se asignan sujetos sin
evidencia primaria y freeze verificable.

El inventario histórico B-01/N-02/C-03/H-01 permanece separado y no ocupa slots C01–C20.
