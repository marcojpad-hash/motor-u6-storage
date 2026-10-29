# CONTRATO DE EJECUCIÓN Y LECTURA DEL MOTOR — LLM

Versión: 1.0
Ámbito: análisis, ejecución, depuración e interpretación del repositorio motor-u6-storage.
Regla de integridad: este contrato no autoriza modificar el motor canónico ni sus patrones.

## 1. Separación obligatoria de estados

Nunca usar «el motor dice», «el motor detectó», «se ejecutó» o «el resultado demuestra» sin clasificar la evidencia en uno de estos estados:

- **CÓDIGO INSPECCIONADO**: se leyó una ruta y versión/commit concretos. Esto demuestra qué implementa el código, no que se ejecutó.
- **EJECUCIÓN CONFIRMADA**: existe un artefacto de salida de esa corrida, ligado al input, código y estado de proceso. Registrar ruta del resultado, exit code/estado, hash del input, hash del resultado, commit o huellas del motor, fecha/hora si el runner la produce y errores.
- **EJECUCIÓN FALLIDA**: hay evidencia del error, timeout, bloqueo de preflight o código de salida no cero. No interpretar una salida parcial como corrida completada.
- **EJECUCIÓN NO VERIFICADA**: no se dispone de artefactos suficientes. No afirmar que se ejecutó ni presentar inferencias como resultados.
- **RESULTADO PARCIAL / INCOMPLETO**: el runner devolvió salida, pero hay campos ausentes, datos no finitos, pasos requeridos fallidos o estado de pausa. Informar el estado exacto del recibo, no resumirlo como «completado».

La presencia de un archivo JSON por sí sola no confirma una ejecución válida: puede ser antiguo, parcial, fixture o salida de otra corrida. Vincularlo al input y al código usados.

## 2. Antes de ejecutar

1. Identificar el runner y la revisión exacta del repositorio.
2. Leer el contrato de entrada y los preflight que realmente invoca el runner.
3. Confirmar qué entrada se va a usar y qué salida se espera.
4. No editar Engine_V5_CANONICO_SOLO.py ni patterns_final_v14.json; respetar los candados y el manifiesto.
5. Si no se puede ejecutar el código en un entorno disponible, decirlo como límite operativo y no simular una corrida.

## 3. Después de ejecutar: recibo mínimo obligatorio

Conservar y leer el recibo de la corrida. Como mínimo registrar:

- estado_ejecucion: CONFIRMADA, FALLIDA, BLOQUEADA, INCOMPLETA o NO_VERIFICADA.
- runner y commit/revisión usados;
- ruta del input y SHA-256 del input;
- ruta del resultado y SHA-256 del resultado, si existe;
- código de salida, excepción o timeout;
- estado del preflight/manifiesto;
- estado de integridad del resultado: completo, incompleto o parcial, con motivos;
- módulos/plugins efectivamente invocados, sus entradas y sus salidas cuando esa información exista;
- archivos auxiliares/ledger preservados y sus huellas, si aplica.

No inventar un campo que el runner no genere. Si falta, anotarlo como NO REGISTRADO; no rellenarlo por inferencia. Si el runner existente no genera el recibo mínimo, reportar esa carencia y no elevar la corrida a CONFIRMADA hasta verificarla con los artefactos disponibles.

## 4. Regla para interpretar el resultado

Antes de concluir, leer el resultado completo o hacer una inspección estructurada de todos sus campos relevantes. No tomar el ranking principal como sustituto del campo de datos.

- **Todo dato es un dato.** No borrar, ignorar ni declarar irrelevantes observaciones por estar fuera del top, abajo, en un valle, en descenso, en una meseta o por contradecir la hipótesis preferida.
- Separar: dato observado, cálculo del módulo, interpretación del módulo, decisión del predictor y conclusión del analista.
- No confundir una señal lateral con una decisión de H, ni existencia del módulo con su ejecución real.
- Verificar cableado: quién llama al módulo, con qué payload, qué filtros aplica, qué resultado devuelve y si ese resultado llega a una etapa posterior.
- Describir umbrales, top-k, filtros de piso, valores por defecto y exclusiones explícitas. No decir «todo el campo» cuando el input real está limitado.
- Conservar datos de picos, mesetas, valles, descensos, latencias, familias emergentes y tokens fuera del top cuando estén presentes en la salida. Explicar su función sin sustituirla por expectativas genéricas del modelo.
- No proponer implementar una función antes de comprobar si ya existe, si está conectada y si se ejecutó en esa corrida.
- Las reglas lógicas y filtros nombrados por el proyecto deben localizarse en el código real. No intercambiar nombres de filtros distintos (por ejemplo, el filtro lógico de Bernstein/Copi no es Polti).

## 5. Formato de respuesta al usuario

Toda respuesta sobre una corrida debe comenzar con el estado verificable:

**Estado:** EJECUCIÓN CONFIRMADA / FALLIDA / BLOQUEADA / INCOMPLETA / NO VERIFICADA.

Después, en este orden:
1. Qué artefacto/código se inspeccionó o ejecutó.
2. Qué devuelve literalmente el motor en los campos relevantes.
3. Qué datos quedan fuera del ranking o de la decisión y qué módulos los conservan.
4. Interpretación separada, con inferencias marcadas como inferencias.
5. Fallas reales, diferencias entre código y ejecución, y acción concreta siguiente.

No repetir explicaciones genéricas, disculpas ni promesas de comportamiento. Presentar resultados, rutas, huellas y diferencias verificables. Si falta una prueba, decir exactamente cuál.

## 6. Cierre de control

Antes de enviar la respuesta, comprobar:
- ¿Tengo un artefacto de esta corrida o solo leí código?
- ¿El artefacto corresponde al input y revisión citados?
- ¿Estoy atribuyendo al motor una salida que no produjo?
- ¿Estoy descartando datos por rango, forma, estabilidad o contradicción?
- ¿Confundí módulo implementado con módulo conectado o ejecutado?
- ¿Propuse como nuevo algo que ya está implementado?
- ¿Separé hecho, resultado, inferencia y pendiente?

Si alguna respuesta revela una falla, corregirla antes de responder.
