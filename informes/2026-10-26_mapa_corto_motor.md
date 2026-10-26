# Mapa corto del motor (para Mj) — 2026-10-26

Español llano. Familias, no la lista de 244. Detalle técnico: `motor/README_MOTOR.md`, `docs/`.

## 1. Qué es, en una frase
Una máquina que lee la historia de un caso **por cortes en el tiempo**, junta evidencia y **apuesta** qué es lo más probable que pase después — y decide ella, no el LLM.

## 2. Engine vs catálogo 244
- **Engine** (`Engine_V5_CANONICO_SOLO.py`) = **la lógica**: cómo pesa, compara y decide.
- **Catálogo 244** (`patterns_final_v14.json`) = **el vocabulario**: los 244 patrones (tramas, roles, dinámicas) que el Engine puede reconocer.
- Analogía: el Engine es el juez, el catálogo es el código de leyes. Ninguno de los dos se toca.

## 3. H1 / H2 / apuesta en la vida real
- **H1** = la explicación principal de "qué está pasando aquí".
- **H2** = la explicación rival (la que gana si H1 falla).
- **Apuesta** = qué esperamos que pase, con probabilidad entre 5 % y 95 % (nunca certeza) y con **falsadores**: qué tendría que pasar para decir "nos equivocamos".
- Regla: H1 no puede ser simplemente "el patrón con más puntos"; tiene que tener canales de evidencia.

## 4. Familias laterales (lentes de apoyo; 1 línea cada una)
| Familia | Qué hace en la práctica |
|---|---|
| **Karpman** | Detecta el triángulo víctima / perseguidor / salvador y quién cambia de papel. |
| **Girard** | Rivalidad por imitación: quién desea lo que el otro desea y si busca chivo expiatorio. |
| **Tucídides** | Poder que sube vs poder establecido: riesgo de choque por miedo a ser desplazado. |
| **Adizes** | Etapa de vida de una organización/proyecto (nace, crece, se burocratiza, muere). |
| **McAdams** | Cómo la persona cuenta su propia historia (redención vs contaminación). |
| **Kishōtenketsu** | Estructura en 4 tiempos sin conflicto central: el giro viene por sorpresa, no por pelea. |
| **Souriau / Polti** | Las 36 situaciones dramáticas y los roles de fuerza: qué "tipo de drama" es. |
| **Caldero (monomito)** | En qué parte del viaje del héroe está el caso (llamado, prueba, regreso…); busca arquetipos en la web sin LLM. |
| **StinkBox** | Guarda las palabras/señales "raras" de cada caso para aprender entre casos. |
| **Sombrero blanco** | Filtro de hechos: separa dato duro de opinión antes de usarlo. |
| **Billar / geometría / anillos / Ricci** | Miran el caso como mapa: si las fuerzas convergen a un punto, si hay cuellos o se dispersan. |
| **Venn de sistemas** | Qué sistemas (familia, trabajo, poder…) se traslapan en el caso. |
| **CEB** | Bitácora de ejecución: comprueba que cada pieza corrió de verdad; si no, marca FALLO. |
| **U7 confianza** | Herramienta aparte que mide cuánto fiarse de la apuesta. |

## 5. Flujo corto
**Entrada** (texto del caso) → **cortes** en el tiempo → **evidencia** (Engine + catálogo + laterales) → **hipótesis** H1/H2 → **apuesta** con falsadores (se congela) → si algo falla o no corrió, **CEB** lo marca para arreglarlo.

## 6. Qué NO tocar
- `motor/Engine_V5_CANONICO_SOLO.py` y `motor/patterns_final_v14.json` (candados sha256, ver `motor/REGLAS.md`).
- Archivos `MOTOR_V15_3_*` bloqueados.
- Todo lo nuevo va como **lateral** (archivo nuevo), nunca reemplazo silencioso.

## 7. "Puntos π"
Con ese nombre: **ausente** (no aparece en `MAPA_NOMBRES.txt`, `REGLAS.md` ni `docs/`). Lo más cercano: en `motor/motor/puente_souriau_caldero_polti_v1.py` cada familia se pone como **un ángulo en un círculo** (Caldero: cuadrantes de π/2; Polti: 36 posiciones en 2π; Souriau: zonas en 2π) para ver si las tres lentes **apuntan al mismo lado**. Eso es lo que probablemente se llamó "puntos π".
