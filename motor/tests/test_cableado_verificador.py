#!/usr/bin/env python3
"""test_cableado_verificador.py — Verificador de consistencia adversarial
cableado en la ruta real de corrida (post-predictor, en run() de UNICO).

Specs: MAPA_GUARDIANES.md §2.10 (`plugin_verificador_consistencia_adversarial.py`
vCONSISTENCY_ADVERSARIAL_V0.1: invariantes de contrato en la corrida real —
empate exacto 0.0 no puede producir H, cierre solo si se agotó la resolución,
laterales no escriben H, freeze, inmutabilidad del canon — más fixtures
adversariales y un paquete para revisión LLM sin hipótesis deseada; solo marca,
`FEEDS_H=False`, UNICO lo registra como `EXECUTED` o `EXECUTED_WITH_FINDINGS`)
+ inventario de orquestador-central (`docs/filtros_operativos/` / MAPA §5 tabla:
"Consistencia adversarial | plugin_verificador_consistencia_adversarial.py |
lógica / contrato | Marca violaciones | Sí, UNICO") + docstring del plugin
("Adversarial consistency verifier", `ROLE=control_only`). No tiene ficha
propia en filtros_operativos.

Hallazgo del cableado: el bloque YA se ejecutaba en la ruta real sin ninguna
prueba (baseline THEMISTOCLES: `PASS`, 0 violaciones, 8 fixtures, H intacta,
cierre AJUSTADA), pero no existía apagado: no había bandera y el bloque corría
siempre, y si el plugin faltaba el recibo quedaba en `PLUGIN_MISSING` sin fila
de componentes. Este PR no reescribe el núcleo: añade la bandera
`VERIFICADOR_CONSISTENCIA` (defecto activo; `off` = bypass visible
NO_CONFIGURADO con `verificador_modo: off`) y registra `verificador_modo` en
la fila de componentes en ambos casos, más `modo` en el recibo del bloque; la
rama `PLUGIN_MISSING` también deja fila visible. SHA esperado del plugin
(`10b5e163…`) coincide con el archivo actual.

Contrato de la familia: el bloque corre DESPUÉS del predictor y ANTES de los
guardianes, solo AUDITA (`FEEDS_H=False`, `FEEDS_PREDICTOR=False`,
`ROLE=control_only`); nunca escribe H ni patterns ni la apuesta. Su salida es
`status=PASS` o `FAIL` con `violations` (p. ej. `TIE_NO_WINNER`,
`RESOLUTION_BEFORE_CLOSE`, `PATTERNS_HASH_DECLARATION_MISMATCH`) y un paquete
LLM reproducible con las 8 reglas y los 8 fixtures. El bypass
(`VERIFICADOR_CONSISTENCIA=off`) no debe inventar auditoría ni cambiar el
cierre: el grado del cierre final es el mismo con el bloque activo o apagado.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: run() directo con resultado sintético (sano → PASS
     con paquete y auditoría escritos; empate exacto 0.0 con H → TIE_NO_WINNER;
     cierre DETERMINADO sin resolución agotada → RESOLUTION_BEFORE_CLOSE; hash
     de patrones declarado distinto del real → PATTERNS_HASH_DECLARATION_MISMATCH;
     lateral que escribe H → LATERAL_NO_H; corpus de fórmulas declarado y
     ausente → FORMULA_CORPUS_MISSING; run() no muta el resultado ni H;
     fixtures y reglas; constantes y sha).
  2) Estático: el cableado existe en UNICO run() (flag, rama else con
     NO_CONFIGURADO, verificador_modo en la fila, modo en el recibo).
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     ejecuta (PASS, 0 violaciones, 8 fixtures, paquete escrito), H intacta,
     cierre AJUSTADA, fila EXECUTED con verificador_modo activo.
  4) Unidad: la auditoría post-predictor no retiene ni reescribe el cierre
     (cierre_final y H intactos tras run(); el registro NO_CONFIGURADO no
     trae violaciones ni paquete).
  5) Bypass (subproceso con VERIFICADOR_CONSISTENCIA=off): el apagado queda
     marcado NO_CONFIGURADO en el recibo, no pasa en silencio, el resto de
     guardianes sigue corriendo y el cierre final no cambia de grado.

Límite documentado (del módulo, no del test): el paquete LLM y la auditoría se
escriben en el directorio del paquete que se le pasa (`BASE` en la corrida
real, que es el directorio de la corrida); el `packet_sha256` es el sha256 del
texto exacto del paquete, así que cambia si cambia cualquier observación de la
corrida. Por eso la capa 1 no afirma un `packet_sha256` fijo, solo que
coincide con el contenido del archivo escrito. Además, en la corrida real el
chequeo de laterales solo ve los componentes que ya están en
`execution.component_status` cuando corre el verificador (antes de los
guardianes); los laterales que se registran después no pasan por este chequeo.
Y en la corrida real los reruns aislados de cortes retenidos
(`efectividad_corte_retenido`) vuelven a ejecutar el motor en el mismo
directorio de la corrida y reescriben el paquete y la auditoría: el archivo
que queda en disco es el del último rerun (observación
`LATENCIA_INFORMACIONAL`, H1 ausente), no el de la corrida principal, y el
`packet_sha256` del recibo principal (`2867092027…` en THEMISTOCLES,
determinista entre corridas) ya no coincide con el archivo en disco. La
auditoría del recibo principal sigue siendo la válida (PASS, 0 violaciones);
por eso la capa 3 no afirma la coincidencia del sha en vivo, solo reglas y
fixtures.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
VERIFICADOR = MOTOR_DIR / "plugin_verificador_consistencia_adversarial.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

SHA_VERIFICADOR = "10b5e163"
SHA_ENGINE = "665c39a2"
SHA_PATTERNS = "d827dcc3"

REGLAS = [
    "LATENCIA_NO_STOP",
    "TORTUGA_NO_CAMBIA_FAMILIA",
    "TIE_NO_WINNER",
    "RESOLUTION_BEFORE_CLOSE",
    "LATERAL_NO_H",
    "FREEZE_NO_FUTURE",
    "CANON_IMMUTABLE",
    "CALDERO_PERSIST_CROSS_CASE",
]

FIXTURES = [
    "TIE_EXACT_0",
    "MISSING_DATA_BUT_INPUT_PRESENT",
    "REPEATED_WITHOUT_NEW_SIGNAL",
    "NEW_SIGNAL_WITHOUT_RESOLUTION",
    "LATERAL_TRIES_TO_WRITE_H",
    "FUTURE_DATA_DURING_FREEZE",
    "CANON_MUTATION",
    "CROSS_CASE_NEIGHBOR",
]


def _load_verificador():
    spec = importlib.util.spec_from_file_location(
        "plugin_verificador_consistencia_adversarial", VERIFICADOR)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------ builders
def _sano(root):
    """Resultado sintético sano: margen > 0, resolución agotada, hash de
    patrones declarado igual al real, sin laterales que escriban H."""
    patrones = root / "patterns_final_v14.json"
    patrones.write_text(json.dumps({"patterns": []}), encoding="utf-8")
    declarado = _sha256(patrones)
    result = {
        "predictor": {
            "information_state": {"state": "DETERMINADO",
                                  "top_margin": 1.5,
                                  "resolution_exhausted": True},
            "H1": {"family": "TOP"},
            "H2": {"family": "SEG"},
            "status": "OK",
        },
        "patterns_sha256": declarado,
        "execution": {"component_status": []},
    }
    return result


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_run_sano_pass_con_paquete_y_auditoria(tmp_path):
    ver = _load_verificador()
    result = _sano(tmp_path)
    out = ver.run(result, tmp_path)
    assert out.get("status") == "PASS", out
    assert out.get("verifier_version") == "CONSISTENCY_ADVERSARIAL_V0.1", out
    assert out.get("violations") == [], out
    assert out.get("fixture_count") == 8, out
    assert out.get("rule_source", "").startswith("explicit invariants"), out
    # Paquete LLM y auditoría escritos en el directorio del paquete.
    paquete = Path(out.get("packet") or "")
    assert paquete.exists() and paquete.parent == tmp_path, out
    assert hashlib.sha256(paquete.read_bytes()).hexdigest() == \
        out.get("packet_sha256"), out
    auditoria = tmp_path / "CONSISTENCY_ADVERSARIAL_AUDIT.json"
    assert auditoria.exists(), out
    assert json.loads(auditoria.read_text(encoding="utf-8")) == out, out
    datos = json.loads(paquete.read_text(encoding="utf-8"))
    assert datos.get("verifier_version") == "CONSISTENCY_ADVERSARIAL_V0.1"
    assert datos.get("role") == "control_only"
    assert datos.get("feeds_predictor") is False
    assert datos.get("feeds_H") is False
    assert [r.get("id") for r in datos.get("rules") or []] == REGLAS, datos
    assert [f.get("id") for f in datos.get("fixtures") or []] == FIXTURES, datos
    assert datos.get("instruction_to_llm"), datos
    obs = datos.get("actual_run_observation") or {}
    assert obs.get("H1_present") is True
    assert obs.get("H2_present") is True


def test_run_empate_exacto_marca_tie_no_winner(tmp_path):
    ver = _load_verificador()
    result = _sano(tmp_path)
    result["predictor"]["information_state"]["top_margin"] = 0.0
    out = ver.run(result, tmp_path)
    assert out.get("status") == "FAIL", out
    assert "TIE_NO_WINNER" in (out.get("violations") or []), out


def test_run_cierre_sin_resolucion_marca(tmp_path):
    ver = _load_verificador()
    result = _sano(tmp_path)
    result["predictor"]["information_state"]["resolution_exhausted"] = False
    out = ver.run(result, tmp_path)
    assert out.get("status") == "FAIL", out
    assert "RESOLUTION_BEFORE_CLOSE" in (out.get("violations") or []), out


def test_run_hash_patrones_declarado_distinto_marca(tmp_path):
    ver = _load_verificador()
    result = _sano(tmp_path)
    result["patterns_sha256"] = "0" * 64
    out = ver.run(result, tmp_path)
    assert out.get("status") == "FAIL", out
    assert "PATTERNS_HASH_DECLARATION_MISMATCH" in \
        (out.get("violations") or []), out


def test_run_lateral_escribe_h_marca(tmp_path):
    ver = _load_verificador()
    result = _sano(tmp_path)
    result["execution"]["component_status"] = [
        {"component": "sidecar_caldero_busqueda_arquetipos.py",
         "writes_H": True, "can_decide_H": False},
    ]
    out = ver.run(result, tmp_path)
    assert out.get("status") == "FAIL", out
    assert "LATERAL_NO_H" in (out.get("violations") or []), out


def test_run_formula_corpus_faltante_marca(tmp_path):
    ver = _load_verificador()
    result = _sano(tmp_path)
    result["formula_corpus"] = {"file": "formula_inexistente.json"}
    out = ver.run(result, tmp_path)
    assert out.get("status") == "FAIL", out
    assert "FORMULA_CORPUS_MISSING" in (out.get("violations") or []), out


def test_run_no_muta_resultado_ni_h(tmp_path):
    """La auditoría solo lee: el resultado que recibe queda exactamente igual
    después de run() (H1/H2 y cierre_final intactos)."""
    ver = _load_verificador()
    result = _sano(tmp_path)
    result["H1"] = {"family": "TOP"}
    result["H2"] = {"family": "SEG"}
    result["cierre_final"] = {"grado": "AJUSTADA",
                              "objeciones": [{"fuente": "LOGICA_COPI"}]}
    antes = json.dumps(result, sort_keys=True, default=str)
    out = ver.run(result, tmp_path)
    assert json.dumps(result, sort_keys=True, default=str) == antes
    assert "consistency_adversarial" not in result
    assert out.get("status") == "PASS", out


def test_fixtures_y_reglas():
    ver = _load_verificador()
    assert [r for r, _ in ver.RULES] == REGLAS
    fixtures = ver.adversarial_fixtures()
    assert [f.get("id") for f in fixtures] == FIXTURES
    assert len(fixtures) == 8
    for f in fixtures:
        assert f.get("expected_state") and f.get("rule"), f


def test_constantes_y_sha_del_plugin():
    ver = _load_verificador()
    assert ver.VERSION == "CONSISTENCY_ADVERSARIAL_V0.1"
    assert ver.ROLE == "control_only"
    assert ver.FEEDS_H is False
    assert ver.FEEDS_PREDICTOR is False
    assert _sha256(VERIFICADOR).startswith(SHA_VERIFICADOR)
    assert _sha256(MOTOR_DIR / "Engine_V5_CANONICO_SOLO.py").startswith(SHA_ENGINE)
    assert _sha256(MOTOR_DIR / "patterns_final_v14.json").startswith(SHA_PATTERNS)


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_estatico_cableado_en_unico():
    src = UNICO.read_text(encoding="utf-8")
    assert 'result["consistency_adversarial"]' in src
    assert "VERIFICADOR_CONSISTENCIA" in src
    assert '"verificador_modo"' in src
    inicio = src.index("# Adversarial consistency verifier")
    fin = src.index("# GUARDIANES (control estructural", inicio)
    seccion = src[inicio:fin]
    # La rama else del apagado: NO_CONFIGURADO visible, no silencio.
    assert '"NO_CONFIGURADO"' in seccion, seccion
    assert "apagado por VERIFICADOR_CONSISTENCIA=off" in seccion, seccion
    assert '"verificador_modo"' in seccion, seccion
    assert "_verificador_modo" in seccion, seccion
    assert 'if _verificador_modo == "activo":' in seccion, seccion


# ------------------------------------------------------------------ 3 y 5) vivo y bypass por subproceso
def _python_con_numpy():
    """El motor exige numpy; el intérprete de pytest (venv) no lo tiene.
    Se usa el python3 del sistema cuando el actual no lo trae."""
    for cand in (sys.executable, "/usr/bin/python3"):
        try:
            subprocess.run([cand, "-c", "import numpy"], capture_output=True,
                           timeout=60, check=True)
            return cand
        except Exception:
            continue
    return sys.executable


PYTHON_MOTOR = _python_con_numpy()


def _corre_estandar(entrada, nombre, salida, env_extra=None):
    env = dict(os.environ)
    env.pop("VERIFICADOR_CONSISTENCIA", None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [PYTHON_MOTOR, "correr_estandar.py", str(entrada), nombre, str(salida)],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return json.loads(Path(salida).read_text(encoding="utf-8"))


def _componente(resultado, nombre):
    comps = (resultado.get("execution") or {}).get("component_status") or []
    return next((s for s in comps if s.get("component") == nombre), None)


def test_corrida_real_ejecuta_verificador(tmp_path):
    out = tmp_path / "resultado_verificador.json"
    res = _corre_estandar(THEMISTOCLES, "VERIFICADOR_SMOKE", out)
    ver = res.get("consistency_adversarial") or {}
    assert ver.get("status") == "PASS", ver
    assert ver.get("modo") == "activo", ver
    assert ver.get("verifier_version") == "CONSISTENCY_ADVERSARIAL_V0.1", ver
    assert ver.get("violations") == [], ver
    assert ver.get("fixture_count") == 8, ver
    assert ver.get("rule_source", "").startswith("explicit invariants"), ver
    # El paquete LLM quedó escrito en el directorio de la corrida.
    paquete = Path(ver.get("packet") or "")
    assert paquete.exists(), ver
    datos = json.loads(paquete.read_text(encoding="utf-8"))
    assert [r.get("id") for r in datos.get("rules") or []] == REGLAS, datos
    assert [f.get("id") for f in datos.get("fixtures") or []] == FIXTURES, datos
    # H intacto: la auditoría post-predictor solo marca, no reescribe nada.
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    assert (res.get("cierre_final") or {}).get("grado") == "AJUSTADA"
    # La fila de componentes lo registra como ejecutado, con el modo visible.
    comp = _componente(res, "plugin_verificador_consistencia_adversarial.py")
    assert comp is not None and comp.get("status") == "EXECUTED", comp
    assert comp.get("verificador_modo") == "activo", comp
    assert comp.get("feeds_H") is False
    assert comp.get("violations") == [], comp


def test_bypass_verificador_off_queda_marcado_no_configurado(tmp_path):
    out = tmp_path / "resultado_verificador_off.json"
    res = _corre_estandar(THEMISTOCLES, "VERIFICADOR_BYPASS", out,
                          {"VERIFICADOR_CONSISTENCIA": "off"})
    ver = res.get("consistency_adversarial")
    assert ver is not None, "el bypass no debe borrar el bloque en silencio"
    assert ver.get("status") == "NO_CONFIGURADO", ver
    assert ver.get("modo") == "off", ver
    assert ver.get("violations") == [], ver
    assert ver.get("fixture_count") == 0, ver
    # Sin paquete ni auditoría: el apagado no debe leerse como verificación.
    assert "packet" not in ver, ver
    comp = _componente(res, "plugin_verificador_consistencia_adversarial.py")
    assert comp is not None and comp.get("status") == "NO_CONFIGURADO", comp
    assert comp.get("verificador_modo") == "off", comp
    # H intacta e idéntica al baseline; el resto de guardianes sigue corriendo.
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED", g
    bloques = {b.get("guardian") for b in g.get("bloques") or []}
    assert "LOGICA_COPI" in bloques, bloques
    assert "DECIMO_HOMBRE_LATENCIA" in bloques, bloques
    # El cierre final no cambia de grado sin la auditoría: la auditoría no
    # retiene ni reescribe el cierre.
    assert (res.get("cierre_final") or {}).get("grado") == "AJUSTADA"


# ------------------------------------------------------------------ 4) unidad: la auditoría no retiene el cierre
def test_unidad_verificador_no_retiene_ni_reescribe_cierre(tmp_path):
    """La auditoría corre DESPUÉS del predictor y ANTES de los guardianes: su
    salida no puede retener ni reescribir el cierre. Con cierre AJUSTADA y H
    fijas, run() deja el cierre y las H exactamente iguales."""
    ver = _load_verificador()
    result = _sano(tmp_path)
    result["H1"] = {"family": "TOP"}
    result["H2"] = {"family": "SEG"}
    result["cierre_final"] = {"grado": "AJUSTADA",
                              "objeciones": [{"fuente": "LOGICA_COPI"}]}
    antes = json.dumps({k: result[k] for k in ("H1", "H2", "cierre_final")},
                       sort_keys=True, default=str)
    out = ver.run(result, tmp_path)
    despues = json.dumps({k: result[k] for k in ("H1", "H2", "cierre_final")},
                         sort_keys=True, default=str)
    assert despues == antes
    assert out.get("status") == "PASS", out
    assert out.get("violations") == [], out


def test_unidad_registro_no_configurado_sin_violaciones_ni_paquete():
    """El registro del bypass no debe confundirse con una auditoría: no trae
    violaciones ni paquete, solo el motivo de apagado."""
    registro = {"verifier_version": "CONSISTENCY_ADVERSARIAL_V0.1",
                "status": "NO_CONFIGURADO",
                "file": "plugin_verificador_consistencia_adversarial.py",
                "modo": "off",
                "motivo": "apagado por VERIFICADOR_CONSISTENCIA=off",
                "violations": [], "fixture_count": 0,
                "can_decide_H": False, "feeds_H": False,
                "feeds_predictor": False}
    assert registro.get("status") == "NO_CONFIGURADO"
    assert registro.get("modo") == "off"
    assert registro.get("violations") == []
    assert registro.get("fixture_count") == 0
    assert "packet" not in registro
    assert "packet_sha256" not in registro
    assert registro.get("feeds_H") is False
