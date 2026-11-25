# 2026-11-24 — ChatGPT: tercera capa de lectura contextual para Sombrero Blanco

Rama: `alterno/cameo-pesos`
Base inspeccionada: `7fa5709392059a48fb08d2f39c1b844921bab468`
Estado: **PROPUESTA DOCUMENTADA; NO IMPLEMENTADA NI CABLEADA**.
Alcance: guardianes operativos / lateral Sombrero Blanco. No modifica H, el predictor, el Engine V5 ni el catálogo 244.

## Qué se incorpora como hallazgo

La lectura de una interacción no debe limitarse a identificar señales ni a interpretar la intencionalidad y los valores del discurso. Hace falta observar también la trayectoria por la que el modelo construye su interpretación: qué señal activa una lectura, qué peso relativo adquiere, qué contexto queda desplazado y si la corrección del usuario cambia efectivamente la interpretación posterior.

La tercera capa se propone como una extensión observacional del lateral de Sombrero Blanco. No se presenta como un guardián independiente ni como una función ya existente.

## Organización provisional de las tres capas

1. **Contenido y señales observables.** Qué aparece explícitamente en la entrada: afirmaciones, términos, relaciones, contexto y evidencia disponible. El nombre definitivo de esta primera capa queda sujeto a cotejo con la nomenclatura vigente.
2. **Intencionalidad y valores del discurso.** Qué propósito cumple el discurso en su contexto y qué valores, criterios o relaciones organiza. Se conserva la capa previa señalada por el diseño; no se sustituyen ni se renombran sus componentes.
3. **Trayectoria de interpretación y ponderación contextual.** Cómo el modelo pasa de las señales a una lectura: activadores, saliencia asignada, balance frente al contexto, inferencias añadidas, desviación respecto del propósito efectivo y respuesta ante correcciones.

Las capas se relacionan y pueden aportar información entre sí; no son filtros secuenciales que descarten automáticamente lo que no encaja.

## Observables propuestos para la tercera capa

- **Señal activadora:** elemento concreto que parece haber orientado la interpretación.
- **Ponderación contextual:** importancia relativa que la respuesta le asigna frente a las demás señales disponibles.
- **Contexto desplazado:** datos relevantes que quedaron subrepresentados o fuera de la respuesta.
- **Trazabilidad inferencial:** distinción entre lo dicho explícitamente, lo inferido y lo que el modelo no puede conocer.
- **Desviación de propósito:** diferencia entre la función efectiva de la intervención y la tarea que el modelo asumió.
- **Corregibilidad efectiva:** si una aclaración cambia la representación operativa y las respuestas posteriores, no solo si el modelo declara aceptar la corrección.

## Contrato de comportamiento propuesto

- Observar y dejar trazabilidad; no reescribir H ni alterar la decisión del predictor.
- No convertir una señal saliente en explicación total cuando existen datos contextuales relevantes.
- Conservar señales contradictorias, neutrales y de continuidad; no descartarlas por no coincidir con la primera hipótesis.
- Separar las reglas o restricciones conocidas de las inferencias sobre mecanismos internos no observables.
- No afirmar acceso a pesos internos, instrucciones ocultas o estados privados del modelo. La auditoría se basa en entradas, respuestas y cambios observables.
- Una corrección solo cuenta como efectiva si modifica la interpretación posterior de forma consistente y verificable.

## Relación con Sombrero Blanco

La propuesta se acopla conceptualmente al lateral de Sombrero Blanco como una tercera capa de lectura y auditoría contextual. No sustituye sus funciones actuales de admisión, marca o veredicto, ni confunde el sombrero absorbido (`_protocol_quality`) con una puerta de bloqueo.

El resultado esperado sería una traza explicable de la interpretación, no un nuevo puntaje opaco ni un veto automático. La integración deberá respetar el contrato existente de guardianes: marcar, preservar evidencia y no decidir H.

## Criterios de evaluación para una futura implementación

1. Identificar qué señal motivó la lectura sin atribuir causalidad no demostrada.
2. Mostrar qué señales contextuales fueron consideradas y cuáles quedaron fuera.
3. Distinguir la ponderación observable en la respuesta de los pesos internos reales, que no están expuestos.
4. Detectar cuándo la respuesta cambia el propósito de la interacción.
5. Comprobar, mediante turnos posteriores, si una corrección fue incorporada y se mantuvo.
6. Comparar la lectura inicial y la corregida sin borrar la primera traza.

## Estado y límites

- **INSPECCIONADO:** contrato operativo de rama, mapa vigente de guardianes, contrato de ejecución, reglas de avances y estado de la rama.
- **PROPUESTO:** tercera capa de trayectoria de interpretación y ponderación contextual, vinculada al lateral de Sombrero Blanco.
- **NO IMPLEMENTADO:** no se creó módulo, API, flag, prueba ni cableado.
- **NO VERIFICADO EN EJECUCIÓN:** no se ejecutó una corrida ni una prueba de comportamiento para esta propuesta.
- **Pendiente de diseño:** cotejar la nomenclatura exacta de las capas uno y dos con sus artefactos de origen y definir el esquema de salida antes de programar.

## Integridad del motor

Los archivos canónicos no se modificaron. Los selectores y candados de la rama declaran:
- Engine V5: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
- Catálogo: 244 patrones; `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.

Pruebas: **0 passed, 0 skipped, 0 failed**; no ejecutadas porque esta entrada registra una propuesta conceptual y no modifica código.
