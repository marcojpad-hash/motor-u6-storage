# -*- coding: utf-8 -*-
"""Semillas Z — lote F002 (modo histórico, preparación a ciegas).

Preparado por GrokBot-preparador-ciego-F002 sin ver los destinos sellados.
Cada corte está fechado en o antes del Z de trabajo y solo describe hechos
conocidos en esa fecha. Las fuentes secundarias (Wikipedia, reimpresiones)
se usan en modo histórico con preparación ciega declarada; su source_date es
la fecha de consulta. Las fuentes primarias llevan su fecha de publicación.
"""

EV = lambda afirmacion, url, source_date, claim_date, tipo="primaria", **kw: {
    "afirmacion": afirmacion, "source_url": url, "source_date": source_date,
    "claim_date": claim_date, "tipo_fuente": tipo, "conocido_en_Z": "sí", **kw}

CONSULTA = "2026-10-25"  # fecha de consulta de fuentes secundarias en línea
SEC = "secundaria"
CIEGA = {"preparador_entrada": "GrokBot-preparador-ciego-F002",
         "custodio_destino": "GrokBot-custodio-rutina-F002",
         "vio_destino": False}

WP = "https://en.wikipedia.org/wiki/"

SEMILLAS_Z = [
    # ------------------------------------------------------------------ 01
    {
        "id": "F002_01_GALILEI", "person": "Galileo Galilei", "tipo": "cientifico",
        "question": "¿Qué trayectoria sigue Galileo Galilei tras imprimir en Florencia, con licencia eclesiástica, su Diálogo sobre los dos máximos sistemas del mundo?",
        "z_trabajo": "1632-03-31", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta la impresión del Diálogo.",
        "cuts": [
            {"id": "C1_1610", "date": "1610-03-13",
             "hecho": "Publicó el Sidereus Nuncius con sus observaciones telescópicas, dedicado a Cosme II de Médici; llamó estrellas mediceas a las lunas de Júpiter que había descubierto, y el gesto le ayudó a obtener el puesto de matemático y filósofo principal de los Médici.",
             "P": [("conocimiento", .82), ("curiosidad_abstracta", .78)],
             "A": [("herramienta_nueva", .82), ("analisis", .80)],
             "C": [("reconocimiento", .78), ("oportunidad", .75)],
             "evidencia": [
                 EV("El Sidereus Nuncius se publicó el 13 de marzo de 1610 y estaba dedicado a Cosme II de Médici, con las lunas llamadas estrellas mediceas.", WP + "Sidereus_Nuncius", CONSULTA, "1610-03-13", SEC),
                 EV("La dedicatoria le ayudó a obtener el puesto de matemático y filósofo principal de los Médici.", WP + "Sidereus_Nuncius", CONSULTA, "1610", SEC),
             ]},
            {"id": "C2_1623", "date": "1623-10",
             "hecho": "Tras un decreto eclesiástico de 1616 que suspendió el libro de Copérnico hasta su corrección, el cardenal Maffeo Barberini, amigo y admirador suyo que se había opuesto a la amonestación de Galileo, fue elegido papa Urbano VIII en 1623; en octubre de 1623 Galileo publicó en Roma El ensayador, dedicado al nuevo papa y recibido con amplio aplauso.",
             "P": [("busqueda_verdad", .80), ("ambicion", .72)],
             "A": [("persuasion", .75), ("burla", .70)],
             "C": [("redes_prestigio", .78), ("prohibicion", .65)],
             "evidencia": [
                 EV("En 1616 un decreto de una congregación eclesiástica de Roma suspendió De revolutionibus hasta su corrección.", WP + "Galileo_Galilei", CONSULTA, "1616", SEC),
                 EV("Barberini, amigo y admirador de Galileo, se había opuesto a la amonestación de 1616 y fue elegido papa Urbano VIII en 1623.", WP + "Galileo_Galilei", CONSULTA, "1623", SEC),
                 EV("El ensayador se publicó en Roma en octubre de 1623, dedicado a Urbano VIII, con amplio aplauso.", WP + "The_Assayer", CONSULTA, "1623-10", SEC),
             ]},
            {"id": "C3_1632", "date": "1632-02-22",
             "hecho": "Publicó el Diálogo sobre los dos máximos sistemas del mundo, que comparaba el sistema copernicano con el ptolemaico, con autorización formal de la Iglesia y permiso papal; la obra estaba dedicada a Fernando II de Médici, que recibió el primer ejemplar impreso el 22 de febrero de 1632.",
             "P": [("busqueda_verdad", .82), ("orgullo", .70)],
             "A": [("persuasion", .78), ("audacia", .72)],
             "C": [("legitimidad_percibida", .75), ("redes_prestigio", .72)],
             "evidencia": [
                 EV("El Diálogo se publicó en 1632 con autorización formal de la Iglesia y permiso papal.", WP + "Galileo_Galilei", CONSULTA, "1632-02-22", SEC),
                 EV("El Diálogo comparaba los sistemas copernicano y ptolemaico, estaba dedicado a Fernando II y el primer ejemplar impreso se entregó el 22 de febrero de 1632.", WP + "Dialogue_Concerning_the_Two_Chief_World_Systems", CONSULTA, "1632-02-22", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 02
    {
        "id": "F002_02_PASTEUR", "person": "Louis Pasteur", "tipo": "cientifico",
        "question": "¿Qué trayectoria sigue Louis Pasteur tras presentar ante la Academia de Ciencias sus ensayos de inmunización contra la rabia en perros?",
        "z_trabajo": "1885-06-30", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia (inglés y francés), reimpresión en PMC, índice de artículos de Pasteur en los Comptes rendus y una crónica veterinaria de junio de 1884 (Persée, fuente primaria).",
        "cuts": [
            {"id": "C1_1862", "date": "1862",
             "hecho": "Sus experimentos contra la generación espontánea, repetidos con Claude Bernard el 20 de abril de 1862, le valieron ese año el premio Alhumbert de 2500 francos de la Academia de Ciencias.",
             "P": [("busqueda_verdad", .82), ("conocimiento", .78)],
             "A": [("verificacion", .80), ("metodicidad", .78)],
             "C": [("reconocimiento", .76), ("rivalidad_profesional", .66)],
             "evidencia": [
                 EV("Recibió el premio Alhumbert (2500 francos) en 1862 por sus experimentos contra la generación espontánea; las pruebas con Claude Bernard se hicieron el 20 de abril de 1862.", WP + "Louis_Pasteur", CONSULTA, "1862", SEC),
             ]},
            {"id": "C2_1881", "date": "1881-06-02",
             "hecho": "En Pouilly-le-Fort inoculó ovejas y cabras con cultivos atenuados de carbunco el 5 y el 17 de mayo de 1881, expuso a todos los animales al agente virulento el 31 de mayo y el 2 de junio, ante más de 200 espectadores, todos los animales inoculados habían sobrevivido, a diferencia del grupo de control.",
             "P": [("conocimiento", .75), ("ambicion", .70)],
             "A": [("verificacion", .82), ("audacia", .72)],
             "C": [("reconocimiento", .82), ("atencion_social", .75)],
             "evidencia": [
                 EV("Ensayo público de Pouilly-le-Fort: inoculaciones el 5 y 17 de mayo de 1881, exposición el 31 de mayo y resultado observado el 2 de junio de 1881 ante más de 200 personas; sobrevivieron todos los animales inoculados.", WP + "Louis_Pasteur", CONSULTA, "1881-06-02", SEC),
                 EV("Relato del ensayo de Pouilly-le-Fort en una reimpresión comentada.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2588695/", CONSULTA, "1881-06-02", SEC),
             ]},
            {"id": "C3_1884", "date": "1884-06-15",
             "hecho": "En notas a la Academia de Ciencias de febrero y mayo de 1884 informó que la virulencia del agente de la rabia cambiaba al pasar por distintos animales (el mono la atenuaba; el conejo y el cobayo la aumentaban) y el 19 de mayo de 1884 expuso un método de inoculación preventiva en perros; se nombró una comisión de control para verificar los experimentos.",
             "P": [("busqueda_verdad", .80), ("determinacion", .75)],
             "A": [("metodicidad", .80), ("verificacion", .78)],
             "C": [("presion_social", .68), ("legitimidad_percibida", .70)],
             "evidencia": [
                 EV("Notas de Pasteur a la Academia de Ciencias en febrero y mayo de 1884 (Comptes rendus, tomo 98) sobre la modificación de la virulencia rábica por pasajes en animales.", "https://fr.wikipedia.org/wiki/Louis_Pasteur", CONSULTA, "1884-05", SEC),
                 EV("Lista de los artículos de Pasteur publicados en los Comptes rendus, incluidos los de 1884 sobre la rabia.", "https://comptes-rendus.academie-sciences.fr/page/anciens-articles-de-pasteur_fr/", CONSULTA, "1884-05", SEC),
                 EV("Crónica de H. Bouley (15 de junio de 1884): comunicación de Pasteur del 19 de mayo sobre la inoculación preventiva de la rabia, atenuación del virus en el mono y aumento en conejo y cobayo, y nombramiento de una comisión de control.", "https://www.persee.fr/doc/rmv_0034-1843_1884_num_61_1_1817", "1884-06-15", "1884-05-19", "primaria"),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 03
    {
        "id": "F002_03_ARBUCKLE", "person": "Roscoe 'Fatty' Arbuckle", "tipo": "artista",
        "question": "¿Qué trayectoria sigue Roscoe 'Fatty' Arbuckle tras firmar con Paramount un contrato de un millón de dólares al año y pasar de los cortos cómicos a los largometrajes?",
        "z_trabajo": "1921-08-31", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia en inglés (biografía y fichas de películas) y Variety de abril de 1917 en archive.org (fuente primaria).",
        "cuts": [
            {"id": "C1_1913", "date": "1913-06",
             "hecho": "Tras empezar en el cine con Selig Polyscope en julio de 1909, entró en 1913 en Keystone, el estudio de Mack Sennett, donde se volvió figura de la comedia; en junio de 1913 se estrenó A Noise from the Deep, con el pastelazo en la cara más antiguo que se conoce en el cine.",
             "P": [("autoexpresion", .78), ("ambicion", .72)],
             "A": [("humor", .84), ("creatividad", .78)],
             "C": [("oportunidad", .78), ("popularidad", .72)],
             "evidencia": [
                 EV("Empezó en el cine con Selig Polyscope en julio de 1909 y en 1913 entró en Keystone con Mack Sennett.", WP + "Roscoe_Arbuckle", CONSULTA, "1913", SEC),
                 EV("A Noise from the Deep (junio de 1913) contiene el primer pastelazo en la cara conocido del cine.", WP + "A_Noise_from_the_Deep", CONSULTA, "1913-06", SEC),
             ]},
            {"id": "C2_1917", "date": "1917-04-23",
             "hecho": "Fundó con Joseph Schenck la productora Comique, con control creativo propio; su primer corto ahí, The Butcher Boy, estrenado el 23 de abril de 1917, que escribió, dirigió y protagonizó, marcó el debut en el cine de Buster Keaton y fue reseñado por Variety.",
             "P": [("autonomia", .80), ("logro_personal", .75)],
             "A": [("mentoria_activa", .75), ("creatividad", .80)],
             "C": [("reconocimiento", .78), ("alianza", .72)],
             "evidencia": [
                 EV("Arbuckle fundó Comique en sociedad con Joseph Schenck.", WP + "Roscoe_Arbuckle", CONSULTA, "1917", SEC),
                 EV("The Butcher Boy, escrita, dirigida y protagonizada por Arbuckle, primera de la serie de Comique y debut de Buster Keaton, se estrenó el 23 de abril de 1917.", WP + "The_Butcher_Boy_(1917_film)", CONSULTA, "1917-04-23", SEC),
                 EV("Variety de abril de 1917 reseñó The Butcher Boy.", "https://archive.org/details/variety46-1917-04", "1917-04", "1917-04", "primaria"),
             ]},
            {"id": "C3_1920", "date": "1920",
             "hecho": "En 1918 cedió a Keaton su participación en Comique y aceptó la oferta de Paramount de 3 millones de dólares por hasta 18 largometrajes en tres años; en 1920 firmó con Paramount un contrato de un millón de dólares al año y pasó de los cortos a los largometrajes.",
             "P": [("ambicion", .80), ("estatus_social", .75)],
             "A": [("humor", .80), ("audacia", .70)],
             "C": [("popularidad", .84), ("prosperidad", .80)],
             "evidencia": [
                 EV("En 1918 transfirió su parte de Comique a Keaton y aceptó la oferta de Paramount de 3 millones de dólares por hasta 18 largometrajes en tres años.", WP + "Roscoe_Arbuckle", CONSULTA, "1918", SEC),
                 EV("En 1920 firmó con Paramount un contrato de un millón de dólares al año.", WP + "Roscoe_Arbuckle", CONSULTA, "1920", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 04
    {
        "id": "F002_04_BACH", "person": "Johann Sebastian Bach", "tipo": "artista",
        "question": "¿Qué trayectoria sigue Johann Sebastian Bach tras dejar la corte de Köthen y asumir el cargo de cantor de Santo Tomás y director musical de Leipzig?",
        "z_trabajo": "1723-06-01", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia en inglés (biografía, Conciertos de Brandemburgo, BWV 75, Thomaskantor); el informe del secretario de la corte de Weimar se cita a través de la biografía.",
        "cuts": [
            {"id": "C1_1717", "date": "1717-12-02",
             "hecho": "Al insistir con terquedad en que la corte de Weimar lo dejara ir, fue detenido el 6 de noviembre de 1717 y liberado el 2 de diciembre con un despido desfavorable; ese año el príncipe Leopoldo de Anhalt-Köthen, también músico, lo había contratado como maestro de capilla, con buen sueldo y amplia libertad.",
             "P": [("autonomia", .80), ("determinacion", .78)],
             "A": [("desafio_autoridad", .72), ("confrontacion_directa", .66)],
             "C": [("privacion_libertad", .70), ("oportunidad", .76)],
             "evidencia": [
                 EV("Según el secretario de la corte, fue detenido el 6 de noviembre de 1717 por forzar su salida y liberado el 2 de diciembre con despido desfavorable.", WP + "Johann_Sebastian_Bach", CONSULTA, "1717-12-02", SEC),
                 EV("Leopoldo de Anhalt-Köthen lo contrató como maestro de capilla en 1717, le pagaba bien y le daba amplia libertad.", WP + "Johann_Sebastian_Bach", CONSULTA, "1717", SEC),
             ]},
            {"id": "C2_1721", "date": "1721-12-03",
             "hecho": "En Köthen se dedicó sobre todo a la música instrumental; el 7 de julio de 1720 perdió de forma repentina a su esposa Maria Barbara; el 24 de marzo de 1721 dedicó seis conciertos al margrave Christian Ludwig de Brandemburgo y el 3 de diciembre de 1721 se casó con la soprano Anna Magdalena Wilcke.",
             "P": [("logro_personal", .74), ("compromiso_afectivo", .72)],
             "A": [("creatividad", .84), ("esfuerzo_sostenido_reciente", .70)],
             "C": [("duelo", .76), ("soporte", .68)],
             "evidencia": [
                 EV("Bach perdió repentinamente a su esposa Maria Barbara el 7 de julio de 1720 y se casó con Anna Magdalena Wilcke el 3 de diciembre de 1721.", WP + "Johann_Sebastian_Bach", CONSULTA, "1721-12-03", SEC),
                 EV("Los seis conciertos se dedicaron al margrave Christian Ludwig de Brandemburgo-Schwedt con dedicatoria del 24 de marzo de 1721.", WP + "Brandenburg_Concertos", CONSULTA, "1721-03-24", SEC),
             ]},
            {"id": "C3_1723", "date": "1723-05-30",
             "hecho": "El concejo de Leipzig le ofreció el puesto de cantor de Santo Tomás después de que Telemann y Graupner lo rechazaran; asumió en 1723 la preparación del coro de Santo Tomás para cuatro iglesias luteranas y la música de los actos de la ciudad, y el 30 de mayo de 1723, su primer domingo en el cargo, estrenó la cantata BWV 75 en la Nikolaikirche.",
             "P": [("deber", .78), ("devocion", .75)],
             "A": [("planificacion", .75), ("transmision_saber", .72)],
             "C": [("jerarquia", .70), ("ascenso_reciente", .74)],
             "evidencia": [
                 EV("El puesto se le ofreció después de que Telemann y Graupner lo rechazaran; fue nombrado en 1723.", WP + "Johann_Sebastian_Bach", CONSULTA, "1723-05", SEC),
                 EV("El Thomaskantor preparaba al coro de Santo Tomás para cuatro iglesias luteranas de Leipzig y organizaba la música de los actos de la ciudad.", WP + "Thomaskantor", CONSULTA, "1723-05", SEC),
                 EV("La cantata BWV 75 se estrenó el 30 de mayo de 1723 en la Nikolaikirche, primer domingo de Bach como Thomaskantor.", WP + "Die_Elenden_sollen_essen,_BWV_75", CONSULTA, "1723-05-30", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 05
    {
        "id": "F002_05_MCCARTHY", "person": "Joseph McCarthy", "tipo": "politico",
        "question": "¿Qué trayectoria sigue el senador Joseph McCarthy tras llevar sus investigaciones anticomunistas al Ejército de Estados Unidos y enfrentarse en audiencia al general Ralph Zwicker?",
        "z_trabajo": "1954-02-28", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia en inglés (biografía de McCarthy y de Ralph W. Zwicker); solo hechos hasta la audiencia del 18 de febrero de 1954.",
        "cuts": [
            {"id": "C1_1950", "date": "1950-02-09",
             "hecho": "En un discurso en Wheeling, Virginia Occidental, mostró un papel que según dijo contenía una lista de comunistas conocidos que trabajaban en el Departamento de Estado; el discurso le dio notoriedad nacional.",
             "P": [("ambicion", .80), ("sed_de_mando", .70)],
             "A": [("audacia", .78), ("oratoria", .74)],
             "C": [("atencion_social", .80), ("desconfianza", .70)],
             "evidencia": [
                 EV("Discurso de Wheeling del 9 de febrero de 1950 con una supuesta lista de comunistas en el Departamento de Estado.", WP + "Joseph_McCarthy", CONSULTA, "1950-02-09", SEC),
             ]},
            {"id": "C2_1953", "date": "1953-01",
             "hecho": "Al iniciar su segundo mandato en enero de 1953 pasó a presidir la Comisión de Operaciones Gubernamentales del Senado, que incluía el Subcomité Permanente de Investigaciones, cuyo mandato flexible usó para sus propias investigaciones sobre comunistas en el gobierno.",
             "P": [("poder", .80), ("sed_de_mando", .72)],
             "A": [("confrontacion_directa", .75), ("astucia", .68)],
             "C": [("autoridad", .78), ("atencion_social", .75)],
             "evidencia": [
                 EV("En enero de 1953 fue nombrado presidente de la Comisión de Operaciones Gubernamentales y usó el Subcomité Permanente de Investigaciones para investigar comunistas en el gobierno.", WP + "Joseph_McCarthy", CONSULTA, "1953-01", SEC),
             ]},
            {"id": "C3_1954", "date": "1954-02-18",
             "hecho": "El subcomité citó el 30 de enero de 1954 al mayor del Ejército Irving Peress, que se acogió a la Quinta Enmienda; el 18 de febrero de 1954 interrogó al general Ralph Zwicker, su comandante, que por consejo del Ejército se negó a responder algunas preguntas, y McCarthy le dijo que no era apto para vestir ese uniforme.",
             "P": [("ambicion", .74), ("obsesion", .70)],
             "A": [("confrontacion_directa", .82), ("impulsividad", .70)],
             "C": [("rivalidad_poder", .78), ("jerarquia", .70)],
             "evidencia": [
                 EV("Peress fue citado el 30 de enero de 1954 y se acogió a la Quinta Enmienda.", WP + "Ralph_Wise_Zwicker", CONSULTA, "1954-01-30", SEC),
                 EV("El 18 de febrero de 1954 Zwicker compareció, se negó a responder algunas preguntas por consejo del Ejército y McCarthy le dijo que no era apto para vestir ese uniforme.", WP + "Ralph_Wise_Zwicker", CONSULTA, "1954-02-18", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 06
    {
        "id": "F002_06_COOLIDGE", "person": "Calvin Coolidge", "tipo": "politico",
        "question": "¿Qué trayectoria sigue Calvin Coolidge tras ganar la elección presidencial de 1924 e iniciar su primer mandato completo como presidente de Estados Unidos?",
        "z_trabajo": "1925-03-05", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia en inglés (biografía, huelga policial de Boston, elección de 1924 y segunda investidura).",
        "cuts": [
            {"id": "C1_1919", "date": "1919-09",
             "hecho": "Como gobernador de Massachusetts enfrentó la huelga de la policía de Boston iniciada el 9 de septiembre de 1919 y respondió por telegrama a Samuel Gompers que no existía el derecho a la huelga contra la seguridad pública; la firmeza le dio fama nacional.",
             "P": [("deber", .80), ("legalidad", .74)],
             "A": [("compromiso_firme", .78), ("prudencia", .70)],
             "C": [("crisis_abrupta", .76), ("popularidad", .70)],
             "evidencia": [
                 EV("La huelga de la policía de Boston empezó el 9 de septiembre de 1919.", WP + "Boston_police_strike", CONSULTA, "1919-09-09", SEC),
                 EV("Telegrama de Coolidge a Gompers (14 de septiembre de 1919): no existe el derecho a la huelga contra la seguridad pública; la huelga le dio reputación nacional de líder decidido.", WP + "Calvin_Coolidge", CONSULTA, "1919-09", SEC),
             ]},
            {"id": "C2_1923", "date": "1923-08-03",
             "hecho": "Vicepresidente de Warren Harding desde 1921, al quedar vacante la presidencia juró el cargo a las 2:47 de la madrugada del 3 de agosto de 1923 en el salón de la casa familiar, ante su padre, notario público, a la luz de una lámpara de queroseno.",
             "P": [("deber", .80), ("humildad", .72)],
             "A": [("discrecion", .75), ("moderacion", .72)],
             "C": [("ascenso_reciente", .80), ("oportunidad", .72)],
             "evidencia": [
                 EV("Su padre, notario, le tomó juramento a las 2:47 de la madrugada del 3 de agosto de 1923.", WP + "Calvin_Coolidge", CONSULTA, "1923-08-03", SEC),
             ]},
            {"id": "C3_1925", "date": "1925-03-04",
             "hecho": "En julio de 1924 perdió a su hijo Calvin Jr., de 16 años, por una septicemia originada en una ampolla; en la elección de noviembre de 1924 obtuvo 382 votos electorales y el 54 % del voto popular, y su investidura del 4 de marzo de 1925 fue la primera transmitida por radio.",
             "P": [("deber", .78), ("moderacion", .72)],
             "A": [("autocontrol", .74), ("prudencia", .72)],
             "C": [("triunfo", .80), ("duelo", .74), ("legitimidad_percibida", .75)],
             "evidencia": [
                 EV("Calvin Jr. se hizo una ampolla el 30 de junio de 1924, desarrolló septicemia y no sobrevivió; tenía 16 años.", WP + "Calvin_Coolidge", CONSULTA, "1924-07", SEC),
                 EV("Coolidge ganó la elección de 1924 con 382 votos electorales y alrededor del 54 % del voto popular.", WP + "1924_United_States_presidential_election", CONSULTA, "1924-11", SEC),
                 EV("La segunda investidura de Coolidge, el 4 de marzo de 1925, fue la primera transmitida por radio.", WP + "Second_inauguration_of_Calvin_Coolidge", CONSULTA, "1925-03-04", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 07
    {
        "id": "F002_07_CATALINA", "person": "Catalina Alexéievna (nacida Sofía de Anhalt-Zerbst)", "tipo": "gobernante",
        "question": "¿Qué trayectoria sigue Catalina Alexéievna, consorte del emperador Pedro III, tras la llegada de su esposo al trono ruso y el creciente distanciamiento entre ambos?",
        "z_trabajo": "1762-06-01", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia en inglés (Catalina, Pedro III, Tratado de San Petersburgo); las fechas siguen a esas fuentes.",
        "cuts": [
            {"id": "C1_1745", "date": "1745-08-21",
             "hecho": "Princesa alemana llegada a Rusia en 1744 a los 15 años, se empeñó en aprender ruso y ganarse a la emperatriz Isabel; el 28 de junio de 1744 fue recibida en la Iglesia ortodoxa con el nombre de Yekaterina Alexéievna y el 21 de agosto de 1745 se casó con el gran duque Pedro.",
             "P": [("ambicion", .75), ("necesidad_pertenencia", .72)],
             "A": [("aprendizaje", .80), ("astucia", .72)],
             "C": [("oportunidad", .76), ("presion_social", .68)],
             "evidencia": [
                 EV("Llegó a Rusia en 1744, fue recibida en la ortodoxia el 28 de junio de 1744 como Yekaterina Alexéievna y se casó con Pedro el 21 de agosto de 1745.", WP + "Catherine_the_Great", CONSULTA, "1745-08-21", SEC),
             ]},
            {"id": "C2_1754", "date": "1754",
             "hecho": "El matrimonio resultó infeliz; Pedro tomó una amante y ella se relacionó con otras figuras de la corte, se ganó el favor de grupos políticos poderosos opuestos a su esposo y se volvió una lectora ávida en francés; en 1754 nació su hijo Pablo, heredero de la dinastía.",
             "P": [("conocimiento", .74), ("autonomia", .72)],
             "A": [("analisis", .72), ("discrecion", .70)],
             "C": [("estancamiento_emocional", .70), ("infidelidad", .68), ("alianza", .66)],
             "evidencia": [
                 EV("El matrimonio fue infeliz; tras tomar Pedro una amante, Catalina se relacionó con otras figuras de la corte, ganó popularidad entre grupos opuestos a su esposo y se volvió lectora ávida.", WP + "Catherine_the_Great", CONSULTA, "1754", SEC),
                 EV("Su hijo Pablo nació en 1754.", WP + "Paul_I_of_Russia", CONSULTA, "1754", SEC),
             ]},
            {"id": "C3_1762", "date": "1762-05-05",
             "hecho": "Pedro subió al trono el 5 de enero de 1762 y ella pasó a ser emperatriz consorte; admirador de Federico II, Pedro firmó el 5 de mayo de 1762 el Tratado de San Petersburgo, que cerró la guerra con Prusia y devolvió las ganancias rusas.",
             "P": [("busqueda_seguridad", .72), ("ambicion", .72)],
             "A": [("cautela", .72), ("discrecion", .70)],
             "C": [("incertidumbre", .72), ("rivalidad_poder", .72)],
             "evidencia": [
                 EV("Pedro III reinó desde el 5 de enero de 1762; Catalina fue emperatriz consorte desde esa fecha.", WP + "Catherine_the_Great", CONSULTA, "1762-01-05", SEC),
                 EV("El Tratado de San Petersburgo del 5 de mayo de 1762 cerró la guerra entre Rusia y Prusia y devolvió las conquistas rusas.", WP + "Treaty_of_Saint_Petersburg_(1762)", CONSULTA, "1762-05-05", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 08
    {
        "id": "F002_08_LUISXVI", "person": "Luis XVI de Francia", "tipo": "gobernante",
        "question": "¿Qué trayectoria sigue Luis XVI, rey bajo la nueva monarquía constitucional, instalado en las Tullerías de París y tras impedírsele la salida hacia Saint-Cloud en abril?",
        "z_trabajo": "1791-06-01", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia en inglés (Luis XVI, Estados Generales de 1789, marcha sobre Versalles, revolución de 1790-1791); la salida a Saint-Cloud solo se fecha en Semana Santa de 1791.",
        "cuts": [
            {"id": "C1_1789A", "date": "1789-05-05",
             "hecho": "Ante una grave crisis fiscal convocó los Estados Generales, que se abrieron en Versalles el 5 de mayo de 1789, la primera reunión desde 1614.",
             "P": [("responsabilidad", .75), ("anhelo_seguridad", .68)],
             "A": [("negociacion", .70), ("consenso", .66)],
             "C": [("crisis_abrupta", .75), ("escasez", .74)],
             "evidencia": [
                 EV("Los Estados Generales, convocados por Luis XVI ante una crisis fiscal, se abrieron el 5 de mayo de 1789 en Versalles, por primera vez desde 1614.", WP + "Estates_General_of_1789", CONSULTA, "1789-05-05", SEC),
             ]},
            {"id": "C2_1789B", "date": "1789-10-06",
             "hecho": "Tras la marcha de las mujeres sobre Versalles, la multitud, con la Guardia Nacional al frente, llevó a la familia real a París el 6 de octubre de 1789 y la instaló en las Tullerías; el 14 de julio de 1790 la Fiesta de la Federación le reservó el papel de rey ciudadano de la naciente monarquía constitucional.",
             "P": [("busqueda_seguridad", .72), ("deber", .70)],
             "A": [("conformidad", .70), ("evitacion_confrontacion", .70)],
             "C": [("presion_social", .80), ("retencion_forzada", .68)],
             "evidencia": [
                 EV("El 6 de octubre de 1789 la multitud escoltó a la familia real de Versalles a París.", WP + "Women%27s_March_on_Versailles", CONSULTA, "1789-10-06", SEC),
                 EV("Tras la marcha de octubre de 1789 la familia real pasó a residir en el palacio de las Tullerías.", WP + "Women%27s_March_on_Versailles", CONSULTA, "1789-10", SEC),
                 EV("La Fiesta de la Federación del 14 de julio de 1790 dio a Luis XVI un papel de rey ciudadano de la monarquía constitucional.", WP + "F%C3%AAte_de_la_F%C3%A9d%C3%A9ration", CONSULTA, "1790-07-14", SEC),
             ]},
            {"id": "C3_1791", "date": "1791-04",
             "hecho": "En Semana Santa de 1791 quiso salir de las Tullerías hacia Saint-Cloud para recibir los servicios de un sacerdote no juramentado, contrario a la Constitución Civil del Clero, y no le dejaron moverse.",
             "P": [("busqueda_libertad", .78), ("devocion", .72)],
             "A": [("resistencia_cambio", .70), ("discrecion", .65)],
             "C": [("privacion_libertad", .78), ("desconfianza", .75)],
             "evidencia": [
                 EV("En Semana Santa de 1791 se impidió al rey salir de las Tullerías hacia Saint-Cloud, donde quería recibir a un sacerdote no juramentado.", WP + "French_Revolution_from_the_summer_of_1790_to_the_establishment_of_the_Legislative_Assembly", CONSULTA, "1791-04", SEC),
                              ]},
        ],
    },
    # ------------------------------------------------------------------ 09
    {
        "id": "F002_09_ROCKEFELLER", "person": "John D. Rockefeller", "tipo": "empresario",
        "question": "¿Qué trayectoria sigue John D. Rockefeller tras constituir en Ohio la Standard Oil Company con sus socios refinadores de Cleveland?",
        "z_trabajo": "1870-01-31", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia en inglés (biografía y Rockefeller, Andrews & Flagler).",
        "cuts": [
            {"id": "C1_1859", "date": "1859",
             "hecho": "Con ahorros propios y 1000 dólares prestados por su padre fundó en Cleveland con Maurice Clark y George Gardner una casa de comisiones de productos agrícolas con 4000 dólares de capital, que pasó a llamarse Clark & Rockefeller.",
             "P": [("ambicion", .78), ("logro_personal", .72)],
             "A": [("metodicidad", .80), ("eficiencia", .75)],
             "C": [("oportunidad", .78), ("dependencia", .62)],
             "evidencia": [
                 EV("En 1859 formó con Clark y Gardner una casa de comisiones con 4000 dólares de capital, con 1000 prestados por su padre; la firma se llamó Clark & Rockefeller.", WP + "John_D._Rockefeller", CONSULTA, "1859", SEC),
             ]},
            {"id": "C2_1868", "date": "1868",
             "hecho": "En febrero de 1865 compró en subasta la parte de los hermanos Clark en la refinería por 72 500 dólares y formó Rockefeller & Andrews, día que llamó decisivo para su carrera; en 1867 entró Henry Flagler y nació Rockefeller, Andrews & Flagler, que hacia 1868 tenía dos refinerías en Cleveland y una filial comercial en Nueva York.",
             "P": [("ambicion", .82), ("control", .75)],
             "A": [("planificacion", .78), ("negociacion", .72)],
             "C": [("competencia", .78), ("prosperidad", .75)],
             "evidencia": [
                 EV("En febrero de 1865 compró la parte de los Clark por 72 500 dólares en subasta y formó Rockefeller & Andrews.", WP + "John_D._Rockefeller", CONSULTA, "1865-02", SEC),
                 EV("En 1867 Flagler se sumó (Rockefeller, Andrews & Flagler); hacia 1868 la firma tenía dos refinerías en Cleveland y una filial comercial en Nueva York.", WP + "Rockefeller,_Andrews_%26_Flagler", CONSULTA, "1868", SEC),
             ]},
            {"id": "C3_1870", "date": "1870-01-10",
             "hecho": "El 10 de enero de 1870 disolvió la sociedad Rockefeller, Andrews & Flagler y cofundó con sus socios la Standard Oil Company de Ohio.",
             "P": [("ambicion", .84), ("poder", .75)],
             "A": [("organizacion", .80), ("eficiencia", .78)],
             "C": [("competencia", .80), ("acumulacion_capital", .75)],
             "evidencia": [
                 EV("El 10 de enero de 1870 Rockefeller disolvió la sociedad y cofundó la Standard Oil de Ohio.", WP + "John_D._Rockefeller", CONSULTA, "1870-01-10", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 10
    {
        "id": "F002_10_DURANT", "person": "William C. Durant", "tipo": "empresario",
        "question": "¿Qué trayectoria sigue William C. Durant tras haber recuperado la presidencia de General Motors en 1916 y lanzar una gran expansión de la empresa?",
        "z_trabajo": "1920-06-30", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Wikipedia en inglés (biografía de Durant, General Motors, Chevrolet, Frigidaire).",
        "cuts": [
            {"id": "C1_1908", "date": "1908-11-12",
             "hecho": "Tomó el control de Buick el 1 de noviembre de 1904; el 16 de septiembre de 1908 fundó General Motors como sociedad de cartera y el 12 de noviembre de 1908 compró Olds Motor Works.",
             "P": [("ambicion", .84), ("vision", .80)],
             "A": [("audacia", .80), ("persuasion", .75)],
             "C": [("oportunidad", .78), ("prosperidad", .70)],
             "evidencia": [
                 EV("Durant tomó el control de Buick el 1 de noviembre de 1904.", WP + "William_C._Durant", CONSULTA, "1904-11-01", SEC),
                 EV("General Motors se fundó el 16 de septiembre de 1908 y compró Olds el 12 de noviembre de 1908.", WP + "General_Motors", CONSULTA, "1908-11-12", SEC),
             ]},
            {"id": "C2_1911", "date": "1911-11-03",
             "hecho": "Sobreendeudado tras sumar Cadillac, Oakland y otras compañías, perdió en 1910 el control de General Motors a manos de los banqueros; el 3 de noviembre de 1911 fundó Chevrolet con el piloto Louis Chevrolet.",
             "P": [("determinacion", .80), ("ambicion", .78)],
             "A": [("resiliencia", .80), ("generacion_ideas", .72)],
             "C": [("derrota_temporal", .78), ("vulnerabilidad_financiera_inmediata", .68)],
             "evidencia": [
                 EV("En 1909 GM sumó Cadillac y Oakland; en 1910 los banqueros apartaron a Durant del control de GM.", WP + "William_C._Durant", CONSULTA, "1910", SEC),
                 EV("Chevrolet se fundó el 3 de noviembre de 1911 por Durant y Louis Chevrolet.", WP + "Chevrolet", CONSULTA, "1911-11-03", SEC),
             ]},
            {"id": "C3_1919", "date": "1919",
             "hecho": "Apoyado en las ventas de Chevrolet recuperó en 1916 el control de General Motors; en febrero de 1918 se anunció el plan para que GM absorbiera Chevrolet, y en 1919 GM compró la Guardian Frigerator Company, en parte propiedad de Durant, rebautizada Frigidaire, y creó la financiera General Motors Acceptance Corporation.",
             "P": [("ambicion", .82), ("vision", .78)],
             "A": [("audacia", .78), ("diversificacion", .80)],
             "C": [("triunfo", .75), ("prosperidad", .75)],
             "evidencia": [
                 EV("En 1916 Durant recuperó el control de GM gracias a Chevrolet.", WP + "William_C._Durant", CONSULTA, "1916", SEC),
                 EV("El plan de absorber Chevrolet se informó el 24 de febrero de 1918; en 1919 GM adquirió Guardian Frigerator (Frigidaire) y creó GMAC.", WP + "General_Motors", CONSULTA, "1919", SEC),
                 EV("Guardian Frigerator Company fue adquirida por GM en 1919 y rebautizada Frigidaire.", WP + "Frigidaire", CONSULTA, "1919", SEC),
             ]},
        ],
    },
]
