# Entrada ciega — C12

> Solo datos anteriores o iguales a Z. Sin identidad, sin desenlace,
> sin fuentes que identifiquen al sujeto. La identidad y el desenlace
> están sellados en custodia y se revelan solo al verificar.

## Metadatos de custodia
- case_id: C12
- sujeto_alias: SUJETO_C12
- fecha_freeze_Z: 1547-01-16
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
- fecha: 1533-12-03
- hecho: Accede al trono con tres años; el poder queda en manos de regentes y facciones de boyardos.
- P: vulnerabilidad 0.8, dependencia 0.78
- A: supervivencia 0.78, resiliencia 0.75
- C: fragmentacion 0.78, rivalidad_poder 0.8

### Corte B
- fecha: 1545-01-01
- hecho: Toma el poder personal a los 15 años; impone su autoridad sobre los boyardos.
- P: autoridad 0.82, determinacion 0.8
- A: audacia 0.8, confrontacion_directa 0.78
- C: hostilidad 0.75, desconfianza 0.78

### Corte C
- fecha: 1547-01-16
- hecho: Coronado primer zar en Moscú; inicia conquistas (Kazán 1552, Astracán 1556).
- P: triunfo 0.82, poder 0.84
- A: liderazgo 0.8, ambicion 0.82
- C: reconocimiento 0.8, escalada_status 0.78

## Salida ciega obligatoria
- Suficiencia: (la fija el motor al correr)
- DATO: ver cortes
- INFERENCIA: (la fija el motor al correr)
- RUIDO: (la fija el motor al correr)
- H1 / H2 / Set / Escenario / Destino: ver SALIDA_CONGELADA.json
- Predictibilidad estructural previa: ver SALIDA_CONGELADA.json
- Condiciones de falsación: el desenlace sellado las decide al verificar
- Qué no puede saberse: la identidad del sujeto (sellada en custodia)
