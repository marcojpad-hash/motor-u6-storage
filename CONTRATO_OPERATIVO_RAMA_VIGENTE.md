# Contrato operativo — rama vigente del motor U6

Vigente desde: 2026-11-11 01:55 CST. Ordena: Mj. Lo deja: Puta 3.

## Regla
1. **Rama de trabajo vigente: `alterno/cameo-pesos`.** Todo trabajo nuevo del motor (parches, corridas, pruebas, inputs humanos, órdenes del bus) sale de esta rama o de ramas hijas de ella (p. ej. `alterno/inputs-humanos`). Los PR van contra `alterno/cameo-pesos`, no contra `main`, hasta que Mj diga otra cosa.
2. **Modelo anterior cancelado.** El motor de `main` (estado previo a 2026-11-11, CAMEO sin `peso_equivalente`) queda **SOLO_CONSULTA**: historial para saber qué no hacer o qué se pasó. No se borra, no se reescriben sus valores ni hashes, y no se usa como base de calibración ni como comparación directa de puntaje. Sus corridas (p. ej. `casos/resultados/resultados.jsonl` hasta 2026-11-10) son consulta.
3. **Lo que NO cambia:** Engine `motor/Engine_V5_CANONICO_SOLO.py` (sha256 665c39a2…) y catálogo 244 `motor/patterns_final_v14.json` (sha256 d827dcc3…) siguen siendo canónicos en ambas ramas (`motor/ACTIVE_ENGINE_SELECTION.json`). No se tocan.
4. **Escala:** todo peso, componente y puntaje publicado vive en 0,01–0,999 (escala del Engine). Sumas crudas fuera de rango (`rank_fusion`, `selected_peso_efectivo_sum`) se reportan como FALLO_ESCALA hasta normalizarlas; ver orden BUS agente-cero-costo #47.
5. **Al iniciar sesión cualquier modelo:** `git checkout alterno/cameo-pesos`, confirmar commit y hashes del Engine/244 en el recibo. Trabajo hecho sobre `main` después de esta fecha no cuenta como hecho.
6. `main` no se fusiona con la rama sin decisión de Mj.

## Evidencia de por qué
- `informes/2026-11-11_cameo-alterno.md` (rama): Napoleón con CAMEO.
- `casos/corridas_alterno/CHURCHILL_CAMEO_ALTERNO/` (rama, commit 428ceee): Churchill, misma entrada que 2026-10-24.
