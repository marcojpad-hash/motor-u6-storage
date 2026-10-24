# Reglas de `casos/`

1. **Sin duplicados**: antes de agregar un caso, calcular el sha256 de su entrada y buscarlo en `HASHES_ENTRADAS.json`, `HISTORIAL_HASHES.json` y `resultados/resultados.jsonl`.
2. **Nunca volver a correr los 15 casos sellados.**
3. **Sellar el caso antes de conocer el desenlace.**
4. Guardar **solo la entrada y sus hashes**. Nada de contenido completo de casos aquí.
5. Un ejercicio de biografía de caso se construye **desde cero**, sin reutilizar ejercicios anteriores.
6. Corridas y calibración: **nunca subir la corrida completa**. Solo un resumen por corrida en `resultados/resultados.jsonl` (una línea JSON): hash del caso (sha256 de la entrada), fecha, H1/H2/apuesta, grado, margen, métricas clave y hashes de entrada/salida. Lo genera `scripts/sincronizar_storage.py despues`.
7. Caso nuevo: partir de `PLANTILLA_CASO_NUEVO.json`.
