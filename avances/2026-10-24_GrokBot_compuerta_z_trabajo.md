# 2026-10-24 — Grok Bot — Compuerta Z_trabajo + preparación ciega

**Qué cambió:** validador nuevo `motor/calibracion/gate_z90.py` (R1–R7). La fábrica gana `preparar-z` (semillas y destinos en archivos separados; el lote se rechaza completo ante cualquier violación) y vuelve a revisar antes de `correr`. El arnés rechaza (GATE_Z90_RECHAZADO) las entradas con `gate_z` que violen la compuerta. Nuevos: prompt `casos/fabrica/PROMPT_SEMILLAS_Z.md`, plantillas, y addendum de contrato `motor/CONTRATO_ENTRADA_LLM_ADDENDUM_Z_TRABAJO_20261024.txt`.

**Antes → ahora:** antes, una semilla podía traer, sin querer, hechos o años posteriores al corte (solo se revisaba la fecha del corte). Ahora cada afirmación necesita fuente, fechas ≤ Z y "conocido_en_Z: sí", sin futuro y sin palabras del final. Además, quien escribe la entrada no ve el destino.

**Hashes canónicos:** Engine 665c39a2…c36082 y patterns_final_v14 d827dcc3…6667a1 sin cambios.

**Pruebas:** un lote de prueba con fugas (año 1814, "terminará", "Elba", Wikipedia en vivo en modo vivo, primaria fechada después de Z, custodio que no coincide) fue rechazado completo, sin escribir nada en la cola. Arnés: tests 7/7.
