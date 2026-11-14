# lateral_comportamiento_post_meseta_v1.py — Lectura del comportamiento una vez estabilizado (observación)
#
# Contrato: COMPORTAMIENTO_POST_MESETA_V1.md
#   can_decide_H = False (SENSOR, solo observa; no toca H1/H2 ni ranking).
#   No toca Engine ni catálogo 244. Solo LEE el RESULT ya armado.
#
# Idea de Marco (2026-11-13): no es leer nada más el fondo. Una vez que la
# medición SE ESTABILIZA (régimen MESeta_O_ESTABILIZACION), se ve el COMPORTAMIENTO:
# cómo se mueve TODO en general (no solo abajo). Eso da trazabilidad y puede
# hacer emerger un punto que antes no se había considerado. Y se tiene que
# MENCIONAR tal cual en la salida, porque si no los modelos que traducen el
# motor no lo ven: su entrenamiento es ver los top, entonces no ven lo que
# pasa abajo.
#
# Equivalente a cuando se encontró el eje que se armaba con las fórmulas
# después de ver la hélice: la estabilización revela el comportamiento.
#
# Uso (lector post-corrida sobre un RESULT completo):
#   from lateral_comportamiento_post_meseta_v1 import leer_resultado
#   out = leer_resultado(result_dict)
#
# Uso (sensor en post_predictor; fondo/picos opcionales):
#   out = observar(case, motor, pred, fondo=None, picos=None)

CAN_DECIDE_H = False
CONTRATO = "COMPORTAMIENTO_POST_MESETA_V1"
VERSION = "v3_20261113"  # v3: lectura degrada proporcionalidad si BAJA_MUESTRA + Sol nunca es nudo y distancia negativa documentados (revisión DeepSeek 2026-11-13)
REGIMEN_MESETA = "MESeta_O_ESTABILIZACION"


def _regimen_de_pred(pred):
    """Régimen dominante entre las candidatas (trazabilidad_geometrica)."""
    cands = (pred or {}).get("candidates") or []
    regs = []
    for c in cands:
        tg = (c or {}).get("trazabilidad_geometrica") or {}
        if tg.get("regimen"):
            regs.append(tg["regimen"])
    if not regs:
        return None, {}
    # el régimen de la H1 (primera candidata)
    return regs[0], {"regimenes_top": regs}


def _top_set(pred, result=None):
    """El 'top' que ven los modelos que traducen el motor: H1/H2 + top5 del 020."""
    top = set()
    cands = (pred or {}).get("candidates") or []
    for c in cands[:5]:
        if c.get("family"):
            top.add(c["family"])
    if result:
        si = result.get("salida_interpretable") or {}
        for h in (si.get("H1"), si.get("H2")):
            if isinstance(h, dict) and h.get("familia"):
                top.add(h["familia"])
        for h in (si.get("conjunto_hipotesis_abiertas") or {}).get("hipotesis") or []:
            if h.get("familia"):
                top.add(h["familia"])
    return top


def _confianza_prop(n):
    """Confianza de la proporcionalidad según el número de nudos (Gemini, 2026-11-13).
    Con pocos nudos un solo valor atípico puede invertir el signo de Pearson
    y cambiar la lectura de convergencia a consolidación. Por eso el valor
    siempre va acompañado de su n y de esta etiqueta."""
    if n < 8:
        return "BAJA_MUESTRA"
    if n < 12:
        return "MEDIA"
    return "ALTA"


def leer_gravedad(result):
    """Lectura gravitatoria (Marco, 2026-11-13): NO es gravedad terrestre.
    Es inercia de gravedad como un cometa que arrastra, o como el sol jalando
    a todos los cuerpos celestes dentro de su casa (la Vía Láctea).

    - SOL: la familia más pesada (H1), el atractor central. Todo es jalado
      hacia su peso. El Sol NUNCA es nudo: los nudos vienen de
      familias_bajo_top5_subiendo_de_rango (familias BAJO el top5) y H1 es el
      rango 1, así que está excluido por definición. El cometa mide el salto
      simultáneo de los NUDOS, no del Sol (el salto propio de H1 en el corte
      del cometa es pequeño o negativo en los casos verificados).
      Distancia negativa: si un nudo tuviera más peso que H1 en Z (no ocurre
      en los casos verificados: 0 distancias negativas en 5 casos + Bolívar),
      la distancia sería negativa y caería en CAPTURADO por definición
      (dist <= 0.01), es decir, por encima del Sol = capturado.
    - NUDOS: las familias que se movieron (bajo el top5 subiendo de rango).
      Se mide su distancia al Sol y su pendiente: ¿hay proporcionalidad?
      CAPTURADO = ya llegó al peso del Sol (dist <= 0.01).
      SIENDO_JALADO = lejos del Sol (dist > 0.05) y sube rápido (pend >= 0.5).
      ACERCANDOSE = lejos del Sol (dist > 0.05) y sube a velocidad media
      (0.2 <= pend < 0.5). RESISTE = lejos del Sol pero no sube (pend < 0.2):
      su propia gravedad, posible atractor rival. EN_TRANSITO = cerca del Sol
      (0.01 < dist <= 0.05), aún no capturado, a cualquier velocidad.
    - COMETA: el corte donde varios nudos saltan a la vez (un arrastre).
      Desempate: en empate de (nudos_que_suben, salto_total) gana el corte
      más temprano (primera ocurrencia, por comparación estricta).
      NOTA (DeepSeek 2026-11-13): el salto del cometa NO es separable del
      pulso de input. En los casos verificados, el 11-19% de TODA la
      masa_favor del run llega en el corte del cometa (Napoleón 16%,
      Mozart 11%, Transición1 18%, Mandela 19%). Los nudos saltan porque
      entró masa nueva (tokens) en ese corte. El cometa es un evento real
      y medible (el salto simultáneo), pero su causa es el pulso de input,
      no una dinámica gravitatoria pura.
    - PROPORCIONALIDAD: correlación de Pearson pendiente ~ distancia al Sol.
      Unidades heterogéneas (DeepSeek 2026-11-13): la pendiente es cambio
      de RANGO Z por corte y la distancia es diferencia de PESO (P_FULL_244).
      Pearson es invariante a escala, así que el número es válido, pero la
      lectura es SOLO DE SIGNO (convergencia + / consolidación -), no de
      elasticidad. Si la varianza de la distancia o de la pendiente es cero
      (todos los nudos con la misma distancia o la misma pendiente) es None
      (indefinida). Siempre va con su n y su confianza (ver _confianza_prop).
      Si la confianza es BAJA_MUESTRA, la lectura dice NO CONCLUYENTE: el
      número se reporta pero no se presenta como hallazgo.
    """
    result = result or {}
    si = result.get("salida_interpretable") or {}
    h1 = None
    h1d = si.get("H1")
    if isinstance(h1d, dict):
        h1 = h1d.get("familia")
    if not h1:
        cands = (result.get("pred") or {}).get("candidates") or []
        if cands:
            h1 = (cands[0] or {}).get("family")
    motor = result.get("motor") or {}
    cuts = motor.get("cuts") or []
    if not cuts or not h1:
        return {"sol": None, "nudos": [], "cometa": None, "proporcionalidad": None,
                "lectura": "sin cortes o sin H1: no hay lectura gravitatoria"}
    # peso del Sol y de cada nudo por corte (P_FULL_244)
    def peso(fam, idx):
        p = (cuts[idx] or {}).get("P_FULL_244") or {}
        v = p.get(fam)
        return v if isinstance(v, (int, float)) else None
    z = len(cuts) - 1
    peso_sol_z = peso(h1, z)
    mf = result.get("movimiento_de_fondo") or {}
    fams = mf.get("familias_bajo_top5_subiendo_de_rango") or []
    nudos = []
    for f in fams:
        fam = f.get("familia")
        pz = peso(fam, z)
        if pz is None:
            continue
        dist = (peso_sol_z - pz) if peso_sol_z is not None else None
        pend = f.get("pendiente_rango_por_corte_(+sube)")
        if dist is not None and dist <= 0.01:
            estado = "CAPTURADO"
        elif pend is not None and dist is not None and dist > 0.05 and pend >= 0.5:
            estado = "SIENDO_JALADO"
        elif dist is not None and dist > 0.05 and pend is not None and 0.2 <= pend < 0.5:
            # Gemini 2026-11-13: antes caía en EN_TRANSITO aunque estuviera lejos
            # del Sol, contradiciendo su definición ("cerca del Sol").
            estado = "ACERCANDOSE"
        elif dist is not None and dist > 0.05 and (pend is None or pend < 0.2):
            estado = "RESISTE"
        else:
            # cerca del Sol (0.01 < dist <= 0.05) a cualquier velocidad, o datos
            # incompletos: en tránsito hacia el Sol, aún no capturado.
            estado = "EN_TRANSITO"
        nudos.append({
            "familia": fam, "peso_Z": round(pz, 3),
            "distancia_al_sol": round(dist, 3) if dist is not None else None,
            "pendiente": pend, "rango_Z": f.get("rango_en_Z"),
            "primera_aparicion": f.get("primera_aparicion"),
            "clase": f.get("clase"), "estado": estado,
        })
    # cometa: corte con el mayor salto simultáneo de los nudos.
    # Desempate (Gemini 2026-11-13): comparación estricta (>) -> en empate de
    # (nudos_que_suben, salto_total) gana el corte más temprano (primera ocurrencia).
    cometa = None
    if len(cuts) >= 2 and nudos:
        mejor = None
        for i in range(1, len(cuts)):
            saltos = []
            for nd in nudos:
                a = peso(nd["familia"], i - 1)
                b = peso(nd["familia"], i)
                if a is not None and b is not None:
                    saltos.append(b - a)
            if saltos:
                suben = sum(1 for s in saltos if s > 0.05)
                total = sum(saltos)
                if mejor is None or (suben, total) > (mejor["nudos_que_suben"], mejor["salto_total"]):
                    mejor = {"corte": (cuts[i] or {}).get("corte"), "nudos_que_suben": suben,
                             "salto_total": round(total, 3)}
        cometa = mejor
    # proporcionalidad: correlación pendiente ~ distancia.
    # Varianza cero (todos los nudos con la misma distancia o la misma
    # pendiente) -> None (indefinida, división por cero evitada).
    # Confianza según n (Gemini 2026-11-13): con pocos nudos el signo es frágil.
    prop = None
    pares = [(nd["distancia_al_sol"], nd["pendiente"]) for nd in nudos
             if nd.get("distancia_al_sol") is not None and nd.get("pendiente") is not None]
    n_prop = len(pares)
    conf_prop = None
    if len(pares) >= 3:
        import math
        ds = [p[0] for p in pares]; ps = [p[1] for p in pares]
        n = len(ds); md = sum(ds) / n; mp = sum(ps) / n
        cov = sum((d - md) * (p - mp) for d, p in zip(ds, ps))
        sd = math.sqrt(sum((d - md) ** 2 for d in ds)); sp = math.sqrt(sum((p - mp) ** 2 for p in ps))
        prop = round(cov / (sd * sp), 3) if sd > 0 and sp > 0 else None
        conf_prop = _confianza_prop(n_prop) if prop is not None else None
    caps = [nd["familia"] for nd in nudos if nd["estado"] == "CAPTURADO"]
    jal = [nd["familia"] for nd in nudos if nd["estado"] == "SIENDO_JALADO"]
    acer = [nd["familia"] for nd in nudos if nd["estado"] == "ACERCANDOSE"]
    res = [nd["familia"] for nd in nudos if nd["estado"] == "RESISTE"]
    # Degradar la lectura si la confianza es BAJA_MUESTRA (DeepSeek 2026-11-13):
    # el número se reporta pero NO se presenta como hallazgo.
    if prop is not None and conf_prop == "BAJA_MUESTRA":
        prop_txt = f"proporcionalidad pendiente~distancia: {prop} (NO CONCLUYENTE, n={n_prop}, BAJA_MUESTRA)"
    elif prop is not None:
        prop_txt = f"proporcionalidad pendiente~distancia: {prop} (confianza {conf_prop}, n={n_prop})"
    else:
        prop_txt = ""
    lectura = (
        f"sol {h1} (peso Z {peso_sol_z}); capturados: {len(caps)}; siendo jalados: {len(jal)}; "
        f"acercándose: {len(acer)}; resisten: {len(res)}"
        + (f"; cometa en {cometa['corte']} ({cometa['nudos_que_suben']} nudos suben)" if cometa and cometa.get("nudos_que_suben", 0) >= 2 else "")
        + (f"; {prop_txt}" if prop_txt else "")
    )
    return {
        "sol": {"familia": h1, "peso_Z": peso_sol_z},
        "nudos": nudos,
        "cometa": cometa,
        "proporcionalidad": prop,
        "n_nudos_proporcionalidad": n_prop,
        "confianza_proporcionalidad": conf_prop,
        "capturados": caps, "siendo_jalados": jal, "acercandose": acer, "resisten": res,
        "lectura": lectura,
    }


def proyectar_gravedad(result, hasta_corte=None):
    """Versión PROYECTIVA de la gravedad (Marco, 2026-11-13). La retrospectiva
    (leer_gravedad) NO se elimina: queda como referencia para comparación e
    ingeniería inversa. Esta función es una ADICIÓN.

    Lee solo los cortes hasta `hasta_corte` (por defecto, todos los que trae
    el RESULT) y proyecta hacia adelante, corte por corte:

    - CAPTURA PREVISTA: si la distancia al Sol se está cerrando de forma
      monótona (últimos 3 cortes), se extrapola linealmente el corte en que
      llega a 0. Si la distancia oscila o no se cierra: NO_PROYECTABLE.
    - PULSO DETECTADO: si en el corte `hasta_corte` llegó masa_favor (>0),
      un pulso acaba de entrar. Los pulsos se repiten a los ~3-4 cortes
      (Napoleón C5->C9, Mozart C6->C9): se advierte un posible cometa en
      los siguientes 1-3 cortes (alerta, no predicción exacta).
    - DIRECCIÓN: signo de la proporcionalidad hasta ahora (convergencia +
      o consolidación -), si hay suficientes nudos.

    LÍMITE HONESTO: el salto del cometa lo causa un pulso nuevo de masa_favor
    que llega con el contenido del corte (tokens nuevos del input). No se
    puede predecir el corte exacto ni el tamaño del salto antes de que el
    pulso llegue, porque eso sería predecir el contenido del siguiente corte.
    Lo proyectivo es la extrapolación de la tendencia y la alerta temprana
    cuando el pulso ya entró.
    """
    result = result or {}
    si = result.get("salida_interpretable") or {}
    h1 = None
    h1d = si.get("H1")
    if isinstance(h1d, dict):
        h1 = h1d.get("familia")
    if not h1:
        cands = (result.get("pred") or {}).get("candidates") or []
        if cands:
            h1 = (cands[0] or {}).get("family")
    motor = result.get("motor") or {}
    cuts = motor.get("cuts") or []
    if not cuts or not h1:
        return {"proyectable": False, "motivo": "sin cortes o sin H1"}
    # hasta_corte: nombre de corte ('C6') o índice; por defecto el último
    if hasta_corte is None:
        k = len(cuts) - 1
    elif isinstance(hasta_corte, str):
        k = next((i for i, c in enumerate(cuts) if (c or {}).get("corte") == hasta_corte), len(cuts) - 1)
    else:
        k = max(0, min(int(hasta_corte), len(cuts) - 1))
    corte_k = (cuts[k] or {}).get("corte")

    def peso(fam, idx):
        p = (cuts[idx] or {}).get("P_FULL_244") or {}
        v = p.get(fam)
        return v if isinstance(v, (int, float)) else None

    mf = result.get("movimiento_de_fondo") or {}
    sf = mf.get("series_familias") or {}
    fams = mf.get("familias_bajo_top5_subiendo_de_rango") or []
    # familias a proyectar: las del fondo + las que tienen serie
    fams_nombres = []
    for f in fams:
        if f.get("familia"):
            fams_nombres.append(f["familia"])
    peso_sol_k = peso(h1, k)
    proyecciones = []
    for fam in fams_nombres:
        # distancia al Sol en los últimos cortes (hasta k)
        dists = []
        for i in range(max(0, k - 4), k + 1):
            ps = peso(h1, i); pn = peso(fam, i)
            if ps is not None and pn is not None:
                dists.append((i, ps - pn))
        if len(dists) < 3:
            proyecciones.append({"familia": fam, "proyectable": False, "motivo": "pocos cortes con peso"})
            continue
        # ¿se cierra de forma monótona en los últimos 3?
        ult = [d for _, d in dists[-3:]]
        cierra = all(ult[i + 1] <= ult[i] + 1e-9 for i in range(len(ult) - 1)) and ult[-1] < ult[0]
        captura = None
        if cierra and len(ult) >= 2:
            # extrapolación lineal con la pendiente de los últimos 3
            import math
            xs = list(range(len(ult))); ys = ult
            n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
            den = sum((x - mx) ** 2 for x in xs)
            m = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0
            if m < -1e-9:
                pasos = my / (-m) if my > 0 else 0
                idx_cap = k + int(math.ceil(pasos))
                captura = (cuts[idx_cap] or {}).get("corte") if idx_cap < len(cuts) else f"despues_de_{(cuts[-1] or {}).get('corte')}"
        # pulso de masa en el corte k
        s = sf.get(fam) or {}
        masa = s.get("masa_favor_por_corte") or []
        pulso_k = masa[k] if k < len(masa) else 0
        proyecciones.append({
            "familia": fam,
            "distancia_al_sol_k": round(dists[-1][1], 3),
            "cierra": bool(cierra),
            "captura_prevista": captura,
            "pulso_masa_en_k": pulso_k,
            "proyectable": True,
        })
    # alerta de cometa: ¿llegó un pulso en k?
    pulsos_k = [p for p in proyecciones if isinstance(p.get("pulso_masa_en_k"), (int, float)) and p["pulso_masa_en_k"] > 0]
    cometa_previsto = None
    if len(pulsos_k) >= 2:
        cometa_previsto = {
            "alerta": f"pulso de masa en {corte_k} en {len(pulsos_k)} nudos; posible cometa en los siguientes 1-3 cortes",
            "nudos_con_pulso": [p["familia"] for p in pulsos_k],
        }
    # dirección hasta ahora (proporcionalidad con los datos hasta k).
    # Misma regla que en leer_gravedad: varianza cero -> None; confianza por n.
    prop = None
    pares = []
    for p in proyecciones:
        if p.get("proyectable") and p.get("distancia_al_sol_k") is not None:
            f = next((x for x in fams if x.get("familia") == p["familia"]), {})
            pend = f.get("pendiente_rango_por_corte_(+sube)")
            if pend is not None:
                pares.append((p["distancia_al_sol_k"], pend))
    n_prop_k = len(pares)
    conf_prop_k = None
    if len(pares) >= 3:
        import math
        ds = [x[0] for x in pares]; ps = [x[1] for x in pares]
        n = len(ds); md = sum(ds) / n; mp = sum(ps) / n
        cov = sum((d - md) * (p - mp) for d, p in zip(ds, ps))
        sd = math.sqrt(sum((d - md) ** 2 for d in ds)); sp = math.sqrt(sum((p - mp) ** 2 for p in ps))
        prop = round(cov / (sd * sp), 3) if sd > 0 and sp > 0 else None
        conf_prop_k = _confianza_prop(n_prop_k) if prop is not None else None
    # Degradar la lectura si la confianza es BAJA_MUESTRA (DeepSeek 2026-11-13).
    if prop is not None and conf_prop_k == "BAJA_MUESTRA":
        prop_txt_k = f"proporcionalidad hasta aquí: {prop} (NO CONCLUYENTE, n={n_prop_k}, BAJA_MUESTRA)"
    elif prop is not None:
        prop_txt_k = f"proporcionalidad hasta aquí: {prop} (confianza {conf_prop_k}, n={n_prop_k})"
    else:
        prop_txt_k = ""
    return {
        "contrato": CONTRATO, "version": VERSION, "can_decide_H": CAN_DECIDE_H,
        "modo": "PROYECTIVO", "hasta_corte": corte_k,
        "sol": h1, "peso_sol_k": peso_sol_k,
        "proyecciones": proyecciones,
        "cometa_previsto": cometa_previsto,
        "proporcionalidad_hasta_k": prop,
        "n_nudos_proporcionalidad_hasta_k": n_prop_k,
        "confianza_proporcionalidad_hasta_k": conf_prop_k,
        "lectura": (
            f"proyección hasta {corte_k}: "
            f"{sum(1 for p in proyecciones if p.get('captura_prevista'))} capturas previstas; "
            + (cometa_previsto["alerta"] if cometa_previsto else "sin pulso de masa en este corte")
            + (f"; {prop_txt_k}" if prop_txt_k else "")
        ),
    }


def leer_resultado(result):
    """Lee un RESULT completo y produce la lectura de comportamiento post-meseta."""
    result = result or {}
    si = result.get("salida_interpretable") or {}
    # régimen: de la apuesta / del conjunto de hipótesis
    regimen = None
    apuesta = si.get("apuesta_multiescenario") or {}
    ap = apuesta.get("apuesta_principal") or {}
    if ap.get("escenario"):
        regimen = ap["escenario"]
    if not regimen:
        hips = (si.get("conjunto_hipotesis_abiertas") or {}).get("hipotesis") or []
        if hips:
            regimen = ((hips[0] or {}).get("trazabilidad_geometrica") or {}).get("regimen")
    if not regimen:
        # fallback: trazabilidad de la primera hipótesis en /hipotesis
        hips = result.get("hipotesis") or []
        if hips:
            regimen = ((hips[0] or {}).get("trazabilidad_geometrica") or {}).get("regimen")

    en_meseta = (regimen == REGIMEN_MESETA)
    if not en_meseta:
        return {
            "contrato": CONTRATO, "version": VERSION, "can_decide_H": CAN_DECIDE_H,
            "en_meseta": False, "regimen": regimen,
            "lectura": "no estabilizado en meseta: no hay lectura de comportamiento post-meseta",
        }

    mf = result.get("movimiento_de_fondo") or {}
    pm = (result.get("features") or {}).get("plugin_picos_mesetas.py") or {}
    # trazabilidad geométrica (H1)
    hips = (si.get("conjunto_hipotesis_abiertas") or {}).get("hipotesis") or []
    tg_h1 = ((hips[0] or {}).get("trazabilidad_geometrica") or {}) if hips else {}

    # --- comportamiento: cómo se mueve todo ---
    resumen = mf.get("resumen_clases") or {}
    cocina = mf.get("lo_que_se_cocina_abajo") or []
    toks_cocina = mf.get("tokens_que_se_cocinan_abajo") or []
    fams_subiendo = mf.get("familias_bajo_top5_subiendo_de_rango") or []
    # curvas picos/mesetas: forma por familia
    curvas = pm.get("curvas") or {}
    formas = {f: (c or {}).get("forma") for f, c in curvas.items()}

    # --- lo que emerge (con peso), ordenado por pendiente ---
    emergentes = []
    for f in fams_subiendo:
        if f.get("emergente"):
            emergentes.append({
                "familia": f.get("familia"),
                "rango_en_Z": f.get("rango_en_Z"),
                "pendiente_rango_por_corte": f.get("pendiente_rango_por_corte_(+sube)"),
                "clase": f.get("clase"),
            })
    emergentes.sort(key=lambda x: (x.get("pendiente_rango_por_corte") or 0), reverse=True)

    # --- punto no considerado: lo que emerge y NO está en el top ---
    top = _top_set(None, result)
    punto_no_considerado = None
    for e in emergentes:
        if e.get("familia") and e["familia"] not in top:
            punto_no_considerado = e
            break
    # si nada emerge, el punto no considerado puede ser una familia subiendo
    # de rango que no está en el top (aunque su clase sea LATENTE_DORMIDO)
    if punto_no_considerado is None:
        for f in fams_subiendo:
            fam = f.get("familia")
            if fam and fam not in top:
                punto_no_considerado = {
                    "familia": fam,
                    "rango_en_Z": f.get("rango_en_Z"),
                    "pendiente_rango_por_corte": f.get("pendiente_rango_por_corte_(+sube)"),
                    "clase": f.get("clase"),
                    "nota": "sube de rango bajo el top5 pero clasificada LATENTE_DORMIDO (no emergente por umbral)",
                }
                break

    # --- trazabilidad: el eje geométrico en meseta ---
    trazabilidad = {
        "regimen": regimen,
        "micro": tg_h1.get("micro"),
        "meso": tg_h1.get("meso"),
        "macro": tg_h1.get("macro"),
        "aceleracion": tg_h1.get("aceleracion"),
        "divergencia_entre_escala": tg_h1.get("divergencia_entre_escala"),
        "n_cortes_observados": tg_h1.get("n_cortes_observados"),
    }

    n_fams_subiendo = len(fams_subiendo)
    lectura = (
        f"estabilizado en meseta: {n_fams_subiendo} familias bajo el top5 suben de rango; "
        f"lo que se cocina abajo: {len(cocina)} familias / {len(toks_cocina)} tokens; "
        f"emergentes: {len(emergentes)}"
        + (f"; punto no considerado: {punto_no_considerado['familia']} (rango Z {punto_no_considerado.get('rango_en_Z')}, pendiente {punto_no_considerado.get('pendiente_rango_por_corte')})" if punto_no_considerado else "; sin punto emergente fuera del top")
    )
    gravedad = leer_gravedad(result)
    return {
        "contrato": CONTRATO, "version": VERSION, "can_decide_H": CAN_DECIDE_H,
        "en_meseta": True, "regimen": regimen,
        "comportamiento": {
            "resumen_clases_fondo": resumen,
            "familias_bajo_top5_subiendo_de_rango": n_fams_subiendo,
            "lo_que_se_cocina_abajo_n": len(cocina),
            "tokens_que_se_cocinan_abajo_n": len(toks_cocina),
            "formas_picos_mesetas": formas,
        },
        "lo_que_emerge": emergentes,
        "punto_no_considerado": punto_no_considerado,
        "trazabilidad": trazabilidad,
        "gravedad": gravedad,
        "lectura": lectura + "; " + gravedad.get("lectura", ""),
    }


def observar(case, motor, pred, fondo=None, picos=None):
    """Sensor para post_predictor. Lee el régimen de pred y el comportamiento
    del fondo/picos si se pasan; si no, reporta el régimen y queda en espera
    de la lectura completa (leer_resultado sobre el RESULT)."""
    regimen, info = _regimen_de_pred(pred)
    if regimen != REGIMEN_MESETA:
        return {
            "contrato": CONTRATO, "version": VERSION, "can_decide_H": CAN_DECIDE_H,
            "en_meseta": False, "regimen": regimen,
            "lectura": "no estabilizado en meseta: no hay lectura de comportamiento post-meseta",
        }
    # En meseta: si no hay fondo/picos disponibles aquí (el fondo corre después
    # de post_predictor), la lectura completa se hace con leer_resultado().
    return {
        "contrato": CONTRATO, "version": VERSION, "can_decide_H": CAN_DECIDE_H,
        "en_meseta": True, "regimen": regimen,
        "lectura": "estabilizado en meseta: lectura completa con leer_resultado() sobre el RESULT (fondo + picos/mesetas)",
        "nota": "el fondo corre después de post_predictor; la lectura completa se hace post-corrida",
    }
