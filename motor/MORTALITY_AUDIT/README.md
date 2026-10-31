# Mortality audit — source register and schema

## Estado real

No existe aún una matriz estadística cargada. El paquete de preparación del 23-octubre contiene solo un registro de fuentes y una plantilla vacía. El sidecar está conectado al runner, pero no alimenta H1/H2, no decide hipótesis y no altera el motor ni los patrones canónicos.

## Contrato de datos

El esquema activo es MORTALITY_STATISTICS_SCHEMA_V1.json, versión 1.1. La plantilla normalizada es mortality_statistics_template.csv. La plantilla de preparación externa tiene otro esquema, con indicator/value y source_file_sha256; para convertirla se usa motor/scripts/normalizar_mortalidad_preparacion.py.

Tipos permitidos:
- deaths_per_100000_exposure: requiere deaths y exposure; la tasa se calcula explícitamente.
- q_x: requiere rate_value en [0,1].
- m_x: requiere rate_value >= 0.
- life_table_mx_qx: requiere mx y qx; ambos se conservan sin convertirlos.

No convertir q_x en m_x ni al revés. No confundir valores de una cohorte hipotética de tabla de vida con muertes o exposición observadas.

## Fuente inicial recomendada

UN World Population Prospects 2024, tabla de vida abreviada, variante Medium, 1950-2023. Es una fuente oficial pública y su licencia es CC BY 3.0 IGO. El archivo incluye mx, qx, dx, Lx y ex. No requiere Google API key ni token privado.

La fuente INED Bonneuil 1806-1906 es especialmente pertinente para mortalidad histórica francesa, pero data.gouv.fr no especifica licencia de reutilización; no se incorpora hasta aclarar las condiciones. CONAPO ofrece defunciones estimadas/proyectadas por edad y sexo para México; verificar denominadores y separar estimaciones de proyecciones.

## Procedimiento

1. Descargar el archivo oficial y conservarlo en el espacio temporal del workflow.
2. Calcular SHA-256 del archivo original.
3. Normalizar dimensiones y unidades sin inventar valores.
4. Validar el esquema y la integridad.
5. Generar la matriz compacta y su manifiesto de procedencia.
6. Ejecutar pruebas del sidecar.
7. Mantener feeds_H=false y can_decide_H=false hasta una validación independiente explícita.

## Google tokens

La solicitud de tokens Google del paquete antiguo no es necesaria para descargar WPP 2024 ni para consultar los catálogos públicos citados. No solicitar ni almacenar claves de Google para esta ruta.

## Archivo de tabla y carga en streaming

La ruta canónica para una tabla grande es MORTALITY_AUDIT/mortality_statistics.jsonl.gz. El sidecar la procesa línea por línea y agrega por año/época sin cargar el conjunto completo en memoria. Para tablas pequeñas se mantiene compatibilidad con mortality_statistics.json. El formato JSONL conserva una fila por observación; cada línea debe cumplir el esquema 1.1.
