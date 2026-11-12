# Corrección: "no deciden" no es "ignórenlo" — los laterales convergen en la predicción

Fecha: 2026-11-11 ~23:31 CST. Orden de Marco: "Hay que cambiar eso."
Estado: PROPUESTA, no cableada. No toca Engine ni catálogo 244.

## La corrección

La instrucción "los laterales no deciden" se malentendió como "ignórenlo".
No es así. **"No deciden" ≠ "ignórenlo".** Los laterales no deciden H solos,
pero NO están de adorno. No se crearon aditamentos de adorno. Si algo está
cableado pero no llega a ningún lado y no se activa, ahí hay un error enorme
y se tiene que corregir en cuanto a CÓMO meterlo.

## Las dos partes que convergen

El motor es predictivo basado en trayectorias hechas por la matriz de datos
más grande de la humanidad y a la vez más corta (244 patrones / 36 situaciones /
arquetipos): trayectos canónicos que han funcionado a lo largo de cientos de
miles de años de humanidad o de historias, que es lo mismo.

Las dos partes convergen en la predicción:

1. **Lo geométrico** — da la trazabilidad del espacio-tiempo: billar, Forman-Ricci,
   traza_P, Schrödinger. Mide dónde está la trayectoria y cómo se mueve.
2. **La estructura del arquetipo** — mide hacia dónde se va a desarrollar el héroe
   (el personaje, el protagonista, sea un objeto histórico u otra cosa), conforme
   lo suele dictar la estadística del arquetipo. Se vale de las cosas que ya han
   pasado antes: otros arquetipos similares que tuvieron ese momento y hacia dónde
   evolucionaron en su camino arquetípico.

## Lo que está roto (verificado en Napoleón 10 cortes)

- **Cuadrantes del monomito**: existen (`plugin_circulo_monomito`,
  `posicion_monomito_por_corte`, 8 cortes con cuadrante), pero las familias
  monomito están 11/12 planas en 0.5. No mueven el ranking ni alimentan la
  predictibilidad (Fórmula 22). Deberían mostrar hacia dónde podría dirigirse
  la trayectoria según el camino del héroe y los arquetipos similares.
- **Capa2 (arquetipos)**: cableada vía el hub como voto lateral; alimenta
  candidate_support pero no gatea H ni alimenta la predictibilidad.
- **Décimo Hombre**: existe (`decimo_hombre_esteroides`) pero su bandera es
  LATENTE; su "no" no cierra nada y no descarta. Su "no" se toma como ignorarlo.
- **Forman-Ricci (negativo)**: el proxy no descarta nada (5→5); el exacto sobre
  grafo denso descarta todo (5→0). Sin grafo disperso y/o término +3, no discrimina.

## Cómo meterlo (propuesta)

1. **Dirección por cuadrante**: a partir de `posicion_monomito_por_corte`
   (cuadrante activo por corte) + arquetipos similares en ese momento y su
   evolución, computar la dirección más probable (próximo cuadrante).
   Esa dirección alimenta `predictibilidad_021` como factor, no solo como
   voto lateral.
2. **Capa2 → dirección**: los antecedentes de arquetipos de capa2 alimentan
   la señal de dirección (qué arquetipos están activos en este momento y
   hacia dónde evolucionaron).
3. **El "no" del Décimo Hombre → negativo**: cuando el DH dice que una hipótesis
   no se sostiene, eso es un voto DESCARTE en la lectura en negativo
   (igual que Forman-Ricci DESCARTE = 0.0), no una bandera LATENTE.
   El "no" del DH y el negativo de Forman-Ricci son el mismo lado: lo que no es.
4. **Regla**: ningún lateral queda como voto que no alimenta nada. Si un lateral
   no alimenta ni H ni la predictibilidad ni el negativo, está mal cableado
   y se corrige el CÓMO, no se borra el componente.

## Lo que NO cambia

- Engine y catálogo 244 canónicos, no se tocan.
- "No deciden" sigue valiendo: ningún lateral decide H solo. Lo que cambia es
  que todos alimentan la predicción (H, predictibilidad o negativo).
- La traza sigue siendo el máster; la apuesta final sigue siendo H1.
