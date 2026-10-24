# Guía corta: agregar casos nuevos y calibrar el peso geométrico

**Regla de oro:** primero se sella y después se mira el desenlace. Nunca al revés, y nunca se inventa un desenlace.

## 1. Preparar el caso
- Copie `PLANTILLA_CASO_NUEVO.json` a una carpeta propia, por ejemplo `casos_cal/`, con un nombre por caso.
- Llene `case_id`, `question` y `freeze`, la fecha de congelamiento.
- Llene los `cuts` en orden temporal. Cada corte lleva `P` (propósito), `A` (acción) y `C` (contexto): listas de `[token, peso]` con pesos entre 0 y 1.
- Use **solo información anterior al freeze**. Anote las fuentes en `source_notes`.
- Con un solo corte no hay trayectoria y no se apuesta. Lo útil es **3 o más cortes**.
- No ponga en el input campos de desenlace (`desenlace`, `outcome`…). El arnés rechaza el caso si los encuentra.
- No use aquí los 15 casos sellados.

## 2. Sellar (antes de conocer el desenlace)
```
python3 calibracion/arnes_calibracion.py correr casos_cal/ salida_cal_AAAAMMDD/ --pesos 0   # esta copia: un solo peso (el motor no expone GEOMETRIA_PESO)
```
- El arnés corre cada caso con cada peso.
- Guarda `salida_cal_.../REGISTRO_CALIBRACION.json` con, por peso: H1/H2, la lista de hipótesis, los escenarios, el escenario principal y el hash del núcleo.
- El registro lleva su propio sha256 y no se reescribe; para otra tanda use otra carpeta.

## 3. Evaluar (cuando el desenlace real ya se conoce)
- Copie `PLANTILLA_DESENLACES.json` y escriba por `case_id`:
  - las familias del catálogo que el desenlace confirma;
  - opcionalmente, el escenario;
  - y la fuente.
- Luego ejecute:
```
python3 calibracion/arnes_calibracion.py evaluar salida_cal_AAAAMMDD/REGISTRO_CALIBRACION.json desenlaces.json
```
- Sale `EVALUACION_CALIBRACION.json`. Por peso trae:
  - **tasas de acierto** de H1, del set abierto y del escenario principal, crudas y con Laplace (k+1)/(n+2);
  - **Brier**, con probabilidades recortadas a 5–95 %.
- Si el registro fue modificado después del sello, la evaluación lo marca.

## 4. Elegir el peso (adaptado a esta copia)
- Este motor mete la geometría como dimensiones normales del rank_fusion y **no** expone `GEOMETRIA_PESO` ni `config_geometria.json`.
- Por eso aquí se calibra con un solo peso nominal (`--pesos 0`); varios pesos se rechazan con `MOTOR_SIN_GEOMETRIA_PESO`.
- Lo que sí se mide: aciertos y Brier de H1, del set abierto y del escenario principal, sobre casos sellados antes del desenlace.
- Con menos de 10 casos evaluados el arnés avisa `MUESTRA_INSUFICIENTE`: no saque conclusiones todavía.
- Tras cualquier cambio en `motor/`, regenere el manifiesto: `python3 -B scripts/regenerar_manifestos_trabajo.py`.
- Modo seco (no corre el motor ni sella): `python3 calibracion/arnes_calibracion.py validar casos_cal/`.
