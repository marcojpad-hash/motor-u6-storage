#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clasificación de la auditoría de activación (SOLO LECTURA).
Une: barrido de estados (auditoria_activacion_evidencia.json),
registro_componentes y estado_verificado del RESULT de Semmelweis,
INVENTARIO_COMPONENTES_UNICO.json (estaticas), y la clasificación
manual verificada por lectura de código. Produce la tabla JSON final.
"""
import json
from pathlib import Path

W = Path("/home/hatch/workspace/u6-alterno")
ROOT = Path("/home/hatch/workspace/u6-alterno/motor-cameo/motor")
RESULT = ROOT / "RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json"

ev = json.load(open(W / "auditoria_activacion_evidencia.json"))
res = json.load(open(RESULT))
inv = json.load(open(ROOT / "motor/INVENTARIO_COMPONENTES_UNICO.json"))

# --- registro_componentes del RESULT: pieza -> fila ---
reg = {}
for f in (res.get("registro_componentes") or {}).get("filas", []):
    reg.setdefault(f.get("pieza"), f)
# --- estado_verificado del RESULT: componente -> fila ---
ever = {}
for f in ((res.get("laterales_unico") or {}).get("post", {}).get("estado_verificado") or {}).get("filas", []):
    ever.setdefault(f.get("componente"), f)
# --- estaticas del inventario ---
estaticas = {e.get("pieza"): e for e in inv.get("estaticas", [])}

def norm(s):
    return (s or "").lower().replace("_", "").replace(" ", "").replace(".py", "")

import re as _re
def core(s):
    """Núcleo del nombre: sin prefijos plugin/sidecar/motor, sin versiones ni fechas."""
    s = (s or "").lower().replace(".py", "")
    s = _re.sub(r"^(plugin|sidecar|motor|laterales|v153|lat_|lu_)", "", s)
    s = _re.sub(r"(_v\d+(_\d+)?|_v\d|_202\d+|_unico|_v1_1|_v1|_v2|_v0_1|_v0_2)$", "", s)
    return s.replace("_", "")

def lookup(table):
    """Tabla con varias claves por fila: norm completo y núcleo."""
    out = {}
    for k, v in table.items():
        for key in {norm(k), core(k)}:
            if key:
                out.setdefault(key, v)
    return out

reg_norm = lookup(reg)
ever_norm = lookup(ever)

# --- clasificación manual verificada (componente -> (clase, freno, lector, evidencia)) ---
MANUAL = {
    # (c) CABLEADO PERO NO ACTIVADO — freno exacto
    "capa_integracion_semantica_v1_2": ("c", "Su propio estado es PROPUESTA (línea 190: \"estado\": \"PROPUESTA\"); el principio central (token_es_unidad, reaparicion_no_duplica) está escrito pero el Engine nunca lo aplica. El sensor del hub lo reporta tal cual en el RESULT (sensores_pre.integracion_semantica estado PROPUESTA).", "nadie (sensor: solo reporta)", "RESULT laterales_unico.sensores_pre.integracion_semantica estado=PROPUESTA; registro ACTIVA '7 configuraciones'"),
    "capa_interrelacion_tokens": ("c", "Su propio estado es PROPUESTA (analizar_corte/analizar_cortes devuelven \"estado\": \"PROPUESTA\", líneas 151/182); cuenta_doble_global=False. El sensor del hub lo reporta en PROPUESTA.", "nadie (sensor: solo reporta)", "RESULT sensores_pre.interrelacion_tokens estado=PROPUESTA"),
    "plugin_arquetipos_dinamicos": ("c", "Cargado (opt_dyn) y llamado (dyn.info), pero ACTIVA_MUDA_SIN_MAPEO (MOTOR UNICO línea 667): info() devuelve 3 claves PROPUESTAS fuera del 244, sin valor por caso. No hay puente nombre->familia.", "nadie (llega=[])", "registro ACTIVA_MUDA; estado_verificado ACTIVA_MUDA llega=[]; MOTOR UNICO:667"),
    "plugin_sombrero_blanco_token": ("c", "Declarado feeds_predictor=True en UNICO, VERIFICADO=False en el run (registro: n_esta_corrida=0). Su salida no llega a ningún consumidor en este run.", "nadie (llega=no)", "registro GUARDIAN_FILTRO 'declarado=EXECUTED feeds_predictor=True | llega=no'; estado_verificado llega=[]"),
    "sidecar_caldero_busqueda_arquetipos": ("c", "EJECUTADO con 74 vecinos crudos, pero 0 mapean al 244 (current_neighbors=[]); llm_neighbor_hints_n=0 (las pistas vienen de la entrada y no se pusieron). Su salida no llega a H.", "nadie (llega=no)", "RESULT caldero_bridge current_neighbors=[]; estado_verificado ACTIVA_MUDA llega=[]"),
    "vecinos_caldero_neighbor_store": ("c", "Declarado EJECUTADO feeds_H=True, VERIFICADO llega=no. Los 74 vecinos persisten al StinkBox pero no votan (0 mapeados al 244).", "nadie (llega=no)", "estado_verificado ACTIVA_MUDA 'declarado=EJECUTADO feeds_H=True | llega=no'"),
    "predictor_vecinos_prefijo_v1": ("c", "Cableado y llamado, pero MEDIDA_O_ESTADO_NO_EMITIDO: ningún corte trae estado monomítico exacto (sin prefijo), 0 candidatos. No hay vecinos mapeados de donde predecir.", "nadie (0 candidatos)", "RESULT sensores_pre.predictor_vecinos_prefijo prefijo_detalle sin_estado, candidatos=[]"),
    "filtro_identidad_zoom_out_zoom_in": ("c", "Cableado y llamado, pero ACTIVA_MUDA: sin fuentes de búsqueda verificables (caldero_search_sources o puente conectado). Además el umbral zoom-out está PENDIENTE de validación independiente (línea 24).", "nadie (filtro_identidad_estado=MEDIDA_O_ESTADO_NO_EMITIDO)", "RESULT sensores_pre.filtro_identidad_estado"),
    "matriz_mortalidad_z90_v0_2": ("c", "WIRED_WAITING_VERIFIED_MORTALITY_DATA: cableada en el runner pero sin tabla (data_table NO_APLICA_SIN_TABLA, 0 filas aceptadas). Espera datos de mortalidad verificados.", "nadie (feeds_H=False; solo diagnóstico)", "RESULT matriz_mortalidad_z90 status WIRED_WAITING_VERIFIED_MORTALITY_DATA; recibo huellas_declaradas_ausentes $.matriz_mortalidad_z90.data_table_sha256"),
    "lectura_negativo_ricci_vs_billar_v0_1": ("c", "Su cabecera dice ESTADO=PROPUESTA, 'no cableado, no tubo' (líneas 4, 43), pero el hub SÍ lo lee como voto (voto_negativo). La REGLA (la lectura por negativo DESCARTA) sigue en PROPUESTA; el voto llega a H como señal lateral, el descarte no se aplica.", "hub voto_negativo -> H(rank_fusion:señal_lateral) solo como voto, no como descarte", "RESULT pre.negativo_ricci_vs_billar ACTIVA, 13 familias; registro hub:negativo_ricci_vs_billar ACTIVA llega_a_H True"),
    "plugin_pregunta_detras_v2": ("c", "Su cabecera dice 'PROPUESTA. No cablear al limpio sin OK de Marco' (línea 4), pero MOTOR UNICO lo carga (opt_qd, línea 489) y lo llama (interrogar, línea 490) como control observacional. Su salida no altera H. Pregunta para Marco: ¿existe el OK?", "nadie (observacional; llega=[])", "MOTOR UNICO:489-490; estado_verificado ACTIVA_MUDA llega=[]"),
    "schrodinger_transport_esqueleto_v0_1": ("c", "PROPUESTA / ESQUELETO. NO EJECUTA TRANSPORTE (línea 2). El sensor schro del hub lo necesita presente para no dar NO_CORRE, pero el esqueleto no transporta nada.", "nadie", "código línea 2; hub laterales_unico_v1.py:721"),
    "schrodinger_transport_v0_2": ("c", "Computa (sensor schro: salida estado V0_2_IMPLEMENTADO, rho=0.1) pero Marco ancló el puente en V0_1 sin V0_2 (2026-11-12: V0_2 destruyó ~40% de la masa). El núcleo del motor (MOTOR UNICO) no tiene ninguna referencia a schrodinger: ni V0_1 ni V0_2 alimentan el rank en esta copia.", "nadie en el núcleo (sensor: solo calcula)", "RESULT sensores_pre.schrodinger v02 V0_2_IMPLEMENTADO; grep schrodinger en MOTOR UNICO = 0 refs"),
    "plugin_pregunta_dirigida_v0_5_1": ("d", "PROPUESTA SIDECAR unificada (no cableado al limpio), PENDIENTE de autorización al ON del limpio (líneas 3, 25). El motor carga plugin_pregunta_dirigida.py (sin versión, opt_qdir), NO la v0_5_1.", "nadie (no cargado)", "código líneas 3, 25, 42; _load solo opt_qdir->plugin_pregunta_dirigida.py"),
    "normalizar_familia_tokens": ("d", "Sin puente la familia queda cableada pero muda (línea 91: 'puente_244: PENDIENTE'); status LATERAL_NORMALIZADO_PENDIENTE_CORRIDAS. Ningún archivo lo carga (0 referencias fuera de sí mismo).", "nadie (no cargado)", "grep: 0 _load/import; código líneas 85, 91-92"),
    "observador_externo_v1": ("d", "0 referencias en todo motor/, correr_estandar.py, laterales/ y reconexion_v2a1/. Módulo local de la sesión (lee el RESULT sellado); nunca cableado al motor.", "nadie", "grep observador_externo = 0 refs"),
    "no_duplicacion_latencia": ("d", "Lateral construido esta noche (2026-11-12); standalone, no cableado al motor (por diseño: no toca Engine/244). Su puerta de cordura pasa (reproduce el canónico exacto con la regla apagada).", "nadie (tablero sombra aparte)", "reconexion_v2a1/no_duplicacion_latencia.py; NO_DUPLICACION_VERIFICACION_20261112.md"),
    "rueda_conjuncion": ("d", "Lateral construido esta noche (2026-11-12); standalone, no cableado al motor (por diseño). Lee COLOR_RESULT y tableros sombra.", "nadie (ruedas PNG + resumen aparte)", "laterales/teoria_color/rueda_conjuncion.py; RUEDA_CONJUNCION_VERIFICACION_20261112.md"),
    "cuartos_monomito": ("d", "Lateral construido esta noche (2026-11-12); standalone, no cableado al motor (por diseño).", "nadie", "laterales/teoria_color/cuartos_monomito.py"),
    "marco_funciones_souriau": ("c", "Sub-función mathematical_momentum_map: NOT_IMPLEMENTED_BY_THIS_MODULE (líneas 102, 111). El resto corre (el sensor souriau14 deriva las funciones por PATCH 007).", "nadie (esa sub-función)", "código líneas 102, 111; RESULT sensores_pre.souriau_v1_4"),
    "puente_souriau_caldero_polti_v1": ("c", "Corre (marco_7783_geometria EXECUTED), pero el mapeo seis funciones -> 7783 está PENDIENTE de la regla de Mj (líneas 21, 146: solo 729 alcanzables). La brecha_7783 no se cierra sin esa regla.", "hub marco_7783_geometria (solo lo alcanzable)", "código líneas 21, 146; RESULT sensores_pre.marco_7783_geometria EXECUTED"),
    "guardian_tropos_beristain_v1": ("b", "Corre vía guardianes_control (cargado). 4 tropos con código PENDIENTE_DE_REGLA (METALEPSIS, IMAGEN, ASINDETON, ZEUGMA, líneas 65-87): sin regla de detección, no se marcan. El guardián en sí corre.", "guardianes_control (registro)", "código líneas 65-87; guardianes_control_v1.py:319 lo carga"),
    "caldero_ii_cuadrantes_apuesta_t1": ("d", "La apuesta t+1 de MOVIMIENTO de cuadrante (HIT/MISS Q→Q) 'no implementada en ningún archivo en disco' (RESULT sensores_pre.caldero_ii_cuadrantes.falta). Los cuadrantes Q1-Q4 sí se marcan por corte.", "nadie", "RESULT sensores_pre.caldero_ii_cuadrantes.falta"),
    "consulta_dirigida_caldero": ("c", "Recibo: consulta_dirigida NO_CONFIGURADO (modo off, 0 preguntas). La consulta LLM obligatoria del Caldero (#50 del bus) no está configurada en esta corrida.", "nadie (modo off)", "recibo stage consulta_dirigida NO_CONFIGURADO"),
    "sidecar_trazabilidad_temporal": ("c", "El trazado corre (47 tokens, estados ON/PARPADEO/NO_APAGADO) pero su k empírico es PROPUESTA_EMPIRICA (línea 166) y el sensor reporta estado CABLEADO_BUS_LATERAL. La regla empírica de k no está autorizada como tal.", "sensor (solo traza)", "RESULT sensores_pre.trazabilidad_temporal estado=CABLEADO_BUS_LATERAL, k_estado=PROPUESTA_EMPIRICA"),
    "sidecar_area_tokens_v1": ("c", "El sidecar corre (30 familias registradas), pero la asignación de tokens a las 2 subfamilias es PROPUESTA (línea 106: 'asignación = PROPUESTA').", "hub area_tokens (registro)", "código línea 106; RESULT pre.area_tokens ACTIVA"),
    "sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR": ("b", "Cabecera PROPUESTA 'No se cablea al motor limpio' (líneas 5-6), pero el hub lo carga como SENSOR (no como motor limpio). En este caso ACTIVA_MUDA: sin tokens de cuerpo/salud en P/A/C. La distinción sensor-vs-limpio es la que lo sostiene; su regla corporal sigue sin autorizar al limpio.", "nadie en este caso (sin tokens de cuerpo)", "RESULT pre/sensores cuerpo_arco ACTIVA_MUDA; código líneas 5-6, 207"),
    "tusi_par_indice_exploratorio_v0_1": ("b", "PROPUESTA / EXPLORATORIO por diseño (línea 2); Alimenta_H=NO. Corre (ACTIVA, 6 pares con índice de Tusi). Diagnóstico por diseño, no freno.", "nadie por diseño (exploratorio)", "código línea 2; registro tusi_par ACTIVA"),
    "gate_z90": ("b", "ACTIVA_DIAGNOSTICA por diseño (pre-motor, no bloquea ni escribe H1/H2). En este run RECHAZADO_DIAGNOSTICO con 11 errores R1/R3: el caso no declara disciplina Z90. El bloqueo (exit 7) solo existe para casos con disciplina declarada (PR #8, sin merge).", "nadie (diagnóstico)", "recibo stage gate_z90 RECHAZADO_DIAGNOSTICO; registro gate_z90 ACTIVA_DIAGNOSTICA"),
    "decimo_hombre_esteroides_mayeutica_v1": ("a", "EJECUTADO_CIERRE_ADVERSARIAL. Sub-análisis orthogonal_residual_analysis: NOT_IMPLEMENTED (línea 355) — eso es un hueco dentro del módulo, no su estado. El contador_supervivencia SÍ lo lee ahora predictibilidad_set_021 (línea 106: la fuga original está cerrada en esta copia vía pred_ajustada, no vía H).", "predictibilidad_set_021 (contador_supervivencia); cierre adversarial", "RESULT decimo_hombre_esteroides EJECUTADO_CIERRE_ADVERSARIAL; predictibilidad_set_021.py:106"),
    "schrodinger_transport_v0_1": ("e", "El sensor schro lo computa (salida V0_1_IMPLEMENTADO, alimenta_convergencia=True según el propio sensor), pero el núcleo del motor no tiene ninguna referencia a schrodinger y no se encontró el consumidor de esa 'convergencia' en el árbol buscado. No se puede determinar desde código+RESULT si V0_1 alimenta algún ajuste en esta copia.", "DESCONOCIDO (el sensor dice alimenta_convergencia=True; sin consumidor localizado)", "RESULT sensores_pre.schrodinger salida V0_1_IMPLEMENTADO; grep schrodinger fuera de laterales_unico = 0 archivos"),
    # --- correcciones manuales del join ---
    "MOTOR_V15_3_UNICO_20260927": ("a", "Núcleo del motor (no es un lateral). La mención PROPUESTA en su línea 667 es el registro de plugin_arquetipos_dinamicos, no su propio estado.", "todo el motor", "código: es el motor UNICO; registro componente motor"),
    "Engine_V5_CANONICO_SOLO": ("a", "Engine canónico (núcleo, no lateral).", "todo el motor", "código: Engine_V5_CANONICO_SOLO.py"),
    "MOTOR_V15_3_NATIVO_V0_9": ("a", "Motor nativo V0.9 (núcleo alterno, no lateral).", "todo el motor", "código: MOTOR_V15_3_NATIVO_V0_9.py"),
    "MOTOR_V15_3_NATIVO_V0_9_UNICO": ("a", "Motor nativo V0.9 único (núcleo alterno, no lateral).", "todo el motor", "código: MOTOR_V15_3_NATIVO_V0_9_UNICO.py"),
    "correr_estandar": ("a", "Corredor estándar (no es un lateral).", "todo el run", "recibo: 18 stages COMPLETED"),
    "teoria_color": ("b", "Lateral post-corrida cableado en correr_estandar; EJECUTADO en Semmelweis (COLOR_RESULT json/md/png). can_decide_H=False por diseño: observa, no decide.", "nadie por diseño (archivos COLOR_RESULT)", "recibo stage teoria_color EJECUTADO; laterales_post_corrida.teoria_color"),
    "filogenia_mezcla": ("b", "Lateral post-corrida cableado en correr_estandar; EJECUTADO en Semmelweis (FILOGENIA_MEZCLA json/md). Lectura, no decide.", "nadie por diseño (archivos FILOGENIA_MEZCLA)", "recibo stage filogenia_mezcla EJECUTADO"),
    "equivalencias": ("b", "Biblioteca de la rueda (hue/hx), usada por teoria_color y rueda_conjuncion. No es un componente que corra solo.", "teoria_color, rueda_conjuncion", "laterales/teoria_color/equivalencias.py"),
    "cameo_to_244_adapter_v1": ("b", "Cargado (cameo_to_244_adapter_v1) pero declarado NOT_APPLICABLE en este run (adaptador CAMEO->244 legado; solo auditable). No aplica por diseño aquí.", "nadie (no aplicable)", "estado_verificado ACTIVA_MUDA 'declarado=NOT_APPLICABLE | llega=no'"),
    "plugin_guardia_no_cruce": ("b", "Cargado como artefacto auxiliar; su lógica corre ABSORBIDA en GuardiaNoCruce dentro de _run_transversal_guards. No se invoca como API independiente por diseño.", "guardia transversal (absorbido)", "MOTOR UNICO: estado ABSORBIDO_EN_GUARDIA_TRANSVERSAL"),
    "sidecar_geometria": ("c", "Corre (u_geo) pero su salida no nombra ningún candidato del top: el puente no llega (registro 'geometria' ACTIVA_MUDA). La geometría del sidecar no alimenta el ranking.", "nadie (el puente no llega)", "registro geometria ACTIVA_MUDA 'su salida no nombra ningún candidato del top'; estado_verificado geometria ACTIVA_MUDA llega=[]"),
    # --- resolución de (e) por evidencia del RESULT/registro ---
    "sidecar_amantes_arquetipos": ("b", "ACTIVA_MUDA en este caso: gatillo None (ningún arquetipo amante se activa con estos tokens). Muda por ausencia de señal, no por freno.", "nadie en este caso", "registro amantes_arquetipos ACTIVA_MUDA 'gatillo: None'"),
    "billar_circular_convergencia_v0_2": ("a", "ACTIVA; llega a H como señal lateral del rank_fusion (junto a ricci). v0_2 importa v0_1 como base.", "H (rank_fusion:señal_lateral)", "estado_verificado billar_circular_v0_2 ACTIVA llega_a_H True"),
    "billar_circular_convergencia_v0_1": ("b", "Biblioteca base de v0_2 (importada por v0_2 y por el adaptador de convergencia) y cargada por el hub (lu_billar1_geo). No decide; alimenta a v0_2 y a la geometría del hub.", "billar v0_2, hub geometría", "laterales_unico_v1.py:474 _load lu_billar1_geo; v0_2.py:20 import"),
    "caldero_zoomout_acero_v0_1": ("a", "ACTIVA; llega a H como señal lateral (acero_zoomout).", "H (rank_fusion:señal_lateral)", "estado_verificado acero_zoomout ACTIVA llega_a_H True"),
    "ricci_forman_coocurrencia_v0_1": ("a", "ACTIVA; llega a H como señal lateral del rank_fusion (proxy de deriva temporal, NO el Forman exacto).", "H (rank_fusion:señal_lateral)", "estado_verificado ricci_forman_v0_1 ACTIVA llega_a_H True"),
    "plugin_souriau_210141": ("b", "MARCAJE por decisión Mj 2026-10-06: la aritmética Souriau 210141 es marcaje, no trazabilidad. Corre como sensor de marcaje.", "nadie por decisión (marcaje)", "registro souriau_v1_4 MARCAJE"),
    "zri_coupling_v0_2": ("b", "ACTIVA (v0.1: 7 sellos; v0.2: acople P/A/C en 7 cortes). E_n no se calcula. Diagnóstico; sus anillos los usa el sensor schro del hub.", "hub schro (anillos_helice_zri)", "registro zri_v0_1_v0_2 ACTIVA"),
    "sidecar_corte_memento": ("b", "ACTIVA; proto-H leída en post.memento_vs_top1 (contraste, no Top1). Diagnóstico.", "post.memento_vs_top1", "registro memento ACTIVA"),
    "plugin_capa2_antecedentes_arquetipos": ("b", "ACTIVA_MUDA en este run (capa2 sin señal discriminante). Diagnóstico.", "nadie en este caso", "estado_verificado capa2_antecedentes ACTIVA_MUDA llega=[]"),
    "estabilidad_vectorial_h": ("b", "ACTIVA_MUDA. Diagnóstico de estabilidad vectorial; no decide.", "nadie", "estado_verificado estabilidad_vectorial ACTIVA_MUDA llega=[]"),
    "lente_lateral_metrics_v1_1_galileo": ("b", "ACTIVA_MUDA. Lente de métricas laterales; no decide.", "nadie", "estado_verificado lateral_metrics_v1_1 ACTIVA_MUDA llega=[]"),
    "candado_plugins": ("a", "Corre como stage del recibo: candado_plugins OK, 112 verificados, 0 fallos. Es el candado que verifica los plugins antes de la corrida.", "recibo (bloquea si falla)", "recibo stage candado_plugins OK"),
    "ceb_runtime_v0_6_flow": ("a", "Runtime CEB (ceb_runtime_v03): ejecuta los 77 stages del run (todos started/ended salvo UNSCOPED_RUNTIME).", "todos los stages CEB", "RESULT ceb.stages 77; _load ceb_runtime_v03"),
    "control_flujo_soluciones": ("a", "Controlador de flujo: cargado por NATIVO y usado por matriz_corrida y protocolo_kernel_motor (contornar). Corre.", "matriz_corrida, protocolo_kernel", "MOTOR_V15_3_NATIVO_V0_9_UNICO.py:189,295; matriz_corrida.py:37"),
    "control_latencia_decimo_hombre": ("a", "Control de latencia activo (el alias sidecar_latencia_decimo_hombre está contenido en él).", "predictor (estados LATENCIA/ALMACENADO_ESPERANDO_DATOS)", "INVENTARIO estaticas; MOTOR UNICO _load implícito"),
    "analogos_fase_v1": ("b", "Corre como stage CEB analogos_fase#1 (started/ended, sin error). Análogos por fase; diagnóstico, sin lector de su salida localizado en RESULT.", "DESCONOCIDO (stage corre; lector no localizado)", "RESULT ceb.stages analogos_fase#1"),
    "protocolo_kernel_motor": ("b", "ACTIVA_MUDA: protocolo_orden0 constante por diseño (contrato fijo de arranque).", "nadie por diseño", "estado_verificado protocolo_orden0 ACTIVA_MUDA"),
}

def clasificar(row):
    stem = row["componente"]
    archivo = row["archivo"]
    if stem in MANUAL:
        return MANUAL[stem]
    # estaticas del inventario: solo coincidencia EXACTA de nombre (nunca
    # subcadena: 'plugin_pregunta_dirigida' no es la 0.4.1 superada)
    for pieza, e in estaticas.items():
        if norm(pieza) == norm(stem):
            est = e.get("estado")
            if est in ("SUPERADA", "FUERA_DEL_MOTOR", "PROHIBIDA", "NO_CORRE"):
                return ("d", f"Inventario: estado {est}. Motivo: {e.get('motivo')}", "nadie", f"INVENTARIO_COMPONENTES_UNICO.json estaticas: {pieza}")
    rn = reg_norm.get(norm(stem)) or reg_norm.get(core(stem))
    en = ever_norm.get(norm(stem)) or ever_norm.get(core(stem))
    estados = row["estados"]
    # PROPUESTA autodeclarada -> (c)
    if "PROPUESTA" in estados:
        lineas = "; ".join(f"L{h['linea']}: {h['texto'][:100]}" for h in estados["PROPUESTA"][:2])
        return ("c", f"Autodeclarado PROPUESTA en código: {lineas}", "revisar caso por caso", f"barrido de estados {archivo}")
    if rn:
        est = rn.get("estado")
        if est == "ACTIVA" and rn.get("alimenta_H"):
            return ("a", "", "H (rank_fusion o dimensión)", f"registro_componentes: {rn.get('pieza')} ACTIVA alimenta_H=True; motivo: {str(rn.get('motivo'))[:120]}")
        if est == "ACTIVA":
            llega = (en or {}).get("llega")
            if llega:
                return ("a", "", f"H ({llega})", f"registro ACTIVA; estado_verificado llega={llega}")
            if "can_decide_H_False" in estados:
                return ("b", "can_decide_H=False por contrato (lateral: observa, no decide)", "nadie por diseño", f"registro ACTIVA; can_decide_H=False en {archivo}")
            return ("b", "ACTIVA sin alimenta_H y sin llega registrado; sin freno localizado", "nadie registrado", f"registro ACTIVA; estado_verificado: {en}")
        if est == "ACTIVA_MUDA":
            motivo = str(rn.get("motivo") or "")
            if any(s in motivo for s in ("sin ", "0", "ninguna", "ningún", "constante por diseño", "sin alarma", "neutral", "limpia", "fuera del catálogo", "no hay")):
                return ("b", f"Muda en este caso por ausencia de señal: {motivo[:140]}", "nadie en este caso", f"registro ACTIVA_MUDA: {motivo[:140]}")
            return ("c", f"ACTIVA_MUDA: {motivo[:140]}", "nadie (llega=[])", f"registro ACTIVA_MUDA; estado_verificado: {en}")
        if est == "MARCAJE":
            return ("b", "MARCAJE por decisión Mj 2026-10-06: aritmética Souriau 210141 = marcaje, no trazabilidad", "nadie por decisión", "registro MARCAJE")
        if est == "GUARDIAN_FILTRO":
            return ("b", "GUARDIAN_FILTRO por diseño (filtra, no decide)", "nadie por diseño", "registro GUARDIAN_FILTRO")
        if est == "ACTIVA_DIAGNOSTICA":
            return ("b", "ACTIVA_DIAGNOSTICA por diseño", "nadie (diagnóstico)", f"registro: {motivo if (motivo := str(rn.get('motivo') or '')) else ''}"[:200])
        if est in ("SUPERADA", "FUERA_DEL_MOTOR", "PROHIBIDA", "NO_CORRE"):
            return ("d", f"Registro: {est}. {str(rn.get('motivo'))[:140]}", "nadie", "registro_componentes")
    # sin registro: cableado?
    if row["cableado_motor_unico"] or row["cableado_laterales_unico"] or row["cableado_correr_estandar"] or row["en_features_result"] or row["en_ceb_stages"] or row["en_laterales_unico_result"]:
        if "can_decide_H_False" in estados:
            return ("b", "Cableado; can_decide_H=False por contrato", "nadie por diseño", f"cableado MU/LU/CE; presente en RESULT")
        return ("e", "Cableado/presente pero no se verificó su punto de llamada ni su lector individualmente", "DESCONOCIDO", "presente en _load o RESULT; sin verificación individual")
    return ("e", "Sin _load, sin registro en laterales_unico, sin presencia en RESULT; no se puede determinar si corre por otra vía", "DESCONOCIDO", "sin evidencia de cableado ni de ejecución")

rows = []
for r in ev["componentes"]:
    clase, freno, lector, evidencia = clasificar(r)
    estados_txt = {}
    for k, hits in r["estados"].items():
        estados_txt[k] = [f"L{h['linea']}: {h['texto'][:150]}" for h in hits[:3]]
    rows.append({
        "nombre": r["componente"],
        "archivo": r["archivo"],
        "cableado": {
            "correr_estandar": r["cableado_correr_estandar"],
            "motor_unico": r["cableado_motor_unico"],
            "laterales_unico": r["cableado_laterales_unico"],
            "en_features_result": r["en_features_result"],
            "en_ceb_stages": r["en_ceb_stages"],
            "en_laterales_unico_result": r["en_laterales_unico_result"],
        },
        "estado_textual": estados_txt,
        "clase": clase,
        "freno": freno,
        "quien_lee_su_salida": lector,
        "evidencia": evidencia,
    })

# piezas del registro/inventario que no son archivos .py del barrido (caldero_run, Engine falso, etc.)
extras = []
for pieza, f in reg.items():
    if not any(norm(pieza) == norm(r["nombre"]) for r in rows):
        est = f.get("estado")
        clase = {"ACTIVA": "a", "ACTIVA_MUDA": "b", "SUPERADA": "d", "FUERA_DEL_MOTOR": "d",
                 "PROHIBIDA": "d", "NO_CORRE": "d", "MARCAJE": "b", "GUARDIAN_FILTRO": "b",
                 "ACTIVA_DIAGNOSTICA": "b"}.get(est, "e")
        extras.append({"nombre": pieza, "archivo": "(registro_componentes, sin archivo .py propio en el barrido)",
                       "cableado": {}, "estado_textual": {"registro": [f"{est}: {str(f.get('motivo'))[:150]}"]},
                       "clase": clase, "freno": str(f.get("motivo"))[:200],
                       "quien_lee_su_salida": "H" if f.get("alimenta_H") else "nadie registrado",
                       "evidencia": f"registro_componentes: {pieza}"})
rows.extend(extras)

from collections import Counter
print("total filas:", len(rows))
print(Counter(r["clase"] for r in rows))
out = W / "auditoria_activacion_laterales.json"
out.write_text(json.dumps({"resumen_clases": dict(Counter(r["clase"] for r in rows)),
                           "filas": rows}, ensure_ascii=False, indent=1))
print("escrito:", out)
print()
print("=== clase (c) ===")
for r in rows:
    if r["clase"] == "c":
        print(" -", r["nombre"])
print()
print("=== clase (e) ===")
for r in rows:
    if r["clase"] == "e":
        print(" -", r["nombre"], "|", r["archivo"])
