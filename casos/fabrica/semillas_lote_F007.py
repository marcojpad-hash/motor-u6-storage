# -*- coding: utf-8 -*-
"""Semillas Z — lote F007 (modo histórico, preparación a ciegas).
8 sujetos. Tokens solo de F004/F005. Destinos aparte.
"""
EV = lambda afirmacion, url, source_date, claim_date, tipo="secundaria", **kw: {
    "afirmacion": afirmacion, "source_url": url, "source_date": source_date,
    "claim_date": claim_date, "tipo_fuente": tipo, "conocido_en_Z": "sí", **kw}
CONSULTA = "2026-10-31"
SEC = "secundaria"
CIEGA = {"preparador_entrada": "GrokPrincipal-preparador-F007",
         "custodio_destino": "GrokPrincipal-custodio-ensayo-F007", "vio_destino": False}
WP = "https://en.wikipedia.org/wiki/"

SEMILLAS_Z = [
    {"id": "F007_01_VAN_GOGH", "person": "Vincent van Gogh", "tipo": "artista",
     "question": "¿Qué trayectoria sigue Vincent van Gogh después de su situación a finales de 1888?",
     "z_trabajo": "1888-12-31", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
     "source_notes": "Wikipedia EN a ciegas; hechos hasta 1888.",
     "cuts": [
         {"id": "C1_1886", "date": "1886",
          "hecho": "Llega a París, conoce impresionistas y empieza colores más brillantes; vive con Theo.",
          "P": [("autoexpresion", .78), ("inconformismo", .74)], "A": [("audacia", .76), ("esfuerzo_sostenido_reciente", .72)],
          "C": [("reconocimiento", .68), ("cambio", .70)],
          "evidencia": [EV("En 1886 se mudó a París y conoció a impresionistas; su paleta se volvió más brillante.", WP+"Vincent_van_Gogh", CONSULTA, "1886", SEC)]},
         {"id": "C2_1888", "date": "1888-02",
          "hecho": "Se traslada a Arles, alquila la Casa Amarilla y planea una colonia de artistas; pinta intensamente.",
          "P": [("idealismo", .76), ("ambicion", .72)], "A": [("planificacion_activa", .74), ("produccion", .78)],
          "C": [("aislamiento", .70), ("expectativa", .68)],
          "evidencia": [EV("En febrero de 1888 se mudó a Arles y alquiló la Casa Amarilla con la idea de una colonia de artistas.", WP+"Vincent_van_Gogh", CONSULTA, "1888-02", SEC)]},
     ]},
    # Nota: plantilla reducida. Expandir a 8 sujetos con tokens exactos de F005 antes del siguiente dispatch.
]
