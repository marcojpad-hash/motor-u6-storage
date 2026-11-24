# Contrato operativo — rama vigente del motor U6

Vigente desde: 2026-11-11 01:55 CST. Ordena: Mj. Lo deja: Puta 3.
Alineado con el cableado real el 2026-11-19 (base `alterno/cameo-pesos` e60a29f, lote #16–#34 completo y fusionado).

## Regla
1. **Rama de trabajo vigente: `alterno/cameo-pesos`.** Todo trabajo nuevo del motor (parches, corridas, pruebas, inputs humanos, órdenes del bus) sale de esta rama o de ramas hijas de ella (p. ej. `alterno/inputs-humanos`). Los PR van contra `alterno/cameo-pesos`, no contra `main`, hasta que Mj diga otra cosa.
2. **Modelo anterior cancelado.** El motor de `main` (estado previo a 2026-11-11, CAMEO sin `peso_equivalente`) queda **SOLO_CONSULTA**: historial para saber qué no hacer o qué se pasó. No se borra, no se reescriben sus valores ni hashes, y no se usa como base de calibración ni como comparación directa de puntaje. Sus corridas (p. ej. `casos/resultados/resultados.jsonl` hasta 2026-11-10) son consulta.
3. **Lo que NO cambia:** Engine `motor/Engine_V5_CANONICO_SOLO.py` (sha256 665c39a2…) y catálogo 244 `motor/patterns_final_v14.json` (sha256 d827dcc3…) siguen siendo canónicos en ambas ramas (`motor/ACTIVE_ENGINE_SELECTION.json`). No se tocan.
4. **Escala:** todo peso, componente y puntaje publicado vive en 0,01–0,999 (escala del Engine). Sumas crudas fuera de rango (`rank_fusion`, `selected_peso_efectivo_sum`) se reportan como FALLO_ESCALA hasta normalizarlas; ver orden BUS agente-cero-costo #47.
5. **Al iniciar sesión cualquier modelo:** `git checkout alterno/cameo-pesos`, confirmar commit y hashes del Engine/244 en el recibo. Trabajo hecho sobre `main` después de esta fecha no cuenta como hecho.
6. `main` no se fusiona con la rama sin decisión de Mj.

## 7. Módulos cableados (lote #16–#34, base e60a29f)

Los 18 módulos siguientes están cableados en la ruta real de corrida y probados con `motor/tests/test_cableado_*.py` (18 archivos, uno por módulo). Un contrato dice QUÉ HACE cada componente; los módulos no "quieren" nada, hacen lo que hacen.

**Entrada**
- **Sombrero blanco v2** (`motor/capa_llm/sombrero_blanco_filtro_v2.py`): filtro de admisión en la puerta de entrada. Puerta en `motor/correr_estandar.py` (`SOMBRERO_BLANCO=activo` por defecto) y red de seguridad en `run()` de UNICO. Bypass: `SOMBRERO_BLANCO=off` (apagado visible).
- **Autoevidencia** (`motor/motor/guardian_entrada_autoevidencia_v1.py`): marca tokens de entrada P/A/C que son nombres de familia del catálogo (circularidad entrada→salida). Solo marca; no quita tokens. Bypass: `LAT_GUARDIAN_ENTRADA_AUTOEVIDENCIA=0` (apagado visible `APAGADA_POR_FLAG`).
- **Filtro 017** (`motor/capa_llm/filtro_entrada_dirigida_017.py`): marca datos dirigidos en el payload. UNICO lo corre en modo `traza` por defecto (analiza sin modificar el caso).
- **Z90** (`_validate_case` en `run()` de UNICO): validador duro de entrada; rechaza la corrida cuando un corte trae `date` posterior a `z90_date` (`ValueError("POST_Z90_EN_INPUT: <id>")`). **Sin bypass, por diseño** (es un validador duro, como `INPUT_INVALIDO`).

**Lógica post-predictor** (orquestador `motor/motor/guardianes_control_v1.py`, `correr_guardianes()`)
- **Copi**, **Beristáin**, **Pregunta detrás v2**, **Pregunta dirigida + post hoc/falacias**, **Polaridad causal**, **Sherlock/rigor**, **Décimo hombre/latencia**, **Hombre de acero**. Cada uno corre sobre copias, marca (`LIMPIO | MARCA | NO_RESUELTO | LATENTE | ERROR`) y no escribe H. Cada uno tiene bypass visible: con su variable en `off` el bloque queda marcado `NO_CONFIGURADO` en el recibo (nunca desaparece en silencio). Variables: `COPI_GUARDIAN`, `BERISTAIN_GUARDIAN`, `PREGUNTA_DETRAS_GUARDIAN`, `PREGUNTA_DIRIGIDA_GUARDIAN`, `POLARIDAD_GUARDIAN`, `SHERLOCK_GUARDIAN`, `DECIMO_HOMBRE_GUARDIAN`, `ACERO_GUARDIAN`.
- **Modo estricto** (`modo_estricto_v1.py`): cierre estricto (C0–C4); retiene el estado de cierre, no toca H. Bypass: `MODO_ESTRICTO=0` (apagado visible `NO_CONFIGURADO`).
- **Esteroides** (`decimo_hombre_esteroides_mayeutica_v1.py`): contrafactuales y mayéutica después del cierre; auditoría, no toca H. Bypass: `ESTEROIDES_GUARDIAN=off` (apagado visible `NO_CONFIGURADO`).
- **Verificador de consistencia** (`plugin_verificador_consistencia_adversarial.py`): invariantes de contrato en la corrida real; solo marca violaciones. Bypass: `VERIFICADOR_CONSISTENCIA=off` (apagado visible `NO_CONFIGURADO`).

**Salida**
- **respuesta_humana** (`motor/motor/respuesta_humana_v1.py`): responde LA pregunta en prosa desde el RESULT sellado, con evidencia citada en las palabras de la persona. Contrato: `motor/CONTRATO_SALIDA_LLM.txt`. Bypass: `RESPUESTA_HUMANA=0` (apagado visible `APAGADA_POR_FLAG`).
- **Traductor de salida** (`motor/motor/lateral_traduccion_salida_v1.py` v2.8): lectura en prosa del RESULT sellado (descripción de estados), no una respuesta. Corre en `motor/correr_estandar.py` tras sellar el RESULT, junto a `respuesta_humana`; la salida va en `result["traduccion_salida"]`. Necesita el RESULT sellado y la `entrega` (caminos/luces del Caldero); no decide H ni reescribe el RESULT. Bypass: `TRADUCCION_SALIDA=0` (apagado visible `APAGADA_POR_FLAG`). Si falla, queda `FALLO_TRADUCCION_SALIDA` visible y la corrida sigue. Prueba: `motor/tests/test_cableado_traduccion_salida.py` (5 tests). Contrato: `motor/TRADUCCION_SALIDA_V1.md`.

**Veredicto honesto**
- **Sombrero absorbido** (`_protocol_quality` en UNICO): el veredicto de protocolo se deriva de comprobaciones reales. `status` es `PASS` solo sin violaciones (si no, `FAIL`); `sombrero_blanco` es `ENFORCED` solo sin violaciones (si no, `VIOLATED`); las violaciones quedan listadas en `violaciones` (`SIN_PREGUNTA`, `RUIDO_PROTOCOLO_EN_PREGUNTA`, `CAMPOS_PROBABILISTICOS_EN_ENTRADA`, `SIN_CORTES`). **Sin bypass, por diseño** (el contrato del veredicto ES la honestidad; el veredicto es REPORTE, no puerta: un FAIL no bloquea la corrida ni reescribe H).

**Regla de lenguaje (Marco):** en los contratos, un módulo no "quiere", no "se niega" ni "no quiere hacer" algo. El contrato dice QUÉ HACE el componente (qué vigila, qué devuelve, si bloquea o marca, dónde se llama) y qué NO HACE (qué no toca, qué no decide). Si un componente no hace algo, se dice así, en presente y con evidencia, no como voluntad.

**Pendientes (no cableados todavía, no son adorno):** control de flujo (`control_flujo_soluciones.py`, no está en el tubo de `run()` de UNICO), candado de plugins (solo corre vía `correr_estandar.py`, no en `run()` solo), `verificar_salida_llm` (cero llamadores). Ver `docs/MAPA_GUARDIANES.md` §5–§6.

## Evidencia de por qué
- `informes/2026-11-11_cameo-alterno.md` (rama): Napoleón con CAMEO.
- `casos/corridas_alterno/CHURCHILL_CAMEO_ALTERNO/` (rama, commit 428ceee): Churchill, misma entrada que 2026-10-24.

 
## Addendum 2026-11-22 — guardián Z90 en runner estándar

Además de la validación temporal interna de UNICO, motor/correr_estandar.py ejecuta _guardian_z90(case) después de normalizar/filtros y antes de llamar al motor. Se activa cuando la entrada declara gate_z, z_trabajo + modo_z o se establece FABRICA_GATE_Z90=1. La gate motor/calibracion/gate_z90.py valida Z90 histórico calculado desde nacimiento/muerte, z_trabajo=z90_date, ventanas acumulativas desde nacimiento, cierres crecientes, último corte en Z90 y evidencia temporal. Si hay errores, el runner bloquea antes del motor y escribe RESULT + recibo con BLOQUEADO_GUARDIAN_Z90 (exit 8); si la disciplina no está declarada, deja NO_CONFIGURADO visible y conserva la ruta previa.

La integración está en alterno/cameo-pesos (runner commit bb6a31d9a77d43ac106f77927f9347b8bbadee7d). Las siete pruebas específicas se ejecutaron junto con el contrato existente: Actions run [#45002771468](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45002771468), **60 passed**, job runner-contract SUCCESS. Esta gate no demuestra custodia independiente ni convierte F007 en cohorte válida. La ejecución del motor real sigue separada de la prueba de bloqueo y no se realizó en esta actualización.


## Addendum 2026-11-24 — lateral de contexto enunciativo

Se incorpora el guardián observacional `CONTEXTO_ENUNCIATIVO`, implementado en `motor/motor/lateral_contexto_enunciativo_v1.py` y llamado por `correr_guardianes()` en `guardianes_control_v1.py` después de Beristáin. Conserva los candados de los guardianes: no decide H, no escribe H ni patterns y no reordena candidatos. Su salida se adjunta como contexto trazable a controles hermanos, sin alterar sus banderas. Contrato: `motor/LATERAL_CONTEXTO_ENUNCIATIVO_V1.md`. Pruebas de integración: `motor/tests/test_runner_json_contract.py` (CTX-01 y CTX-02).
