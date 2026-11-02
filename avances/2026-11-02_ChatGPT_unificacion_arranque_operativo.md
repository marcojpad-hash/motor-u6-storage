# 2026-11-02 — ChatGPT — corrección de arranque operativo

## Qué cambió
Se corrigió la duplicación documental creada el 2026-11-02 y se unificó la secuencia de inicio de ChatGPT. No se modificó código del motor ni evidencia de corridas.

## Antes → ahora (por archivo / función)
- `INICIO_SESION_CHATGPT.md` — antes empezaba por README y continuidad, mientras FEEDME y continuidad establecían FEEDME como punto inicial; ahora fija una sola secuencia: FEEDME → README/contratos/sidecar → protocolo/autoridad/CEB/bitácoras → inspección → ejecución y verificación. Añade la obligación de resolver con herramientas disponibles y no delegar al usuario trabajo ejecutable.
  blob SHA antes: `77332de30deb8bb1fe226e0e3b7d176e4297534d` | blob SHA después: `f5896403403e152072e42446842936a5204434bf`
- `README.md` — antes enlazaba como obligatorio un contrato adicional redundante; ahora remite a la ruta de arranque ya existente.
  blob SHA antes: `0ff34d55aac264dca19c3a7b1adf2b52e1a3c619` | blob SHA después: `5263b8d44356fb940ebc8919c0250db684faf75f`
- `CONTRATO_OPERATIVO_LLM_LECTURA_Y_EVIDENCIA.md` — antes duplicaba y ampliaba reglas ya presentes; ahora eliminado para evitar una segunda autoridad documental.
  blob SHA eliminado: `282de0ee231194f33ed8297f780389132989f11e`

## Hashes canónicos verificados (motor y catálogo)
No revalidados en esta intervención porque no se modificó ningún archivo del motor ni del catálogo. No se afirma verificación criptográfica nueva de los canónicos.

## Pruebas: 0 passed, 0 skipped, 0 failed (¿pasaron? no aplica)
Cambios exclusivamente documentales. Verificación de contenido por lectura posterior pendiente de completar en este mismo cierre.
