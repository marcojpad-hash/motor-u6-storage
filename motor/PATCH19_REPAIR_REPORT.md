# PATCH19 — reparación de cableado y contrato terminal

## Cambios aplicados

1. **Búsqueda PRE-H:** `pre_h_analogical_search` ahora consume el puente conectado ya registrado en la entrada antes de la etapa predictora. Revalida el estado/origen del puente, el hash de la consulta ciega, la consulta enviada y las URLs de las fuentes. No ejecuta una búsqueda web nueva desde el runner Python.
2. **Filtro de identidad:** `laterales_unico_v1.filtro_id` acepta las tres fuentes del puente conectado cuando `caldero_search_sources` no está presente. Solo filtra fuentes; no decide H.
3. **Serialización de fuente:** `SearchSource.as_dict()` deja de serializar `metadata: null`. Si la fuente no entregó metadata, emite `metadata_estado=NO_ENTREGADA_POR_FUENTE` sin inventar contenido.
4. **Auditoría terminal:** el JSON final y el recibo se conservan sin `null` ni valores no finitos. Las ausencias que no se pueden derivar permanecen registradas con estado y motivo.

## Resultado ejecutado

- Caso: `GIORDANO_BRUNO_V15_3_PATCH09_20261010` (ocho cortes; entrada vectorial P/A/C; el contenido de corte no aporta `hecho`/`narracion`).
- H1: `arquetipo_el_sabio`.
- H2: `kwml_03_mago`.
- Búsqueda lateral del puente: 3 fuentes registradas; 70 tokens analógicos generados para PRE-H.
- Filtro de identidad: 3 fuentes procesadas; 3 conservadas; 0 descartadas por coincidencia de identidad.
- Búsqueda externa: resultado del puente conectado ya registrado; **no** se hizo una nueva búsqueda web en vivo desde el runner Python.
- Recibo: `COMPLETED`; 0 `null`; 0 valores no finitos en JSON final y recibo.
- Campos que no tienen valor de origen: 474, clasificados en `auditoria_terminal_valores`. No se rellenan con ceros ni con puntuaciones inventadas.
- Suite completa: 41 aprobadas, 1 advertencia preexistente (`PytestReturnNotNoneWarning` en `test_nuevos_guardianes_UNICO.py::test_falacias`).
- Pruebas de regresión del paquete compacto: 4 aprobadas.

## Integridad

- Engine canónico SHA-256: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` — conservado.
- `patterns_final_v14.json` SHA-256: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` — conservado; 244 patrones.
- H1/H2 finales coinciden con la corrida PATCH18.

## Ausencias que no se deben disfrazar de valores resueltos

La entrada es vectorial y no contiene texto narrativo por corte. Por ello, las funciones de personajes/Souriau, agentes y ciertos campos Polti/Caldero no pueden deducirse legítimamente de este input. También faltan en el paquete los módulos opcionales `autoevidencia_stores_011.py`, `filtro_relleno_013.py`, `sujetos_014.py`, `billar_circular_convergencia_v0_2.py`, `sidecar_area_tokens_v1.py`, `sidecar_sombrero_blanco_filtro_v1.py` y `guardian_entrada_autoevidencia_v1.py`; las búsquedas en la carpeta de trabajo, la biblioteca de archivos y Dropbox no localizaron sus fuentes. No se reconstruyeron a partir del nombre.
