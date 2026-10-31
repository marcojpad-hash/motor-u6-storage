# README_MOTOR — Motor V15.3 UNICO, estado U6 (+ herramienta U7)
Generado 2026-10-13 desde `TRABAJO/packs/U6_correcciones` (solo lectura). Snapshot histórico; estado operativo y autoridad de versiones actualizados al 2026-10-31 en [MAPA_VERSIONES_Y_AUTORIDAD.md](../docs/MAPA_VERSIONES_Y_AUTORIDAD.md) y [auditoría](../informes/2026-10-31_AUDITORIA_CONTINUIDAD_Y_ESTADO.md).

> Engine V5 es el componente canónico protegido; V15.3 es la capa de runner integrado. No son nombres intercambiables. El hash `48333cd11b9234f1` del runner no sustituye el SHA-256 `665c39a2...` del Engine V5.

## Integridad
- `motor/Engine_V5_CANONICO_SOLO.py` sha256 `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` (= candado 665c39a2, coincide con UNIFICACION_SHA256_MANIFEST.json)
- `motor/patterns_final_v14.json` sha256 `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` (= d827dcc3, 244 patrones, coincide con manifiesto)

## Punto de entrada
```
python3 correr_estandar.py cuts.json NOMBRE [salida.json]      # corrida estándar
python3 correr_estandar.py RESULT.json --t1 futuro.json [out]  # contraste T+1
python3 u5/u5_instrumentar.py INPUT.json TAG RESULT_out.json   # corrida instrumentada (harness U5/U6, genera RECIBOs)
python3 u7/confianza_apuesta_u7.py ...                         # confianza de apuesta U7 sobre RESULTs
```
Harness offline de referencia (U6): `u6/run_u6.sh CASE INPUT REP [off|mock]` — ojo: tiene rutas absolutas a `/workspace/UNIFICADO_20261011/TRABAJO` y `/workspace/PATCH015_WORK/STORES_VACIO`; en otra máquina use el equivalente: copia fresca, stores vacíos (`STORES_VACIO/`), `SEARCH_PROVIDER=offline`, sin EXA/OPENAI keys, `CONSULTA_CASE_KEY=<caso>`. Exit 3 en offline es lo esperado (la búsqueda externa está apagada).

## Variables de entorno encontradas en el código
- `BRAVE_SEARCH_API_KEY`
- `CEB_ROOT`
- `CONSOLIDADO_OFF`
- `CONSULTA_CASE_KEY`
- `CONSULTA_DIRIGIDA`
- `CONSULTA_FIXTURE`
- `EXA_API_KEY`
- `FAMILIAS_TOKENS`
- `LLM_API_KEY`
- `MODO_ESTRICTO`
- `MOTOR_N_PATRONES_ESPERADO`
- `MOTOR_PATTERNS_PATH`
- `OPENAI_API_KEY`
- `OPENAI_SEARCH_MODEL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_SEARCH_MODEL`
- `OPENROUTER_WEB_SEARCH_ENGINE`
- `PYTHONHASHSEED`
- `SEARCH_PROVIDER`
- `SOURIAU_FUNCIONES_016`
- `TAVILY_API_KEY`
- `U6_DESEMPATE_CUELLO`

Claves: `SEARCH_PROVIDER` (offline | exa | openai | openrouter | brave | tavily según módulo; offline = sin web), `EXA_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `BRAVE_SEARCH_API_KEY`, `TAVILY_API_KEY`, `LLM_API_KEY`; `CONSULTA_DIRIGIDA=mock` + `CONSULTA_FIXTURE=capa_llm/FIXTURE_MOCK_CONSULTA_20261011.json` para la capa LLM simulada; `MODO_ESTRICTO`; `PYTHONHASHSEED` para reproducibilidad.

## Parches aplicados e interruptores
- PATCH_STACK 001–016 (docs en SPECS_CONTRATOS.zip): 001_sombrero_blanco_cableado.md, 002_stinkbox_portable_biblioteca.md, 003_ricci_P_top5_y_negativo_schema.md, 004_trazabilidad_temporal_PAC_y_NO_APARECIDO_AUN.md, 005_vecinos_prefijo_gate_real.md, 006_caldero_II_cuadrantes_superada_escaleta.md, 007_souriau_v1_4_alimentado_por_funciones_derivadas.md, 008_guardian_entrada_autoevidencia.md, 009_marco_7783_geometria_y_210141_marcaje.md, 00X_modo_estricto_diagnostico_sin_parche.md, 00_README.md, 011_AUTOEVIDENCIA_STORES.md, 012_SOPORTE_VECINOS_MIN2.md, 013_FILTRO_RELLENO_VECINOS.md, 014_SUJETO_UNICO_SOPORTE.md, 015_AGNOSTICO_NOMBRES_Y_ANOS.md, 016_CIERRE_FINAL_Y_PERSONAJES.md
- Parches 017–021 (filtro entrada dirigida 017, consulta dirigida U1, cierre 020 "motor manda escala/mezcla", predictibilidad/traducción contextual 021) y PATCH19 (reparación cableado, candado engine).
- Etapas U0 (base unificada) → U1 (consulta dirigida) → U2 (cierre 020) → U3 (predictibilidad 021) → U4 (todos los tokens y movimiento de fondo) → U5 (anomalías, instrumentación y recibos) → U6 (correcciones). U7 = herramienta de confianza de apuesta (fuera del motor).
- Interruptores U6 (ablación): `CONSOLIDADO_OFF=picos_score_u6,frye_normalizado_u6` (apaga score de picos/mesetas y la normalización de frye /2.17); `U6_DESEMPATE_CUELLO=posicion` (vuelve al desempate por posición de U5). Con todo apagado se reproduce el H1 de U5.
- Otros: `SOURIAU_FUNCIONES_016` (funciones Souriau del parche 016), `FAMILIAS_TOKENS`, `MOTOR_PATTERNS_PATH`, `MOTOR_N_PATRONES_ESPERADO`, `CEB_ROOT`.
- Parches U6 reproducibles con `u6/parche_u6_unico.py` y `u6/parche_u6_nativo.py`.

## Stores
Se entregan VACÍOS: `motor/stinkbox_vault/` vacío, `motor/stinkbox_tokens_descubiertos.json` plantilla, `motor/vecinos_caldero/` solo con `neighbor_store.py`, `STINKBOX_STORAGE/vecinos_caldero/` vacío. Plantilla extra en `STORES_VACIO/`. Los stores poblados están en CASOS_HISTORIAL.

## Excluido
`motor/_ARCHIVADO_U6`, `__pycache__`, `runs/`, `results/`, stores poblados, `motor/*.diff`, logs, reportes/specs (ver SPECS_CONTRATOS). Algunos `scripts/` (ensamblar_piezas, orquestador_unico, analizar_unico, congelar_base, construir_equivalencias_ORIGINAL, comparar_con_registrado_unico) tienen rutas absolutas a carpetas históricas de /workspace: son de mantenimiento, no del camino de ejecución.

## Manifiesto SHA256 (190 archivos)
| archivo | sha256 | bytes |
|---|---|---|
| correr_estandar.py | d66a0169f634d4571eecd467aa413ab5e94f601809288062fb54a3794e103d13 | 20399 |
| ACTIVE_ENGINE_SELECTION.json | 8980e79507f6392955b10e9e662eef4c91870c0dd4519fed52db2e5a5ed5e43f | 930 |
| CANDADO_ENGINE.json | 40066336b6a7c836563cd61297796b1f9f01a640159c99b28f9ac6902de04ea0 | 543 |
| HISTORICAL_PREDICTIVE_REFERENCE.json | 6a33195d011d6b06bd55b4eee86952dee2c966c22e70a64bdc67ff03025a0423 | 853 |
| UNIFICACION_MANIFEST.json | 10ed555638ab39b781de64f8bc66fe2986bf73b24482024aa250be526d8ccc2a | 3131 |
| UNIFICACION_SHA256_MANIFEST.json | 3316a8209ed0365474700a2822ed57d335e82c51361f7c54d872978e95da2a7c | 37065 |
| motor/CONSISTENCY_ADVERSARIAL_AUDIT.json | 0c4a6c864746bab053fb4a42ced3536b3b0658160076e7bc27b5e44c99563eb6 | 394 |
| motor/CONSISTENCY_ADVERSARIAL_LLM_PACKET.json | fe87b7456086a7d4ae83dc4c901deb1d12a8e0b1c01d2078b9bdbaa209e5adf9 | 5752 |
| motor/CONSISTENCY_AUTONOMA_LLM_PACKET.json | 4a6755214c0b8063737c66fd98461c4834138755d1c5fae0511279ba98dbd536 | 1231 |
| motor/Corpus_Final_Unificado_17_Formulas.txt | 8f10b0072ea28436c53c04531696496fc5545a4185808395e7f9f22589b64446 | 12047 |
| motor/Engine_V5_CANONICO_SOLO.py | 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082 | 30507 |
| motor/INVENTARIO_COMPONENTES_UNICO.json | 8328b3e40dd184fe6b9b757579b24f869e056b819ce08a9a109d23693d310874 | 2477 |
| motor/MATRIZ_EQUIVALENCIAS_ESCALA.json | 66f83e77409c404a9f00b2250a81b0bfffa2fbb94577abed4792ebcf4e9368d7 | 105190 |
| motor/MOTOR_V15_3_NATIVO_V0_9.py | cfbb3b0974a7e241dc4c20cb5353d17cc610cedfd1621ef4d0cd46fdf135c4b3 | 594 |
| motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py | ad400183b225cfdc8de9ef63c5cab58815ac0cfde545a20a7e0fe15c65a4a57e | 36331 |
| motor/MOTOR_V15_3_UNICO_20260927.py | 9431d1a8d152dc0162518f57db3782c73769f2eae57fd9e513f3eb15acd894be | 292445 |
| motor/PROTOCOLO_METACOGNICION_V01.md | 02843569f6394e681c7cf82d73d1241bc3a0831a978dbcd8b425e1b5bc715cfa | 1593 |
| motor/PUENTE_244_FAMILIAS.json | 3cc9fd253d1d669f81663839ed46d47429db7467ecaadd49b6b41303f46adfbf | 193162 |
| motor/analogos_fase_v1.py | d70be0fd85c4627c014b76dda49799837cc92f56465b3ff1f9088489d229ee8f | 1019 |
| motor/arcos_emocionales_laterales.json | 396393e5d2093b534b0ba83b0aa5cbb2b8cb02ac97d019ad6422c7d4471adcb2 | 1061 |
| motor/autoevidencia_stores_011.py | 8513d64f4587acd55d5f29ff24d61c3ce20c14d19550b8a87ee8c9a07e0449ee | 12279 |
| motor/billar_circular_convergencia_v0_1.py | 940dc874fc0336a931cb8b3be4bce4c865b6549f84e859bafac17e19d0b65f68 | 8272 |
| motor/billar_circular_convergencia_v0_2.py | 9c501ac312260282507f551b4f8e75c5ad314ef76dcb05b3da35f2027c8d8b4f | 4821 |
| motor/caldero_II_runner_generico.py | 14c0a8130f3951c1fd0e8139bbba8d7a572b4ddebe1e1083767da2b7a4c8f9f7 | 2745 |
| motor/caldero_zoomout_acero_v0_1.py | aef329444ca2bac0c9e0d7d2c56e3a7cdfa959a8ec855008a3940cadb2e66ed4 | 5570 |
| motor/calibracion_predictiva_v1.py | e399c4845b7070dd3ff52032b59ba9d4d15b599218a8d33f1b595136429e6640 | 3980 |
| motor/cameo_codebook_lateral_v1.json | d575473d4ea4a81f71ab37b36da9a342e623e99c18bae7fd99eeee8bc2162057 | 11554 |
| motor/cameo_to_244_adapter_v1.py | 1e1ac4759692c897f986171cf3b6e9b21708858d45f1fdb9d317f8a4e2c94947 | 4038 |
| motor/cameo_to_703_lateral_v1.json | 7c15ddc7861e598c72bd1b01c785b447bd43a74c76a46b39f84dfac036a98376 | 4550 |
| motor/cameo_to_703_lateral_v1.py | 1f9589d1bc16fa230a953c709a6bcdc2a9cc0b5709e9315eef7188daef83fb8b | 3314 |
| motor/candado_plugins.py | 2a66950516dfa751b0d1a4e4162d80046ba59187b7041dffd6831cff31842de1 | 6423 |
| motor/capa_integracion_semantica_v1_2.py | 4de3ddef696e8686a8ff272ca02c6d9e84cd8b9c540221d63c6f46bd213a6f2c | 9833 |
| motor/capa_interrelacion_tokens.py | c7491981db4e46d23ec29b7df82d326dc3be9a445321d83f2ab41e7e4a0bfe05 | 6066 |
| motor/catalogo_capa2_familias_semilla.json | a7142b3eb59a2d3151decc734b56d331ca8abb259e412267cde08feeaf080f4e | 14657 |
| motor/ceb_runtime_v0_6_flow.py | 05f86a0d7109e329c485a94ae22f4b8846e22879ba1dcb97bd43e9dc8d8f755b | 27884 |
| motor/coactivacion_escalas.py | f316ebb07bf84d8169c69ecd076392af73c5aa5c8c9426e34c2f475ee4b822c5 | 10318 |
| motor/control_flujo_soluciones.py | 058e834825495f153b53afffbdca99ce3ca089a6aa37dc296eaeb8106b9427ea | 11121 |
| motor/control_latencia_decimo_hombre.py | ff03241d42d7770c2af83de60eeb41db6bdbba78a0511f7470ca65b766220345 | 10038 |
| motor/decimo_hombre_esteroides_mayeutica_v1.py | c000284559cb084e83dc11ab777431319e41401c8044f07105abf84f9763ed2f | 22756 |
| motor/estabilidad_vectorial_h.py | 60574cb3d1a0431461e7550547c180b30b5e643e41bebb7fbb90b073aa23de04 | 4120 |
| motor/estado_latencia_decimo_hombre.json | 6185e900848fdccb0d7588f145c81ef8c8763234e8ee008ad058f9b25630efc4 | 6515 |
| motor/estado_latencia_v15_3_nativo.json | 906cef79c8475115115c0ce30a44d772bf330347c121e07a4078f0d6682cc67f | 2616 |
| motor/filtro_identidad_zoom_out_zoom_in.py | 1d00fb10f02f0e0f68863654d67d5d368a66c3e3b7b1ec4accb319e1430f48be | 17266 |
| motor/filtro_relleno_013.py | a69aa7bc1cf0988dcc22f26adda332f0f029ad92926fdcb55dfffee91e0287be | 6234 |
| motor/formular_h_apuesta.py | 0319a42b8ef011ab09f48dfc9a973a553f5e7280d1266881998c61444c97ff27 | 7764 |
| motor/guardian_acero_rival_v1.py | 314d19f5d477d4be370d1c40e7ee06ce391383c2eef26139e42a52e43a007f79 | 6623 |
| motor/guardian_entrada_autoevidencia_v1.py | 42dd6c1c08a8a35287c8f903fc67edba8a4671b033dd81ac2444e2ff8d5d3011 | 3479 |
| motor/guardian_logica_copi_v1.py | 0101f666ecd70c9cd7aeaa3691f8c34e8d04e75a68594e61c2af3f481a12d519 | 18385 |
| motor/guardian_tropos_beristain_v1.py | 1886af5e9247464a7f87f74a25863cf4a5eee46375c22d44668f80d81e8baf68 | 65554 |
| motor/guardianes_control_v1.py | e043b84cca0c3af1f2297615936f9ba5e533d1dd977a56aed3b914c02f629f4b | 29862 |
| motor/laterales_unico_v1.py | 3845fbccafdbf8cb5c36885abab4dffc4b945be4b5ee48833a13885a22a5aa20 | 89701 |
| motor/lectura_negativo_ricci_vs_billar_v0_1.py | 76cd1a1fb2e5db822d18484e5d8255467836d9cf7d0298e6cafa6701a115ddda | 10241 |
| motor/lente_lateral_metrics_v1_1_galileo.py | 3fa20944fc6fc6026eafbc399911503953f5630d5454b17fbdf144dbdd63cbca | 4988 |
| motor/lexico_narrador_v0_1.py | 0d6bc005e8e55e002fa16e33790bcc51e69ac166d115c2f29fc3e81aaec45c4a | 7557 |
| motor/marco_7783.py | 991932e24845e1b0c76e9c28d5ea4ecf3861ef9af5935d9fceae612fa88f86c5 | 1637 |
| motor/marco_funciones_souriau.py | 4e7f825109c8b32b76c57291ac632a1ae155334b04c7c5608efee0109401ec81 | 5132 |
| motor/matriz_corrida.py | 9cf60a5404ba876615f27efbfaf584aa2e5a2b9af4192c1d1671d769f0875cd3 | 6636 |
| motor/metacognition_v0_1.py | 935c78871f886ce2cb103f4e8084b11148d1fd9e0bd812745af8a3ad24b9ec20 | 7219 |
| motor/modo_estricto_v1.py | c0fe7fbdc2a49cb7b8f11e837e8b2cb084214416092822d254933f8341f07c1e | 17194 |
| motor/motor_interrelacion_extensible_v0_1.py | e40c3c29a2c9971bcf69e265975e5bcb366ff6c1d31af057af85d99ebf87358c | 6192 |
| motor/movimiento_de_fondo_u4.py | e29af58808bd3ac275a96ed1975f78b87f4a524927a7f1015e63bbe4dcb1d7aa | 18929 |
| motor/normalizar_familia_tokens.py | da1235298b85d89701de19f9c26a7b38f6b5cca16f2968cf9c71244f624cd739 | 6232 |
| motor/patterns_final_v14.json | d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1 | 123937 |
| motor/personajes_corte_016.py | 9760ae26cc47cdb321a7a6517145727a60bba5fed4223c624f98dc21dfa8a93e | 24319 |
| motor/plugin_alias_reactivacion.py | 5c630bc563cc46959134b72d6de174ed50e68b1c679ef35dfff597fd7212ee4e | 2368 |
| motor/plugin_aquiles_ancla_estricto.py | 16b793d38ce72c74c6925b42e4b69435e983db05fe6a1956c8de318926ae8640 | 9852 |
| motor/plugin_aquiles_h.py | 3fe976dfc40259003ea828fb39f58adbc17c4da9045b2639fa98a8f1371c1ecc | 5831 |
| motor/plugin_arco_field_snyder_mckee.py | ed672db0cf93ffacbbe79fd58fadee4997e845319ac5c3fe9dbdd633fae91acc | 6105 |
| motor/plugin_arcos_emocionales_laterales.py | 3bd4e1ac24968f5c49c79b997e811ae098d1470c93d98579b1e20fd7a03fe0ec | 2508 |
| motor/plugin_arquetipos_dinamicos.py | 529e79afb7dfabd605da3dc220949d1325e786700e59b58b1fde3e11b23f2d79 | 2853 |
| motor/plugin_cameo_institucional.py | 98a58d5bed02a0fececb3cb9df2f7fb76b78cd7c8b1947bd7887c8d0dfefe36c | 2753 |
| motor/plugin_capa2_antecedentes_arquetipos.py | e20f2ad955cc63bfa1811789bf9d1f31fee7d0a550eb28751e6e11171a01657d | 15243 |
| motor/plugin_circulo_monomito_v2.py | 9a6d858200f80e0cda09e46bc1cd487a885c6d36787c959417e4a2242e3c8a0f | 8132 |
| motor/plugin_embudo_clinico.py | deb37f7e0124217c6f4ad329782063a830b61977e531fa91d6d144339413b2ee | 3294 |
| motor/plugin_entrega_luces_v1.py | ca79faf6429bba9984776e273a2c221539ba887ea7f9cbdf854a43cb8d45abf2 | 1010 |
| motor/plugin_familias_gloria_sacro.py | 8cc568a9009bde662ee167126772b7c87a08d7091b2d4cc61f96530ea98cef0f | 2564 |
| motor/plugin_fix_entrada.py | 8ebdcd0de1c52392d996716fe0c472beafd9568ed79b6de56e30379d91fb87dd | 2637 |
| motor/plugin_guardia_no_cruce.py | 27759007f33abe577cc53ebaff785d922cbdd096072ac7c2fcf9ec614cb6e828 | 5133 |
| motor/plugin_metodo_rigor.py | a4f5659e14e6aab2e40a0929a3c1f2388b89f304dcc2c9a4cb43ebe7cc332cf0 | 1594 |
| motor/plugin_otto_numinoso.py | 2f22f06e6c3e8eececb54a839aa08a1391a7ab0c27f739492417768fed24954e | 2309 |
| motor/plugin_picos_mesetas.py | 7720b6eb614497fb6aaf38d527ea323dbef31b9748f9835385ae9c3ba6081149 | 2071 |
| motor/plugin_polaridad_causal.py | 534ae6366b525f5114ff36217fca0760585602ff2ba513b13a642dcb1082e739 | 5316 |
| motor/plugin_pregunta_detras_v2.py | 771cb526eafe56e10967e31d1c9320296beff77b83ef81bf76ac46114244c247 | 36628 |
| motor/plugin_pregunta_dirigida.py | b9dc7533cd83047654f666ca40e6e961ebfe8fd01082d703b9ba08a7dc404ca8 | 605 |
| motor/plugin_pregunta_dirigida_v0_5_1.py | 8aa9fc79eb591e1bd29fce121606311f51edfef7166691f2704aa6491963204e | 56609 |
| motor/plugin_reporte_3d.py | 20ecefed3def18319ea7a93a237148ab3092208d940dbe4d6d8a0e0621dfb05e | 1698 |
| motor/plugin_resolucion_autonoma_consistencia.py | 18771a3127d547bb4e77ca2ec1d4356678313e3a295f4f268531800adcd9563f | 5117 |
| motor/plugin_sesgo_lectura.py | fe098108d85ccc8a44d13a7a0beb556cf50d6e4450e7b631b5b665edb02e21a0 | 3341 |
| motor/plugin_sombrero_blanco_token.py | 52cd7d13aef7d7f5769622b24a604428d50e7fe286364ff3671bb23fa3cee9c5 | 1596 |
| motor/plugin_souriau_210141.py | 2129f5d66230458745c3659b90c6ecd39704fbd04d90acb88d4f02186cc3a7af | 11330 |
| motor/plugin_trayectoria_hosteleria.py | 06b368ff5ce1cc41ce401224d105e0020421993aed6566852c34757c662b1433 | 1438 |
| motor/plugin_verificador_consistencia_adversarial.py | 10b5e163c22e002715a39c4997194e6211d3179fe2d4ae5ab37bf168d2dfef19 | 6702 |
| motor/predictibilidad_set_021.py | 1d1ac27244ac50bdd086ebf5655671631db986ed9eda28ea5873f7682b13053d | 24322 |
| motor/predictor_vecinos_prefijo_v1.py | 903d4a5bbd0a6d91d8d6b7df0ed3ec2568a2fa39161ef061d62853b73fb9d257 | 7499 |
| motor/protocolo_kernel_motor.py | e95f180246e5fad23615eedf74efd2464777cb6ffb2931a653f0888868209d99 | 11132 |
| motor/puente_souriau_caldero_polti_v1.py | 2a5d23962d60232e16ac152ac0ee443fb9bc4f261f6274dbd9934266eaa31338 | 24749 |
| motor/registro_luces_gemini_packs.json | bafef9f108a96e6524d644c6f66bee3db1e22c19e775b813766992fc24116e62 | 119250 |
| motor/registro_sidecar_amantes_arquetipos.json | 3dab8d38d979efa5a4948a0e05b0a2dbd14421d9ab7ff6e09d5cda99c276aecc | 11579 |
| motor/ricci_forman_coocurrencia_v0_1.py | a8c57df73cf6228d01cfaa921e49a8a474cb1c565a5902cb4754e9341d9b8110 | 4732 |
| motor/schrodinger_transport_esqueleto_v0_1.py | e88cd66f1fbe4aead9a36c231d6f727d2cbdb8f0d138412215d448d1af68f599 | 2173 |
| motor/semiotica_deriva_v0_1.py | 21c84195c45a88725fc3dd7d90f9152e6d324223805a724258ddd3a9be0cc8ff | 2245 |
| motor/sensor_perfil_narrador_v0_1.py | bacdd4a4cc145e48ef333504682a3c753d6a8d84ac7dc7cb23f6ec2873eea2a7 | 27535 |
| motor/sidecar_ablacion_hombre_acero.py | 7db774c0c4934260db59f0a9305e074792488e75bde1560ed7a562f1de277f60 | 22186 |
| motor/sidecar_amantes_arquetipos.py | 7923d49cde131871186358ab078590da4d21a3f842a5ce268016c731c2c46ca9 | 5436 |
| motor/sidecar_area_tokens_v1.py | 0568dce427a907a323429477e79fc63f3cbf2a3fed6ad303e141329fecf3d448 | 18682 |
| motor/sidecar_caldero_busqueda_arquetipos.py | 0bf535df4a08769458f5bcf4e07d7bc534bb272e014e3f18e129ca4c6b0f0010 | 42300 |
| motor/sidecar_corte_memento.py | e56f5fb140484fe5ecaedece3871112d64cd1fd4067f68c40064d6dfca1f52d9 | 23844 |
| motor/sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py | cf153eeb6d8fb80823eecb71f0aac3d37d3999015977a55e5b1c2b01bdd103bd | 7657 |
| motor/sidecar_geometria.py | 27475c07abd38ebb842affda8ee3e952f2e47a109a0c4a90f1f6269694c5ecf9 | 1463 |
| motor/sidecar_lente_souriau.py | 2fb351df37b4466c6923b22c22cea9ef4429f6c3d5c6e824ea5ea47e22eb7191 | 5319 |
| motor/sidecar_luces_gemini_packs.py | 493c434b44c064c2111978d95fc95162ea0218cabbe182276365784dc23518ec | 9390 |
| motor/sidecar_polti_caldero.py | f72dbdaa37fe91f789de71e5317035a51bc2ca7accf663ca9bfb7d21b38ff4ff | 4303 |
| motor/sidecar_sombrero_blanco_filtro_v1.py | 6c9d907cc0b4a4ec8c7bc517b81c55716d9551fe372cabbbea93558334855df2 | 6884 |
| motor/sidecar_trazabilidad_temporal.py | 881898fbf26bacb9cf9fb8900803ee45189dc1c4a8f1feb1b738577396b19d98 | 8988 |
| motor/sidecar_venn_sistemas_v1.py | 1d0401fdc509b4c91f58aad99087c6d66166fc744447e2f9115974bd901a03b6 | 9655 |
| motor/stinkbox_transport_v0_2.py | b53c885f80b3cdd5a6cb64ecc196b8651b179adf5aeddc270829f303c287a874 | 18791 |
| motor/sujetos_014.py | 1d8e285a3c228d7f243152a56ffd0b982048c3da3374883823224354e219bd8d | 5238 |
| motor/traza_campo_244.py | 7d1f397563b8f925349da22d7c4fea125bbe0eebd2a9fff44fa0da8de8d3097d | 5687 |
| motor/tusi_par_indice_exploratorio_v0_1.py | 290d1bb32bb86766593557bf5d139991cf708ac7b4b568412761f4e98b0f86f8 | 2727 |
| motor/v153_lateral_metrics_v1_1.py | 1234e121fb7f516c843b3f9251c88315ab36d7fdbc549aeeea6eacadbddb5ff3 | 8815 |
| motor/vecinos_caldero_neighbor_store.py | 0e8e1c1875e13dff5cb009d8a650fc294b02d4ce506a9ee5a4dfbf0841993d41 | 598 |
| motor/zri_coupling_v0_2.py | 38aaeb5dcaded0e7c15ab3d5613de84baad2aefd3ed053611e2f4edce89efe61 | 4181 |
| motor/zri_experience_v0_1.py | 500fa2b12a4eae491c7b7dc2e0e42db5651dce6cce5d98f44acd28ac55586a85 | 4875 |
| motor/familias_tokens/arquetipos_sistemicos_senge_faltantes.json | 7761b4ecc0aba3e9fc324822310a5dd133ccac7b633872c4d6a76269d1d62b94 | 2568 |
| motor/familias_tokens/ciclo_vida_organizacional_adizes.json | 7f8481a38523b98a0fed5a331b18f9f2f651e1accd20fdbd142e84c9fd678864 | 4465 |
| motor/familias_tokens/ciclos_poder_decadencia_macrohistoria.json | 1e1615a0946dd79c47121e9ba67893ccdda94ec75cdf689e424905c32bcf9d2a | 2935 |
| motor/familias_tokens/deseo_mimetico_chivo_expiatorio.json | 65bc3b7d83740aa8743ad8676b36d47509d8f3deb171a2c8296672ac24a64bec | 2845 |
| motor/familias_tokens/estructura_dramatica_clasica.json | fb73c3d2da5160504874a02193e6ce71841f773c7c0f5491334688b19516f0d2 | 2958 |
| motor/familias_tokens/etapas_vitales_evolutivas.json | defaa4881ce47ffac986c25feb202ff5b58f423a73d3a4bd5a042ef1772b5886 | 2583 |
| motor/familias_tokens/geopolitica_trampa_tucidides.json | 38a12c52796afc9936ed92bd2a454d256bf28e22a9592db7844bf1679ffba67f | 5240 |
| motor/familias_tokens/kishotenketsu_estructura_giro.json | ac99be9589e5c673664651a7211992361f60ca26ee3fb9104fcfbf74304700a8 | 3651 |
| motor/familias_tokens/narrativa_vida_mcadams.json | bb94d0a41c51d79d8d0466e3e8fef1ed0094ac731fc459d988c3f50c9a28384c | 2498 |
| motor/familias_tokens/triangulo_dramatico_karpman.json | 4a98ae64a559a35152a086253f9d1bc09650fda84f72229bb0916eabec159d55 | 2786 |
| motor/familias_tokens/viaje_del_heroe.json | f177b5bb8186a9fb75f5e3108f63197982c223bd55f8f100c5f7042dd1f24b46 | 2750 |
| motor/tokens_laterales/PROTOCOLO_ARCO_ANALOGICO_V018.md | a5342cd8cc751f465ec51a1311f34625e289fcec43bff45653d239b4c1ab340d | 2264 |
| motor/tokens_laterales/REGISTRO_TOKENS_LATERALES_V0_2_ARCO.json | 9d53189cfb8907ee50483ec65621bc56950127f38b50d423e7c613c35e5e4726 | 1729 |
| motor/tokens_laterales/dynamis_dramatica_sistemica_v0_1.json | e07086165d0a2b6b7d2f59c7bc59a0e9cb9a97aabc318c0e7ccdf1f5fcb0d408 | 1136 |
| motor/vecinos_caldero/neighbor_store.py | 6989d1e959cfa049c8b0258a48f20e97ed5b07fb236fb360d9ba6fc39bbcd4f9 | 2618 |
| capa_llm/FIXTURE_MOCK_CONSULTA_20261011.json | 2a2a27194a9aeff1fa7870234d5c9ff493b1b052159c16b589307e5f00cd344e | 36537 |
| capa_llm/consulta_dirigida_v1.py | 573870a998fb2ac68b4a75913c64a251b19e9c6b8c88ef00ebd5a9bee9425dfc | 31031 |
| capa_llm/filtro_entrada_dirigida_017.py | 533d68e042f0d5305fa3e84712f08e6ff6cb628e308028f29314740e36a85705 | 46133 |
| capa_llm/traduccion_contextual_021.py | af9077fd031febb2a77d68b27bd3cec5c6667a921fe5b8b9d33d3884c396533b | 9134 |
| scripts/analizar_unico.py | 0ac07089b55b7457b314bc342177689db6516f92916b9da00255bc6c8c5b9405 | 7342 |
| scripts/candados.py | 2c0cd9973b4a8d8abbb24af416cd3b7112fdbff432e215bf015e0642ae8463a6 | 1768 |
| scripts/comparar_con_registrado_unico.py | 1bdaa945c57f2d98432b6323ca41eb9cd9fb83acc35a2bd5cee17f3228fcfda6 | 2424 |
| scripts/comparar_corridas.py | c0c35780571b27b990f16351251da5e4a1f5c81248aa0aaa23a624223d78646f | 3637 |
| scripts/congelar_base.py | d42bcc66bf3182fa9c3550eb3a55270aabf9320fa7d4bd074265c99e21f365c1 | 4707 |
| scripts/construir_equivalencias_ORIGINAL.py | 16cc55302e79b16f0c14f5f4c38a886b100ad01f77e6df4993f39dd1028c504e | 10298 |
| scripts/correr_todo.sh | 247ad8640dbf8e99d6acfde956ff5f87cc8e1cfe5b257137025fa1e16e28c920 | 743 |
| scripts/ensamblar_piezas.py | 4054455c95f66e52a3218a34b6743950f55eb7390877f2f7dee8fbb506cc1c00 | 8109 |
| scripts/evaluar_calibracion.py | 1b6a6ab87aa9e2e507de4566b6b43434e7077f9890f2903ffa4b18db151478bf | 1772 |
| scripts/orquestador_unico.py | d59af986d01b812e7cf2fd93485398e9bf0ff32ef74f938aea9568d92046262b | 4881 |
| scripts/preflight_integridad.py | 6f4ba098f643396fd0f84055f0d13a5a53037ada40e11088aaa1f02952ab1689 | 1854 |
| scripts/regenerar_puentes.py | 899e22253e0e68ddd12d625a8221cf05b3f315130eaf7d05a8c90fc1ca0dd7a9 | 1705 |
| scripts/reglas_equivalencias.py | ec638c5079cd85f9c5008a7f56f9f9cdb23111ae54d7e230c23123b7fed5846e | 31397 |
| scripts/tabla_componentes.py | 134a7b020c0b291bc937f904793f0ee0a3f76a59b276e61e13acc4f433a08109 | 1604 |
| u5/jobs.txt | 8188ea5b1a7a2ab5f595965df331e69866b3b1a627e167490555dbb2bf6cd5df | 2227 |
| u5/run_u5.sh | 7fd3059954e933e2d03793a9cdc4ca48a810e1ea34db2be758ffcd7ab23c90c4 | 1463 |
| u5/test_u5_detector.py | 99fec6d2597e17a13ea5d882797794b23fd1d7bbb829a3f339d6cf1a5bfa7cfc | 2688 |
| u5/u5_comun.py | 56e0b5bc514198b1ceb7e6df492674bfb272190a70a0bc08d5a7d1f7e239d8e3 | 778 |
| u5/u5_detector.py | 37ad4bb1380ce34b01db284be7b8d00a90dc77c7a004fb6ec238a4b5cf521c6b | 19519 |
| u5/u5_instrumentar.py | 8408ef8832293fd8f81b2ce0a3b58ff42185cea767890977f8b98564038dcfb1 | 3065 |
| u5/u5_monitor.py | 0d495855d37d0717213d459f5d281ac155ae8d91e9590272d5ab1d379ab5c1e4 | 4376 |
| u5/u5_recibo.py | b4a79e49c8188f0b87a554b2634510e2caa01a2948dce83a51441c2e7cc4608c | 10775 |
| u5/u5_verificar.py | 457df365cb126c0e870642494018598d31ee31c9ef9771af83ef4bdc5493d49f | 2360 |
| u6/A7_REFERENCIAS_CLASIFICADAS.json | 3dd76656c49cbac927c3cab921753be5190a19d8e0e20e44dba0457562b7667f | 2331 |
| u6/TOKENS_LATENTES_BASE.json | 7ea6a260fdd0318f41f6198574c3e3f9d1ae893124b889c7bfb5a151d9e98f1f | 1774 |
| u6/UNIFICACION_SHA256_MANIFEST_U5_PREVIO.json | 0759b9e31d07cdf00b379266d73cdf34db68894006746ab4056f9bc9a62e170c | 33888 |
| u6/jobs.txt | 1d968ce79ff00296e215abac0740f053e1d8b76e03dbddcbea1797523f5a12a1 | 2140 |
| u6/parche_u6_nativo.py | 20188cd2e903c1d07e39dc2bb7a297421e2be4774bba94fa5af11bbca7dda04e | 7341 |
| u6/parche_u6_unico.py | 3883f962f3b20988126a824b53ca29a75858451dd6739369f9b95e8b4088c737 | 12798 |
| u6/regenerar_manifiesto.py | cf696990dddd6b3831227999ab4fd0342cb36ba847a3e9459ccce3b16ca38882 | 1531 |
| u6/run_ablacion.sh | beff76c39d94a6c84890c03038573ca6091032613287cb1b11d1311a768eda56 | 1643 |
| u6/run_u6.sh | 0eb385c1fcaf17a71e26492102ce53337d24f99670bba1ebc3671eb94932c38a | 1476 |
| u6/u6_diff.py | caedaa3628c893bd5199e565eebf0163bf107aa85d59dc3e5e7fb3b9526f7331 | 5002 |
| tests/run_tests_unico.py | e1e9272b1fff379a174675623d6eb5eb38c157aaaa40d09619e805c221351141 | 3155 |
| tests/test_cierre_020.py | d54b3484860313fbd507130b77f5387971cbee10c96304080256f0600c6caac5 | 2534 |
| tests/test_consulta_dirigida_v1.py | 458e5901711988180719090466419187fc1353ad89a415e3a3c1d7c271266995 | 3981 |
| tests/test_detras_2_3_3.py | 999a31b12d6e87a3459fc0d86a25a9256b3028ea72c174de13949360b9989a19 | 1127 |
| tests/test_nuevos_guardianes_UNICO.py | 79014e6b1766bad885da44048461100883cc25fe2c680ff3849a0738c03a7cef | 12862 |
| tests/test_patch19_bridge_reuse.py | 6f748359b64df706e4805834c14416f7ef60a34de55588991e2e8419bbbe5fba | 2978 |
| tests/test_predictibilidad_021.py | fe4d74b9a5c9d02c0846ffb7bef7b850fb20a363f92ab3d78f3977fe84ca46c2 | 4673 |
| tests/test_u4_todos_tokens.py | f31b7a33e9e91c761cd3a9dd3aa098f9b71a85f1f177b13991b8d88a985c39c6 | 4246 |
| tests/test_u6_correcciones.py | 9f623abaa335ec98e79467f5e72329f4394c8eda0e6d708a535080172964421e | 2651 |
| tests/fixtures/catalogo_sintetico_243.json | 76849281eac3515a45f8ade73f388577faab0e285e0492ec74b5837f24958372 | 105297 |
| inputs/GIORDANO_BRUNO_PATCH19_COMPACTO.json | 56daf3601390af5115fe159f223516e03589247b59c44d9f2ff5ba90e52b64a3 | 8852 |
| u7/confianza_apuesta_u7.py | 6b5c289342905ed5a3e14c478e8274d7eaf7eae28c0445939ac1b74830767a92 | 5205 |
| motor/stinkbox_tokens_descubiertos.json | d4c2fe3879f6ca0929e784ecca2b8a53b465906e12faa213013218603e8d656f | 454 |
| STORES_VACIO/stinkbox_tokens_descubiertos.json | d4c2fe3879f6ca0929e784ecca2b8a53b465906e12faa213013218603e8d656f | 454 |
| STORES_VACIO/vecinos_caldero/neighbor_store.py | 6989d1e959cfa049c8b0258a48f20e97ed5b07fb236fb360d9ba6fc39bbcd4f9 | 2618 |
