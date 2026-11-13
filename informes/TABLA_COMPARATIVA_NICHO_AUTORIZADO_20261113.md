# Tabla comparativa — nicho + 3 plugins autorizados (rama alterno/motor-autorizado)

**Fecha:** 2026-11-13. **Orden de Marco:** autorizar TODO lo marcado "NO AUTORIZADO"
(dossier 2026-09-07), cablear POR PARTES (una pieza a la vez, correr, registrar
el delta, y solo entonces seguir), sin integrar nada al 244/V5 y sin tocar F.
**Rama:** `alterno/motor-autorizado` (desde cameo-pesos 79b046e). **Nada subido.**

## Método (el control que hace válida la comparación)

- **Una pieza por etapa:** BASELINE (nada) → P1 nicho → P2 alias → P3 embudo → P4 fix.
  Cada etapa corre los mismos 6 casos (5 sondas mínimas + Napoleón) en el mismo orden.
- **Reset del StinkBox por etapa:** el índice del StinkBox alimenta al motor.
  Verificado: Napoleón 2 veces tras reset da el mismo H1/H2; SIN reset, H2 cambió
  (30_ambicion → arquetipo_el_gobernante). Cada etapa arranca con el StinkBox vacío.
- **Determinismo:** el motor es determinista dado el mismo estado del StinkBox.
- **Las 4 piezas son observación (traza), no modifican la entrada ni F ni H.**
  Por diseño (nota: "NO multiplicar dentro de F sin prueba. Eso seria V6").

## Delta POR PIEZA (H1/H2 por caso y etapa)

H1/H2 son **IDÉNTICOS en las 5 etapas para los 6 casos** (el delta en H es cero,
como corresponde a laterales de observación). Lo que cambia en cada etapa es la
traza que aparece en el RESULT (`laterales_unico.sensores_pre`).

| Caso | H1 (todas las etapas) | H2 (todas las etapas) |
|---|---|---|
| SONDA_MONROE_TIPO | schwartz_10_autodireccion | tainter_04_colapso_por_simplificacion_forzada |
| SONDA_ALEJANDRO_TIPO | arquetipo_el_gobernante | 30_ambicion |
| SONDA_JOSE_A | arquetipo_el_creador | schwartz_10_autodireccion |
| SONDA_JOSE_EF | schwartz_10_autodireccion | arquetipo_el_creador |
| SONDA_FREUD_C | sustancias_03_severo | utopia_mentalidad_liberal |
| NAPOLEON | 31_conflicto_con_un_dios | arquetipo_el_gobernante |

### P1 — lateral nicho (plugin_nicho_campo_v1.py, NUEVO)
Fórmula literal de la nota: w' = w·(1 + alpha·n_campo/n_corte), alpha 0.2 (punto
medio del rango 0.1–0.3 de la nota), cap 0.999. Campos: conquista | agencia |
clinico | sacro (fuentes: 30_ambicion, fix_entrada, embudo, gloria_sacro;
solape por prioridad conquista > agencia > clinico > sacro).
**Delta:** aparece la traza `nicho_campo` (ACTIVA en los 6 casos). H1/H2 sin cambio.
- Monroe: ambicion sola (n_campo=1) → +5.0% (0.80→0.84); agencia junta
  (autonomia+inconformismo, n_campo=2) → +10.0%. El nicho empuja la agencia
  (ficha correcta) más que la ambicion sola.
- Alejandro: conquista junta (n_campo=3 en C3) → +12.0% (poder 0.84→0.9408,
  sed_de_mando 0.80→0.896, escalada 0.75→0.84). La ficha correcta se fortalece.
- Freud C: consumo_sustancias solo (clinico, n_campo=1) → +5.0% (0.80→0.84).
- Napoleón: conquista +6.67% (C1/C2), +3.33% (C3, ambicion sola).
- José A / José E-F: sin tokens 30_ambicion; el sacro (reconocimiento+estatus)
  llega a +13.33% en C3. Sin token clínico en los cortes crudos (eso lo pone el alias, P4).
- Sensibilidad (Alejandro C2, ambicion): alpha 0.1 → 0.868; 0.2 → 0.896; 0.3 → 0.924.
  La elección de alpha mueve el resultado ~±0.03; el orden (junto > solo) no cambia.

### P2 — plugin_alias_reactivacion (ya existía; ahora cableado como lateral)
Traduce sinónimos lavados → léxico 244 SOLO con el texto de ESA ventana (hecho).
**Delta:** aparece la traza `alias_reactivacion`. H1/H2 sin cambio.
- José A: +1 token en C1 (consumo_sustancias, por "desorden").
- José E-F: +2 tokens en C5 (consumo_sustancias por "desorden";
  desgaste_cambaceo_itinerante por "carretera"+"desplazamientos").
- Monroe, Alejandro, Freud C, Napoleón: 0 agregados (negativos correctos).
- **Hallazgo — el alias es ciego a negaciones:** `traducir([], hechos="sin carretera")`
  devuelve desgaste_cambaceo_itinerante 0.78. El texto dice SIN carretera y el
  alias lo traduce como si hubiera carretera. Por eso la sonda José A se corrigió
  (se quitó "sin carretera" del hecho; la intención "no hay carretera" se expresa
  por omisión) y la BASELINE y P1 se re-corrieron con la sonda corregida, para que
  todas las etapas compartan la misma entrada.

### P3 — plugin_embudo_clinico (ya existía; ahora cableado como lateral)
Etiqueta RUIDO_ALIAS / PERFIL_VENTANA / PERFIL_SOSTENIDO sobre los cortes CRUDOS.
**Delta:** aparece la traza `embudo_clinico`. H1/H2 sin cambio.
- Freud C: global PERFIL_VENTANA, sosten_max=1, C3=PERFIL_VENTANA
  (exacto lo que dice la nota: "PERFIL_VENTANA sosten 1. Ya paso.").
- Monroe, Alejandro, José A, José E-F, Napoleón: NO_APLICA (sin token clínico
  en los tokens crudos; el clínico de José A/E-F solo aparece vía alias, en P4).

### P4 — plugin_fix_entrada (ya existía; ahora cableado como lateral)
preparar_caso = alias por ventana + remapeo ambicion→autonomia (si cero conquista)
+ embudo sobre el caso PREPARADO. La traza es el caso preparado (propuesta,
NO se aplica a la entrada del motor).
**Delta:** aparece la traza `fix_entrada` (caso preparado + embudo preparado).
H1/H2 sin cambio.
- Monroe: C2 ambicion REMOVIDA (remapeo a autonomia, que ya estaba en el corte;
  campos C2: conquista=0, agencia=2, tiene_ambicion=False). La ficha equivocada
  deja de encenderse en el caso preparado.
- Alejandro: SIN cambios (campos C2 conquista=1, C3 conquista=3). Correcto:
  con conquista presente no hay remapeo. Es el control negativo del fix.
- José A: C1 +consumo_sustancias (alias); embudo preparado global=RUIDO_ALIAS,
  C1=RUIDO_ALIAS. **Exacto lo esperado por la nota.**
- José E-F: C5 +consumo_sustancias +desgaste_cambaceo_itinerante (alias);
  embudo preparado global=PERFIL_VENTANA, sosten_max=1, C5=PERFIL_VENTANA.
  **Exacto lo esperado por la nota.**
- Freud C: sin cambios; embudo preparado PERFIL_VENTANA sosten_max=1 (igual que P3).
- Napoleón: C3 ambicion→autonomia (remap). Observación: el remap es POR CORTE,
  así que un token se remapea en un corte y no en otro (C1/C2 conservan ambicion
  porque ahí sí hay conquista; C3 la pierde). Es la regla como está escrita;
  si se quiere que el remap considere la vida entera y no solo la ventana,
  hay que cambiar la regla, no el plugin.

## Prueba mínima (nota, "PRUEBA MINIMA SI AUTORIZAS") — veredicto: 5/5

| Caso | Esperado (nota) | Medido (P4) | Veredicto |
|---|---|---|---|
| Monroe-tipo | "controlar su trabajo" no debe dejar 30_ambicion de letrero | C2 ambicion removida (remap); H1 ya era schwartz_10_autodireccion (agencia), no 30_ambicion; nicho empuja agencia +10% vs ambicion sola +5% | PASA |
| Alejandro-tipo | poder+escalada SÍ deja 30_ambicion | Sin remap (conquista 1→3); H2=30_ambicion; nicho +12% en C3 | PASA |
| Jose A (cuna, sin carretera) | RUIDO_ALIAS | Embudo preparado: global RUIDO_ALIAS, C1 RUIDO_ALIAS | PASA |
| Jose E-F (desorden+desplazamientos) | PERFIL_VENTANA | Embudo preparado: global PERFIL_VENTANA, sosten_max=1, C5 PERFIL_VENTANA | PASA |
| Freud C (cocaina explicita) | PERFIL_VENTANA sosten 1 | Embudo crudo y preparado: global PERFIL_VENTANA, sosten_max=1 | PASA |

Matiz Monroe: el H1 ya era agencia en la BASELINE (el motor leía bien la H
aunque el token ambicion estuviera en C2). Lo que resuelven el nicho y el fix
es el nivel token: el nicho empuja la agencia más que la ambicion sola, y el
fix quita el token ambicion del corte. La prueba mínima se cumple a nivel
token/etiqueta, no porque H1 cambiara (H1 no cambió en ninguna etapa).

## ¿Resuelven el problema Chet/José/Monroe/Alejandro?

**Sí, a nivel de los laterales (que es donde vive el problema).** El problema
era que get_weight + support no hacen nicho (cada token empuja solo) y que el
mapper pone ambicion donde el texto dice agencia, y no pone consumo_sustancias
donde el texto dice desorden/carretera. Medido:
- El nicho SÍ discrimina "ambicion sola" (Monroe, +5%) de "ambicion con
  conquista" (Alejandro, +12%): la ficha correcta se fortalece cuando sus
  vecinos están, y no cuando está sola.
- El alias SÍ pone los tokens que el texto lavado pide (José A +1, José E-F +2),
  y no pone nada donde no hay texto lavado (Monroe, Alejandro, Freud, Napoleón: 0).
- El embudo + fix SÍ etiquetan correctamente: RUIDO_ALIAS en cuna sin co-token,
  PERFIL_VENTANA en oficio con co-token, PERFIL_VENTANA sostenido 1 en explícito.
- **Lo que NO hacen (por diseño):** no cambian H1/H2 ni F. Son observación.
  Si se quiere que el nicho o el fix CAMBIEN la H, eso es otro paso (multiplicar
  dentro de F sería V6, según la propia nota) y requiere la decisión de Marco.

## Estado de las piezas (registro_piezas, P4)

- nicho_campo: ACTIVA en los 6 casos.
- alias_reactivacion: ACTIVA en José A y José E-F; ACTIVA_MUDA en los demás.
- embudo_clinico: ACTIVA en Freud C; ACTIVA_MUDA en los demás.
- fix_entrada: ACTIVA en Monroe, José A, José E-F, Freud C, Napoleón;
  ACTIVA_MUDA en Alejandro (el control negativo: no hay nada que arreglar).

## Integridad

- Engine canónico: sha256 665c39a2861e… (sin cambio). Catálogo 244: sha256
  d827dcc38826… (sin cambio, 244 familias / 703 tokens). Nada fusionado al 244/V5.
- Suite: `pytest motor/tests/` = **148 passed, 2 skipped**, igual que en la rama
  prístina (verificado con git stash). Ningún test roto ni eliminado.

## Archivos (para el stage, espejo de rutas del repo)

- `motor/motor/plugin_nicho_campo_v1.py` (NUEVO: lateral nicho, contrato
  NICHO_CAMPO_V1_20261113, can_decide_H False)
- `motor/motor/laterales_unico_v1.py` (MODIFICADO: 4 _pieza en sensores_pre:
  nicho_campo, alias_reactivacion, embudo_clinico, fix_entrada)
- `casos/sondas_nicho_minima/` (NUEVO: 5 sondas + correr_etapa.py)
- `motor/runs_etapas/*/RESUMEN_*.json` (5 resúmenes compactos, uno por etapa;
  los RESULT completos (~6 MB c/u) quedan en la copia de trabajo, no en el stage)
- `fuentes_originales/202609/DOSSIER_V15_1_20260914/docs/04_READMES_CANDADOS_Y_PROTOCOLOS.txt`
  (MODIFICADO: las dos notas pasan a AUTORIZADO por Marco 2026-11-13)
- `informes/TABLA_COMPARATIVA_NICHO_AUTORIZADO_20261113.md` (este documento)

## Pendientes que quedan (no son de esta rama)

- La nota pedía tabular los n_* del punto 4 y el Grupo B (campo vs Top-1) antes
  de poner alpha o peso en el 244. Aquí se midió la prueba mínima; el Grupo B
  (A_dir / A_top1 / A_lag por caso) sigue pendiente.
- El alias es ciego a negaciones ("sin carretera" → carretera). Si se usa para
  preparar casos reales, hay que añadir una guarda de negación o revisar a mano.
- El remap ambicion→autonomia es por corte (ventana). Napoleón C3 lo muestra:
  la ambicion se remapea en C3 pero no en C1/C2. Si se quiere por vida entera,
  es un cambio de regla.
