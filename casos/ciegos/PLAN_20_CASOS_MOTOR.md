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

## Reglas de independencia

1. Un case_id único por sujeto/entrada.
2. Ninguna reevaluación del mismo input_sha256 incrementa el n.
3. F006/Courbet queda como reevaluación histórica de F005.
4. Cada caso debe congelar Z antes de formular hipótesis.
5. El desenlace se sella por separado y no se consulta hasta que la salida esté congelada.
6. No ajustar pesos ni motor sobre un caso cuyo desenlace ya se conoce.
7. Registrar Engine V5 SHA-256 y catálogo de 244 patrones antes/después.

## Plantilla y estructura

Usar PLANTILLA_ENTRADA_CIEGA.md. Por caso crear:
- casos/ciegos/lote_20/CXX/ENTRADA_CIEGA.md
- COMPROMISO.json
- SALIDA_CONGELADA.json
- RECIBO_EJECUCION.json
- DESENLACE_SELLADO.json bajo custodia separada, no visible durante la formulación.

## Registro de slots

| Slot | Estado | Nota |
|---|---|---|
| C01–C20 | PENDIENTE | No se crean entradas sintéticas ni se asignan sujetos sin evidencia primaria y freeze verificable. |

El inventario histórico B-01/N-02/C-03/H-01 permanece separado y no ocupa slots C01–C20.
