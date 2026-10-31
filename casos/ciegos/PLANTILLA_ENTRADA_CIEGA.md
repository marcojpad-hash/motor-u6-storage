# Plantilla de entrada ciega — Z final

> **Solo datos anteriores o iguales a Z.** No incluir identidad, desenlace, fuentes posteriores ni claves selladas en este archivo.

## Metadatos de custodia
- case_id:
- sujeto_alias:
- fecha_freeze_Z:
- rango_temporal_observado:
- fuente(s) del material pre-Z:
- input_sha256:
- responsable del freeze:
- estado: PREPARADO / SELLADO / EJECUTADO / REVELADO

## Reglas
- La identidad y el desenlace permanecen fuera de este archivo.
- No buscar en internet ni intentar identificar al sujeto durante la corrida ciega.
- Separar DATO, INFERENCIA, HIPÓTESIS y RUIDO.
- No completar huecos con conocimiento posterior.
- No modificar el texto después del freeze.
- H1/H2, set, escenario, destino y condiciones de falsación se congelan antes de abrir la clave.
- Registrar explícitamente qué no puede saberse.

## Cortes hasta Z
### Corte A
- P:
- A:
- C:

### Corte B
- P:
- A:
- C:

### Corte C
- P:
- A:
- C:

### Corte D
- P:
- A:
- C:

### Corte E
- P:
- A:
- C:

## Salida ciega obligatoria
- Suficiencia:
- DATO:
- INFERENCIA:
- RUIDO:
- H1:
- H2:
- Set:
- Escenario principal:
- Destino:
- Predictibilidad estructural previa:
- Evidencia a favor:
- Evidencia en contra:
- Condiciones de falsación:
- Qué no puede saberse:

## Archivos separados después del freeze
- COMPROMISO.json con hashes de entrada, desenlace y destino.
- SALIDA_CONGELADA.json con H1/H2, set, escenario, destino y predicción estructural.
- RECIBO_EJECUCION.json con versión, hashes de motor/patrones, returncode y compuertas.
- DESENLACE_SELLADO.json en custodia separada; nunca en la carpeta visible durante la formulación.
