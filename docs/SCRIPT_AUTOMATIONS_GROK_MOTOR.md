# Script de automations — Motor U6 → Grok principal

Fecha: 2026-10-31 CDMX · De: Puta 3 · Para: Mj pega esto en **grok.com → Automations**

Grok ya tiene GitHub App con write (All repositories). El bot Puta 3 **deja de correr** estas rutinas; tú las programas en Grok.

Zona horaria: **America/Mexico_City**. Repo motor: `marcojpad-hash/motor-u6-storage`. Bandeja: `marcojpad-hash/ChatGPT-migracion`.

Candado global (aplica a todas): no tocar Engine V5 ni catálogo 244; candados antes/después `true`; no inventar hechos; piezas no decorativas (CEB).

---

## A1 — Fábrica diaria de calibración

- **Cuándo:** todos los días ~04:30 CDMX  
- **Nombre sugerido:** `Motor — Fábrica lote diario`

**Prompt (pegar tal cual):**

```
Eres Grok principal con write en GitHub (marcojpad-hash). Corre el lote diario de la fábrica de casos del motor.

Repo: https://github.com/marcojpad-hash/motor-u6-storage
Sigue casos/fabrica/README.md y docs/HANDOFF_MOTOR_GROK.md.

Candado: no modificar Engine V5 ni catálogo 244. Verifica hashes antes y después (README / último resumen de lote). Si no coinciden, para y avisa a Mj.

Pasos:
1) Mira el último lote en casos/fabrica/ (F00N). Crea semillas_lote_F00N+1 con preparar-z: 8–10 sujetos reales nuevos (mezcla artistas/científicos/políticos/empresarios/gobernantes), sin repetir calibracion_acumulada.csv ni Mozart/Musk/Pío/Casanova/ciego15. Incluye caídas y rupturas, no solo auges. Destinos en archivo aparte (custodio ≠ preparador si es posible; si eres ambos, márcalo como ensayo metodológico, no ciego certificado). Fuentes con link.
2) python3 casos/fabrica/fabrica.py preparar-z <semillas> <destinos>
3) python3 casos/fabrica/fabrica.py correr --lote F00N+1
4) Actualiza CALIBRACION_ACUMULADA / csv; nota en avances/; commit + push.
5) Tras correr, sincronizar_storage (StinkBox) si la fábrica no lo hizo sola.

Responde a Mj en español corto: aciertos hoy (H1, set, apuesta, destino/polaridad), acumulado, sesgo de continuidad si aparece, link del commit. Si algo bloquea, di exactamente qué.
```

---

## A2 — Bandeja entre modelos (cada hora)

- **Cuándo:** cada hora 08:00–23:00 CDMX  
- **Nombre:** `Motor — Bandeja ChatGPT-migracion`

**Prompt:**

```
Revisa el repo privado https://github.com/marcojpad-hash/ChatGPT-migracion carpeta bandeja/ (no bandeja/resueltos/) por avisos .md nuevos entre modelos.

Por cada aviso abierto:
- Si es para Grok / cualquiera y se resuelve solo dentro de este repo: resuélvelo, agrega sección Resolucion, muévelo a bandeja/resueltos/, commit y push.
- Si necesita decisión de Mj o toca motor/CAPCOT fuera de este repo: no inventes; avisa a Mj con nombre de archivo, quién lo escribió y la pregunta.
- No triangules por Mj reescrituras simples dentro del repo.

Si no hay avisos nuevos desde el último chequeo: no digas nada (silencio).
```

---

## A3 — Caso 35A HIT/MISS (cada 15 días)

- **Cuándo:** cada 15 días (mañana CDMX)  
- **Nombre:** `Motor — 35A e14→Q2`

**Prompt:**

```
Caso base 35A. En el repo o workspace del motor busca TRANSFER_V15_1 / CASO_MARCO_35A_ESTUDIO (o el path actual en motor-u6-storage / pred_hist). Lee 01_DATOS/NOTAS_AFINAR_CADA_15D.txt, BANDERA_MARCO_EPISTEMICO_PRUEBAS.txt y APUESTA_CONGELADA_e14_Q2.json.

Cada 15 días, en español llano, hechos SIN juicio:
1) Desde la última vez: ¿pasó algo notable en el día a día, o sigue parecido?
2) Loop IAs/proyecto vs delivery: ¿igual, más, menos?
3) ¿Se ve más bajada/prueba, o que se asentó?
4) Ex/compromiso: ¿hecho nuevo? (solo hecho)
5) Chequeo EKT/Holmes/Schopenhauer: ¿es lo que queríamos ver, o lo que se está mostrando?
6) BANDERA: ¿la luz «pruebas» viene de HECHO nuevo, o del modo «todo es dato»? Si solo es modo de hablar, NO cuentes HIT solo por eso.
7) Cierra HIT / MISS / NO_VERIFICABLE según apuesta e14→Q2 (NO reescribir la apuesta).

Anota en 03_SALIDA/revisiones/YYYY-MM-DD.txt y commit. Si el caso cierra, desactiva esta automation.
```

---

## A4 — Salud CEB / integridad (2× semana)

- **Cuándo:** lunes y jueves ~09:00 CDMX  
- **Nombre:** `Motor — Smoke CEB e integridad`

**Prompt:**

```
Repo motor-u6-storage. Sin tocar Engine/244:
1) Corre smoke/tests de contratos si existen (.github/workflows/test-motor-contracts.yml o pytest local de motor/tests).
2) Revisa el último lote de fábrica: ¿CEB marca EJECUTADO real o fixture? ¿compuerta piezas OK?
3) Mira stinkbox/tokens.jsonl: ¿sigue entrando basura? Si el filtro falla, abre issue o PR de endurecimiento (docs/HANDOFF_MOTOR_GROK.md punto 2).
4) Confirma hashes Engine/244 iguales al compromiso del último lote.

Si todo OK: silencio o una línea a Mj. Si hay fallo: message corto + link commit/PR.
```

---

## A5 — Backlog de cableado (una vez, luego al terminar desactivar)

- **Cuándo:** una sola corrida ahora (o diaria hasta cerrar la lista)  
- **Nombre:** `Motor — Cableado pendiente (HANDOFF)`

**Prompt:**

```
Lee docs/HANDOFF_MOTOR_GROK.md en motor-u6-storage y ejecuta en orden, con PRs o commits claros, sin tocar Engine/244:

1) Cablear fábrica → caldero_llm_neighbor_hints + guardián vivo; smoke 1 caso.
2) Endurecer filtro StinkBox.
3) Alinear status componente con CEB (no EXECUTED con fixture).
4) Cablear 017 (filtro_entrada_dirigida + consulta_dirigida) al runner UNICO.
5) Corte temporal Caldero (vecinos ≤ Z).
6) Documentar sesgo continuidad; NO cambiar pesos con n<10; avanzar cohorte C01–C20 solo con protocolo de custodia.
7) Intercapa (Bombe / mensajes / token→eje) solo si Mj lo prioriza por escrito.

Tras cada ítem cerrado: commit + avisar a Mj con link. Cuando 1–5 estén hechos, desactiva esta automation.
```

---

## Qué NO programar en Grok (queda parado o es de otros)

| Cosa | Estado |
|------|--------|
| Corrida nocturna Mozart/Pío/Musk 05:47 | **Pausada** a propósito — no reactivar salvo Mj |
| CAPCOT métricas / pantallas / cápsulas | Ya cedido a Grok/Imaginantes en handoff aparte — no mezclar con motor |
| Aviso unificar Premium (~2 dic) | Lo sigue el bot Puta 3 |
| Intercapa / Ricci / luces | Solo cuando Mj decida; no cron |

---

## Cómo activarlo en grok.com

1. Abre grok.com → **Automations** (sidebar).  
2. Crea una automation por bloque A1–A5.  
3. Pega el prompt. Pon horario CDMX como arriba.  
4. Asegúrate de que el conector GitHub esté conectado (App ya instalada: All repos + write).  
5. Prueba A1 o A5 una vez a mano antes de dejarlas solas.

Handoff de contexto: `docs/HANDOFF_MOTOR_GROK.md`
