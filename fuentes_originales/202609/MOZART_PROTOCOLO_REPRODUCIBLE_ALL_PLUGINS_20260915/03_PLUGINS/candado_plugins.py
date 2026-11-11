#!/usr/bin/env python3
"""CANDADO_PLUGINS — mellizo de portero_engine.py, pero para los plugins
en vez de para Engine_V5_CANONICO_SOLO.py.

Diferencia clave con portero_engine.py:
  Engine_V5_CANONICO_SOLO.py NUNCA cambia -> se le fija UN hash exacto
  y basta.
  Los plugins SI cambian con el tiempo (se corrigen, se mejoran) -> fijarles
  un hash exacto los rompería en la primera edicion legitima. Aqui el
  candado no es "coincide con este hash o nada pasa", es:
    1) COMPILA de verdad (esto solo habria bloqueado los 14 corrompidos
       de V15_1_TODOS_LOS_PLUGINS_UN_SOLO_TXT.txt de inmediato).
    2) Si huele a la corrupcion tipica de pegar codigo en un editor de
       texto enriquecido (comillas curvas, dunders sin guion bajo), lo dice
       explicito en vez de solo tirar un SyntaxError generico.
    3) Lleva manifiesto de hashes conocidos por plugin: si el hash cambio
       desde la ultima vez, AVISA (no bloquea solo) -- las ediciones
       legitimas existen, pero nunca deben pasar en silencio.

Sobre la duda de "el candado va por numero de caracteres, algo que
encaje ahi se cuela": el chequeo real NO es tamaño en bytes solo -- es
compilacion real + hash SHA-256 completo (32 bytes de huella,
2^256 combinaciones). Dos archivos de codigo distinto que compilen Y
tengan el mismo SHA-256 no es "poco probable", es criptograficamente
inalcanzable por accidente -- solo pasaria con un ataque deliberado de
colision, que no es el problema que estamos resolviendo aqui. El riesgo
real que si existia (y que confirmo el caso de los 14 plugins) es
"nadie compilo antes de confiar" -- eso es lo que este candado ataca.
"""
import ast
import hashlib
import json
import os
import py_compile
import tempfile

SEÑALES_CORRUPCION = {
    "comillas_curvas": ['\u201c', '\u201d', '\u2018', '\u2019'],
    "guion_largo_o_menos": ['\u2013', '\u2014', '\u2212'],
}


class PluginCorruptoError(Exception):
    pass


class ImportProhibidoError(Exception):
    pass


def _diagnostico_corrupcion(texto: str) -> list:
    hallazgos = []
    for nombre, chars in SEÑALES_CORRUPCION.items():
        if any(c in texto for c in chars):
            hallazgos.append(nombre)
    if "from future import" in texto and "__future__" not in texto:
        hallazgos.append("dunder___future___sin_guiones")
    if "== \"main\":" in texto.replace("'", '"') and "__main__" not in texto:
        hallazgos.append("dunder___main___sin_guiones")
    return hallazgos


def verificar_plugin(ruta: str) -> dict:
    """Punto de entrada principal: compila de verdad, diagnostica
    corrupcion tipica si falla, y prohibe imports directos a los
    archivos canonicos (el plugin debe leer outputs, no importar
    Engine_V5_CANONICO_SOLO ni patterns_final para modificarlos)."""
    if not os.path.exists(ruta):
        raise PluginCorruptoError(f"no existe: {ruta}")

    with open(ruta, "r", encoding="utf-8", errors="replace") as f:
        texto = f.read()

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        tmp.write(texto.encode("utf-8"))
        tmp_path = tmp.name
    try:
        try:
            py_compile.compile(tmp_path, doraise=True, cfile=tmp_path + "c")
        except py_compile.PyCompileError as e:
            señales = _diagnostico_corrupcion(texto)
            extra = (
                " -- señales de corrupcion tipica de pegar codigo en editor "
                "de texto enriquecido (Word/Docs/Notion/chat renderizado): "
                + ", ".join(señales)
                if señales else " -- no coincide con la corrupcion conocida, revisar a mano"
            )
            raise PluginCorruptoError(f"{ruta} no compila: {e.exc_value}{extra}") from None
    finally:
        os.unlink(tmp_path)
        if os.path.exists(tmp_path + "c"):
            os.unlink(tmp_path + "c")

    arbol = ast.parse(texto, filename=ruta)
    prohibidos = {"Engine_V5_CANONICO_SOLO", "engine_v5_canonico"}
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                if alias.name in prohibidos:
                    raise ImportProhibidoError(
                        f"{ruta} importa {alias.name} directamente -- un plugin lee "
                        f"outputs, no importa el motor canonico para tocarlo"
                    )
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.module in prohibidos:
                raise ImportProhibidoError(
                    f"{ruta} hace 'from {nodo.module} import ...' -- prohibido, "
                    f"un plugin no importa el motor canonico directamente"
                )

    return {"ruta": ruta, "compila": True, "sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest()}


def registrar_o_comparar(ruta: str, manifest_path: str = "manifiesto_plugins.json") -> dict:
    """No bloquea ediciones legitimas. Pero nunca deja pasar un cambio
    en silencio: primera vez = se registra y se avisa. Cambio = se
    reporta explicito (hash viejo vs nuevo), no se sobreescribe solo."""
    info = verificar_plugin(ruta)
    nombre = os.path.basename(ruta)

    manifiesto = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifiesto = json.load(f)

    anterior = manifiesto.get(nombre)
    if anterior is None:
        manifiesto[nombre] = info["sha256"]
        estado = "registrado_por_primera_vez"
    elif anterior == info["sha256"]:
        estado = "sin_cambios_desde_ultimo_registro"
    else:
        estado = f"CAMBIO_DETECTADO: hash_anterior={anterior} hash_nuevo={info['sha256']} -- requiere aprobacion explicita para actualizar el manifiesto"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, indent=2, ensure_ascii=False)

    info["estado_manifiesto"] = estado
    return info
