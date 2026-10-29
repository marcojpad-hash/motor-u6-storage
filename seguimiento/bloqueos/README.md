# Bloqueos y fallos

Registra piezas que no se ejecutan, errores, omisiones, fallos de contrato, recibos incompletos y herramientas que debían correr pero no corrieron.

## Protocolo

1. Leer `alerta`, `accion`, `error` y `aporte/motivo` del CEB.
2. Abrir el archivo de la pieza y rastrear la rama real que la invoca.
3. Reproducir con un caso mínimo cuando haya entorno de ejecución.
4. Corregir la causa raíz permitida; no cambiar la lógica predictiva para silenciar el error.
5. Repetir el smoke y comprobar el recibo/estado del CEB.
6. Si el entorno no permite ejecutar, dejar claro qué comprobación queda bloqueada y por qué.

Crear `AAAA-MM-DD_bloqueo_<tema>.md`. No cerrar un bloqueo solo porque quedó documentado.
