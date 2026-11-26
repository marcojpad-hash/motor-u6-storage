#!/usr/bin/env python3
"""Candado operativo V7 — generar y verificar motor/CANDADO_OPERATIVO_V7.json.

Uso:
  python3 scripts/verificar_candado_v7.py generar    # escribe el candado con los hashes actuales
  python3 scripts/verificar_candado_v7.py verificar  # (a) los hashes del candado coinciden
                                                      #     con los archivos de V7;
                                                      # (b) el runner antiguo (53ea887)
                                                      #     NO pasa el candado V7.

El candado registra los hashes operativos de V7 (runner V15.3 en V7, cada
módulo cableado, lateral enunciativo, adaptador del orquestador) LINKEADOS a
los canónicos (Engine V5 y catálogo 244, que NO cambian) y a los commits base
de V7. El motor antiguo no pasa este candado porque su hash de runner difiere.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDADO = ROOT / "motor" / "CANDADO_OPERATIVO_V7.json"

# Archivos operativos de V7 (relativos a la raíz del repo). Los canónicos van
# aparte como "link" (no cambian); el resto es lo que el candado protege.
ARCHIVOS_OPERATIVOS = [
    # Runner y puerta principal
    "motor/motor/MOTOR_V15_3_UNICO_20260927.py",
    "motor/correr_estandar.py",
    # Lateral enunciativo (PR #38) y control de guardianes
    "motor/motor/lateral_contexto_enunciativo_v1.py",
    "motor/motor/guardianes_control_v1.py",
    # Capa de entrada
    "motor/capa_llm/filtro_entrada_dirigida_017.py",
    "motor/motor/plugin_sombrero_blanco_token.py",
    "motor/motor/autoevidencia_stores_011.py",
    "motor/calibracion/gate_z90.py",
    # Capa de lógica
    "motor/motor/control_latencia_decimo_hombre.py",
    "motor/motor/plugin_pregunta_detras_v2.py",
    "motor/motor/plugin_pregunta_dirigida_v0_5_1.py",
    "motor/motor/guardian_logica_copi_v1.py",
    "motor/motor/plugin_polaridad_causal.py",
    "motor/motor/sidecar_ablacion_hombre_acero.py",
    "motor/motor/guardian_acero_rival_v1.py",
    "motor/motor/plugin_metodo_rigor.py",
    "motor/motor/modo_estricto_v1.py",
    "motor/motor/decimo_hombre_esteroides_mayeutica_v1.py",
    "motor/motor/plugin_verificador_consistencia_adversarial.py",
    # Retórica
    "motor/motor/guardian_tropos_beristain_v1.py",
    # Investigación
    "motor/motor/sidecar_caldero_busqueda_arquetipos.py",
    "motor/motor/guardian_pistas_llm_caldero_v1.py",
    "motor/motor/filtro_identidad_zoom_out_zoom_in.py",
    "motor/motor/filtro_relleno_013.py",
    "motor/motor/sujetos_014.py",
    # Ejecución y flujo
    "motor/motor/protocolo_kernel_motor.py",
    "motor/motor/control_flujo_soluciones.py",
    "motor/motor/candado_plugins.py",
    "motor/motor/plugin_guardia_no_cruce.py",
    # Runtime de auditoría CEB (V7 C-F3: call() sin traza si el ledger está
    # cerrado + close() limpia el trazador global obsoleto)
    "motor/motor/ceb_runtime_v0_6_flow.py",
    # Salida
    "motor/motor/respuesta_humana_v1.py",
    "motor/motor/lateral_traduccion_salida_v1.py",
    # Herramienta U7 (fuera del motor, pero parte de V7)
    "motor/u7/confianza_apuesta_u7.py",
]

CANONICOS = {
    "motor/motor/Engine_V5_CANONICO_SOLO.py": "665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082",
    "motor/motor/patterns_final_v14.json": "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1",
}

# Adaptador del orquestador (repo orquestador-central, main 8253eaf tras PR #10).
ORQUESTADOR = {
    "repo": "marcojpad-hash/orquestador-central",
    "commit": "8253eafd15481cbfd078744880e10a544323fe32",
    "archivos": {
        "runtime/diagnostics/ruta_contexto_enunciativo.py": "9396e609b33319270cf09cbe212ddeaf646d4f1b478bf5084c131269025fbd0b",
        "runtime/diagnostics/lateral_contexto_enunciativo.py": "9dce1dc805c2c213d2eac8f142cb2f01c37a01e1e0e8bb64657eba1025cb4833",
    },
}

BASE_COMMITS = {
    "alterno_cameo_pesos_base": "53ea887",
    "lateral_enunciativo_merge": "792d881",
    "orquestador_pr10_merge": "8253eafd15481cbfd078744880e10a544323fe32",
}


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def generar():
    hashes = {}
    for rel in ARCHIVOS_OPERATIVOS:
        p = ROOT / rel
        if not p.is_file():
            print(f"FALTA: {rel}")
            sys.exit(1)
        hashes[rel] = _sha256(p)
    candado = {
        "version": "CANDADO_OPERATIVO_V7",
        "fecha": "2026-11-25",
        "rama": "alterno/version-unificada-7",
        "base_commits": BASE_COMMITS,
        "canonicos": CANONICOS,
        "orquestador": ORQUESTADOR,
        "hashes_operativos": hashes,
        "nota": ("El runner antiguo (53ea887) NO pasa este candado: su hash de "
                 "runner difiere del registrado aquí. Los canónicos NO cambian."),
    }
    CANDADO.write_text(json.dumps(candado, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    print(f"escrito {CANDADO} con {len(hashes)} hashes operativos")
    return 0


def _git_show_sha(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"],
                       cwd=str(ROOT), capture_output=True, timeout=60)
    if r.returncode != 0:
        return None
    return hashlib.sha256(r.stdout).hexdigest()


def verificar():
    if not CANDADO.is_file():
        print(f"FALTA CANDADO: {CANDADO}")
        return 1
    candado = json.loads(CANDADO.read_text(encoding="utf-8"))
    ok = True
    print("(a) hashes del candado vs archivos de V7:")
    for rel, esperado in sorted(candado["hashes_operativos"].items()):
        p = ROOT / rel
        actual = _sha256(p) if p.is_file() else None
        marca = "OK  " if actual == esperado else "FALLO"
        if actual != esperado:
            ok = False
        print(f"  {marca} {rel} {((actual or 'AUSENTE')[:12])}")
    print("(a) canónicos (link, no cambian):")
    for rel, esperado in sorted(candado["canonicos"].items()):
        p = ROOT / rel
        actual = _sha256(p) if p.is_file() else None
        marca = "OK  " if actual == esperado else "FALLO"
        if actual != esperado:
            ok = False
        print(f"  {marca} {rel} {((actual or 'AUSENTE')[:12])}")
    print("(b) el runner antiguo NO pasa el candado V7:")
    runner_v7 = candado["hashes_operativos"].get(
        "motor/motor/MOTOR_V15_3_UNICO_20260927.py")
    runner_viejo = _git_show_sha(
        candado["base_commits"]["alterno_cameo_pesos_base"],
        "motor/motor/MOTOR_V15_3_UNICO_20260927.py")
    print(f"  runner V7:     {runner_v7}")
    print(f"  runner 53ea887: {runner_viejo}")
    if runner_viejo is None:
        print("  FALLO: no se pudo leer el runner antiguo de git")
        ok = False
    elif runner_viejo == runner_v7:
        print("  FALLO: el runner antiguo COINCIDE con el de V7 (el candado no lo distingue)")
        ok = False
    else:
        print("  OK: difieren — el runner antiguo NO pasa el candado V7")
    print("RESULTADO:", "OK" if ok else "FALLO")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("generar", "verificar"):
        print("uso: verificar_candado_v7.py [generar|verificar]")
        sys.exit(2)
    sys.exit(generar() if sys.argv[1] == "generar" else verificar())
