# U6_MOTOR_SOLO_20261020 — el motor solo

**Qué es:** el motor V15.3/U6 listo para correr por sí mismo. No trae laterales ni resultados de corridas.

**Contenido:**
- **Motor canónico** `motor/Engine_V5_CANONICO_SOLO.py`, huella `665c39a2…`.
- **244 patrones** `motor/patterns_final_v14.json`, huella `d827dcc3…`. Ninguno de los dos se tocó.
- **Motor de trabajo con el parche V0.4** `motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py`: publica los tableros exactos con los que se calculó R732. El diff está en `PARCHES/PATCH_SERIALIZACION_GEOMETRICA_V04.diff`.
- **Runner y herramientas:** `correr_estandar.py`, `scripts/`, `u5/`, `u6/`, `u7/`, `capa_llm/`, `inputs/`, `STORES_VACIO/`.
- **Manifiesto** `UNIFICACION_SHA256_MANIFEST.json`, regenerado para este paquete compacto. El runner debe decir **MATCH**.
- **Contratos de funcionamiento:** `CONTRATO_ENTRADA_LLM*.txt`.
- **Documentos de correcciones y parches:**
  - `README_MOTOR.md`, `INFORME_CIERRE_FINAL_*`, `PATCH*`, `T1_STINKBOX_PATCH.diff`, `RESTAURADO_LINEA_A/`
  - las notas de `audit/` y el paquete de parche de mortalidad (`audit/FAMILIA_LATERAL_MORTALIDAD_U6_V0_1/`)
  - los módulos de parche 011…021 están dentro de `motor/` y `capa_llm/`
- **Pruebas propias del motor:** `tests/`. Dos archivos de `results/` y las salidas de ablación de `audit/` vienen solo porque las pruebas los necesitan.

**Cómo usarlo:**
```
cd U6_UNIFICADO_20261020
python3 -m pytest -q -p no:cacheprovider          # 82 pasan, 2 se saltan
python3 correr_estandar.py inputs/THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2 SALIDA.json
sha256sum -c SHA256SUMS_MOTOR.txt
```

**Comprobado al sacarlo solo en una carpeta vacía:**
- Manifiesto: MATCH, con deriva 0.
- Temístocles: H1 `13_enemistad_de_parientes`, H2 `social_08_girard_mimesis_y_chivo_expiatorio`, R732 `[0.78355, 0.67027]`, idénticos a los del pack unificado.

**Lo que NO trae (va en U6_LATERALES_Y_ANEXOS_20261020.zip o se descartó):**
- laterales, resultados y corridas previas
- `runs/` y las cachés
- `STINKBOX_STORAGE/` no se distribuye dentro del ZIP: el runner lo resuelve en el almacenamiento persistente externo indicado por `STINKBOX_HOME` (por defecto, el registro persistente hermano).


**Persistencia StinkBox:** el runner importa automáticamente tokens tras las corridas estándar y T+1; el recibo indica el resultado. Mantén `STINKBOX_PERSISTENTE_20261020/` fuera de las actualizaciones del motor. Los 18 candidatos Black Mirror están en un registro documental separado y no se suman a las observaciones de corridas.

El reporte `tokens_vocabulario_externo.csv` separa términos capturados de resultados web; no deben interpretarse como arquetipos faltantes sin evidencia contextual.

El checkpoint primario de StinkBox ocurre antes de las subcorridas de cortes retenidos; el recibo registra `stinkbox_persistent_registry_primary_checkpoint` y la importación final.
