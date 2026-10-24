"""Léxico estructural del PERFIL DEL NARRADOR v0.1 (sombrero blanco).
Todo es regla escrita y auditable. Vocabulario neutro: describe CÓMO está escrito el input,
no juzga a nadie. NO hay dimensiones de escolaridad, lugar, origen ni demografía.

Por token de entrada (los 117 del diagnóstico) se asignan 3 rasgos:
  naturaleza : EVENTO (hecho filmable / acto / suceso) | ESTADO_INTERNO (afecto, emoción, estado subjetivo)
               | RASGO (atributo o etiqueta del sujeto) | COGNICION (proceso mental) | RELACION (vínculo)
  locus      : a quién atribuye agencia el token: SUJETO | OTROS_PERSONAS | GRUPO_INSTITUCION
               | CIRCUNSTANCIA | COMPARTIDA (dos o más partes) | INDETERMINADO
  tiempo     : PASADO | PRESENTE | FUTURO | NEUTRO (orientación temporal del token)
Tokens no listados -> NO_CLASIFICADO (se reporta; no se adivina).
"""
E, I, R, C, V = "EVENTO", "ESTADO_INTERNO", "RASGO", "COGNICION", "RELACION"
S, O, G, K, X, N = "SUJETO", "OTROS_PERSONAS", "GRUPO_INSTITUCION", "CIRCUNSTANCIA", "COMPARTIDA", "INDETERMINADO"
PA, PR, FU, NE = "PASADO", "PRESENTE", "FUTURO", "NEUTRO"
TOKENS = {
 "abandono_en_prueba": (E, S, NE), "aburrimiento": (I, N, PR), "aislamiento_voluntario": (E, S, PR),
 "alianza": (V, X, NE), "alivio": (I, N, PR), "ambicion": (R, S, FU), "analisis": (C, S, NE),
 "ansiedad": (I, N, FU), "antesala": (E, K, FU), "anuncio": (E, K, FU), "aprendizaje": (C, S, NE),
 "audacia": (R, S, NE), "autoexpresion": (E, S, NE), "autonomia": (R, S, NE), "autonomia_temprana": (R, S, PA),
 "autoridad": (V, G, NE), "bloqueo": (E, N, PR), "busqueda_cercania": (V, S, NE), "busqueda_identidad": (C, S, NE),
 "busqueda_libertad": (R, S, FU), "busqueda_verdad": (C, S, NE), "cambio_identidad": (E, S, NE),
 "catarsis": (I, N, NE), "competitividad": (R, S, NE), "comprension_nueva": (C, S, NE), "compromiso": (V, S, NE),
 "compromiso_afectivo": (V, X, NE), "compromiso_pragmatico": (V, X, NE), "conflicto_lealtad": (V, X, NE),
 "confrontacion_directa": (E, X, NE), "conocimiento": (C, S, NE), "consejo": (E, O, NE),
 "consumo_sustancias": (E, S, NE), "cotidiano": (E, K, PR), "creatividad": (R, S, NE), "crisis_abrupta": (E, K, NE),
 "crisis_existencial": (I, S, NE), "desafio": (E, K, NE), "desafio_autoridad": (E, S, NE), "desafio_sagrado": (E, S, NE),
 "desapego_emocional": (I, S, NE), "desastre": (E, K, NE), "desconfianza_autoridad": (I, S, NE),
 "desobediencia": (E, S, NE), "desorientacion_relacional": (I, S, NE), "dilema_moral": (C, S, NE),
 "disrupcion": (E, S, NE), "dogmatismo": (R, N, NE), "duelo": (I, N, PA), "empresa": (E, G, NE), "enigma": (C, K, NE),
 "error_juicio": (E, S, PA), "escalada": (E, X, NE), "escepticismo": (R, S, NE), "estancamiento": (E, K, PR),
 "estancamiento_generativo_personal": (I, S, PR), "evitacion": (E, S, NE), "evitacion_intimidad": (E, S, NE),
 "evitacion_riesgo": (E, S, NE), "formacion_literaria": (E, S, PA), "formacion_literaria_creativa": (E, S, PA),
 "frialdad_ante_crisis": (R, S, NE), "generacion_ideas": (C, S, FU), "guia": (E, O, NE), "herramienta_nueva": (E, N, NE),
 "hostilidad": (V, X, NE), "huida_del_llamado": (E, S, NE), "incertidumbre": (I, N, FU), "incidente_detonante": (E, K, NE),
 "indecision": (I, S, NE), "intuicion_alta": (C, S, NE), "invitacion": (E, O, FU), "lealtad_pareja": (V, X, NE),
 "liderazgo": (R, S, NE), "llamado": (E, K, FU), "llamado_aventura": (E, K, FU), "miedo_cambio": (I, S, FU),
 "miedo_estancamiento": (I, S, FU), "misterio": (C, K, NE), "noticia_ruptura": (E, O, NE), "obstaculo": (E, K, NE),
 "obstaculo_amoroso": (E, X, NE), "obtencion": (E, S, NE), "oportunidad": (E, K, FU), "optimismo": (I, N, FU),
 "organizacion": (E, G, NE), "orgullo_superacion": (I, S, PA), "partida": (E, S, NE), "perdida": (E, K, PA),
 "perdida_familiar": (E, O, PA), "persecucion": (E, G, NE), "planificacion": (C, S, FU), "pragmatismo_frio": (R, S, NE),
 "proposito_claro": (R, S, FU), "prueba": (E, K, NE), "rebeldia": (R, S, NE), "rebelion": (E, X, NE),
 "rechazo_ritual_autoritario": (E, S, NE), "recompensa": (E, K, NE), "reconocimiento": (E, O, NE),
 "recuperacion": (E, S, NE), "reflexion": (C, S, NE), "resolucion": (E, S, NE), "responsabilidad": (R, S, NE),
 "retorno": (E, S, PA), "rivalidad": (V, X, NE), "ruptura_pasado": (E, S, PA), "rutina": (E, K, PR),
 "sabiduria": (R, S, NE), "sacrificio": (E, S, NE), "tension_alta": (I, N, PR), "transformacion": (E, S, NE),
 "turno_atipico_nocturno": (E, K, PR), "umbral_abierto": (E, K, FU), "viaje": (E, S, NE),
 "vinculo_compartido": (V, X, NE), "visionario": (R, S, FU),
}

# ---- Capa TEXTO (es + en; los source_note vienen en inglés). Conteo de marcadores, APROX_BARATA. ----
ESCALA_TEXTO = {
 "micro": ["familia", "pareja", "hijo", "hija", "padre", "madre", "hermano", "amigo", "amiga", "personal", "infancia",
           "matrimonio", "divorcio", "salud", "family", "wife", "husband", "son", "daughter", "father", "mother",
           "brother", "friend", "personal", "childhood", "marriage", "divorce", "health", "graduation", "interest"],
 "meso": ["empresa", "compania", "equipo", "organizacion", "socios", "colegas", "pares", "comunidad", "universidad",
          "laboral", "gerencial", "operativo", "company", "firm", "team", "startup", "organization", "board",
          "investors", "partners", "peers", "university", "academy", "founded", "founding", "ipo", "acquisition",
          "launch", "product", "scale", "ceo", "role", "studio", "store"],
 "macro": ["estado", "gobierno", "nacion", "pais", "ley", "regimen", "iglesia", "inquisicion", "institucional",
           "politica", "guerra", "imperio", "sociedad", "mercado", "state", "government", "nation", "country", "law",
           "regulation", "church", "inquisition", "institutional", "authority", "political", "public", "war",
           "empire", "society", "market", "paradigm", "censorship", "nasa", "federal"],
}
EMOCION_TEXTO = ["miedo", "alegria", "tristeza", "ira", "enojo", "ansiedad", "orgullo", "verguenza", "culpa", "amor",
                 "odio", "frustracion", "alivio", "esperanza", "sufrimiento", "feliz", "afectivo", "afectiva", "pasion",
                 "fear", "joy", "sad", "anger", "anxiety", "pride", "shame", "guilt", "love", "hate", "frustration",
                 "relief", "hope", "grief", "happy", "passion", "obsession", "emotional", "turmoil"]
CERTEZA_ALTA = ["siempre", "nunca", "claramente", "sin duda", "definitivamente", "obviamente", "evidente", "seguro",
                "always", "never", "clearly", "definitely", "obviously", "certainly", "undoubtedly", "proven"]
CERTEZA_BAJA = ["quiza", "quizas", "posiblemente", "probablemente", "parece", "aproximadamente", "aprox", "tal vez",
                "supuestamente", "presunto", "maybe", "perhaps", "possibly", "probably", "seems", "reportedly",
                "allegedly", "approximately", "around", "circa", "unclear", "may", "might"]
FUTURO_TEXTO = ["proximos", "futuro", "sera", "va a", "iran", "will", "future", "next", "plans", "upcoming"]
PASADO_TEXTO = ["fue", "era", "hubo", "desde", "antes", "was", "were", "had", "former", "early", "before"]
VERBO_ACCION_SUJETO = ["fundo", "creo", "lanzo", "dejo", "construyo", "publico", "decidio", "renuncio", "entro",
                       "founded", "launched", "created", "left", "built", "published", "decided", "resigned",
                       "joined", "returned", "sold", "bought", "moved", "started", "led", "invented", "designed"]
PASIVA_IMPERSONAL_RX = r"\b(?:fue|fueron|was|were|been|is|are)\s+\w+(?:ado|ada|ido|ida|ed|en)\b|\bse\s+[a-z]+(?:a|o|e|an|en|aron|ieron)\b"
