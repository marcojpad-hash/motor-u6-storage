# V0.18 — Arco Analógico Simbiótico

## Arquitectura trazada

`OBSERVACIÓN → ARCO PRE-H → ORIENTACIÓN LATERAL → H1/H2 → APUESTA → ARCO POST-H → VALIDACIÓN`

### 1. Arco pre-H
Se ejecuta **antes** de formular H. Su función es descubrimiento/orientación, no decisión.

Entrada ciega:
- tokens observados de P/A/C;
- tokens relacionales ya observados;
- familias/lentes laterales que hayan aparecido como estructura observable.

Exclusiones:
- identidad real del caso;
- nombre;
- fechas biográficas;
- hechos únicos identificadores;
- H1/H2;
- desenlace futuro.

Salida:
- casos/fuentes análogas;
- tokens nuevos;
- coactivaciones;
- relaciones;
- trayectorias descritas;
- contexto temporal/histórico;
- referencias de fuente.

La salida es **evidencia lateral de orientación**. Puede entrar en la superficie que formula H, pero no asigna pesos canónicos ni decide H.

### 2. Formulación de H
El predictor recibe el campo canónico + evidencia lateral pre-H.

La búsqueda no se considera una hipótesis y no puede convertirse directamente en un peso de `patterns_final_v14.json`.

### 3. Arco post-H
Una segunda lectura/consulta puede contrastar H contra los análogos encontrados. Su función es verificar convergencias, divergencias y relaciones nuevas.

No puede reescribir la H ya formulada.

## API

El motor conserva un contrato `SearchAdapter`. V0.18 añade `ExaSearchAdapter` como transporte concreto, con `EXA_API_KEY` y endpoint `/search`. Exa documenta su Search API y el endpoint `/search`; el adaptador del motor queda desacoplado del proveedor. 

## Persistencia
Los resultados deben conservarse como memoria lateral:
- query ciega exacta;
- fuentes crudas;
- fuentes descartadas por self-match;
- fuentes retenidas;
- tokens descubiertos;
- relaciones;
- fase (`PRE_H_ORIENTATION` / `POST_H_CONTRAST`);
- hash/proveniencia;
- motivo de activación.

No se incorporan automáticamente al canon 244.

## Regla de activación
El arco pre-H no depende de `caldero_search_sources` como condición arbitraria. Su activación deriva de que existe un campo observable susceptible de orientación analógica. Si no existe transporte API disponible, el resultado debe declarar `API_PENDING`; nunca fingir una búsqueda ejecutada.
