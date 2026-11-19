# controles_generales — Coordinador general de controles operativos

Paquete autónomo y **agnóstico**: no conoce al proyecto que lo usa, no
sabe qué significan sus datos ni para qué sirven. Solo conoce
unidades, fases, piezas, salidas, contextos y ventanas. Se puede meter
en cualquier proyecto o extraerlo sin confusión: el proyecto lo invoca,
él no invoca al proyecto.

## Los controles

| Control | Qué hace |
|---|---|
| `FiltroAdmision` | Solo admite lo objetivamente medible / verificable, con procedencia. Lo demás se aparta, tipado, en la traza. Nunca borra nada y nunca decide el resultado. |
| `SecuenciaFases` | Fases en orden: no se puede completar una sin las anteriores. Ante un obstáculo, contornea y registra; solo para ante una parada dura declarada. |
| `VerificadorIntegridad` | Verifica que una pieza sea íntegra antes de confiar en ella (compila, sin señales de corrupción, huella conocida). Un cambio de huella se avisa y se registra, no bloquea. Una pieza corrupta sí bloquea. |
| `VerificadorSalida` | La salida cumple su contrato: campos requeridos presentes, sin huecos, en el orden declarado, y todo lo que referencia existe en lo admitido (nada inventado). |
| `CompuertaCierre` | Cierre solo si no hay pendientes vivos, ni contradicciones sin resolver, con la secuencia completa y la salida verificada. Si algo falta, la decisión es LATENTE: todavía no. |
| `GuardiaSeparacion` | No mezcla contextos: toma una foto del contexto al entrar y si alguien lo mutó dentro del bloque, es contaminación. También rechaza salidas con campos de otro contexto. |
| `CorteTemporal` | Ventana con fecha de cierre: solo entra información que ya existía hasta esa fecha; lo posterior se aparta. Al cerrar, la ventana se sella. |
| `CoordinadorControles` | Reúne todos los controles en un solo objeto, con bitácora común y recibo final. |

Política operativa del coordinador (su única regla de conducta):
**parar solo ante una parada dura declarada; ante cualquier otro
obstáculo, contornear y registrar.** Nada pasa en silencio.

## Ejemplo mínimo

```python
from controles_generales import CoordinadorControles, UnidadEntrada

coord = CoordinadorControles(
    fases=["recoger", "revisar", "cerrar"],
    campos_requeridos_salida=["resumen", "referencias"],
    orden_salida=["resumen", "referencias"],
    fecha_cierre_ventana="2026-11-19",
    paradas_duras=["pieza_canonica_corrupta"],
)

# 1. Entrada: solo lo verificable entra; el juicio queda apartado en la traza.
admision = coord.admitir_entrada([
    UnidadEntrada("llovió 12 mm", procedencia="estación norte, registro 41",
                  marcas=frozenset({"medible"}), identificador="u1"),
    UnidadEntrada("fue un día horrible", procedencia="estación norte, registro 41",
                  marcas=frozenset({"juicio"}), identificador="u2"),
])
# admitidas: [u1]; apartadas: [u2, tipo=juicio]

# 2. Flujo en orden.
coord.completar_fase("recoger")
coord.completar_fase("revisar")

# 3. Salida contra contrato: completa y anclada a lo admitido.
salida = {"resumen": "llovió 12 mm", "referencias": ["u1"]}
coord.verificar_salida(salida, referencias_permitidas=["u1"])

# 4. Cierre.
coord.completar_fase("cerrar")
decision = coord.evaluar_cierre()
assert decision.cerrado  # CERRADO

# 5. Recibo: qué se hizo, qué se contorneó, qué se apartó.
print(coord.recibo())
```

## Cómo lo invoca el proyecto anfitrión

Con un **adaptador fino** que vive **fuera** de este paquete: el
adaptador traduce las estructuras propias del proyecto (sus registros,
sus fases, sus campos) a unidades, fases y salidas genéricas, llama al
coordinador, y traduce el resultado de vuelta. El coordinador nunca
importa nada del proyecto; el proyecto nunca entra en el coordinador.

Ver el ejemplo en `motor/ejemplos/adaptador_proyecto_a_controles_generales.py`
(no cableado: es documentación ejecutable, no parte de ninguna ruta).

## Tests

`motor/tests/test_coordinador_controles_generales.py` — un test por
control, y cada test falla si el control no se aplica (por ejemplo:
si el filtro admitiera un juicio, si la secuencia dejara saltarse una
fase, si la salida pasara con un hueco o con una referencia inventada,
si el cierre se diera con pendientes vivos, o si la guardia no
detectara una mutación).
