README V15 — LEER ANTES DE CORRER
Quien llega NO estuvo en la conversacion. No asuma Aquiles, picos, 246 ni el eje.
Si no esta en este paquete, no existe para usted.

========================================
1. QUE ES ESTO
Plugin de traza y perfil. NO es un LLM. NO predice fechas ni iPhones.
Motor de cuenta: Engine_V5_CANONICO_SOLO.py + patterns_final_v14.json (244).
Paquete que se ejecuta: Engine_V15_INTEGRADO.py
  (V5 + plugins; en memoria 244 + fama + otto = 246)
En DISCO el 244 no se modifica.

========================================
2. ARCHIVOS OBLIGATORIOS (misma carpeta)
Engine_V5_CANONICO_SOLO.py
patterns_final_v14.json
Engine_V15_INTEGRADO.py
plugin_aquiles_h.py
plugin_picos_mesetas.py
plugin_reporte_3d.py
traza_campo_244.py
plugin_sesgo_lectura.py
plugin_arco_field_snyder_mckee.py
plugin_familias_gloria_sacro.py
plugin_otto_numinoso.py
PROTOCOLO_HIPOTESIS_E_INVERSA.txt
METODO_HECATE_HOLMES_SCHOPENHAUER.txt
CHECKPOINT_V15_2026-09-07.txt

========================================
3. COMO CORRER
python3
>>> from Engine_V15_INTEGRADO import correr
>>> cortes = [
...   ("A", [("creatividad", 0.80), ("aprendizaje", 0.70)]),
...   ("B", [("ambicion", 0.85), ("poder", 0.75)]),
... ]
>>> out = correr(cortes, pregunta="CASO", monte_carlo=True, sidecar=True)
Entrada: lista de cortes. Cada corte = (id, [(token, valor 0-1), ...]).
Tokens SOLO del lexico de las 244. Token inventado no prende.

sidecar=False -> solo 244.
sidecar=True  -> 246 en memoria (fama + otto). No pisa el json maestro.

========================================
4. COMO LEER LA SALIDA (NO APLASTAR)
cadena_top1     = el LETRERO. Es el tema/aristos. NO es el hallazgo.
reporte_3d      = letrero + lo que se MOVIO + lo que NO se apago.
picos_mesetas   = forma ↗ → ↘ de cada lampara. Importa el ↗ ANTES de ser Top1.
Aquiles         = ¿esta FOTO aguanta si la barajas? No es la pelicula en el tiempo.
sesgo_lectura   = mismas palabras no son sesgo; D vacio = sin carne nueva.
arco            = lector Field/Snyder/McKee. Periferico.

PROHIBIDO reportar solo el campeon y decir "no cambio".

========================================
5. PROTOCOLO DE UN CASO
1. Adelante, cortes en orden, campo+curvas.
2. HIPOTESIS de perfil ANTES de mirar el cierre.
3. INVERSA: que acerto, que fallo, atencion de mas, atencion de menos.
Sin el paso 2, se esta ejecutando mal (spoiler / campana).

========================================
6. LO QUE ESTE PAQUETE NO TIENE
- Los casos de estudio (van aparte, texto plano + un JSON ejemplo).
- Prueba LOO 64.46/97.52 (Grupo B): no esta en esta carpeta.
- V6: no existe. No reescribir el V5 salvo cambio de F.
- Agente2 (alias) no esta cableado en este V5.

========================================
7. QUE SI TOCARIA EL V5 (entonces seria otra version de motor)
Cambiar p_final, meter Aquiles dentro de process_observation,
fusionar Otto al json de 244, piso obligatorio de perfilar,
cablear alias. Hasta entonces: V5 + mochila V15.

========================================
8. REGLA CONTRA AUTOCONFIRMACION
El modelo de turno NO "ya sabe" picos, Aquiles ni el hueco sacro.
Si va a afirmar un hallazgo, tiene que salir de out["reporte_3d"]
o out["picos_mesetas"], no de la memoria del chat.
Pregunta de aduana: ¿esto lo vi en el tablero o lo estaba defendiendo yo?
