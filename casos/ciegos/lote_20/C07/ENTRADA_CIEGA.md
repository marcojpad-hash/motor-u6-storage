# Entrada ciega — C07

> Solo datos anteriores o iguales a Z. Sin identidad, sin desenlace,
> sin fuentes que identifiquen al sujeto. La identidad y el desenlace
> están sellados en custodia y se revelan solo al verificar.

## Metadatos de custodia
- case_id: C07
- sujeto_alias: SUJETO_C07
- fecha_freeze_Z: 1609-01-01
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
- fecha: 1600-01-01
- hecho: Llega a Praga como asistente de Tycho Brahe; hereda sus observaciones planetarias precisas.
- P: busqueda_verdad 0.82, conocimiento 0.8
- A: analisis 0.82, mentoria_activa 0.75
- C: oportunidad 0.78, jerarquia 0.7

### Corte B
- fecha: 1601-10-24
- hecho: Muere Tycho Brahe; el sujeto lo sucede como matemático imperial de Rodolfo II.
- P: responsabilidad 0.8, ambicion 0.75
- A: metodicidad 0.8, determinacion 0.78
- C: reconocimiento 0.75, presion_social 0.7

### Corte C
- fecha: 1609-01-01
- hecho: Publica Astronomia Nova con las dos primeras leyes del movimiento planetario (órbitas elípticas).
- P: vision 0.84, logro_personal 0.82
- A: teorizacion 0.82, verificacion 0.8
- C: reconocimiento 0.78, desafio_autoridad 0.72

## Salida ciega obligatoria
- Suficiencia: (la fija el motor al correr)
- DATO: ver cortes
- INFERENCIA: (la fija el motor al correr)
- RUIDO: (la fija el motor al correr)
- H1 / H2 / Set / Escenario / Destino: ver SALIDA_CONGELADA.json
- Predictibilidad estructural previa: ver SALIDA_CONGELADA.json
- Condiciones de falsación: el desenlace sellado las decide al verificar
- Qué no puede saberse: la identidad del sujeto (sellada en custodia)
