# Auditoría de continuidad y estado — Motor U6 / V15.3

Fecha: 2026-10-31. Alcance: lectura del repositorio \`motor-u6-storage\`, registro de corrida F006 R7, contratos y documentos de entrada. No se modificó código canónico ni se ejecutó una corrida nueva.

## Hallazgos y correcciones

### 1. F006 R7 estaba en un artifact de Actions, no en el registro Git

**Causa:** el run \`41081591816\` produjo artifact \`12989457446\`, pero el repositorio terminaba en F005 y \`casos/resultados/resultados.jsonl\` no contenía F006.

**Corrección:** se descargó el ZIP, se verificó SHA-256 \`0ef1887f395e229e77f1ea6b37ae9025fc23d63c6e3789fedfa7489913871ffb\`, y se persistieron compromiso, resumen, evaluación, registro de calibración y manifiesto en \`casos/fabrica/lotes/F006_TRAZA_V2_R7_*\`. Se añadió una fila de corrida a \`casos/resultados/resultados.jsonl\`.

Los archivos de salida de 5.39 MB y ledger CEB de 11.33 MB no se copiaron al repo; el manifiesto conserva sus hashes y líneas. El archivo \`desenlaces.json\` no se copió: contiene el paquete sellado post-Z.

### 2. F006 no es un caso independiente

F006 vuelve a ejecutar \`CAL_F005_01_COURBET\` con el mismo \`input_sha256\` de F005. Es una reevaluación de un caso ya contado.

**Corrección:** se añadió una sección de reevaluaciones a \`casos/fabrica/CALIBRACION_ACUMULADA.md\`, pero no se alteraron los denominadores ni \`calibracion_acumulada.csv\`. Evita inflar la muestra por repetir el mismo caso.

### 3. Resultado mixto que no debe ocultarse

- H1 \`30_ambicion\`: 0.
- H2 \`20_sacrificio_por_un_ideal\`: 0.
- Set abierto: 1.
- Escenario principal \`CONTINUIDAD_ASCENDENTE\`: 1.
- Destino personal: \`auge\`; desenlace sellado: \`ruptura\`; destino exacto y polaridad: 0.

La corrida terminó con returncode 0. Monte Carlo: 9 llamadas, 6,310 simulaciones, 9 convergencias y 0 no convergencias. Compuertas Caldero y piezas: OK. Manifiesto: 304 archivos, sin deriva ni ausentes. Candados del motor y patrones: intactos.

### 4. Calibración insuficiente para elegir peso

La evaluación de F006 tiene n=1 para peso 0 y declara \`MUESTRA_INSUFICIENTE (<10): no elegir peso con esto\`. El registro también dice que el peso no fue aplicado por el motor.

**Corrección:** se registró la limitación y se abrió una duda técnica para el siguiente lote. No se cambió ningún peso ni motor.

### 5. Versiones y hashes podían confundirse

Notion conserva páginas de septiembre con V15.1 y un hash antiguo \`e5d9...\`. El archivo actual de selección/candado identifica Engine V5 de 30,507 bytes con hash \`665c...\` y catálogo de 244 patrones con hash \`d827...\`. El runner integrado V15.3 es una capa distinta.

**Corrección:** se creó \`docs/MAPA_VERSIONES_Y_AUTORIDAD.md\` y se aclaró el alcance de la regla numérica en \`motor/REGLAS.md\`.

### 6. Puntos de entrada desactualizados

\`FEEDME_ACTUALIZADO.md\`, \`INICIO_SESION_CHATGPT.md\` y \`README.md\` dirigían al informe del 25-oct, aunque existían avances y evidencia hasta el 30-oct.

**Corrección:** se actualizaron para apuntar a esta auditoría, el mapa de versiones y el informe del 30-oct.

## Incidencia empírica abierta

El error de destino no se puede resolver con documentación ni con una sola reevaluación. Se abrió \`seguimiento/dudas/2026-10-31_duda_destino_personal_F006_R7.md\` con el protocolo para casos independientes y calibración sin fuga de información. No se ajustó el motor.

## Estado de integridad

- Engine V5 canónico: sin cambios.
- Catálogo de 244 patrones: sin cambios.
- Candados antes/después: true.
- Corrida F006: evidencia de ejecución recuperada y persistida.
- Nueva corrida durante esta auditoría: no ejecutada.
- Notion: intento de insertar aviso de vigencia bloqueado por la herramienta; no se modificaron esas páginas. La vigencia se documenta aquí y en el repo.


## Archivo histórico Notion y casos ciegos

Se localizaron cuatro ejercicios históricos en Notion: B-01, N-02, C-03 y H-01. Se migraron a casos/ciegos/2026-09-20/ únicamente las entradas pre-Z y las predicciones congeladas de Grok/ChatGPT. Se excluyeron las secciones post-revelación, identidades y desenlaces. El inventario y las reglas de custodia están en casos/ciegos/README.md.

Se creó casos/ciegos/PLAN_20_CASOS_MOTOR.md y una plantilla Z final. Los cuatro ejercicios migrados no son corridas del motor; el plan de 20 casos independientes sigue pendiente y no se fabricaron datos para completarlo.

## Notion

La actualización/creación de una página de aviso de vigencia en Notion fue rechazada por el límite de bloques gratuitos del workspace (entitlement_required; sin efectos laterales). Las páginas antiguas siguen intactas. GitHub queda como fuente de verdad; no se reintentó la operación.
