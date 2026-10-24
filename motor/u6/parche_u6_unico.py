#!/usr/bin/env python3
"""Aplica los cambios U6 sobre motor/MOTOR_V15_3_UNICO_20260927.py del pack U6 (idempotente: falla si el ancla no está)."""
from pathlib import Path
P = Path(__file__).resolve().parent.parent / "motor" / "MOTOR_V15_3_UNICO_20260927.py"
s = P.read_text(encoding="utf-8")
def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:120])
    s = s.replace(old, new)

# --- U6 #1: tabla de declaración veraz por componente (fuente única; la usan run() y el pase 010b)
rep("_RUN_CTX={}\ndef _off(name): return name in _off_set()",
'''_RUN_CTX={}
def _off(name): return name in _off_set()

# U6 #1 (2026-10-12): declaración VERAZ de cada componente frente al ranking (rank_fusion).
#   ACTIVA                       -> su salida llega a rank_fusion como señal lateral o dimensión (can_decide_H=False siempre)
#   CABLEADA_SIN_SENAL_EN_CASO   -> hay vía real al ranking; en este caso la entrada está vacía o es igual para todas las candidatas
#   TRAZA_SOLO                   -> salida de nivel caso (sin campo por candidata): por construcción no puede ordenar candidatas
#   ACTIVA_MUDA_SIN_MAPEO        -> salida por entidad, pero en un espacio de nombres fuera del 244 sin puente aprobado (no se inventa mapeo)
#   FILTRO_AGUAS_ARRIBA          -> no produce dimensión: filtra/condiciona la entrada de otra pieza que sí llega
_DECL_U6={
 "geometria":("TRAZA_SOLO","lee R732 (dX_norm, persist_cos, kappa_dir) del motor; la misma señal R732 entra al vector de candidata por vía directa (geometric_inertia_alignment, geometric_direction_change; PATCH11). El sidecar no se suma dos veces"),
 "otto_numinoso":("ACTIVA_MUDA_SIN_MAPEO","neto por familias otto_* que no están en el 244 ni en PUENTE_244_FAMILIAS; mapearlas sería inventar familias"),
 "embudo_clinico":("TRAZA_SOLO","listas clínicas / co-oficio por corte (nivel caso), sin campo por candidata"),
 "trayectoria_hosteleria":("ACTIVA_MUDA_SIN_MAPEO","favor/contra de la plantilla hostelería (no es familia del 244); sin puente aprobado"),
 "estabilidad_vectorial":("TRAZA_SOLO","estado de estabilidad de la H ya calculada (post-ranking); control de cierre, no ordena candidatas"),
 "aquiles_h":("TRAZA_SOLO","SEGUIR/PARAR por ventanas sobre la H (nivel caso); control de cierre, no ordena candidatas"),
 "capa2_antecedentes":("ACTIVA_MUDA_SIN_MAPEO","estereotipos/prototipos capa2 (estereo_*, alianza_*...) fuera del 244; el propio plugin declara que SUGIERE luces, no apuesta"),
 "plugin_arco_field_snyder_mckee.py":("TRAZA_SOLO","beats Field/Snyder/McKee por corte (nivel caso)"),
 "plugin_sesgo_lectura.py":("TRAZA_SOLO","transiciones de letrero entre cortes (nivel caso); sospecha de sesgo, no ordena"),
 "plugin_pregunta_detras":("TRAZA_SOLO","control de la pregunta (marcajes ETIQUETA_SUJETO); no tiene salida por candidata"),
 "plugin_metodo_rigor":("TRAZA_SOLO","alarma HECATE sobre la cadena top1 por corte (nivel caso)"),
 "plugin_pregunta_dirigida":("TRAZA_SOLO","hallazgos sobre la pregunta (nivel caso)"),
 "plugin_arquetipos_dinamicos":("ACTIVA_MUDA_SIN_MAPEO","info() devuelve 3 claves PROPUESTAS fuera del 244, sin valor por caso"),
 "plugin_circulo_monomito_v2.py":("TRAZA_SOLO","posición/cuadrante por corte en tokens, sin nombres de candidata; recibe vecinos Caldero"),
 "plugin_arcos_emocionales_laterales.py":("ACTIVA_MUDA_SIN_MAPEO","arcos del catálogo lateral (no 244); sus arcos ACTIVOS siembran la consulta ciega pre-H (aguas arriba), no el ranking"),
 "sujetos_014.py":("FILTRO_AGUAS_ARRIBA","identidad de sujeto: condiciona autoevidencia_stores_011 (un sujeto cuenta una vez); no es dimensión"),
 "filtro_relleno_013.py":("FILTRO_AGUAS_ARRIBA","saca relleno/años del voto de vecinos (caldero_neighbor_*); lo consume el predictor vía _RUN_CTX"),
 "plugin_cameo_institucional.py":("CABLEADA_SIN_SENAL_EN_CASO","dims cameo_activity/cameo_profile_activity son de nivel caso (iguales para todas); sus tokens explícitos van al bus de luces -> interrelation -> relational_alignment"),
 "sidecar_caldero_busqueda_arquetipos.py":("CABLEADA_SIN_SENAL_EN_CASO","vía caldero_neighbor_alignment; sin fuentes de búsqueda (offline / input sin caldero_search_sources) no hay vecinos"),
 "vecinos_caldero/neighbor_store.py":("CABLEADA_SIN_SENAL_EN_CASO","vía caldero_neighbor_memory/alignment; store vacío en la corrida estándar"),
 "motor_interrelacion_extensible_v0_1.py":("CABLEADA_SIN_SENAL_EN_CASO","vía relational_alignment; solo trabaja sobre external_lights/external_activations, ausentes en el input"),
 "stinkbox_to_light_bus_v1":("CABLEADA_SIN_SENAL_EN_CASO","vía relational_alignment; sin luces persistentes registradas"),
 "stinkbox_transport_v0_2.py":("CABLEADA_SIN_SENAL_EN_CASO","vía stinkbox_support (candidate_support); con stores vacíos el soporte es 0 para todas"),
 "hub:negativo_ricci_vs_billar":("CABLEADA_SIN_SENAL_EN_CASO","voto del hub por el puente de nombres; llega a candidatas pero no discrimina en este caso"),
 "lateral_metrics_v1_1":("CABLEADA_SIN_SENAL_EN_CASO","vía puente de nombres (node_mass_pairs de curvatura negativa); sin masa incidente no nombra candidatas"),
 "plugin_picos_mesetas.py":("ACTIVA","U6: score = fracción de transiciones ↗ (eps del plugin) de la serie P_top5 por corte; señal lateral por candidata"),
}
def _decl_u6(name):
    return _DECL_U6.get(str(name)) or _DECL_U6.get(str(name).replace("hub:",""))''')

# run(): la declaración sale de la tabla
rep('''            status.append({"component": name, "status": "EXECUTED", "feeds_predictor": True})''',
'''            _d6=_decl_u6(name)
            status.append({"component": name, "status": "EXECUTED",
                           "feeds_predictor": (_d6 is None or _d6[0] in ("ACTIVA","CABLEADA_SIN_SENAL_EN_CASO")),
                           **({"declaracion_U6": _d6[0], "motivo_declaracion_U6": _d6[1]} if _d6 else {})})''')

# --- U6 #1: picos/mesetas cableado como señal lateral (campo numérico que el puente de nombres lee)
rep('''        elif hasattr(mod,api):
            run(fn,lambda mod=mod,api=api,payload=payload:getattr(mod,api)(payload))''',
'''        elif hasattr(mod,api):
            if fn=="plugin_picos_mesetas.py" and not _off("picos_score_u6"):
                def _picos_u6(mod=mod,api=api,payload=payload):
                    o=getattr(mod,api)(payload)
                    for _k,_c in ((o or {}).get("curvas") or {}).items():
                        _fz=str(_c.get("forma") or "")
                        # U6: misma lectura del plugin (signo con su eps); fracción de ↗ en la serie. No usa datos post-Z.
                        _c["score"]=round(_fz.count("↗")/len(_fz),6) if _fz else 0.0
                    if isinstance(o,dict): o["score_u6"]="score=fracción de transiciones ↗ (eps del plugin) por familia; señal lateral can_decide_H=False"
                    return o
                run(fn,_picos_u6)
            else:
                run(fn,lambda mod=mod,api=api,payload=payload:getattr(mod,api)(payload))''')

# --- U6 #1/#2: semiótica de deriva como TRAZA (fuera del puente de nombres)
rep('''BRIDGE_EXCLUDE={"laterales_unico_detalle",''', '''BRIDGE_EXCLUDE={"semiotica_deriva","laterales_unico_detalle",''')
rep('''    dyn=_load("opt_dyn","plugin_arquetipos_dinamicos.py")''',
'''    # U6 #2: semiotica_deriva_v0_1 cableada como TRAZA_SOLO (antes 0 llamadas). Marca SIGNIFICANTE_SIN_OBJETO / SIGNO_AISLADO.
    #   Su 'por_familia' suma también tokens CONTRA como apoyo: por eso NO entra al puente de nombres (BRIDGE_EXCLUDE).
    sem=_load("opt_sem","semiotica_deriva_v0_1.py")
    if sem and hasattr(sem,"revisar") and not _off("semiotica_deriva"):
        def _sem_u6():
            o=dict(sem.revisar({"cuts":cuts},{}))
            o["feeds_predictor"]=False; o["can_decide_H"]=False; o["rol_U6"]="TRAZA_SOLO"
            return o
        run("semiotica_deriva",_sem_u6)
        if status and status[-1].get("component")=="semiotica_deriva":
            status[-1].update({"feeds_predictor":False,"declaracion_U6":"TRAZA_SOLO","motivo_declaracion_U6":"traza semiótica; por_familia cuenta tokens contra como apoyo -> no apta como señal de ranking"})
    dyn=_load("opt_dyn","plugin_arquetipos_dinamicos.py")''')

# --- A7: alias monomito (MAPA_NOMBRES: plugin_circulo_monomito.py = plugin_circulo_monomito_v2.py)
rep('''    circ=_load("opt_circ","plugin_circulo_monomito_v2.py") or _load("opt_circ","plugin_circulo_monomito.py")''',
'''    circ=_load("opt_circ","plugin_circulo_monomito_v2.py")  # U6 A7: el fallback al alias v1 (ausente) se quitó; MAPA_NOMBRES: mismo rol''')

# --- frye_support: suma lineal sin normalizar -> saturaba en 1.0 para relative>=~0.47 (constante entre candidatas)
rep('''    frye_support=_clip01(0.95*frye_mythic + 0.72*frye_high_mimetic + 0.50*frye_low_mimetic - frye_iron_atrition)''',
'''    if _off("frye_normalizado_u6"):
        frye_support=_clip01(0.95*frye_mythic + 0.72*frye_high_mimetic + 0.50*frye_low_mimetic - frye_iron_atrition)
    else:
        # U6 BUG FIX: misma combinación lineal dividida por su máximo positivo (0.95+0.72+0.50=2.17); antes saturaba en 1.0.
        frye_support=_clip01((0.95*frye_mythic + 0.72*frye_high_mimetic + 0.50*frye_low_mimetic - frye_iron_atrition)/2.17)''')

# --- CEB: sujetos_014 -> consumidor autoevidencia_011 (antes dict() rompía la identidad del objeto)
rep('''            _ctx014=dict(_ceb_stage("sujetos_014.py", lambda: _s014.contexto(case)))''',
'''            _o014=_ceb_stage("sujetos_014.py", lambda: _s014.contexto(case)); _RUN_CTX["_o014_obj"]=_o014
            _ctx014=dict(_o014)''')
rep('''            _RUN_CTX["vecinos_011"]=dict(_ceb_stage("autoevidencia_stores_011.py", lambda: _ae011.memoria_vecinos_sin_propios(''',
'''            _RUN_CTX["vecinos_011"]=dict(_ceb_stage("autoevidencia_stores_011.py", shared=[case,motor,features]+([_RUN_CTX["_o014_obj"]] if _RUN_CTX.get("_o014_obj") is not None else []), fn=lambda: _ae011.memoria_vecinos_sin_propios(''')
# filtro_013 -> consumidor predictor
rep('''            _ceb_stage("filtro_relleno_013.py", _filtrar013)''', '''            _RUN_CTX["_o013_obj"]=_ceb_stage("filtro_relleno_013.py", _filtrar013)''')
rep('''    pred=_ceb_stage("predictor", lambda: _predict(boards,histories,motor,features,gate_ctx))''',
'''    pred=_ceb_stage("predictor", lambda: _predict(boards,histories,motor,features,gate_ctx),
                    shared=[case,motor,features]+[_RUN_CTX[k] for k in ("_o013_obj",) if _RUN_CTX.get(k) is not None])''')

# --- motivo de cada dimensión constante (documental, no cambia el ranking)
rep('''                                "excluded_constant":excl_const,"excluded_duplicate":excl_dup,''',
'''                                "excluded_constant":excl_const,"excluded_constant_motivo_U6":{k:_motivo_constante_u6(k) for k in excl_const},"excluded_duplicate":excl_dup,''')
rep('''def _dimension_guard(rows, keys):''',
'''_CONST_U6_CASO=("relational_activity","caldero_neighbor_activity","caldero_neighbor_memory","cameo_activity","cameo_profile_activity",
                "geometric_persistence_context","geometric_turn_context","geometric_latest_movement")
_CONST_U6_ENTRADA=("relational_alignment","caldero_neighbor_alignment","stinkbox_support","lateral_shared_evidence","analog_alignment")
def _motivo_constante_u6(k):
    if k in _CONST_U6_CASO: return "NIVEL_CASO_POR_CONSTRUCCION: el valor no depende de la candidata (contexto); no es bug"
    if k in _CONST_U6_ENTRADA: return "ENTRADA_VACIA: depende de external_lights / fuentes Caldero / stores, ausentes o vacíos en esta corrida"
    if k.startswith("dynamis_") or k.startswith("propp_") or k.startswith("booker_") or k.startswith("greimas_"):
        return "SIN_ACIERTOS_DE_PALABRA_CLAVE: los tokens propios de las candidatas no contienen las raíces del bucket (igual valor para todas)"
    if k=="frye_support": return "SATURACION (corregido en U6 con normalización); si sigue constante, todas las candidatas tienen el mismo poder relativo"
    return "CONSTANTE_EN_ESTE_CASO"

def _dimension_guard(rows, keys):''')

# --- 010b: clasificación veraz también en las filas explícitas (component_status)
rep('''            _row["llega_verificado"]=_f.get("llega")''',
'''            _row["llega_verificado"]=_f.get("llega")
            _d6=_decl_u6(_row.get("component"))
            if _row["feeds_predictor"]:
                _row["declaracion_U6"]="ACTIVA"
            elif _d6:
                _row["declaracion_U6"]=_d6[0]; _row["motivo_declaracion_U6"]=_d6[1]
                if _d6[0] not in ("ACTIVA","CABLEADA_SIN_SENAL_EN_CASO") and _row["feeds_predictor_declarado"]:
                    _row["feeds_predictor_declarado_original"]=True; _row["feeds_predictor_declarado"]=False''')
P.write_text(s, encoding="utf-8")
print("OK", P)
