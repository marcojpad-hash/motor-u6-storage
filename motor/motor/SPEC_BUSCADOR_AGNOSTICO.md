# SPEC — Buscador agnóstico de Caldero

Regla: Caldero busca como una persona que usa un buscador. Es buscador, no LLM. No depende de ninguna IA ni proveedor, y no requiere claves de API.

## Piezas obligatorias
- `ddgs`: el buscador. Se conecta a DuckDuckGo, Bing y otros motores libres.
- `primp`: hace las consultas web como navegador normal.
- `lxml`: lee el HTML de los resultados.
- `click`: dependencia de `ddgs`.

## De dónde se sacan
1. **Si vienen en el paquete** (`motor/_vendor_buscador/`, parte 3 `U6_PARTE3_BUSCADOR.zip`): se usan de ahí. El motor los carga primero desde esa carpeta.
2. **Si no vienen en el paquete:** hay que instalarlos antes de correr:
   `pip install ddgs primp lxml click`
   Los de la parte 3 están compilados para Linux x86_64 con Python 3.13; en otro sistema se instalan con pip aunque vengan en el paquete.

## Orden de buscadores (`CALDERO_BUSCADOR=auto`)
ddgs → DuckDuckGo html → DuckDuckGo lite → Bing → SearXNG → Wikipedia → Google html.
Claves opcionales (EXA, Brave, Serper, Tavily) van al final y nunca son requisito.

## Interruptores
- `CALDERO_BUSQUEDA_VIVA=1`: busca en vivo e ignora resultados grabados.
- `CALDERO_BUSCADOR`: fija un buscador (`auto` por defecto).
- `CALDERO_REGION`: región (`wt-wt` por defecto).

## Prohibido
- Atar Caldero a un LLM o proveedor (p.ej. `chatgpt_connected_tool`, Exa obligatorio).
- Exigir claves de API.
- Quitar la consulta ciega o el filtro de identidad.
