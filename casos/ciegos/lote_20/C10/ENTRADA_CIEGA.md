# Entrada ciega — C10

> Solo datos anteriores o iguales a Z. Sin identidad, sin desenlace,
> sin fuentes que identifiquen al sujeto. La identidad y el desenlace
> están sellados en custodia y se revelan solo al verificar.

## Metadatos de custodia
- case_id: C10
- sujeto_alias: SUJETO_C10
- fecha_freeze_Z: 0800-12-25
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
- fecha: 0768-09-24
- hecho: Hereda el reino franco junto a su hermano; tras la muerte de este (771) queda como único rey.
- P: ambicion 0.8, poder 0.82
- A: liderazgo 0.8, organizacion 0.78
- C: oportunidad 0.78, rivalidad_poder 0.72

### Corte B
- fecha: 0782-01-01
- hecho: Campañas contra los sajones; masacre de Verden y sumisión de los territorios del norte.
- P: conquista 0.84, autoridad 0.82
- A: audacia 0.8, determinacion 0.82
- C: terreno_hostil 0.78, hostilidad 0.75

### Corte C
- fecha: 0800-12-25
- hecho: Coronado emperador en Roma por el papa León III; une gran parte de Europa occidental bajo su corona.
- P: triunfo 0.84, logro_personal 0.84
- A: liderazgo 0.82, legitimidad_percibida 0.8
- C: reconocimiento 0.82, escalada_status 0.8

## Salida ciega obligatoria
- Suficiencia: (la fija el motor al correr)
- DATO: ver cortes
- INFERENCIA: (la fija el motor al correr)
- RUIDO: (la fija el motor al correr)
- H1 / H2 / Set / Escenario / Destino: ver SALIDA_CONGELADA.json
- Predictibilidad estructural previa: ver SALIDA_CONGELADA.json
- Condiciones de falsación: el desenlace sellado las decide al verificar
- Qué no puede saberse: la identidad del sujeto (sellada en custodia)
