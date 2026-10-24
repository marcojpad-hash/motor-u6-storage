# -*- coding: utf-8 -*-
"""PATCH 022 (2026-10-24) — APUESTA DE DESTINO PERSONAL.

Campo NUEVO y separado: result["apuesta_destino_personal"]. Una sola etiqueta: auge | meseta | caida | ruptura.
No toca H1/H2, ni el set abierto, ni la apuesta temática multiescenario (hipotesis_trayectoria_abierta_v1),
ni rank_fusion, ni Engine/catálogo. can_decide_H=False. Se apaga con DESTINO_022=0.

Por qué existe: la apuesta temática mide si el soporte de cada HIPÓTESIS crece entre cortes (las hipótesis
del set son las que más ganaron, así que casi siempre sale CONTINUIDAD_ASCENDENTE). Esta apuesta mide otra cosa:
el BALANCE del sujeto entre familias de su lado (auge) y familias en su contra (caída / ruptura) corte a corte.

Fuente de las series: movimiento_de_fondo (U4) -> series_familias[f].serie_activacion, que ya es la activación
por corte de cada familia del catálogo 244 sobre el tablero canónico de la corrida (cortes <= Z, post-freeze).
Umbrales: los MISMOS de movimiento_de_fondo (umbrales.familias: EPS, GRANDE, NETO_ASC/NETO_DESC); no se ajustan.

Polos: listas fijas por SIGNIFICADO del nombre de la familia (definidas antes de correr, sin mirar desenlaces):
  RUPTURA = quiebre brusco contra el sujeto (desastre, colapso, crisis, bifurcación, choque con un poder superior).
  CAIDA   = pérdida gradual de posición o apoyo (persecución, víctima, error, tragedia, aislamiento, declive, delación).
  AUGE    = ganancia o consolidación (obtención, logro, salvación, recuperación, recompensa, expansión, apoyo).

Regla (en este orden, Z = último corte, Z-1 = el anterior):
  adv = act(CAIDA)+act(RUPTURA); rup = act(RUPTURA); fav = act(AUGE); bal = fav - adv
  net = bal_Z - bal_{Z-1};  dR = rup_Z - rup_{Z-1};  d_eje = act(eje)_Z - max(act(eje) antes de Z)
  1) ruptura : dR >= GRANDE  y  adv_Z > fav_Z                       (conflicto que se cierra de golpe contra el sujeto)
  2) caida   : net <= -NETO_DESC, o (adv_Z > fav_Z y adv sube > EPS), o (d_eje <= -NETO_DESC y net < 0)
                                                                      (pierde apoyo / lo adverso domina / su eje se apaga)
  3) auge    : net >= NETO_ASC y fav_Z >= adv_Z
  4) meseta  : todo lo demás (o menos de 2 cortes -> meseta con SIN_TRAYECTORIA)
"""
from __future__ import annotations

VERSION = "APUESTA_DESTINO_PERSONAL_022_20261024"

RUPTURA = ["6_desastre", "31_conflicto_con_un_dios", "16_locura", "cliodinamica_03_fase_crisis_colapso",
           "tainter_04_colapso_por_simplificacion_forzada", "predictivo_04_caos_bifurcacion_critica",
           "predictivo_01_markov_estado_absorbente", "strauss_howe_04_the_crisis", "social_10_cohen_panico_moral",
           "distopia_coercion_total", "anacyclosis_06_oclocracia", "eterno_retorno_01_caos_primordial"]
CAIDA = ["5_persecucion", "7_caer_victima", "17_fatal_imprudencia", "33_error_de_juicio", "24_rivalidad_de_superior_e_inferior",
         "36_perdida_de_los_seres_queridos", "frye_mythos_tragedia", "frye_mythos_ironia_satira",
         "jaldun_03_entropia_y_perdida_de_cohesion", "kondratiev_03_otonio_estancamiento", "kondratiev_04_invierno_recesion",
         "tainter_02_rendimientos_decrecientes", "tainter_03_vulnerabilidad_sistemica", "cliodinamica_02_fase_estanflacion_presion",
         "minsky_03_ponzi", "erikson_06_intimidad_vs_aislamiento", "erikson_08_integridad_vs_desesperacion",
         "social_07_noelle_neumann_espiral_silencio", "social_08_girard_mimesis_y_chivo_expiatorio",
         "sistema_domiciano_delacion", "sistema_domiciano_maiestas", "predictivo_03_cox_survival_riesgo",
         "vulnerabilidad_sistemica", "ttm_06_recaida_ciclica", "duelo_bonanno_03_cronico",
         "eterno_retorno_03_desgaste_y_reinicio", "strauss_howe_03_the_unraveling"]
AUGE = ["12_obtencion", "2_salvacion", "35_recuperacion_de_lo_perdido", "9_audaz_empresa", "schwartz_07_logro",
        "monomito_09_la_recompensa", "monomito_11_la_resurreccion", "monomito_12_regreso_con_el_elixir",
        "kondratiev_01_primavera_expansion", "kondratiev_02_verano_auge", "cliodinamica_01_fase_expansiva_orden",
        "cliodinamica_04_fase_depresion_reconstruccion", "jaldun_01_asabiyyah_alta_cohesion", "duelo_bonanno_01_resiliencia",
        "duelo_bonanno_02_comun_recuperacion", "duelo_bonanno_05_mejoria_tras_perdida", "frye_mythos_comedia",
        "frye_mythos_romance", "eterno_retorno_02_cosmizacion_fundacion", "tainter_01_inversion_complejidad_productiva",
        "dialectica_03_sintesis_superacion_estructural", "strauss_howe_01_the_high", "social_04_rogers_difusion_innovaciones",
        "aliado", "mentor"]
ETIQUETAS = ("auge", "meseta", "caida", "ruptura")


def _serie(sf, fam, n):
    s = list(((sf.get(fam) or {}).get("serie_activacion")) or [])
    s = [float(x or 0.0) for x in s][:n]
    return s + [0.0] * (n - len(s))


def construir(result: dict) -> dict:
    mdf = result.get("movimiento_de_fondo") or {}
    sf = mdf.get("series_familias") or {}
    cortes = list(mdf.get("cortes") or [])
    u = ((mdf.get("umbrales") or {}).get("familias")) or {}
    EPS, GRANDE = float(u.get("EPS", 0.01)), float(u.get("GRANDE", 0.0624))
    NA, ND = float(u.get("NETO_ASC", 0.03)), float(u.get("NETO_DESC", 0.03))
    base = {"version": VERSION, "can_decide_H": False, "toca_H1_H2": False, "toca_apuesta_tematica": False,
            "etiquetas_posibles": list(ETIQUETAS), "es_probabilidad": False, "fuente_series": "movimiento_de_fondo.series_familias",
            "umbrales": {"EPS": EPS, "GRANDE": GRANDE, "NETO_ASC": NA, "NETO_DESC": ND}}
    n = len(cortes)
    if not sf or n < 2:
        return {**base, "estado": "SIN_TRAYECTORIA", "apuesta": "meseta", "motivo": "menos de 2 cortes o sin series de familias"}
    suma = lambda fams: [round(sum(_serie(sf, f, n)[k] for f in fams), 6) for k in range(n)]
    rup, cai, fav = suma(RUPTURA), suma(CAIDA), suma(AUGE)
    adv = [round(r + c, 6) for r, c in zip(rup, cai)]
    bal = [round(f - a, 6) for f, a in zip(fav, adv)]
    eje = mdf.get("eje"); se = _serie(sf, eje, n) if eje else [0.0] * n
    net = bal[-1] - bal[-2]; dR = rup[-1] - rup[-2]; dA = adv[-1] - adv[-2]; d_eje = se[-1] - max(se[:-1])
    if dR >= GRANDE and adv[-1] > fav[-1]:
        lab, por = "ruptura", "lo adverso brusco (RUPTURA) salta >= GRANDE en el último tramo y domina sobre lo favorable"
    elif net <= -ND or (adv[-1] > fav[-1] and dA > EPS) or (d_eje <= -ND and net < 0):
        lab, por = "caida", "el balance favorable-adverso empeora / lo adverso domina y sube / el eje del sujeto se apaga"
    elif net >= NA and fav[-1] >= adv[-1]:
        lab, por = "auge", "el balance mejora y lo favorable domina en Z"
    else:
        lab, por = "meseta", "sin cambio neto suficiente del balance"
    activas = lambda fams: sorted([(f, round(_serie(sf, f, n)[-1], 4)) for f in fams if _serie(sf, f, n)[-1] > 0], key=lambda x: -x[1])[:6]
    return {**base, "estado": "EJECUTADO", "apuesta": lab, "porque": por, "cortes": cortes,
            "series": {"favorable_auge": fav, "adverso_caida": cai, "adverso_ruptura": rup, "adverso_total": adv, "balance": bal, "eje": se},
            "senales": {"net_balance_ultimo_tramo": round(net, 6), "salto_ruptura": round(dR, 6), "salto_adverso": round(dA, 6),
                        "eje": eje, "caida_eje_vs_max_previo": round(d_eje, 6)},
            "familias_activas_en_Z": {"ruptura": activas(RUPTURA), "caida": activas(CAIDA), "auge": activas(AUGE)}}
