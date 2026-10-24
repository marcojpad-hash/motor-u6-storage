# Reglas de `motor/`

1. **Nunca modificar** `motor/Engine_V5_CANONICO_SOLO.py` (sha256 `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`) ni `motor/patterns_final_v14.json` (sha256 `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`). `scripts/sincronizar_storage.py antes` los verifica en cada corrida.
2. Todo lo nuevo es **lateral**: archivo o versión nueva (por ejemplo en `laterales/`), nunca reemplazo silencioso.
3. Cada cambio va en un **commit nuevo con descripción** y una **entrada en `avances/`** (antes → después, sha antes/después, pruebas).
4. Solo se suben versiones modificadas; nada de corridas, salidas, binarios ni `_vendor_buscador`.
5. **Ningún número mayor a 1**; las probabilidades se recortan a **5–95 %**.
6. La búsqueda del Caldero sigue **agnóstica**: sin LLM y sin claves obligatorias. Si faltan las bibliotecas empacadas: `pip install ddgs primp lxml click` (ver `motor/SPEC_BUSCADOR_AGNOSTICO.md`).
7. **El motor decide** con la evidencia acumulada; **el LLM no decide**.
8. Tras cambiar código de `motor/`, correr la suite y regenerar manifiestos (`python3 -B scripts/regenerar_manifestos_trabajo.py`).
