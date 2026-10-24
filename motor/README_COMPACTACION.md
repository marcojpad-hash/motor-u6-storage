# U6 compactado — 2026-10-20

Paquete operativo separado de los resultados históricos. El ZIP motor contiene código, catálogo, entradas y pruebas; el ZIP laterales contiene código lateral, fuentes de corpus, pruebas y fixtures mínimos. Ambos comparten la raíz `U6_UNIFICADO_20261020` y se extraen en el mismo directorio para habilitar pruebas integradas.

Los resultados completos y ledgers grandes no se incluyen en las entregas operativas. La evolución se documenta en `HISTORIAL_EVOLUCION.md` y `REGISTRO_CORRIDAS.md`; hashes en `MANIFIESTO_COMPACTO_SHA256.json`. Los ZIP originales del 20-10-2026 no se modifican.

Instalación lateral: `pip install -r laterales_unificado/requirements_laterales.txt`. Pruebas: `python3 -m pytest -q -p no:cacheprovider`.


## StinkBox persistente y calibración

`correr_estandar.py` resuelve `STINKBOX_HOME` fuera del ZIP y, al finalizar cada corrida estándar o T+1, importa automáticamente el almacén de tokens y los artefactos de descubrimiento. El recibo incluye `stinkbox_persistent_registry_ingest`. Por defecto busca el registro persistente hermano `STINKBOX_PERSISTENTE_20261020`; se puede fijar otra ruta mediante `STINKBOX_HOME`. No extraigas la entrega persistente sobre una instalación que ya acumula datos.

Los 18 conceptos de Black Mirror/ficción de IA están en `STINKBOX_BLACK_MIRROR_CANDIDATOS.json` y se registran aparte como candidatos documentales; no son tokens observados en corridas ni están integrados al motor canónico.

Se eliminó la equivalencia por subcadena para tokens fuera de catálogo: solo una normalización exacta puede proponer equivalencia automática. El token que no tenga equivalencia exacta queda pendiente de revisión.

Pruebas tras la integración: 82 aprobadas, 2 omitidas por falta de líneas base históricas. Una corrida de humo de un corte confirmó que el runner terminó y registró 7 eventos; la búsqueda externa obligatoria falló en esa prueba, por lo que no cuenta como corrida válida para calibración.

El registro distingue `tokens_nuevos.csv`, `tokens_fuera_catalogo.csv` y `tokens_vocabulario_externo.csv`: términos nuevos procedentes de búsquedas externas no se presentan como familias faltantes.

El runner guarda un checkpoint de StinkBox inmediatamente después de la corrida primaria, antes de los análisis retenidos y ledgers, y vuelve a importar al final. El recibo separa ambos estados.
