# Contrato de carpetas — motor-u6-storage

## Regla de lectura (obligatoria)
- **Prohibido depender de ZIP/zipball.** Ningún modelo debe pedir ni necesitar descargar el ZIP.
- Leer archivo por archivo con la API de GitHub o el conector (`contents/<ruta>`, raw), o `git clone`.
- Orden sugerido: este archivo → `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` → último informe en `informes/` → `avances/` reciente.

## Para qué es cada carpeta
- `motor/` — Motor U6 (código, contratos, candados, laterales). **Engine y catálogo 244 no se tocan.** Leer `motor/REGLAS.md`.
- `casos/` — Hashes de casos, plantilla, calibración, fábrica y resúmenes de resultados. El resumen de una línea por corrida va en `resultados/resultados.jsonl`; la corrida completa va en `motor/runs/<LOTE>_<FECHA>/` para el historial (ver `CONTRATO_GUARDAR_CORRIDAS.md`).
- `stinkbox/` — Tokens StinkBox deduplicados (`tokens.jsonl`), procedencia y reportes de brechas.
- `avances/` — Bitácora técnica por cambio (antes → después, hashes, pruebas). Una entrada por commit relevante.
- `informes/` — **Resúmenes para Mj y modelos** en español llano, uno por sesión: `AAAA-MM-DD_tema.md`. Empezar aquí para saber "dónde vamos".
- `docs/` — Documentos estables de método (brújula, playbook CEB investigar/resolver).
- `scripts/` — Utilidades (`sincronizar_storage.py` antes/después de cada corrida).
- `tests/` — Pruebas del repo (smoke, compuertas).
- Raíz — `README.md`, este contrato, `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md`.

## Reglas generales
- Nada se borra ni sobrescribe en silencio; cambios = versiones nuevas + entrada en `avances/`.
- Sin binarios ni ZIPs en el repo.
