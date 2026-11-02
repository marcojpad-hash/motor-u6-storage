# Investigación: algoritmo subexponencial, Lean y posible aplicación al Motor U6

Fecha: 2026-11-02
Estado: INVESTIGACIÓN DOCUMENTADA; NO INTEGRADO EN EL RUNNER NI EN EL MOTOR CANÓNICO.

## 1. Qué afirma el trabajo

El preprint de OpenAI, *The Exponential Time Hypothesis is False* (manuscrito fechado el 17-oct-2026 y revisado el 25-oct-2026), presenta un algoritmo determinista que cuenta exactamente las asignaciones que satisfacen una fórmula k-CNF, para cada k fijo >= 2.

La cota principal del manuscrito es, en su forma general:

- tiempo: (n+m)^{O_k(1)} * 2^{O_k(n log log n / sqrt(log n))};
- espacio: polinómico en n y m.

Para fórmulas dispersas con m <= Dn, el manuscrito indica una cota exponencial aún menor. El caso k=3 implica una resolución de 3-SAT en tiempo subexponencial y, por tanto, contradice ETH si la prueba y la correspondencia con el problema estándar resisten revisión.

Fuentes primarias:
- Manuscrito y código del proyecto: https://github.com/openai/math/tree/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026
- Texto del manuscrito: https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex
- Alcance de la formalización: https://github.com/openai/math/blob/main/lean/docs/378.md

## 2. Qué verifica Lean y qué no

Lean es un asistente de demostración. El kernel comprueba que una prueba formal deriva un teorema formal a partir de definiciones y axiomas aceptados.

La nota oficial lean/docs/378.md dice que Lean formaliza una máquina determinista que cuenta exactamente las asignaciones de una k-CNF canónicamente codificada, con espacio polinómico y una cota subexponencial. La cota formalizada es más débil que la cota principal del manuscrito: contiene un factor adicional log log n en el exponente (en la forma publicada por la nota, O_k(n (log log n)^2 / sqrt(log n))). Sigue siendo subexponencial.

Separación obligatoria:
1. Lean comprueba la prueba del enunciado formal.
2. La correspondencia entre el enunciado formal, la codificación canónica y el problema informal del artículo requiere revisión matemática.
3. El resultado asintótico no promete un solver práctico para instancias pequeñas o medianas.
4. La formalización no demuestra que el algoritmo sea adecuado para los datos, objetivos o métricas del Motor U6.

El proyecto mantiene materiales públicos de revisión externa. La afirmación no debe tratarse como consenso cerrado ni como un resultado ya integrado en herramientas prácticas.

## 3. Qué es una fórmula booleana k-CNF

Una variable booleana solo puede ser 0/falso o 1/verdadero. Un literal es una variable o su negación. Una cláusula es una disyunción (OR) de hasta k literales. Una fórmula k-CNF es una conjunción (AND) de cláusulas.

Ejemplo:
- Variables: A, B, C.
- Fórmula: (A OR B) AND (NOT A OR C) AND (NOT B OR NOT C).

Una asignación satisface la fórmula si todas las cláusulas son verdaderas. SAT pregunta si existe al menos una asignación válida. #SAT pregunta cuántas asignaciones válidas existen. El trabajo es de conteo exacto, no solo de búsqueda de una solución.

## 4. Relación concreta con el Motor U6

El motor actual no es un solver SAT. Su flujo combina:
- entradas temporales con cortes y evidencias;
- tokens P/A/C con pesos;
- un catálogo de 244 patrones;
- puntuación/ranking de familias y trayectorias;
- módulos laterales, compuertas, Caldero y Monte Carlo.

Los pesos y rankings son graduados/numéricos. Convertirlos sin más a verdadero/falso perdería información y podría cambiar el orden de hipótesis. Por eso no se debe reemplazar la puntuación actual por una fórmula booleana.

Sí existe un subproblema experimental que puede modelarse como SAT/CNF: comprobar la consistencia de un conjunto de restricciones discretas sobre escenarios candidatos. Ejemplo de variables:
- x[t,f] = 1 si la familia/estado f está asignada al corte t;
- restricciones exactly-one por corte;
- transiciones permitidas/prohibidas entre cortes;
- restricciones de compatibilidad explícitamente justificadas;
- exclusión de evidencia posterior al freeze.

Esto permitiría:
- detectar conjuntos de restricciones incompatibles;
- enumerar o contar configuraciones que cumplen las reglas;
- medir cuánto reduce cada nueva restricción el espacio de escenarios;
- comprobar que la preparación temporal no admite asignaciones prohibidas.

No permitiría por sí solo:
- elegir la trayectoria verdadera;
- convertir el conteo de soluciones en probabilidad calibrada;
- validar una hipótesis biográfica;
- mejorar la precisión predictiva sin experimentos ciegos.

## 5. Decisión de integración

**No cablear el algoritmo de OpenAI directamente al runner productivo todavía.** El repositorio no contiene una reducción probada desde el ranking ponderado del motor a k-CNF, ni una implementación reutilizable del algoritmo del manuscrito como paquete ejecutable.

Ruta segura:
1. Definir un contrato de entrada discreto para un subproblema real (no para todo el motor).
2. Escribir un codificador CNF independiente en un módulo experimental.
3. Validar el codificador contra enumeración exhaustiva en instancias pequeñas y casos de borde.
4. Comprobar que cada restricción CNF tiene trazabilidad a una regla ya aprobada del motor.
5. Comparar soluciones/contajes con un solver SAT/#SAT convencional en tamaños manejables.
6. Solo después estudiar si la técnica subexponencial del manuscrito aporta una ventaja medible.
7. Mantener el módulo como sidecar no decisor; no alterar Engine V5 ni patterns_final_v14.json.

Criterios mínimos para promover:
- equivalencia comprobada entre el modelo de restricciones y la semántica deseada;
- cero soluciones espurias en el corpus de pruebas;
- resultados reproducibles;
- benchmark de tiempo/memoria frente a alternativas conocidas;
- prueba ciega que demuestre utilidad real, no solo más configuraciones exploradas.

## 6. Hallazgo operativo paralelo: F007

La inspección del código encontró una falla real en preparar-z:
- destinos_lote_F007.py no contiene el campo familias;
- preparar_z() iteraba dz.get("familias") or [], por lo que no rechazaba el dato ausente;
- más adelante escribía dz["familias"], provocando KeyError durante la materialización.

Se corrigió el validador en casos/fabrica/fabrica.py para rechazar antes de escribir la cola cuando familias no sea una lista no vacía, detectar duplicados y validar cada familia contra el catálogo. El arreglo no inventa las familias faltantes: el custodio debe completarlas con base en los destinos sellados y el catálogo.

## 7. Registro de horarios de corrida

La lectura de los logs completos del run 41081591816 permite precisar el horario:
- inicio del runner: 2026-10-30 15:32:11.825 UTC = 09:32:11.825 CDMX;
- cierre del job: 2026-10-30 15:32:55.375 UTC = 09:32:55.375 CDMX;
- duración aproximada: 43.55 segundos;
- el artefacto se creó a las 15:32:54 UTC = 09:32:54 CDMX.

Importante: ese run ejecutó `fabrica.py correr --lote F006_TRAZA_V2_R7 --rehacer CAL_F005_01_COURBET`, con `FABRICA_MODELO=ChatGPT_CEB_smoke` y `FABRICA_SYNC=0`. Fue una reevaluación del mismo caso Courbet de F005, no un caso independiente nuevo ni una corrida de Grok. El propio registro de calibración lo marca como re-evaluación y prohíbe contarlo como caso nuevo.

El workflow `fabrica-lote-diario.yml` solo declara `workflow_dispatch`: no tiene cron. No establece una hora diaria fija; se dispara manualmente o por dispatch externo. No debe confundirse la hora de creación del artefacto con el inicio de la corrida.

Se añadió instrumentación a `fabrica-lote-diario.yml` para que sus siguientes artefactos incluyan `RUN_METADATA.json` con run_id, intento, workflow, evento, lote, SHA, actor, hora UTC de inicio y fin, y estado final.

Además se creó `auditar-corridas-actions.yml`: se activa al terminar cualquier workflow del repositorio y cada hora (minuto 17), consulta ejecuciones, jobs y artefactos de los últimos siete días, calcula horas/duraciones en America/Mexico_City y persiste un snapshot solo si hay cambios. La auditoría no reintenta ni altera corridas.

## 8. Candados

- Engine V5 canónico: no modificado.
- Catálogo patterns_final_v14.json (244): no modificado.
- El nuevo trabajo Lean/SAT queda en investigación y experimentación lateral.
- No declarar integración ni mejora predictiva hasta que exista código, prueba y benchmark verificables.
