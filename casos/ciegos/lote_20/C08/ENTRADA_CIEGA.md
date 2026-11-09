# Entrada ciega — C08

> Solo datos anteriores o iguales a Z. Sin identidad, sin desenlace,
> sin fuentes que identifiquen al sujeto. La identidad y el desenlace
> están sellados en custodia y se revelan solo al verificar.

## Metadatos de custodia
- case_id: C08
- sujeto_alias: SUJETO_C08
- fecha_freeze_Z: 1854-11-04
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
- fecha: 1850-01-01
- hecho: Estudia enfermería en Kaiserswerth (Alemania); rechaza el papel tradicional asignado a las mujeres de su época.
- P: devocion 0.82, altruismo 0.8
- A: aprendizaje 0.8, determinacion 0.82
- C: desafio_autoridad 0.75, oposicion 0.7

### Corte B
- fecha: 1853-08-12
- hecho: Dirige el Instituto para el Cuidado de Damas Enfermas en Londres; reforma su gestión y sus registros.
- P: liderazgo 0.8, organizacion 0.82
- A: metodicidad 0.8, planificacion_activa 0.78
- C: reconocimiento_previo 0.72, legitimidad_percibida 0.75

### Corte C
- fecha: 1854-11-04
- hecho: Llega a Scutari (Crimea) con 38 enfermeras; encuentra un hospital con mortalidad altísima y condiciones insalubres.
- P: deber 0.84, determinacion 0.82
- A: organizacion 0.84, analisis 0.8
- C: crisis_abrupta 0.8, terreno_hostil 0.78

## Salida ciega obligatoria
- Suficiencia: (la fija el motor al correr)
- DATO: ver cortes
- INFERENCIA: (la fija el motor al correr)
- RUIDO: (la fija el motor al correr)
- H1 / H2 / Set / Escenario / Destino: ver SALIDA_CONGELADA.json
- Predictibilidad estructural previa: ver SALIDA_CONGELADA.json
- Condiciones de falsación: el desenlace sellado las decide al verificar
- Qué no puede saberse: la identidad del sujeto (sellada en custodia)
