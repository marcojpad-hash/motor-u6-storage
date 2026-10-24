#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arnés de calibración del peso geométrico (U6_CALIBRABLE_20261020).

Paso 1 (ANTES del desenlace):  python3 calibracion/arnes_calibracion.py correr CARPETA_CASOS SALIDA [--pesos 0,0.05,0.1,0.2]
    Corre cada caso nuevo (formato estándar de correr_estandar.py) con cada peso y SELLA, por peso:
    H1/H2 (alias), lista abierta de hipótesis, apuesta por escenarios, aporte geométrico y hash del núcleo estable.
Paso 2 (DESPUÉS, con desenlaces reales):  python3 calibracion/arnes_calibracion.py evaluar SALIDA/REGISTRO_CALIBRACION.json DESENLACES.json
    Calcula, por peso: tasa de acierto (H1, set abierto, escenario principal) con suavizado de Laplace
    y Brier con probabilidades recortadas a [0.05, 0.95].

Modo seco:  python3 calibracion/arnes_calibracion.py validar CARPETA_CASOS   (no corre el motor, no sella)
Nota copia U6_CONT_AGNOSTICO: el motor no expone GEOMETRIA_PESO -> un solo peso nominal (0); varios pesos se rechazan.

Reglas: no inventa desenlaces; rechaza casos que traigan campos de desenlace en el input; no reescribe el registro sellado.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOTOR = ROOT / "motor" / "MOTOR_V15_3_UNICO_20260927.py"


def motor_soporta_peso() -> bool:
    """LISTO_CALIBRAR_20261024 (copia U6_CONT_AGNOSTICO): este motor integra la geometría como dimensiones del
    rank_fusion y NO expone GEOMETRIA_PESO. Sin ese interruptor, correr varios pesos daría corridas idénticas
    disfrazadas de barrido; por eso se detecta y se exige un único peso nominal."""
    try:
        return "GEOMETRIA_PESO" in MOTOR.read_text(encoding="utf-8")
    except OSError:
        return False


PESOS_DEFECTO = [0.0, 0.05, 0.1, 0.2] if motor_soporta_peso() else [0.0]
P_MIN, P_MAX = 0.05, 0.95
CLAVES_PROHIBIDAS = ("desenlace", "outcome", "resultado_real", "ground_truth", "label_real")
VERSION = "ARNES_CALIBRACION_GEOMETRIA_V1"


def clip(p: float) -> float:
    return max(P_MIN, min(P_MAX, float(p)))


def laplace(aciertos: int, n: int) -> float:
    return (aciertos + 1.0) / (n + 2.0)


def _sha_obj(o) -> str:
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _fam(x):
    return x.get("family") if isinstance(x, dict) else x


def _tiene_desenlace(o) -> bool:
    if isinstance(o, dict):
        return any(str(k).lower() in CLAVES_PROHIBIDAS for k in o) or any(_tiene_desenlace(v) for v in o.values())
    if isinstance(o, list):
        return any(_tiene_desenlace(v) for v in o)
    return False


def extraer(result: dict, peso: float) -> dict:
    pred = result.get("predictor") or {}
    geo = (pred.get("geometria_trayectoria_en_fusion") or {}).get("por_candidata") or {}
    si = result.get("salida_interpretable") if isinstance(result.get("salida_interpretable"), dict) else {}
    ap = result.get("apuesta_escenarios") or si.get("apuesta_multiescenario") or result.get("apuesta") or {}
    hyp = [{"familia": h.get("familia"), "rank_fusion": h.get("rank_fusion"),
            "soporte_estructural_relativo": h.get("soporte_estructural_relativo"),
            "regimen": (h.get("trazabilidad_geometrica") or {}).get("regimen"),
            "aporte_geometria": (geo.get(h.get("familia")) or {}).get("aporte_rank_fusion")}
           for h in (result.get("hipotesis") or []) if isinstance(h, dict)]
    princ = ap.get("apuesta_principal") or {}
    return {"peso": peso, "H1": _fam(result.get("H1")), "H2": _fam(result.get("H2")), "hipotesis": hyp,
            "apuesta_estado": ap.get("estado"),
            "escenarios": [{"escenario": e.get("escenario"), "hipotesis": e.get("hipotesis_que_convergen"),
                            "soporte": e.get("soporte_estructural_agregado")} for e in (ap.get("escenarios") or [])],
            "escenario_principal": princ.get("escenario"),
            "apuesta_destino_personal": (result.get("apuesta_destino_personal") or {}).get("apuesta"),  # PATCH 022
            "hipotesis_escenario_principal": princ.get("hipotesis_que_convergen") or [],
            "nucleo_estable_sha256": (result.get("nucleo_estable") or {}).get("sha256"),
            "huella_salida_sha256": _sha_obj({"H1": _fam(result.get("H1")), "H2": _fam(result.get("H2")),
                                              "hip": [h["familia"] for h in hyp], "esc": princ.get("escenario")}),
            "estado_ejecucion": result.get("estado_ejecucion") or "SIN_PAUSA",
            "peso_aplicado_por_motor": motor_soporta_peso()}


def correr(carpeta: Path, salida: Path, pesos) -> int:
    casos = sorted(p for p in Path(carpeta).glob("*.json") if not p.name.startswith("PLANTILLA"))
    if not casos:
        print(json.dumps({"ok": False, "error": f"sin casos *.json en {carpeta}"})); return 2
    if len(pesos) > 1 and not motor_soporta_peso():
        print(json.dumps({"ok": False, "error": "MOTOR_SIN_GEOMETRIA_PESO: este motor no expone el peso; use un solo peso (--pesos 0)"})); return 4
    salida.mkdir(parents=True, exist_ok=True)
    reg_path = salida / "REGISTRO_CALIBRACION.json"
    if reg_path.exists():
        print(json.dumps({"ok": False, "error": "REGISTRO_CALIBRACION.json ya existe: el sello no se reescribe; use otra carpeta de salida"})); return 3
    registro = {"version": VERSION, "sellado_utc": datetime.now(timezone.utc).isoformat(), "pesos": pesos, "casos": {}, "errores": []}
    for p in casos:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if _tiene_desenlace(raw):
            registro["errores"].append({"caso": p.name, "error": "INPUT_CON_CAMPO_DE_DESENLACE_RECHAZADO"}); continue
        cid = str(raw.get("case_id") or p.stem) if isinstance(raw, dict) else p.stem
        fila = {"input": p.name, "input_sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "por_peso": {}}
        for w in pesos:
            out = salida / "corridas" / f"{p.stem}__w{w:g}.json"; out.parent.mkdir(parents=True, exist_ok=True)
            env = {**os.environ, "GEOMETRIA_PESO": repr(float(w))}
            pr = subprocess.run([sys.executable, "-B", str(ROOT / "correr_estandar.py"), str(p), f"CAL__{p.stem}", str(out)],
                                cwd=str(ROOT), env=env, text=True, capture_output=True)
            # 0 = COMPLETED, 5 = COMPLETED_WITH_METADATA_GAP (sellable, se anota); 6 = PAUSADA (no sellable) y resto = error
            if pr.returncode not in (0, 5) or not out.is_file():
                registro["errores"].append({"caso": p.name, "peso": w, "returncode": pr.returncode, "stderr": pr.stderr[-1500:]}); continue
            fila["por_peso"][f"{w:g}"] = {**extraer(json.loads(out.read_text(encoding="utf-8")), w), "returncode": pr.returncode}
        registro["casos"][cid] = fila
    registro["sha256_registro"] = _sha_obj({k: v for k, v in registro.items() if k != "sha256_registro"})
    reg_path.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": not registro["errores"], "registro": str(reg_path), "n_casos": len(registro["casos"]),
                      "errores": len(registro["errores"]), "sha256_registro": registro["sha256_registro"]}, ensure_ascii=False))
    return 0 if not registro["errores"] else 1


def _brier(pares):
    return sum((p - y) ** 2 for p, y in pares) / len(pares) if pares else None


def evaluar_registro(registro: dict, desenlaces: dict) -> dict:
    """desenlaces: {case_id: {"familias": [...], "escenario": opcional}}. Solo se evalúan casos con desenlace."""
    esperado = _sha_obj({k: v for k, v in registro.items() if k != "sha256_registro"})
    integridad = "OK" if esperado == registro.get("sha256_registro") else "REGISTRO_MODIFICADO_TRAS_SELLO"
    casos = {c: f for c, f in registro.get("casos", {}).items() if c in desenlaces}
    por_peso = {}
    for w in [f"{float(x):g}" for x in registro.get("pesos", [])]:
        ev = []
        for cid, fila in sorted(casos.items()):
            r = fila["por_peso"].get(w)
            if not r: continue
            d = desenlaces[cid]; fams = set(d.get("familias") or [])
            hs = [h["familia"] for h in r["hipotesis"]]
            esc_ok = (r["escenario_principal"] == d["escenario"]) if d.get("escenario") else bool(fams & set(r["hipotesis_escenario_principal"]))
            # PATCH 022: destino personal (solo si el desenlace trae "destino"); polaridad = {auge,meseta} vs {caida,ruptura}
            _dst = d.get("destino"); _pd = r.get("apuesta_destino_personal")
            _pol = lambda x: "abajo" if x in ("caida", "ruptura") else "arriba_o_igual"
            y_dest = {} if not _dst else {"y_destino": int(_pd == _dst), "y_destino_polaridad": int(bool(_pd) and _pol(_pd) == _pol(_dst))}
            ev.append({"caso": cid, "y_H1": int(r["H1"] in fams), "y_set": int(bool(fams & set(hs))), "y_escenario": int(esc_ok), **y_dest,
                       "hip": [(h["familia"], h.get("soporte_estructural_relativo") or 0.0, int(h["familia"] in fams)) for h in r["hipotesis"]],
                       "soporte_principal": next((e["soporte"] for e in r["escenarios"] if e["escenario"] == r["escenario_principal"]), 0.0) or 0.0})
        n = len(ev); res = {"n_casos": n}
        for key in ("y_H1", "y_set", "y_escenario") + (("y_destino", "y_destino_polaridad") if ev and all("y_destino" in e for e in ev) else ()):
            k = sum(e[key] for e in ev)
            # Brier prospectivo: cada caso se pronostica con la tasa Laplace de los DEMÁS casos (leave-one-out).
            pares = [(clip(laplace(k - e[key], n - 1)), e[key]) for e in ev]
            res[key[2:]] = {"aciertos": k, "tasa_cruda": (k / n) if n else None, "tasa_laplace": clip(laplace(k, n)),
                            "brier_loo_laplace": _brier(pares)}
        res["brier_diagnostico_soporte_hipotesis"] = _brier([(clip(s), y) for e in ev for _, s, y in e["hip"]])
        res["brier_diagnostico_soporte_escenario"] = _brier([(clip(e["soporte_principal"]), e["y_escenario"]) for e in ev])
        res["detalle"] = [{k: e[k] for k in ("caso", "y_H1", "y_set", "y_escenario", "y_destino", "y_destino_polaridad") if k in e} for e in ev]
        por_peso[w] = res
    n = len(casos)
    return {"version": VERSION, "integridad_registro": integridad, "n_casos_con_desenlace": n,
            "n_casos_sellados_sin_desenlace": len(registro.get("casos", {})) - n,
            "aviso_muestra": "MUESTRA_INSUFICIENTE (<10): no elegir peso con esto" if n < 10 else "ok",
            "probabilidades": f"Laplace (k+1)/(n+2), recortadas a [{P_MIN}, {P_MAX}]",
            "nota": "brier_diagnostico_* trata soporte_estructural_relativo como pronóstico SOLO para comparar pesos; no lo convierte en probabilidad del motor",
            "por_peso": por_peso}


def validar(carpeta: Path) -> int:
    """Modo SECO: revisa los casos sin correr el motor ni sellar nada."""
    casos = sorted(p for p in Path(carpeta).glob("*.json") if not p.name.startswith("PLANTILLA"))
    filas = []
    for p in casos:
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            filas.append({"caso": p.name, "ok": False, "error": f"JSON_INVALIDO: {exc}"}); continue
        cuts = raw.get("cuts") if isinstance(raw, dict) else None
        err = ("INPUT_CON_CAMPO_DE_DESENLACE_RECHAZADO" if _tiene_desenlace(raw) else
               ("SIN_CORTES" if not cuts else None))
        filas.append({"caso": p.name, "ok": err is None, "error": err, "n_cortes": len(cuts or []),
                      "input_sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    out = {"modo": "SECO_SIN_MOTOR_SIN_SELLO", "version": VERSION, "motor_soporta_GEOMETRIA_PESO": motor_soporta_peso(),
           "pesos_por_defecto": PESOS_DEFECTO, "n_casos": len(filas), "casos": filas, "ok": bool(filas) and all(f["ok"] for f in filas)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["ok"] else 1


def main(argv) -> int:
    if len(argv) >= 3 and argv[1] == "validar":
        return validar(Path(argv[2]).resolve())
    if len(argv) >= 4 and argv[1] == "correr":
        pesos = PESOS_DEFECTO
        if "--pesos" in argv: pesos = [float(x) for x in argv[argv.index("--pesos") + 1].split(",")]
        return correr(Path(argv[2]).resolve(), Path(argv[3]).resolve(), pesos)
    if len(argv) >= 4 and argv[1] == "evaluar":
        reg = json.loads(Path(argv[2]).read_text(encoding="utf-8")); des = json.loads(Path(argv[3]).read_text(encoding="utf-8"))
        out = evaluar_registro(reg, des)
        dst = Path(argv[2]).with_name("EVALUACION_CALIBRACION.json")
        dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: out[k] for k in ("integridad_registro", "n_casos_con_desenlace", "aviso_muestra")} | {"salida": str(dst)}, ensure_ascii=False))
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
