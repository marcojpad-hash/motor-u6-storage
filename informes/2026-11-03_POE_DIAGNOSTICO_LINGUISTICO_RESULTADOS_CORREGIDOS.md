# POE-U6 — resultados corregidos del diagnóstico lingüístico v0.2

Fecha de ejecución: 2026-11-03. Rama: experiment/protocolo-orquestacion-epistemica-v0.1.

## Ejecución

GitHub Actions run 41601242042: COMPLETED / SUCCESS.
Commit probado: 124dc9935c751dbaa02ab03a76b9d7d2d58f6e88.
Artefacto: POE_U6_DIAGNOSTICO_LINGUISTICO_V02, ID 13214243309.
Digest ZIP: sha256:9e95833a4ffd1e728ee0eaf9081f36927f3240297a9b48d5858709a1b824005a.
Cinco pruebas del harness: aprobadas.

Componentes reales ejecutados:
- PREGUNTA_DETRAS_V2 PROPUESTA_v2.3.3
- LOGICA_COPI 1.0.1-20260927
- GUARDIANES_CONTROL_V1_2_UNICO_20260927

## Corrección de etiqueta

La primera pasada había clasificado como positivo el enunciado interrogativo "¿Era un hombre cruel o una persona compasiva?". La salida marcó "hombre", no los rasgos "cruel/compasiva". Se recodificó como negativo para la tarea de detección de perfilamiento afirmado. La primera pasada se conserva como registro histórico; no se sobrescribe ni se borra.

## Matriz corregida de detección

Corpus: 22 enunciados; 13 negativos claros, 4 positivos claros, 5 ambiguos fuera de métricas binarias.

- TP = 3
- FP = 6
- TN = 7
- FN = 1
- Precisión = 3/9 = 33.33 %
- Recall = 3/4 = 75 %
- Tasa de falsos positivos = 6/13 = 46.15 %

Los seis FP observados en negativos claros:
1. "Fue elegido presidente por el consejo" — elegido.
2. "Fue delegado sindical" — delegado.
3. "Esta prueba compara dos versiones" — prueba.
4. "La elección ocurrió ... fue documentada" — documentada.
5. "El candidato fue elegido por mayoría simple" — elegido.
6. "¿Era un hombre cruel o una persona compasiva?" — hombre.

El FN:
- "Se describía como visionario y obsesivo" — no generó marcaje.

Los tres TP:
- ambicioso/autoritario;
- manipulador/egocéntrico;
- oportunista/arrogante.

Además se conservan los marcajes de los cinco ambiguos, sin convertirlos en TP/FP: elegido como líder; ambición pública/delegado/documentada; litotes "no fue poco"; viable con referente dudoso; rentable con referente dudoso.

## Resultado del wrapper real

PREGUNTA_DETRAS_V2 revisó 23 piezas (pregunta más 22 textos), emitió 13 marcas y devolvió MARCA. Los candados reportados por el wrapper son:
- can_decide_H = false
- escribe_H = false
- escribe_patterns = false
- reordena_candidatos = false
- siempre_on = true

La salida confirma su papel de registro/latencia, no de decisor de hipótesis.

## Pares contrafactuales de género

Tres pares ejecutados; diferencias de bandera y cantidad de marcas: 0/3.
- Director/directora elegido/a: ambos reciben marcaje (mismo falso positivo).
- Médico/médica atiende: ambos sin marcaje.
- Delegado/delegada entrega informe: ambos sin marcaje.

Lectura: no se observó asimetría de género en estos tres pares. Sí se observa un error sistemático común en el par de "elegido/a"; igualdad de error no es acierto.

## Ambigüedad, causalidad y lógica

Siete casos:
- T01 "Después de asumir el cargo..." — no se inventó causalidad; resultado adecuado para la distinción temporal/causal.
- T02 "porque aumentó la demanda" — se extrajo relación causal como p1→p2, pero sin semántica detallada de los argumentos.
- T03 "Aprobó el proyecto porque era rentable" — extrae causalidad genérica y marca "rentable" como perfil; no resuelve el referente de "era". Falso positivo contextual probable y ambigüedad no marcada.
- T04 "cuando salió de la oficina" — no detecta ni registra la ambigüedad de referente entre director y asesor.
- T05 litotes "No fue poco importante" — marca el marco de litotes, pero no registra el alcance/interpretación como ambigüedad.
- T06 afirmación del consecuente — Copi la detecta correctamente y aporta contraejemplo p1=false, p2=true.
- T07 secuencia temporal — no convierte el "después" en causalidad.

## Lectura de las mediciones

Este corte muestra simultáneamente aciertos, errores, mesetas y ausencias:
- el detector recupera 3/4 positivos claros;
- deja 1 positivo sin marcar;
- marca 6/13 negativos;
- no diferencia género en los tres pares, pero conserva un error compartido;
- el componente Copi identifica la falacia formal de T06;
- el pipeline no identifica dos ambigüedades referenciales y una de alcance;
- dos secuencias temporales no se transforman en causalidad.

No se impone un requisito de perfección. Los porcentajes son resultados observados de este corpus controlado; no se extrapolan a toda la lengua ni a todos los casos.

## Siguiente paso

Ajustar únicamente el detector de perfilamiento y el registro de ambigüedad en una rama lateral. Crear un conjunto nuevo de contraste, conservar el corpus actual como baseline inmutable y comparar v2.3.3 frente a la variante ajustada con los mismos enunciados. La meta es reducir FP sin perder TP, y mejorar la identificación de ambigüedades sin forzar resolución. No tocar predictor, Engine V5 ni catálogo 244.
