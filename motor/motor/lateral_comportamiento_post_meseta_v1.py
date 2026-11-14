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
VERSION = "v1_20261113"
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


def leer_gravedad(result):
    """Lectura gravitatoria (Marco, 2026-11-13): NO es gravedad terrestre.
    Es inercia de gravedad como un cometa que arrastra, o como el sol jalando
    a todos los cuerpos celestes dentro de su casa (la Vía Láctea).

    - SOL: la familia más pesada (H1), el atractor central. Todo es jalado
      hacia su peso.
    - NUDOS: las familias que se movieron (bajo el top5 subiendo de rango).
      Se mide su distancia al Sol y su pendiente: ¿hay proporcionalidad?
      CAPTURADO = ya llegó al peso del Sol. SIENDO_JALADO = sube hacia el
      Sol, proporcional a su distancia. RESISTE = lejos del Sol pero no sube
      (su propia gravedad, posible atractor rival).
    - COMETA: el corte donde varios nudos saltan a la vez (un arrastre).
    - PROPORCIONALIDAD: correlación pendiente ~ distancia al Sol.
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
        elif dist is not None and dist > 0.05 and (pend is None or pend < 0.2):
            estado = "RESISTE"
        else:
            estado = "EN_TRANSITO"
        nudos.append({
            "familia": fam, "peso_Z": round(pz, 3),
            "distancia_al_sol": round(dist, 3) if dist is not None else None,
            "pendiente": pend, "rango_Z": f.get("rango_en_Z"),
            "primera_aparicion": f.get("primera_aparicion"),
            "clase": f.get("clase"), "estado": estado,
        })
    # cometa: corte con el mayor salto simultáneo de los nudos
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
    # proporcionalidad: correlación pendiente ~ distancia
    prop = None
    pares = [(nd["distancia_al_sol"], nd["pendiente"]) for nd in nudos
             if nd.get("distancia_al_sol") is not None and nd.get("pendiente") is not None]
    if len(pares) >= 3:
        import math
        ds = [p[0] for p in pares]; ps = [p[1] for p in pares]
        n = len(ds); md = sum(ds) / n; mp = sum(ps) / n
        cov = sum((d - md) * (p - mp) for d, p in zip(ds, ps))
        sd = math.sqrt(sum((d - md) ** 2 for d in ds)); sp = math.sqrt(sum((p - mp) ** 2 for p in ps))
        prop = round(cov / (sd * sp), 3) if sd > 0 and sp > 0 else None
    caps = [nd["familia"] for nd in nudos if nd["estado"] == "CAPTURADO"]
    jal = [nd["familia"] for nd in nudos if nd["estado"] == "SIENDO_JALADO"]
    res = [nd["familia"] for nd in nudos if nd["estado"] == "RESISTE"]
    lectura = (
        f"sol {h1} (peso Z {peso_sol_z}); capturados: {len(caps)}; siendo jalados: {len(jal)}; "
        f"resisten: {len(res)}"
        + (f"; cometa en {cometa['corte']} ({cometa['nudos_que_suben']} nudos suben)" if cometa and cometa.get("nudos_que_suben", 0) >= 2 else "")
        + (f"; proporcionalidad pendiente~distancia: {prop}" if prop is not None else "")
    )
    return {
        "sol": {"familia": h1, "peso_Z": peso_sol_z},
        "nudos": nudos,
        "cometa": cometa,
        "proporcionalidad": prop,
        "capturados": caps, "siendo_jalados": jal, "resisten": res,
        "lectura": lectura,
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
