#!/usr/bin/env python3
"""PLUGIN_CIRCULO_MONOMITO — lente lateral, NO pattern.
No toca Engine_V5_CANONICO_SOLO.py ni patterns_final_v14.json.
No agrega tokens nuevos a la biblioteca 244.
Reutiliza origenes_renovables por corte.

R1: listas Q1-Q4 CANDIDATAS, no asignacion exclusiva.
R2: posicion real = co-ocurrencia + pregunta_activa.
R3: sombra vs mentor mirando corte siguiente.
R4: ciclo nuevo cuando reaparece mundo_ordinario.
Catarsis: cierre en Q4 por conexion contextual con otro hilo (anagnorisis/peripecia).
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any

ESTRUCTURAS_CANDIDATAS = {
    "Q1_Separacion_1_3": {
        "etapas": ["01_mundo_ordinario","02_llamada_aventura","03_rechazo_llamada"],
        "nota": "CANDIDATO",
        "tokens_candidatos": ["ruptura_pasado","adaptacion_forzada","mundo_ordinario","llamada_aventura","rechazo_o_duda","autonomia","rebeldia","dogmatismo","escepticismo"],
        "pregunta_tipo": "origen"
    },
    "Q2_Descenso_4_6": {
        "etapas": ["04_encuentro_mentor","05_cruce_primer_umbral","06_pruebas_aliados_enemigos"],
        "nota": "CANDIDATO",
        "tokens_candidatos": ["sabiduria","consejo","guia","herramienta_nueva","entrenamiento","aprendizaje","desafio_autoridad","aburrimiento","racionalidad","cautela"],
        "pregunta_tipo": "con_que_contra_quien"
    },
    "Q3_Ordeal_7_9": {
        "etapas": ["07_acercamiento_cueva_interior","08_prueba_suprema","09_recompensa"],
        "nota": "CANDIDATO - prueba ANTES, caverna DESPUES recompensa",
        "tokens_candidatos": ["acercamiento_cueva_interior","prueba_suprema","recompensa","consumo_sustancias","turno_atipico","liderazgo","desapego_emocional","pragmatismo_frio","evitacion","crisis_existencial","duelo","perdida_familiar","aislamiento_social"],
        "pregunta_tipo": "donde_se_rompe"
    },
    "Q4_Retorno_10_12": {
        "etapas": ["10_camino_regreso","11_resurreccion_transformacion","12_retorno_con_elixir"],
        "nota": "CANDIDATO - cierre + catarsis (anagnorisis/peripecia)",
        "tokens_candidatos": ["camino_regreso","resurreccion_transformacion","retorno_con_elixir","obtencion","resolucion","reconciliacion","comprension_nueva","sabiduria_compartida","proposito_claro","mentoria_activa","resiliencia","catarsis","anagnorisis","peripecia"],
        "pregunta_tipo": "que_queda"
    }
}

HILOS = {
    "hilo_formacion": {"tokens_ancla": ["formacion_literaria"]},
    "hilo_desafio": {"tokens_ancla": ["desafio_autoridad"]},
    "hilo_sombra_consumo": {"tokens_ancla": ["consumo_sustancias","antagonismo","autodestruccion","ira_institucional"]},
    "hilo_vinculo": {"tokens_ancla": ["lealtad","apoyo_activo","duelo","perdida_familiar"]},
}

def _cuadrantes_activos_por_coocurrencia(tokens_corte: List[str]) -> List[str]:
    scores = {}
    for q, data in ESTRUCTURAS_CANDIDATAS.items():
        overlap = len(set(tokens_corte) & set(data["tokens_candidatos"]))
        if overlap:
            scores[q] = overlap
    if not scores:
        return []
    max_s = max(scores.values())
    return [q for q,s in scores.items() if s >= max_s]

def posicion_por_corte(cortes_tokens: List[Tuple[str, List[str], str]]) -> Dict[str, Any]:
    """Resolve Q1-Q4 with the frozen cut tokens plus CURRENT Caldero neighbors.

    Caldero memory is not treated as current evidence merely because it persists.
    The caller may provide a fourth tuple element with current-run Caldero context:
    {"tokens_neighbors": [...]}. Only those current neighbors are injected into
    the corresponding cut. The original cut tokens remain separately visible.
    """
    resultados = []
    pendientes: Dict[str, str] = {}
    for idx, item in enumerate(cortes_tokens):
        cid, tokens, pregunta = item[:3]
        caldero_ctx = item[3] if len(item) > 3 and isinstance(item[3], dict) else {}
        caldero_neighbors = [str(x).strip().casefold() for x in (caldero_ctx.get("tokens_neighbors") or []) if str(x).strip()]
        tokens_base = [str(x).strip().casefold() for x in tokens if str(x).strip()]
        # Caldero is a resolver input for the lateral lens, not a new 244 token.
        # It participates only as current contextual evidence for this cut.
        tokens_resolucion = list(dict.fromkeys(tokens_base + caldero_neighbors))
        q_act = _cuadrantes_activos_por_coocurrencia(tokens_resolucion)
        hilos_presentes = [h for h,d in HILOS.items() if any(t in tokens_resolucion for t in d["tokens_ancla"])]
        r3 = None
        if any(t in tokens for t in HILOS["hilo_sombra_consumo"]["tokens_ancla"]):
            resuelto = False
            for k in range(idx+1, len(cortes_tokens)):
                sig = cortes_tokens[k][1]
                if any(x in sig for x in ["aprendizaje","comprension_nueva","resolucion","reconciliacion"]):
                    r3 = "fue_mentor_demora_etiqueta"
                    for h in hilos_presentes:
                        pendientes.setdefault(h, cid)
                    resuelto = True
                    break
                elif any(x in sig for x in ["autodestruccion","aislamiento","estancamiento"]):
                    r3 = "sombra_confirmada_demora_etiqueta"
                    resuelto = True
                    break
            if not resuelto:
                r3 = "sin_resolucion_en_serie_completa" if idx+1 < len(cortes_tokens) else "sin_siguiente_corte_aun"
        r4 = False
        if ("mundo_ordinario" in tokens or "ruptura_pasado" in tokens) and idx>0:
            if any("Q4" in "".join(r["cuadrante_activo"]) for r in resultados):
                r4 = True
        estabilidad = {}
        for h in hilos_presentes:
            cnt=1
            for j in range(idx-1,-1,-1):
                if h in resultados[j]["hilos_presentes"] and set(resultados[j]["cuadrante_activo"]) & set(q_act):
                    cnt+=1
                else:
                    break
            estabilidad[h]=cnt
        catarsis=[]
        if any("Q4" in q for q in q_act):
            for hp, orig in list(pendientes.items()):
                catarsis.append({"hilo": hp, "origen": orig, "cierre_en": cid, "tipo": "catarsis_contextual_Q4"})
            for it in catarsis:
                pendientes.pop(it["hilo"], None)
        resultados.append({
            "corte": cid,
            "pregunta_activa": pregunta,
            "tokens_corte": tokens_base,
            "caldero_neighbors_actuales": caldero_neighbors,
            "tokens_resolucion_monomito": tokens_resolucion,
            "caldero_inyectado_en_resolucion": bool(caldero_neighbors),
            "cuadrante_activo": q_act,
            "hilos_presentes": hilos_presentes,
            "estabilidad_hilo": estabilidad,
            "r3_sombra_mentor": r3,
            "r4_nuevo_ciclo": r4,
            "catarsis_de_hilo": catarsis,
            "pendientes_consolidar_restantes": list(pendientes.keys()),
            # PATCH 010a-7: orden determinista (antes list(set(...)) -> orden dependiente de PYTHONHASHSEED); mismo contenido.
            "huecos": [q for q in ESTRUCTURAS_CANDIDATAS.keys() if q not in set(q_act)] if q_act else list(ESTRUCTURAS_CANDIDATAS.keys())
        })
    mas=None
    lineas={}
    for r in resultados[-3:]:
        for h,est in r["estabilidad_hilo"].items():
            if any("Q4" in q for q in r["cuadrante_activo"]):
                lineas[h]=max(lineas.get(h,0), est)
    if lineas:
        mas=max(lineas, key=lineas.get)
    return {
        "plugin": "PLUGIN_CIRCULO_MONOMITO",
        "tipo": "lente_lateral_no_pattern",
        "no_toca": ["Engine_V5_CANONICO_SOLO.py","patterns_final_v14.json"],
        "r1_corregida": "listas por cuadrante son estructuras semanticas candidatas",
        "posicion_monomito_por_corte": resultados,
        "linea_mas_avanzada_actual": mas,
        "nota_catarsis": "catarsis = cierre en Q4 por conexion contextual con otro hilo (anagnorisis/peripecia)",
        "caldero_contract": "solo vecinos Caldero del run actual; memoria persistente no se convierte sola en evidencia corriente",
        "feeds_H": False,
        "can_decide_H": False
    }
