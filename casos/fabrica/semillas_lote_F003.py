# -*- coding: utf-8 -*-
"""Semillas Z — lote F003 (modo histórico, preparación a ciegas).

Preparado por GrokBot-preparador-ciego-F003 sin ver los destinos sellados.
Cada corte está fechado en o antes del Z de trabajo y solo describe hechos
conocidos en esa fecha. Las fuentes secundarias (Wikipedia, reimpresiones)
se usan en modo histórico con preparación ciega declarada; su source_date es
la fecha de consulta. Las fuentes primarias llevan su fecha de publicación.
"""

EV = lambda afirmacion, url, source_date, claim_date, tipo="primaria", **kw: {
    "afirmacion": afirmacion, "source_url": url, "source_date": source_date,
    "claim_date": claim_date, "tipo_fuente": tipo, "conocido_en_Z": "sí", **kw}

CONSULTA = "2026-10-26"  # fecha de consulta de fuentes secundarias en línea
SEC = "secundaria"
CIEGA = {"preparador_entrada": "GrokBot-preparador-ciego-F003",
         "custodio_destino": "GrokBot-custodio-rutina-F003",
         "vio_destino": False}

WP = "https://en.wikipedia.org/wiki/"

SEMILLAS_Z = [
    # ------------------------------------------------------------------ 01
    {
        "id": "F003_01_CARAVAGGIO", "person": "Michelangelo Merisi da Caravaggio", "tipo": "artista",
        "question": "¿Qué trayectoria sigue Caravaggio tras otro año de pleitos y riñas en Roma mientras sus mecenas siguen encargándole cuadros?",
        "z_trabajo": "1605-12-31", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta finales de 1605.",
        "cuts": [
            {"id": "C1_1600", "date": "1600",
             "hecho": "Con el apoyo del cardenal Francesco Maria del Monte, entregó en 1600 los dos lienzos de San Mateo para la capilla Contarelli de San Luigi dei Francesi; fueron una sensación inmediata y desde entonces no le faltaron encargos ni mecenas.",
             "P": [("ambicion", .78), ("autoexpresion", .80)],
             "A": [("creatividad", .82), ("audacia", .74)],
             "C": [("reconocimiento", .80), ("redes_prestigio", .76)],
             "evidencia": [
                 EV("Hacia 1599, se supone que por influencia de del Monte, recibió el encargo de la capilla Contarelli; los dos cuadros de San Mateo se entregaron en 1600 y fueron una sensación inmediata, y desde entonces no le faltaron encargos ni mecenas.", WP + "Caravaggio", CONSULTA, "1600", SEC),
                 EV("El cardenal Francesco Maria del Monte, uno de los principales conocedores de Roma, compró sus primeros cuadros y se volvió su mecenas.", WP + "Caravaggio", CONSULTA, "1600", SEC),
             ]},
            {"id": "C2_1603", "date": "1603",
             "hecho": "El 28 de noviembre de 1600 golpeó con un garrote al noble Girolamo Stampa, huésped de del Monte, y las riñas se hicieron frecuentes; en 1603 fue arrestado por difamar al pintor Giovanni Baglione con versos ofensivos y, tras un mes en la cárcel de Tor di Nona, pasó a arresto domiciliario por intervención del embajador de Francia.",
             "P": [("orgullo", .78), ("impulsividad", .80)],
             "A": [("confrontacion_directa", .80), ("burla", .72)],
             "C": [("rivalidad_profesional", .78), ("privacion_libertad", .70)],
             "evidencia": [
                 EV("El 28 de noviembre de 1600 golpeó con un garrote a Girolamo Stampa da Montepulciano, huésped del cardenal del Monte; las riñas se hicieron cada vez más frecuentes y a menudo fue encarcelado en Tor di Nona.", WP + "Caravaggio", CONSULTA, "1600-11-28", SEC),
                 EV("En 1603 fue arrestado por difamar a Giovanni Baglione, que lo demandó junto con Orazio Gentileschi y Onorio Longhi por versos ofensivos; intervino el embajador de Francia y pasó a arresto domiciliario tras un mes en Tor di Nona.", WP + "Caravaggio", CONSULTA, "1603", SEC),
             ]},
            {"id": "C3_1605", "date": "1605-08",
             "hecho": "Entre mayo y octubre de 1604 fue arrestado varias veces por portar armas ilegales e insultar a los guardias, y un mesero lo demandó por arrojarle un plato de alcachofas; el 29 de julio de 1605 hirió gravemente con espada al notario Mariano Pasqualone en una disputa por Lena, su modelo, huyó tres semanas a Génova y sus mecenas lograron encubrir el incidente.",
             "P": [("impulsividad", .82), ("pasion", .72)],
             "A": [("confrontacion_directa", .82), ("evasion", .70)],
             "C": [("impunidad", .76), ("soporte", .72)],
             "evidencia": [
                 EV("Entre mayo y octubre de 1604 fue arrestado varias veces por posesión de armas ilegales y por insultar a los guardias de la ciudad; un mesero lo demandó por arrojarle un plato de alcachofas a la cara.", WP + "Caravaggio", CONSULTA, "1604-10", SEC),
                 EV("En 1605 tuvo que huir a Génova tres semanas tras herir gravemente al notario Mariano Pasqualone por Lena; el notario denunció el ataque con espada del 29 de julio y los mecenas intervinieron para encubrir el incidente.", WP + "Caravaggio", CONSULTA, "1605-08", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 02
    {
        "id": "F003_02_DICKENS", "person": "Charles Dickens", "tipo": "artista",
        "question": "¿Qué trayectoria sigue Charles Dickens tras reunir sus Sketches by Boz en libro y empezar una serie mensual para Chapman and Hall?",
        "z_trabajo": "1836-04-02", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta el 2 de abril de 1836.",
        "cuts": [
            {"id": "C1_1824", "date": "1824",
             "hecho": "Su padre, John Dickens, entró en la prisión de deudores de Marshalsea en 1824; Charles, de 12 años, tuvo que dejar la escuela y trabajar jornadas de diez horas pegando etiquetas en la fábrica de betún Warren's Blacking por seis chelines a la semana.",
             "P": [("verguenza_infantil", .76), ("anhelo_seguridad", .74)],
             "A": [("esfuerzo_sostenido_reciente", .78), ("supervivencia", .74)],
             "C": [("escasez", .82), ("vulnerabilidad_financiera_inmediata", .80)],
             "evidencia": [
                 EV("En 1824 John Dickens fue enviado por sus acreedores a la prisión de deudores de Marshalsea; Charles, de 12 años, dejó la escuela y trabajó jornadas de diez horas en Warren's Blacking Warehouse.", WP + "Charles_Dickens", CONSULTA, "1824", SEC),
             ]},
            {"id": "C2_1834", "date": "1834-08",
             "hecho": "En diciembre de 1833 publicó su primer relato en The Monthly Magazine; trabajaba como periodista parlamentario y para el Morning Chronicle, y en agosto de 1834 firmó por primera vez con el seudónimo Boz.",
             "P": [("ambicion", .78), ("autoexpresion", .78)],
             "A": [("creatividad", .80), ("esfuerzo_sostenido_reciente", .76)],
             "C": [("oportunidad", .76), ("reconocimiento", .66)],
             "evidencia": [
                 EV("En 1833 envió su primer relato, A Dinner at Poplar Walk, a The Monthly Magazine; trabajó como periodista político cubriendo los debates del Parlamento y campañas para el Morning Chronicle.", WP + "Charles_Dickens", CONSULTA, "1833", SEC),
                 EV("Su primer relato apareció en The Monthly Magazine en diciembre de 1833; ninguno llevó firma hasta agosto de 1834, cuando The Boarding House apareció con el seudónimo Boz.", WP + "Sketches_by_Boz", CONSULTA, "1834-08", SEC),
             ]},
            {"id": "C3_1836", "date": "1836-04-02",
             "hecho": "En febrero de 1836 se publicaron en libro sus Sketches by Boz; por su éxito, la editorial Chapman and Hall le propuso escribir el texto para los grabados de Robert Seymour en una serie mensual, The Pickwick Papers, iniciada en marzo de 1836; el 2 de abril de 1836 se casó con Catherine Hogarth, hija del editor George Hogarth.",
             "P": [("ambicion", .80), ("compromiso_afectivo", .74)],
             "A": [("creatividad", .82), ("humor", .78)],
             "C": [("popularidad", .76), ("oportunidad", .80)],
             "evidencia": [
                 EV("La primera serie de Sketches by Boz la publicó John Macrone en dos volúmenes en febrero de 1836, un mes antes del primer número de The Pickwick Papers.", WP + "Sketches_by_Boz", CONSULTA, "1836-02", SEC),
                 EV("El éxito de Sketches by Boz llevó a Chapman and Hall a proponerle escribir el texto para los grabados de Robert Seymour en una entrega mensual.", WP + "Charles_Dickens", CONSULTA, "1836-03", SEC),
                 EV("The Pickwick Papers se publicó por entregas a partir de marzo de 1836, encargada por Chapman & Hall tras el éxito de Sketches by Boz.", WP + "The_Pickwick_Papers", CONSULTA, "1836-03", SEC),
                 EV("El 2 de abril de 1836, tras un año de compromiso, se casó con Catherine Thomson Hogarth, hija de George Hogarth, editor del Evening Chronicle.", WP + "Charles_Dickens", CONSULTA, "1836-04-02", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 03
    {
        "id": "F003_03_LAVOISIER", "person": "Antoine Lavoisier", "tipo": "cientifico",
        "question": "¿Qué trayectoria sigue Antoine Lavoisier tras publicar su Traité élémentaire de chimie mientras sigue siendo socio de la Ferme générale?",
        "z_trabajo": "1790-01-01", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta 1789.",
        "cuts": [
            {"id": "C1_1771", "date": "1771",
             "hecho": "En 1768 recibió un nombramiento provisional en la Academia de Ciencias y, hacia esa fecha, compró una participación en la Ferme générale, la compañía privada que adelantaba al rey los impuestos a cambio de cobrarlos; en 1771 se casó con Marie-Anne Paulze, hija de un alto miembro de la Ferme.",
             "P": [("ambicion", .76), ("curiosidad_abstracta", .80)],
             "A": [("acumulacion_capital", .74), ("alianza", .72)],
             "C": [("estatus_social", .78), ("redes_prestigio", .76)],
             "evidencia": [
                 EV("En 1768 Lavoisier recibió un nombramiento provisional en la Academia de Ciencias.", WP + "Antoine_Lavoisier", CONSULTA, "1768", SEC),
                 EV("A los 26 años, cerca de su elección en la Academia, compró una participación en la Ferme générale, compañía de arrendamiento de impuestos que adelantaba al gobierno el ingreso estimado a cambio del derecho a cobrarlo.", WP + "Antoine_Lavoisier", CONSULTA, "1769", SEC),
                 EV("En 1771, a los 28 años, se casó con Marie-Anne Pierrette Paulze, de 13 años, hija de un alto miembro de la Ferme générale.", WP + "Antoine_Lavoisier", CONSULTA, "1771", SEC),
             ]},
            {"id": "C2_1783", "date": "1783",
             "hecho": "En 1775 fue nombrado uno de los cuatro comisarios de la pólvora y mejoró la cantidad y calidad de la pólvora francesa; en 1783 leyó en la Academia sus Réflexions sur le phlogistique, un ataque frontal a la teoría del flogisto, y reconoció el agua como óxido de un gas que llamó hidrógeno.",
             "P": [("busqueda_verdad", .82), ("conocimiento", .80)],
             "A": [("verificacion", .82), ("metodicidad", .80)],
             "C": [("reconocimiento", .76), ("rivalidad_profesional", .68)],
             "evidencia": [
                 EV("En 1775 fue nombrado uno de los cuatro comisarios de la pólvora; gracias a su trabajo mejoraron la cantidad y calidad de la pólvora francesa, que se volvió fuente de ingresos para el gobierno.", WP + "Antoine_Lavoisier", CONSULTA, "1775", SEC),
                 EV("En 1783 leyó en la Academia Réflexions sur le phlogistique, un ataque completo a la teoría del flogisto, y en junio de 1783 reconoció el agua como óxido de un gas hidrogenador.", WP + "Antoine_Lavoisier", CONSULTA, "1783", SEC),
             ]},
            {"id": "C3_1789", "date": "1789",
             "hecho": "En 1787 presentó con Guyton de Morveau, Berthollet y Fourcroy la Méthode de nomenclature chimique, ligada a su teoría del oxígeno, y en 1789 publicó el Traité élémentaire de chimie, síntesis de su obra; seguía siendo administrador de la Ferme générale, uno de los organismos más odiados del Antiguo Régimen por sus ganancias, sus contratos secretos y la violencia de sus agentes armados.",
             "P": [("busqueda_verdad", .82), ("orgullo", .70)],
             "A": [("organizacion", .80), ("transmision_saber", .78)],
             "C": [("reconocimiento", .80), ("desconfianza_autoridad", .70)],
             "evidencia": [
                 EV("En 1787 presentó a la Academia, con Guyton de Morveau, Berthollet y Fourcroy, la Méthode de nomenclature chimique, ligada a su nueva teoría del oxígeno.", WP + "Antoine_Lavoisier", CONSULTA, "1787", SEC),
                 EV("El Traité élémentaire de chimie, publicado en 1789, sintetiza su contribución a la química.", WP + "Antoine_Lavoisier", CONSULTA, "1789", SEC),
                 EV("Era administrador de la Ferme générale, uno de los componentes más odiados del Antiguo Régimen por sus ganancias a costa del Estado, el secreto de sus contratos y la violencia de sus agentes armados.", WP + "Antoine_Lavoisier", CONSULTA, "1789", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 04
    {
        "id": "F003_04_FARADAY", "person": "Michael Faraday", "tipo": "cientifico",
        "question": "¿Qué trayectoria sigue Michael Faraday tras publicar su experimento de rotación electromagnética sin reconocer el trabajo previo de Davy y Wollaston?",
        "z_trabajo": "1822-01-01", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta 1821.",
        "cuts": [
            {"id": "C1_1813", "date": "1813-03-01",
             "hecho": "Aprendiz de encuadernador sin estudios formales, en 1812 asistió a las conferencias de Humphry Davy y le envió un libro de 300 páginas con sus notas; el 1 de marzo de 1813 Davy lo hizo contratar como asistente químico de la Royal Institution.",
             "P": [("curiosidad_abstracta", .82), ("ambicion", .70)],
             "A": [("aprendizaje", .82), ("iniciativa_infantil", .62)],
             "C": [("mentoria_activa", .82), ("oportunidad", .78)],
             "evidencia": [
                 EV("En 1812, al terminar su aprendizaje, asistió a conferencias de Humphry Davy y le envió un libro de 300 páginas basado en sus notas; Davy respondió de forma inmediata y favorable.", WP + "Michael_Faraday", CONSULTA, "1812", SEC),
                 EV("Faraday fue nombrado asistente químico de la Royal Institution el 1 de marzo de 1813.", WP + "Michael_Faraday", CONSULTA, "1813-03-01", SEC),
             ]},
            {"id": "C2_1820", "date": "1820",
             "hecho": "Entre 1813 y 1815 viajó por Europa con Davy; como su asistente estudió el cloro y en 1820 informó la primera síntesis de compuestos de carbono y cloro.",
             "P": [("conocimiento", .80), ("devocion", .70)],
             "A": [("metodicidad", .80), ("verificacion", .78)],
             "C": [("reconocimiento", .70), ("jerarquia", .74)],
             "evidencia": [
                 EV("Su primer trabajo químico fue como asistente de Humphry Davy, estudiando el cloro y descubriendo dos compuestos de cloro y carbono.", WP + "Michael_Faraday", CONSULTA, "1820", SEC),
                 EV("En 1820 Faraday informó la primera síntesis de compuestos de carbono y cloro.", WP + "Michael_Faraday", CONSULTA, "1820", SEC),
                 EV("Su diario de viajes con Davy por Europa cubre los años 1813–1815.", WP + "Michael_Faraday", CONSULTA, "1815", SEC),
             ]},
            {"id": "C3_1821", "date": "1821",
             "hecho": "En 1821 fue nombrado superintendente asistente de la casa de la Royal Institution y el 12 de junio se casó con Sarah Barnard; ese año, tras conversar con Davy y Wollaston, que no habían logrado un motor eléctrico, construyó dos aparatos de rotación electromagnética y publicó los resultados sin reconocer el trabajo de ellos, lo que abrió una controversia en la Royal Society.",
             "P": [("curiosidad_abstracta", .82), ("orgullo", .66)],
             "A": [("herramienta_nueva", .82), ("impulsividad", .66)],
             "C": [("rivalidad_profesional", .78), ("reconocimiento", .74)],
             "evidencia": [
                 EV("Fue nombrado superintendente asistente de la casa de la Royal Institution en 1821.", WP + "Michael_Faraday", CONSULTA, "1821", SEC),
                 EV("Se casó con Sarah Barnard el 12 de junio de 1821.", WP + "Michael_Faraday", CONSULTA, "1821-06-12", SEC),
                 EV("En 1821, tras hablar con Davy y Wollaston, que no habían logrado diseñar un motor eléctrico, construyó dos aparatos de rotación electromagnética y publicó sin reconocer el trabajo de ellos, lo que causó una controversia en la Royal Society y tensó su relación con Davy.", WP + "Michael_Faraday", CONSULTA, "1821", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 05
    {
        "id": "F003_05_FOUQUET", "person": "Nicolas Fouquet", "tipo": "politico",
        "question": "¿Qué trayectoria sigue Nicolas Fouquet tras recibir a Luis XIV en la gran fiesta de inauguración de su château de Vaux-le-Vicomte?",
        "z_trabajo": "1661-08-17", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta la fiesta del 17 de agosto de 1661.",
        "cuts": [
            {"id": "C1_1653", "date": "1653-02-07",
             "hecho": "Durante la Fronda se mantuvo leal al cardenal Mazarino y a la regente Ana de Austria; como recompensa obtuvo el 7 de febrero de 1653 la superintendencia de finanzas, la persona más joven en ocupar ese cargo, conservando además el puesto de procurador general del Parlamento de París.",
             "P": [("ambicion", .80), ("lealtad", .74)],
             "A": [("alianza", .78), ("astucia", .76)],
             "C": [("ascenso_reciente", .82), ("poder", .78)],
             "evidencia": [
                 EV("Durante la segunda Fronda permaneció leal a Mazarino y, a su regreso, pidió y obtuvo el 7 de febrero de 1653 la superintendencia de finanzas, siendo el más joven en ese cargo.", WP + "Nicolas_Fouquet", CONSULTA, "1653-02-07", SEC),
                 EV("En 1650 compró el cargo de procurador general del Parlamento de París.", WP + "Nicolas_Fouquet", CONSULTA, "1650", SEC),
             ]},
            {"id": "C2_1658", "date": "1658-12",
             "hecho": "Las finanzas reales estaban en desorden y él cubría a veces los pagos con su propio crédito; en 1658 compró Belle-Île y fortificó la isla con puerto y almacenes; en diciembre de 1658 presentó su renuncia a Mazarino, que no fue aceptada.",
             "P": [("ambicion", .78), ("busqueda_seguridad", .70)],
             "A": [("acumulacion_capital", .78), ("doble_agenda", .68)],
             "C": [("vulnerabilidad_financiera_inmediata", .70), ("poder", .78)],
             "evidencia": [
                 EV("Las largas guerras obligaron a Fouquet a cubrir la demanda de fondos tomando préstamos con su propio crédito; en diciembre de 1658 presentó su renuncia a Mazarino, que no fue aceptada.", WP + "Nicolas_Fouquet", CONSULTA, "1658-12", SEC),
                 EV("En 1658 compró Belle-Île-en-Mer, reforzó sus fortificaciones y construyó un puerto y almacenes.", WP + "Nicolas_Fouquet", CONSULTA, "1658", SEC),
             ]},
            {"id": "C3_1661", "date": "1661-08-17",
             "hecho": "Al morir Mazarino el 9 de marzo de 1661 esperaba ser primer ministro, pero Luis XIV declaró que gobernaría sin primer ministro y Colbert le llevaba informes adversos sobre el déficit; el 17 de agosto de 1661 ofreció al rey en Vaux-le-Vicomte, construido por Le Vau, Le Brun y Le Nôtre, una fiesta fastuosa con el estreno de Les Fâcheux de Molière, cena de Vatel y fuegos artificiales.",
             "P": [("orgullo_hubris", .80), ("ambicion", .80)],
             "A": [("atencion_social", .78), ("persuasion", .70)],
             "C": [("rivalidad_poder", .80), ("desconfianza", .76)],
             "evidencia": [
                 EV("Con la muerte de Mazarino el 9 de marzo de 1661 Fouquet esperaba ser primer ministro, pero Luis XIV, receloso de su lealtad, declaró que gobernaría sin primer ministro; Colbert alimentaba el disgusto del rey con informes adversos.", WP + "Nicolas_Fouquet", CONSULTA, "1661-03", SEC),
                 EV("Vaux-le-Vicomte fue construido entre 1658 y 1661 por Le Vau, Le Nôtre y Le Brun; en su inauguración se representó una obra de Molière, con cena organizada por Vatel y fuegos artificiales.", WP + "Vaux-le-Vicomte", CONSULTA, "1661-08-17", SEC),
                 EV("La fiesta del 17 de agosto de 1661 estrenó Les Fâcheux de Molière.", WP + "Vaux-le-Vicomte", CONSULTA, "1661-08-17", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 06
    {
        "id": "F003_06_TROTSKY", "person": "León Trotski", "tipo": "politico",
        "question": "¿Qué trayectoria sigue León Trotski tras escribir al Comité Central contra la falta de democracia interna mientras Lenin está enfermo?",
        "z_trabajo": "1923-10-15", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta el 15 de octubre de 1923.",
        "cuts": [
            {"id": "C1_1918", "date": "1918-03-13",
             "hecho": "Presidente del Sóviet de Petrogrado, dirigió la organización práctica de la Revolución de Octubre de 1917; fue comisario de Asuntos Exteriores y el 13 de marzo de 1918 fue nombrado comisario del Pueblo para el Ejército y la Marina, con control pleno del Ejército Rojo.",
             "P": [("sed_de_mando", .78), ("idealismo", .76)],
             "A": [("oratoria", .80), ("organizacion", .82)],
             "C": [("poder", .82), ("ascenso_reciente", .80)],
             "evidencia": [
                 EV("Fue elegido presidente del Sóviet de Petrogrado el 8 de octubre de 1917 y dirigió los esfuerzos para derrocar al Gobierno Provisional.", WP + "Leon_Trotsky", CONSULTA, "1917-10-08", SEC),
                 EV("El 13 de marzo de 1918 fue nombrado comisario del Pueblo para el Ejército y la Marina y presidente del Consejo Militar Supremo, con control pleno del Ejército Rojo.", WP + "Leon_Trotsky", CONSULTA, "1918-03-13", SEC),
             ]},
            {"id": "C2_1922", "date": "1922-09-11",
             "hecho": "Con Lenin enfermo tras su primer infarto cerebral de mayo de 1922, Stalin fue nombrado secretario general del Comité Central en abril de 1922 y Zinóviev y Kámenev formaron con él una troika; el 11 de septiembre de 1922 Lenin propuso a Trotski como su adjunto en el Consejo de Comisarios del Pueblo, y Trotski se negó categóricamente.",
             "P": [("orgullo", .76), ("independencia", .72)],
             "A": [("renuncia", .68), ("evitacion_confrontacion", .66)],
             "C": [("rivalidad_poder", .82), ("alianza", .62)],
             "evidencia": [
                 EV("Lenin sufrió infartos cerebrales desde el 25 de mayo de 1922; Stalin fue elevado a secretario general en abril de 1922 y Zinóviev y Kámenev formaron con él una troika frente a Trotski, públicamente el número dos.", WP + "Leon_Trotsky", CONSULTA, "1922", SEC),
                 EV("El 11 de septiembre de 1922 Lenin propuso que Trotski fuera su adjunto en el Sovnarkom; el Politburó aprobó, pero Trotski se negó categóricamente.", WP + "Leon_Trotsky", CONSULTA, "1922-09-11", SEC),
             ]},
            {"id": "C3_1923", "date": "1923-10-15",
             "hecho": "En el XII Congreso de abril de 1923 habló de democracia interna sin enfrentar a la troika y recibió una ovación; el 8 de octubre de 1923 escribió al Comité Central atribuyendo los problemas a la falta de democracia interna, y el 15 de octubre 46 dirigentes enviaron una declaración en el mismo sentido.",
             "P": [("idealismo", .78), ("orgullo", .74)],
             "A": [("desafio_autoridad", .78), ("oratoria", .72)],
             "C": [("rivalidad_poder", .84), ("aislamiento_social", .64)],
             "evidencia": [
                 EV("En el XII Congreso de abril de 1923 habló de democracia interna evitando la confrontación directa con la troika y los delegados le dieron una ovación de pie.", WP + "Leon_Trotsky", CONSULTA, "1923-04", SEC),
                 EV("El 8 de octubre de 1923 Trotski escribió al Comité Central y a la Comisión Central de Control atribuyendo las dificultades a la falta de democracia interna; el 15 de octubre de 1923 se envió la Declaración de los 46.", WP + "The_Declaration_of_46", CONSULTA, "1923-10-15", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 07
    {
        "id": "F003_07_LINCOLN", "person": "Abraham Lincoln", "tipo": "politico",
        "question": "¿Qué trayectoria sigue Abraham Lincoln tras el último de sus siete debates con Stephen A. Douglas en la campaña al Senado por Illinois?",
        "z_trabajo": "1858-10-15", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta el debate de Alton del 15 de octubre de 1858.",
        "cuts": [
            {"id": "C1_1846", "date": "1846",
             "hecho": "Autodidacta criado en la frontera, perdió su primera candidatura a la legislatura de Illinois en 1832; en 1834, como whig seguidor de Henry Clay, entró en la legislatura estatal, y en 1846 ganó un escaño en la Cámara de Representantes federal, prometiendo servir un solo periodo.",
             "P": [("ambicion", .78), ("determinacion", .76)],
             "A": [("aprendizaje", .78), ("persuasion", .74)],
             "C": [("ascenso_reciente", .74), ("derrota_temporal", .62)],
             "evidencia": [
                 EV("En 1832 declaró su candidatura a la Cámara de Representantes de Illinois; en su segunda campaña, en 1834, como seguidor del whig Henry Clay, quedó segundo entre trece candidatos para cuatro puestos.", WP + "Abraham_Lincoln", CONSULTA, "1834", SEC),
                 EV("En 1846 obtuvo la candidatura whig y ganó la elección a la Cámara de Representantes; se había comprometido a servir un solo periodo.", WP + "Abraham_Lincoln", CONSULTA, "1846", SEC),
             ]},
            {"id": "C2_1856", "date": "1856-06",
             "hecho": "Indignado por la Ley Kansas-Nebraska de 1854, que abría los territorios a la esclavitud, dejó el partido whig en crisis; en 1856 se unió a los republicanos, dio el discurso final de la convención de Bloomington y en junio de 1856 recibió apoyos para la vicepresidencia, quedando como republicano destacado de Illinois.",
             "P": [("justicia", .78), ("ambicion", .76)],
             "A": [("oratoria", .82), ("cambio_lealtad", .70)],
             "C": [("legitimidad_percibida", .74), ("reconocimiento", .72)],
             "evidencia": [
                 EV("La Ley Kansas-Nebraska de 1854 abrió los territorios a la esclavitud y lo llevó a ser dirigente del nuevo Partido Republicano.", WP + "Abraham_Lincoln", CONSULTA, "1854", SEC),
                 EV("En 1856 se unió a los republicanos, dio el discurso final de la convención de Bloomington y en la convención nacional de junio de 1856 recibió apoyos para la vicepresidencia; se convirtió en un republicano destacado de Illinois.", WP + "Abraham_Lincoln", CONSULTA, "1856-06", SEC),
             ]},
            {"id": "C3_1858", "date": "1858-10-15",
             "hecho": "En junio de 1858 los republicanos de Illinois lo nominaron al Senado contra el titular Stephen A. Douglas y el 16 de junio pronunció el discurso de la casa dividida; entre el 21 de agosto y el 15 de octubre sostuvo siete debates con Douglas que atrajeron multitudes de hasta 18,000 personas y le dieron audiencia nacional; los senadores aún los elegía la legislatura estatal.",
             "P": [("ambicion", .80), ("justicia", .76)],
             "A": [("oratoria", .84), ("confrontacion_directa", .76)],
             "C": [("popularidad", .78), ("rivalidad_poder", .74)],
             "evidencia": [
                 EV("Pronunció el discurso de la casa dividida el 16 de junio de 1858 en Springfield, tras aceptar la nominación republicana al Senado.", WP + "House_Divided_Speech", CONSULTA, "1858-06-16", SEC),
                 EV("Los siete debates con Douglas se celebraron entre agosto y octubre de 1858, de Ottawa (21 de agosto) a Alton (15 de octubre); se reportaron 16,000 a 18,000 asistentes en Galesburg; los senadores eran elegidos por la legislatura estatal.", WP + "Lincoln%E2%80%93Douglas_debates", CONSULTA, "1858-10-15", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 08
    {
        "id": "F003_08_LAW", "person": "John Law", "tipo": "empresario",
        "question": "¿Qué trayectoria sigue John Law tras ser nombrado controlador general de finanzas de Francia mientras las acciones de su compañía están en máximos?",
        "z_trabajo": "1720-01-31", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta enero de 1720.",
        "cuts": [
            {"id": "C1_1705", "date": "1705",
             "hecho": "Jugador hábil con el cálculo de probabilidades, en 1694 mató en duelo a Edward Wilson en Londres, fue condenado y escapó a Ámsterdam; en 1705 publicó Money and Trade Considered, que proponía un banco nacional y papel moneda, pero su propuesta fue rechazada en Escocia.",
             "P": [("ambicion", .80), ("busqueda_riesgo", .78)],
             "A": [("generacion_ideas", .80), ("apuesta_extrema", .74)],
             "C": [("fugitivo", .70), ("derrota_temporal", .68)],
             "evidencia": [
                 EV("El 9 de abril de 1694 mató a Edward Wilson en duelo en Bloomsbury Square, fue condenado por asesinato y escapó a Ámsterdam.", WP + "John_Law_(economist)", CONSULTA, "1694-04-09", SEC),
                 EV("En 1705 publicó Money and Trade Considered, con propuestas de banco nacional y papel moneda; sus propuestas para Escocia fueron rechazadas y se fue a buscar fortuna al extranjero.", WP + "John_Law_(economist)", CONSULTA, "1705", SEC),
             ]},
            {"id": "C2_1718", "date": "1718",
             "hecho": "En mayo de 1716 el regente Felipe de Orleans aprobó su banco privado de billetes; en 1717 fundó la Compañía de Occidente (Mississippi) para explotar Luisiana, con acciones de 500 libras pagaderas en bonos de deuda; en 1718 el gobierno compró su banco, convertido en Banque royale, y la compañía fundó Nueva Orleans.",
             "P": [("vision", .80), ("ambicion", .80)],
             "A": [("persuasion", .78), ("planificacion", .74)],
             "C": [("redes_prestigio", .78), ("prosperidad", .74)],
             "evidencia": [
                 EV("En 1716 el regente aprobó su plan de banco privado que emitía billetes; en 1718 fue comprado por el gobierno y se convirtió en la Banque royale; en 1717 fundó la compañía del Misisipi para explotar Luisiana.", WP + "John_Law_(economist)", CONSULTA, "1718", SEC),
                 EV("Las acciones se ofrecieron a 500 libras pagaderas en bonos de deuda pública a la par; en la primavera de 1718 se fundó Nueva Orleans.", WP + "Mississippi_Company", CONSULTA, "1718", SEC),
             ]},
            {"id": "C3_1720", "date": "1720-01-05",
             "hecho": "En 1719 su compañía absorbió otras compañías coloniales, la acuñación y el cobro de impuestos, y sus acciones pasaron de 500 a 3,000 libras entre junio y agosto; compró grandes propiedades, se convirtió al catolicismo y entró en la Academia de Ciencias; el 5 de enero de 1720 el regente lo nombró controlador general de finanzas.",
             "P": [("ambicion", .82), ("orgullo_hubris", .78)],
             "A": [("acumulacion_capital", .82), ("audacia", .80)],
             "C": [("poder", .84), ("popularidad", .74)],
             "evidencia": [
                 EV("Las acciones subieron de su par de 500 libras a 750 el 17 de junio, 1,000 el 21 de julio y 3,000 el 17 de agosto de 1719; en 1719 la compañía obtuvo las casas de moneda y el cobro de impuestos.", WP + "Mississippi_Company", CONSULTA, "1719-08-27", SEC),
                 EV("Se convirtió al catolicismo el 17 de septiembre de 1719, fue elegido miembro honorario de la Academia de Ciencias el 2 de diciembre de 1719 y el regente lo nombró controlador general de finanzas el 5 de enero de 1720.", WP + "John_Law_(economist)", CONSULTA, "1720-01-05", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 09
    {
        "id": "F003_09_CARNEGIE", "person": "Andrew Carnegie", "tipo": "empresario",
        "question": "¿Qué trayectoria sigue Andrew Carnegie tras volver de Europa con planes para montar su propia planta de acero con el proceso Bessemer?",
        "z_trabajo": "1873-01-01", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta 1872.",
        "cuts": [
            {"id": "C1_1859", "date": "1859-12-01",
             "hecho": "Hijo de un tejedor escocés empobrecido que emigró a Pittsburgh en 1848, empezó como bobinador de algodón por 1.20 dólares semanales y luego como mensajero de telégrafo; desde 1853 fue secretario y telegrafista de Thomas A. Scott en el Ferrocarril de Pensilvania y el 1 de diciembre de 1859 llegó a superintendente de la División Oeste.",
             "P": [("ambicion", .80), ("anhelo_seguridad", .72)],
             "A": [("esfuerzo_sostenido_reciente", .80), ("aprendizaje", .78)],
             "C": [("mentoria_activa", .80), ("ascenso_reciente", .78)],
             "evidencia": [
                 EV("Su familia llegó a Allegheny en septiembre de 1848; su primer empleo fue de bobinador en una fábrica de algodón por 1.20 dólares a la semana; en 1849 se hizo mensajero de telégrafo.", WP + "Andrew_Carnegie", CONSULTA, "1849", SEC),
                 EV("Desde 1853 Thomas A. Scott, del Ferrocarril de Pensilvania, lo empleó como secretario y telegrafista; el 1 de diciembre de 1859 fue nombrado superintendente de la División Oeste.", WP + "Andrew_Carnegie", CONSULTA, "1859-12-01", SEC),
             ]},
            {"id": "C2_1865", "date": "1865",
             "hecho": "Con ayuda de Scott hizo sus primeras inversiones; en 1864 invirtió en la Columbia Oil Company, que en un año pagó más de un millón de dólares en dividendos; en 1865 fundó la Keystone Bridge Company y dejó el ferrocarril para dedicarse al hierro, usando sus contactos con Scott y J. Edgar Thomson para conseguir contratos.",
             "P": [("vision", .78), ("ambicion", .80)],
             "A": [("acumulacion_capital", .80), ("diversificacion", .76)],
             "C": [("redes_prestigio", .80), ("prosperidad", .78)],
             "evidencia": [
                 EV("En 1864 fue uno de los primeros inversionistas de la Columbia Oil Company, que en un año pagó más de un millón de dólares en dividendos; tras la guerra dejó los ferrocarriles por la siderurgia y usó sus contactos con Scott y Thomson para obtener contratos.", WP + "Andrew_Carnegie", CONSULTA, "1865", SEC),
                 EV("La Keystone Bridge Company fue fundada en 1865 por Andrew Carnegie.", WP + "Keystone_Bridge_Company", CONSULTA, "1865", SEC),
             ]},
            {"id": "C3_1872", "date": "1872",
             "hecho": "En 1868, a los 33 años, escribió un memorando proponiéndose limitar su ingreso a 50,000 dólares anuales y retirarse de los negocios; en el verano de 1872, en Europa, conoció el proceso Bessemer y volvió a Pittsburgh con planes para construir su propia planta Bessemer junto a socios como Henry Phipps y su hermano Thomas.",
             "P": [("ambicion", .80), ("vision", .82)],
             "A": [("herramienta_nueva", .80), ("planificacion", .78)],
             "C": [("oportunidad", .82), ("alianza", .76)],
             "evidencia": [
                 EV("En 1868, a los 33 años, escribió que se proponía no tomar un ingreso mayor de 50,000 dólares al año y dejar los negocios.", WP + "Andrew_Carnegie", CONSULTA, "1868", SEC),
                 EV("En el verano de 1872, estando en Europa, conoció el proceso Bessemer y volvió a Pittsburgh con planes para construir su propia planta Bessemer; entre sus socios estaban Henry Phipps Jr. y Thomas M. Carnegie.", WP + "Edgar_Thomson_Steel_Works", CONSULTA, "1872", SEC),
             ]},
        ],
    },
    # ------------------------------------------------------------------ 10
    {
        "id": "F003_10_PEDRO_II", "person": "Pedro II de Brasil", "tipo": "gobernante",
        "question": "¿Qué trayectoria sigue el emperador Pedro II de Brasil tras volver de Europa enfermo y ser recibido con entusiasmo después de la abolición de la esclavitud?",
        "z_trabajo": "1888-09-01", "modo_z": "historico", "preparacion_ciega": dict(CIEGA),
        "source_notes": "Fuentes secundarias (Wikipedia en inglés) consultadas a ciegas; solo hechos fechados hasta agosto de 1888.",
        "cuts": [
            {"id": "C1_1840", "date": "1840-07-23",
             "hecho": "Emperador desde los cinco años por la abdicación de su padre en 1831, tras una regencia inestable la Asamblea General lo declaró mayor de edad a los 14 años el 23 de julio de 1840; los políticos lo aceptaban como autoridad indispensable para el país.",
             "P": [("deber", .82), ("responsabilidad", .78)],
             "A": [("aprendizaje", .76), ("autocontrol", .72)],
             "C": [("legitimidad_percibida", .82), ("autoridad", .80)],
             "evidencia": [
                 EV("La abdicación de su padre en 1831 lo dejó emperador a los cinco años; el 23 de julio de 1840 la Asamblea General lo declaró mayor de edad a los 14 años, y los políticos lo aceptaban como figura de autoridad indispensable.", WP + "Pedro_II_of_Brazil", CONSULTA, "1840-07-23", SEC),
             ]},
            {"id": "C2_1871", "date": "1871-09-28",
             "hecho": "Dirigió con tenacidad la guerra contra Paraguay hasta la victoria del 1 de marzo de 1870 y rechazó una estatua ecuestre para construir escuelas; en 1867 pidió en el discurso del trono la abolición gradual de la esclavitud, fue muy criticado, y el 28 de septiembre de 1871 se aprobó la Ley del Vientre Libre.",
             "P": [("deber", .80), ("justicia_social", .76)],
             "A": [("determinacion", .82), ("negociacion", .72)],
             "C": [("legitimidad_percibida", .78), ("presion_social", .70)],
             "evidencia": [
                 EV("Su negativa a aceptar menos que la victoria total fue decisiva; la guerra terminó con la muerte de López el 1 de marzo de 1870 y él rechazó una estatua ecuestre para construir escuelas.", WP + "Pedro_II_of_Brazil", CONSULTA, "1870-03-01", SEC),
                 EV("En el discurso del trono de 1867 pidió la erradicación gradual de la esclavitud y fue muy criticado; la Ley del Vientre Libre se promulgó el 28 de septiembre de 1871.", WP + "Pedro_II_of_Brazil", CONSULTA, "1871-09-28", SEC),
             ]},
            {"id": "C3_1888", "date": "1888-08",
             "hecho": "Con la salud muy deteriorada desde junio de 1887, viajó a Europa y en Milán pasó dos semanas entre la vida y la muerte; el 13 de mayo de 1888 su hija Isabel, como regente, firmó la Lei Áurea que abolió la esclavitud; él volvió a Río de Janeiro en agosto de 1888 y fue recibido con un entusiasmo nunca visto.",
             "P": [("deber", .76), ("vulnerabilidad", .74)],
             "A": [("confianza", .70), ("moderacion", .74)],
             "C": [("popularidad", .82), ("crisis_abrupta", .64)],
             "evidencia": [
                 EV("En junio de 1887 su salud había empeorado mucho y fue a Europa a tratarse; en Milán pasó dos semanas entre la vida y la muerte; el 22 de mayo de 1888 recibió la noticia de la abolición y volvió a Río de Janeiro en agosto de 1888, donde todo el país lo recibió con un entusiasmo nunca visto.", WP + "Pedro_II_of_Brazil", CONSULTA, "1888-08", SEC),
                 EV("La Lei Áurea, ley 3,353 del 13 de mayo de 1888, abolió la esclavitud en Brasil y fue firmada por la princesa imperial Isabel como regente.", WP + "Lei_%C3%81urea", CONSULTA, "1888-05-13", SEC),
             ]},
        ],
    },
]
