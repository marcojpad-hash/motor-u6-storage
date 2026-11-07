# FreeLLMAPI en el motor U6 — backend gratis para futuras llamadas LLM

> Estado 2026-11-07: instalado y verificado en la VM de Pecas.
> Sin claves de proveedor todavía (ver lista abajo).
> **Dato importante:** hoy ningún script del motor llama a una API de
> LLM. La fábrica valida pistas, no llama modelos (ver abajo). Este
> documento deja el backend listo para cuando un script sí lo necesite.

## Qué es

[FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) (MIT) es un
router local que junta los planes gratis de 34 proveedores de IA detrás
de un solo endpoint compatible con OpenAI, con failover automático
cuando un modelo agota su cuota. Corre en la VM de Pecas y las
peticiones van de la VM directo a cada proveedor. Las claves quedan
cifradas (AES-256-GCM) en la base local y nunca salen de la máquina,
salvo hacia el proveedor que corresponda. El único contacto con los
servidores del proyecto es el catálogo de modelos (feed firmado,
verificado con Ed25519); ese feed no ve prompts, respuestas ni claves.

## Dónde corre

- Máquina: VM de Pecas. Servidor: `http://127.0.0.1:3001` (solo localhost).
- Código: `~/workspace/freellmapi` (clon de `tashfeenahmed/freellmapi`).
- Base de datos: `~/workspace/freellmapi/server/data/freeapi.db`.
- Clave unificada: en el dashboard, página Keys
  (`http://127.0.0.1:3001`). **Nunca se escribe en este repo.**
- Arrancar: `bash ~/workspace/freellmapi/start-freellmapi.sh`
- Parar: `pkill -f "node dist/index.js"`
- Verificado 2026-11-07: `GET /v1/models` con la clave unificada lista
  289 modelos; `POST /v1/chat/completions` sin claves responde
  `no_providers_configured` (esperado).

## Por qué hoy no se usa (y para qué queda)

El "caldero LLM" del motor no es una llamada a API: son pistas que un
modelo externo propone y que la fábrica valida. `casos/fabrica/
pistas_llm_caldero_v1.py` lo dice en su docstring: *"La fábrica NO
llama a ningún LLM: solo valida y copia."* El guardián
(`motor/motor/guardian_pistas_llm_caldero_v1.py`) es la única autoridad
y el cierre es determinista y sin red.

FreeLLMAPI queda como backend para el día en que un script del motor
necesite llamar a un LLM (por ejemplo, proponer semillas o pistas de
forma programada, o una futura calibración asistida). Cuando eso se
decida, el cliente es trivial porque el endpoint es compatible con
OpenAI:

```python
import json, os, urllib.request

def llamar_llm(prompt, model="auto"):
    req = urllib.request.Request(
        "http://127.0.0.1:3001/v1/chat/completions",
        json.dumps({"model": model,
                    "messages": [{"role": "user", "content": prompt}]}).encode(),
        {"Authorization": "Bearer " + os.environ["FREELLMAPI_API_KEY"],
         "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=180)
                      )["choices"][0]["message"]["content"]
```

Reglas para ese futuro uso (no negociables):

- El cliente vive fuera de `motor/` canónico o como script separado;
  **Engine V5 y el catálogo 244 no se tocan**.
- Toda salida de LLM pasa por el guardián y las validaciones existentes
  antes de entrar a una entrada o al Caldero; nada entra sin validar.
- Los tests de contrato siguen siendo deterministas (fixtures, sin red).
- La clave unificada se lee de variable de entorno, nunca hardcodeada.

## Claves gratuitas que faltan (las crea Marco)

Igual que en CAPCOT: ninguna está guardada; cada una se crea con su
cuenta en la web del proveedor y se carga en el dashboard de FreeLLMAPI
(página Keys). Prioridad:

1. **Google AI Studio (Gemini)** — https://aistudio.google.com/apikey
2. **Groq** — https://console.groq.com/keys
3. **Mistral** — https://console.mistral.ai/api-keys
4. **OpenRouter** — https://openrouter.ai/keys (modelos `:free`)
5. Opcionales: Cohere, HuggingFace, NVIDIA NIM, Z.ai, Cloudflare.

Con Gemini + Groq ya hay failover real.

## Advertencias

- **Uso personal, no producción.** Los planes gratis no son una base
  estable; si un uso se vuelve real, se usa una API de pago.
- **Revisar los términos de cada proveedor** (una cuenta por proveedor,
  no revender, no compartir el endpoint).
- **No pasar datos sensibles por planes gratis.** El motor no maneja
  datos personales; si algún día los manejara, no irían por este router.
- **Calidad variable y caída al final del día UTC** cuando los mejores
  modelos agotan su cuota diaria; se resetea a medianoche UTC.
- **Catálogo gratis con 30 días de retraso** (versión mensual). El
  router es gratis y MIT; lo de pago ($19/año) es solo el catálogo en
  vivo y no hace falta.

## Si algo falla

- Servidor caído: `start-freellmapi.sh`; logs en
  `~/workspace/freellmapi/server.log`.
- `no_providers_configured`: faltan claves de proveedor.
- `401 Invalid API key`: re-tomar la clave unificada del dashboard.
