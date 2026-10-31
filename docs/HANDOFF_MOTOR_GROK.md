# HANDOFF MOTOR U6 → Grok principal (31-oct-2026 CDMX)

**Para:** Grok principal (app grok.com / no bot) · **De:** Puta 3 (Grok Bot) por pedido de Mj  
**Repos:** dar a Grok escritura en repos y que cablee/arregle el motor sin gastar tokens del bot.

## Repos (cuenta `marcojpad-hash`)

| Repo | Uso | Privado |
|------|-----|---------|
| https://github.com/marcojpad-hash/motor-u6-storage | Motor canónico + fábrica + informes | sí |
| https://github.com/marcojpad-hash/ChatGPT-migracion | Bandeja entre modelos | sí |
| https://github.com/marcojpad-hash/capcot-capsulas-imaginantes | CAPCOT / Datos y ociosidades | público |

**Acceso:** instalar/confirmar GitHub App [Grok (by xAI)](https://github.com/apps/grok-by-xai) con Contents + Pull requests **write** sobre esos repos. En grok.com, conectar GitHub si pide vínculo.

Clone motor: `git clone https://github.com/marcojpad-hash/motor-u6-storage.git` · trabajar en `main` · `git pull --rebase` antes de cada commit.

## Candado (no negociable)

- **No tocar** Engine V5 ni el catálogo de **244** patrones. Candados antes/después deben seguir `true`.
- Piezas/herramientas **no son decorativas**: deben ejecutar de verdad; si no, CEB marca dónde/por qué (regla Mj).
- Commits claros; preferir PR si el cambio es grande; no borrar historial de lotes F003–F006.

## Lectura obligatoria (orden)

1. `informes/2026-10-31_AUDITORIA_CONTINUIDAD_Y_ESTADO.md`
2. `informes/2026-10-31_SIGUIENTE_FASE_CASOS_CIEGOS.md`
3. `docs/MAPA_VERSIONES_Y_AUTORIDAD.md`
4. `docs/CEB_INVESTIGAR_Y_RESOLVER.md`
5. `docs/BRUJULA_OBLIGACION_BUSQUEDA_RESOLUCION.md`
6. `informes/2026-10-26_mapa_corto_motor.md`
7. `casos/fabrica/lotes/F005_RESUMEN.json` (+ F003/F004)
8. `casos/ciegos/PROTOCOLO_CUSTODIA_INDEPENDIENTE.md` y `PLAN_20_CASOS_MOTOR.md`

## Estado comprobado (31-oct)

**Bien cableado con evidencia:** CEB 5 estados Caldero (`estado_honesto_caldero`); búsqueda real (ddg/bing, no fixture en F003–F005); sync StinkBox tras fábrica; regla 022 + sellado; parches 014–016 en runner; traza 244 + PAC en CI.

**Débil / decorativo:**
- Guardián pistas LLM Caldero cableado pero fábrica **nunca** llena `caldero_llm_neighbor_hints` → lista vacía.
- Filtro tokens StinkBox deja basura (genéricos, inglés, cortos, dígitos).
- `status` de componente aún puede decir EXECUTED con fixture; el honesto solo vive en CEB.
- Brújula ChatGPT = solo documento.

**A medias / falta:**
- 017: cierre terminal sí; `filtro_entrada_dirigida_017` / `consulta_dirigida_v1` solo en tests.
- Checkpoint unificación 20261011: no integrado al repo (solo en workspace del bot).
- Intercapa: sensor lateral sí; **Bombe**, mensajes laterales y módulo propio token→eje: **sin código**.
- Pack Meta guardián ontológico: no está en este repo.
- F006 = reevaluación Courbet (no caso ciego nuevo). C01–C20 pendientes.

**Riesgo fuerte — sesgo continuidad:** F005: ningún escenario de bajada aunque 6/8 cayeron; H1 0/8. Web viva no filtra por fecha de corte (solo self-match); pistas LLM vacías → no aplica filtro futuro.

## Trabajo que Grok debe hacer (prioridad)

1. **Cablear fábrica → pistas LLM Caldero:** que `fabrica.py` (o el preparador) llene `caldero_llm_neighbor_hints` y el guardián filtre de verdad; smoke en 1 caso de fábrica.
2. **Endurecer filtro StinkBox:** descartar genéricos/inglés basura/tokens cortos/con dígitos inútiles; conservar útiles para familias faltantes; opcional: alimentar `brechas` al pipeline (hoy es reporte muerto).
3. **Alinear status componente con CEB:** no EXECUTED si proveedor=fixture (sin tocar Engine/244).
4. **017 completo:** cablear `filtro_entrada_dirigida_017` + `consulta_dirigida_v1` al runner UNICO (hoy solo tests).
5. **Corte temporal Caldero:** filtrar vecinos/web por fecha ≤ Z (no solo self-match), sin romper candados.
6. **Sesgo continuidad:** documentar + proponer calibración con n≥10 independientes (no cambiar pesos con n=1); preparar cohorte C01–C20 según protocolo de custodia (roles separados; no fabricar sujetos).
7. **Intercapa (si Mj prioriza):** token→eje, Bombe, mensajes laterales no decisores — hoy solo plan en workspace; implementar como laterales, Engine/244 intactos.
8. Seguir `CEB_INVESTIGAR_Y_RESOLVER.md` y la brújula: buscar, ejecutar, arreglar; no etiquetar OK decorativo.

## Qué NO hacer

- No modificar Engine V5 ni patrones 244.
- No inflar n reevaluando el mismo `input_sha256`.
- No publicar CAPCOT ni montar videos desde aquí salvo que Mj lo pida aparte (CAPCOT tiene su propio handoff).
- No pedir al bot Puta 3 que implemente: eso es lo que estás sustituyendo.

## Cómo reportar

Commit + link en el repo; aviso corto a Mj (o nota en `bandeja/` de ChatGPT-migracion firmada). Si te bloquea auth GitHub, di exactamente qué pide la pantalla.

## Contacto roles

- **Mj:** decide Ricci, luces/branch, priorización intercapa, custodio ciegos.
- **Puta 3 (bot):** motor U6 coordinación ligera / rutinas; no gastar tokens en cableado pesado.
- **ChatGPT / Claude / Copilot:** pueden armar en repo si ya tienen acceso; Grok ahora también escribe.
