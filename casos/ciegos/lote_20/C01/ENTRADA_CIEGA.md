# Entrada ciega — C01

> Solo datos anteriores o iguales a Z. Sin identidad, sin desenlace,
> sin fuentes que identifiquen al sujeto. La identidad y el desenlace
> están sellados en custodia y se revelan solo al verificar.

## Metadatos de custodia
- case_id: C01
- sujeto_alias: SUJETO_C01
- fecha_freeze_Z: 1781-03-16
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
- fecha: 1756-01-27
- hecho: Nace en Salzburgo; niño prodigio, gira por las cortes de Europa con su padre.
- P: creatividad 0.8, reconocimiento_previo 0.7
- A: aprendizaje 0.82, mentoria_activa 0.78
- C: oportunidad 0.78, jerarquia 0.65

### Corte B
- fecha: 1777-09-23
- hecho: Viaja a París con su madre (muere en 1778); busca un empleo estable sin conseguirlo.
- P: ambicion 0.8, busqueda_seguridad 0.7
- A: viaje 0.78, esfuerzo_sostenido_reciente 0.7
- C: frustracion 0.72, escasez 0.68

### Corte C
- fecha: 1781-03-16
- hecho: Rompe con el arzobispo de Salzburgo; se establece en Viena como músico independiente.
- P: independencia 0.84, ambicion 0.8
- A: rebeldia 0.78, autoexpresion 0.8
- C: incertidumbre 0.75, oportunidad 0.8

## Salida ciega obligatoria
- Suficiencia: (la fija el motor al correr)
- DATO: ver cortes
- INFERENCIA: (la fija el motor al correr)
- RUIDO: (la fija el motor al correr)
- H1 / H2 / Set / Escenario / Destino: ver SALIDA_CONGELADA.json
- Predictibilidad estructural previa: ver SALIDA_CONGELADA.json
- Condiciones de falsación: el desenlace sellado las decide al verificar
- Qué no puede saberse: la identidad del sujeto (sellada en custodia)
