# PLANTILLA (no correr tal cual). La escribe el PREPARADOR, que NO conoce el final.
EV = lambda afirmacion, url, source_date, claim_date, tipo="primaria", **kw: {"afirmacion": afirmacion, "source_url": url,
     "source_date": source_date, "claim_date": claim_date, "tipo_fuente": tipo, "conocido_en_Z": "sí", **kw}
SEMILLAS_Z = [
 {"id": "LOTE_01_SUJETO", "person": "Nombre", "tipo": "politico|cientifico|artista|empresario|...",
  "question": "¿Qué trayectoria sigue <sujeto> tras <situación en Z>?",
  "z_trabajo": "AAAA-MM-DD", "modo_z": "historico",   # o "vivo" (Z = hoy)
  "preparacion_ciega": {"preparador_entrada": "ChatGPT-conversacion-A", "custodio_destino": "Mj", "vio_destino": False},
  "source_notes": "fuentes generales, solo hasta Z",
  # Opcional (A5 2026-11-07): "pistas_llm": [{"token": "...", "family": "<familia del catálogo 244>", "relevance": 0.8}]
  # Arquetipos que el preparador propone como vecinos del Caldero. Solo familias
  # del 244, sin nombres/alias del sujeto, sin futuro ni desenlace, sin años.
  # La fábrica valida con el guardián y descarta lo que no pasa (queda en la
  # auditoría de la entrada); la familia fuera de catálogo rechaza el lote.
  "cuts": [
    {"id": "C1_AAAA", "date": "AAAA-MM-DD", "hecho": "Hecho atestiguado en pasado, sin futuro.",
     "P": [("token", .80)], "A": [("token", .75)], "C": [("token", .70)],
     "evidencia": [EV("Qué afirma", "https://fuente", "AAAA-MM-DD", "AAAA-MM-DD", "primaria")]},
  ]},
]
