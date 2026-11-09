# Entrada ciega — C06

> Solo datos anteriores o iguales a Z. Sin identidad, sin desenlace,
> sin fuentes que identifiquen al sujeto. La identidad y el desenlace
> están sellados en custodia y se revelan solo al verificar.

## Metadatos de custodia
- case_id: C06
- sujeto_alias: SUJETO_C06
- fecha_freeze_Z: 1605-01-16
- rango_temporal_observado: ver cortes
- fuente(s) del material pre-Z: selladas en custodia
- responsable del freeze: generador lote_20 (2026-11-08)
- estado: PREPARADO

## Reglas
- La identidad y el desenlace permanecen fuera de este archivo.
- No buscar en internet ni intentar identificar al sujeto durante la corrida ciega.
- Separar DATO, INFERENCIA, HIPÓTESIS y RUIDO.
- No completar huecos con conocimiento posterior.
- No modificar el texto después del freeze.

## Cortes hasta Z
### Corte A
- fecha: 1571-10-07
- hecho: Combate en Lepanto; pierde el uso de la mano izquierda.
- P: patriotismo 0.78, determinacion 0.8
- A: audacia 0.8, resiliencia 0.78
- C: terreno_hostil 0.75, crisis_abrupta 0.7

### Corte B
- fecha: 1580-09-19
- hecho: Liberado tras cinco años cautivo en Argel; regresa a España arruinado y busca empleo.
- P: supervivencia 0.82, busqueda_seguridad 0.78
- A: resiliencia 0.8, flexibilidad_adaptativa 0.75
- C: escasez 0.78, frustracion 0.72

### Corte C
- fecha: 1605-01-16
- hecho: Publica la primera parte de Don Quijote de la Mancha; éxito inmediato en España y Europa.
- P: creatividad 0.84, reconocimiento_previo 0.78
- A: autoexpresion 0.82, generacion_ideas 0.8
- C: reconocimiento 0.82, prosperidad 0.72

## Salida ciega obligatoria
- Suficiencia: (la fija el motor al correr)
- DATO: ver cortes
- INFERENCIA: (la fija el motor al correr)
- RUIDO: (la fija el motor al correr)
- H1 / H2 / Set / Escenario / Destino: ver SALIDA_CONGELADA.json
- Predictibilidad estructural previa: ver SALIDA_CONGELADA.json
- Condiciones de falsación: el desenlace sellado las decide al verificar
- Qué no puede saberse: la identidad del sujeto (sellada en custodia)
