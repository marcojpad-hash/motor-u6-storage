# Cosecha del StinkBox — lateral v2 (NO va al catálogo 244)

El StinkBox es el REPOSITORIO DE HALLAZGOS NUEVOS, no un basurero
(orden de Marco, 2026-11-13 ~04:15 CST). Su función es guardar los
tokens nuevos que no habíamos logrado ver, no llenarse de tokens.
La regla es: **SI YA LO TENEMOS, SE OMITE** — ningún token duplicado
entra al StinkBox. Las cosechas sirven para MOSTRAR las familias de
tokens que nos hacen falta, para saber que hay que meterlas: son la
evidencia de lo que falta, no un relleno.

La v1 juntaba lo activado y lo dejaba como propuesta para que Marco
decidiera. La v2 cambia el diseño: EL MOTOR DECIDE POR PROXIMIDAD
(contrato COSECHA_V2_20261113) y el dedupe es por identidad de TOKEN.

## Qué hace

`cosecha.py` lee el índice de casos resueltos
(`STINKBOX_STORAGE/resolved_cases_index.json`, 160 entradas = 53 casos
distintos) y los RESULT disponibles en `motor/`, y escribe
`COSECHA_YYYYMMDD_V2.json` + `REGISTRO_COSECHA.json`.

**Registro.** Los casos se registran por IDENTIDAD de caso (sin los
sufijos _SIN_ULTIMO/_RETENIDO del índice) y los TOKENS por identidad
de token. Una vez cosechado un caso, sus variantes no aportan nada:
en cada re-corrida se saltan los casos ya cosechados y solo se
procesan los NUEVOS o los que CAMBIARON de evidencia (p. ej. un caso
que no tenía RESULT y ahora sí lo tiene, como los 10 de F005 cuando se
corran). Y una vez cosechado un token, no vuelve a entrar: si reaparece
en más casos se omite y queda la constancia con el motivo "ya existe".

**Dedupe por token (filtrar_candidatos_caso).** Al cosechar un caso:
- `token_sin_familia` cuyo token YA está en el registro → OMITIDO
  (motivo "ya existe", ya cosechado). Solo entra la primera vez.
- `token_delta_version` cuyo token YA está en el catálogo 244 →
  OMITIDO (motivo "ya existe", ya existe en el catálogo). Los 6 delta
  de la v1 (consumo_sustancias + 5 de Minsky) están en el 244.
- `familia_top15` / `familia_en_Z` → omitidas (ya están en el 244;
  son contexto, no hallazgo: se cuenta cuántas, no se listan).

**La salida presenta las familias que faltan** (`familias_que_faltan`),
no una acumulación: un hallazgo por token sin familia, con su
decisión, su evidencia y sus vínculos. Lo que ya tenemos no se vuelve
a listar.

## La regla de proximidad (determinista, sin LLM, sin azar)

Para cada token sin familia, el motor decide por proximidad al
catálogo 244 (703 tokens). Primero la no-duplicación, luego la
proximidad a cada familia:

**Duplicado → RECHAZADO.** El token es casi el mismo que uno del
catálogo si: es el mismo token; su similitud Levenshtein normalizada
con alguno es ≥ 0.80; o comparte raíz (subcadena) con largo(corto) /
largo(largo) ≥ 0.60. Un token general ("riesgo") frente a una versión
calificada ("busqueda_riesgo", razón 0.40) NO es duplicado: mide el
concepto general, no la versión calificada.

**Proximidad a cada familia F** (tres componentes, pesos fijos):
- `nombre` (0.5): 1 si el token es un componente del nombre de la
  familia (el nombre se parte por "_"; "arte" en
  `candidato_trayectoria_arte_prestigio`).
- `raiz` (0.3): 1 si algún token de la familia contiene al token como
  subcadena (o al revés): misma raíz ("deuda" en "deuda_de_sangre",
  "riesgo" en "busqueda_riesgo").
- `coact` (0.2): fracción de las apariciones del token (caso, corte,
  eje) en las que algún token de la familia está en el mismo corte y
  eje de la misma entrada.

`puntaje = 0.5·nombre + 0.3·raiz + 0.2·coact`. La co-activación sola
nunca alcanza: las familias genéricas (`monomito_01_mundo_ordinario`)
co-activan con todo y no dicen nada.

**Decisión:**
- `ACTIVADO` como análogo de la familia más cercana si puntaje ≥ 0.50
  Y es la única en el mejor puntaje.
- `PENDIENTE` si puntaje < 0.50 (lejos de todas: necesita familia
  nueva, no análogo) o si hay empate en el mejor puntaje (ambiguo: la
  medida no puede elegir y no se fuerza la activación).
- `RECHAZADO` si es duplicado.

## Las 4 decisiones (corrida 2026-11-13)

| Token | Decisión | Familia | Puntaje | Motivo |
|---|---|---|---|---|
| arte | ACTIVADO | candidato_trayectoria_arte_prestigio | 0.500 | nombre del mismo campo; único con el componente "arte"; margen 0.329 sobre el 2º. Co-act 0.00: los tokens de esa familia no aparecen en las entradas de Rembrandt/Elvis. |
| deuda | ACTIVADO | mauss_02_deuda_de_honor | 0.500 | nombre del mismo campo; margen 0.200 sobre 4_venganza_de_parientes (raíz deuda_de_sangre, 0.300). Matiz: la deuda observada es financiera (bancarrota de Rembrandt, crash del tulipán) y la familia es deuda de honor; el análogo es deuda-como-obligación. |
| enfermedad | PENDIENTE | monomito_01_mundo_ordinario (0.175) | 0.175 | lejos de todas: sin componente en nombre de familia, sin raíz en ningún token del 244. No hay familia de enfermedad/salud en el 244; necesita familia nueva, no análogo. |
| riesgo | PENDIENTE | — (empate en 0.800) | 0.800 | ambiguo: tres familias empatan (candidato_riesgo_operativo_salud_y_medicos, candidato_riesgo_institucional_burocratico, candidato_alto_riesgo_tecnico_infraestructura), todas de riesgo ocupacional; el nombre "riesgo" está repartido y la co-activación está saturada (n=2, mismo corte). |

## Matices de vinculación (para el lateral VINCULACION_TOKENS_V1_20261112)

Un token ya conocido solo vale la pena registrarlo si tiene matices,
y el matiz vive en LA VINCULACIÓN, no en meter el token otra vez.
Cuando un token sin familia co-activa con un token del catálogo en el
mismo (caso, corte, eje), ese par es un VÍNCULO candidato para el
lateral de vinculación. Hoy V=0 porque el token sin familia es inerte
(vector cero, igual que en el canónico): V(t1,t2,c) exige familia
compartida y co-ocurrencia, y el token sin familia no tiene familia.
El vínculo se activa cuando el token tenga familia (análogo). Los
vínculos se deduplean por par: un vínculo ya registrado no se vuelve
a reportar. 27 vínculos registrados (arte 13, deuda 5, enfermedad 6,
riesgo 3):

- **arte** → aprendizaje, audacia, conocimiento, creatividad,
  curiosidad_abstracta, generacion_ideas, independencia,
  logro_personal, proposito_claro, reconocimiento, reflexion, rutina,
  sacrificio (el campo creativo: 110 instancias en 28 apariciones).
- **deuda** → amenaza_central, crisis_abrupta, estabilidad,
  incertidumbre, ruina (el campo crisis/ruina: 21 instancias).
- **enfermedad** → aislamiento_social, amenaza_central,
  busqueda_identidad, consumo_sustancias, crisis_abrupta,
  perdida_familiar (el campo del declive: 24 instancias; nótese
  consumo_sustancias: la enfermedad y las sustancias co-ocurren en
  los cortes tardíos de Elvis).
- **riesgo** → amenaza_central, exposicion_trauma_ajeno, obstaculo
  (el campo peligro/obstáculo: 6 instancias en Tubman C3_1853).

## Qué encontró (corrida 2026-11-13, COSECHA_20261113_V2.json)

99 casos en la unión (53 distintos en el índice); registro antes: 0,
migrados desde v1: 99 casos y 4 tokens; nuevos: 0, saltados: 99.
Hallazgos nuevos: 0 (los 4 ya venían de la v1); omitidos por ya
existir en la migración: 1,230 familias conocidas (top15+Z) y 6 tokens
delta en el catálogo (busqueda_riesgo, cautela, codicia,
consumo_sustancias, negacion_problema, optimismo). Familias que
faltan: 4 (arte, deuda, enfermedad, riesgo). 18 casos del índice no
tienen RESULT todavía (entre ellos los 10 de F005, que no se ha
corrido) y 28 no tienen entrada en la copia de trabajo; quedan
registrados como "sin RESULT" y se reprocesan cuando aparezca la
evidencia (el registro guarda tenia_result/tenia_entrada por caso).

## Puerta

`puerta.py` — **PASA** (2026-11-13). G1: catálogo 244/703, índice 160
entradas, manual 13, can_decide_H False. G2: la cosecha completa
reproduce los 13 descubrimientos del archivo manual
(`STINKBOX_PERSISTENTE/tokens_descubiertos_ciegos_z90_20261113.json`,
mismos casos, mismas familias, mismo lugar, mismo rank_fusion y mismo
regimen; para las de Z, mismo valor) y la salida v2 trae los 4 tokens
con decisión y evidencia. G3: la re-corrida da 0 casos nuevos, 0
hallazgos y 0 matices nuevos; los 53 distintos del índice están en el
registro; el dedupe por token funciona (al filtrar ANONIMO2, arte /
deuda / enfermedad salen como omitidos "ya existe" y no vuelven a
entrar). G4: las 4 decisiones son deterministas (misma entrada, misma
decisión) y las sondas de duplicado (busqueda_riesgo, busqueda_riesgos,
deuda_de_sangre) se rechazan.

Detalle: el regimen del RESULT trae `MESeta_O_ESTABILIZACION` (caja
mezclada del motor); el manual lo normalizó a `MESETA_O_ESTABILIZACION`.
La puerta compara sin caja. La cosecha guarda el valor crudo del RESULT.

## Qué NO hace

- No toca el Engine (MOTOR_V15_3_UNICO) ni el catálogo 244: solo lee.
- No decide H (`can_decide_H = False`): decide activación de
  ANÁLOGOS, nunca H. Los ACTIVADO son análogos propuestos; la
  activación efectiva en el motor es otro paso (no este lateral).
- No reescribe el archivo manual ni la salida v1: la v1 queda como
  está (`COSECHA_20261113.json`); la v2 vive en
  `COSECHA_YYYYMMDD_V2.json` + `REGISTRO_COSECHA.json` y se vuelve a
  correr cuando crezca el StinkBox (solo entran los casos nuevos).

## Cómo se corre

```bash
cd ~/workspace/u6-alterno/motor-cameo
python3 motor/laterales/cosecha_stinkbox/cosecha.py [--fecha YYYYMMDD]
python3 motor/laterales/cosecha_stinkbox/puerta.py   # PUERTA PASA / RECHAZADA
```
