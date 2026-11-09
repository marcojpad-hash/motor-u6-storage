# Entrada ciega — C05

> Solo datos anteriores o iguales a Z. Sin identidad, sin desenlace,
> sin fuentes que identifiquen al sujeto. La identidad y el desenlace
> están sellados en custodia y se revelan solo al verificar.

## Metadatos de custodia
- case_id: C05
- sujeto_alias: SUJETO_C05
- fecha_freeze_Z: 1599-01-01
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
- fecha: 1590-01-01
- hecho: Llega a Londres; escribe sus primeras obras y se hace un nombre en el teatro.
- P: creatividad 0.82, ambicion 0.78
- A: autoexpresion 0.8, aprendizaje 0.75
- C: oportunidad 0.78, reconocimiento_previo 0.7

### Corte B
- fecha: 1594-01-01
- hecho: Se une a los Lord Chamberlain's Men; escribe Romeo y Julieta y El sueño de una noche de verano.
- P: reconocimiento_previo 0.8, creatividad 0.84
- A: organizacion 0.75, generacion_ideas 0.8
- C: prosperidad 0.75, redes_prestigio 0.78

### Corte C
- fecha: 1599-01-01
- hecho: Se construye el Globe Theatre; el sujeto es copropietario y dramaturgo principal de la compañía.
- P: estatus_social 0.8, logro_personal 0.82
- A: planificacion_activa 0.78, liderazgo 0.75
- C: prosperidad 0.8, reconocimiento 0.78

## Salida ciega obligatoria
- Suficiencia: (la fija el motor al correr)
- DATO: ver cortes
- INFERENCIA: (la fija el motor al correr)
- RUIDO: (la fija el motor al correr)
- H1 / H2 / Set / Escenario / Destino: ver SALIDA_CONGELADA.json
- Predictibilidad estructural previa: ver SALIDA_CONGELADA.json
- Condiciones de falsación: el desenlace sellado las decide al verificar
- Qué no puede saberse: la identidad del sujeto (sellada en custodia)
