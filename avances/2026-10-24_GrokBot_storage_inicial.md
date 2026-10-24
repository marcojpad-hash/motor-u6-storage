# 2026-10-24 — Grok Bot

## Qué cambió
Creación del storage común con el motor U6 agnóstico (`U6_CONT_AGNOSTICO_20261024`) y estas mejoras ya presentes en esa copia:
- **Caldero agnóstico**: búsqueda sin LLM ni claves obligatorias (`motor/motor/sidecar_caldero_busqueda_arquetipos.py`, spec `motor/motor/SPEC_BUSCADOR_AGNOSTICO.md`).
- **Pausa y reanudación de TORTUGAS corregidas** (ver `motor/INFORME_IMPLEMENTACION_CONTINUIDAD_TORTUGAS_20261024.md`).
- **Tabla de mortalidad declarada `NO_APLICA_SIN_TABLA`** (`motor/motor/matriz_mortalidad_z90_v0_2.py`): no hay datos reales y no alimenta H.
- **Laterales nuevas**: teoría del color y filogenia de mezcla, en `motor/laterales/`.

## Antes → ahora
- `motor/laterales/teoria_color/teoria_color.py` — antes: no existía en el motor → ahora: lateral añadida. sha256 después `77ef05e16e4d607fa27403d60262d509978888a099ee9e953fe2b4398c95d42e`
- `motor/laterales/teoria_color/equivalencias.py` — antes: no existía → ahora: añadida. sha256 después `5d5ac40e4b2c9fff407f7ecbe891ba6b32b34dc6c87e60c991f5e177fd04c0e1`
- `motor/laterales/teoria_color/SPEC.md` — sha256 `00813812a3ae44619b1bd956b8bf7d6e7a312aef835709f7792fa28eef7bec67`; `EQUIVALENCIAS.md` — sha256 `d09b630d76633215ea805f986241c6ca42fadcd70e177a3fe00e8696cab7b37f`
- `motor/laterales/filogenia_mezcla/filogenia_mezcla.py` — antes: no existía → ahora: añadida. sha256 después `d6026c0b99d1264609cbc11eb643d499e45065483afd9adefdb16c6b290a9928`
- `scripts/sincronizar_storage.py` — nuevo. sha256 `4d673e7df24bad9d612c37704b0ac2f8f6ca4aae150110821e9444074c443162`
- Los cambios internos de Caldero/TORTUGAS/mortalidad no tienen aquí diff "antes" porque es la versión inicial del storage; su detalle está en los informes de `motor/`.

## Hashes canónicos verificados
- `Engine_V5_CANONICO_SOLO.py`: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` — OK
- `patterns_final_v14.json`: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` — OK

## Pruebas
112 passed, 2 skipped (los 2 saltos: código 0.5.0 original y fixture Bezos ausentes; no se inventaron). Cifra reportada por la sesión que hizo los cambios; no se volvió a correr la suite al crear el storage.

## Datos exportados
- StinkBox: 848 tokens únicos de 407 artefactos (ver `stinkbox/MANIFIESTO_EXPORT.json`).
- Casos: `HISTORIAL_HASHES.json` (1498 hashes), `HASHES_ENTRADAS.json`, 9 resúmenes en `casos/resultados/resultados.jsonl`.
