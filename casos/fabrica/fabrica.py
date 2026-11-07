#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fábrica de casos para calibración (motor U6 / V15.3). Determinista: no usa LLM ni claves.

  python3 casos/fabrica/fabrica.py preparar casos/fabrica/semillas_lote_F001.py
      Escribe por sujeto cola/<ID>/entrada.json (sin desenlace) y cola/<ID>/desenlace_sellado.json (aparte).
      Valida: tokens del vocabulario de los 244, pesos 0,60–0,84, sin campos de desenlace, sin duplicados.
  python3 casos/fabrica/fabrica.py correr --lote F001 [--n 5]
      Toma hasta N casos pendientes de cola/, verifica hashes del Engine y patrones, escribe el COMPROMISO
      (sha256 de cada entrada y de cada desenlace) ANTES de correr, sella con calibracion/arnes_calibracion.py,
      vuelve a verificar hashes, abre los desenlaces (comprueba que coinciden con el compromiso), evalúa
      H1 / set abierto / apuesta (escenario principal) y agrega filas a calibracion_acumulada.csv + CALIBRACION_ACUMULADA.md.

El motor corre en una copia temporal de motor/ (el repo no se toca). Las corridas completas quedan fuera del repo
(FABRICA_CORRIDAS, por defecto /workspace/FABRICA_CORRIDAS). Nunca se modifica Engine ni catálogo.
"""
from __future__ import annotations
import csv, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[1]
MOTOR_REPO = REPO / "motor"
COLA = AQUI / "cola"
LOTES = AQUI / "lotes"
CSV = AQUI / "calibracion_acumulada.csv"
MD = AQUI / "CALIBRACION_ACUMULADA.md"
CORRIDAS = Path(os.environ.get("FABRICA_CORRIDAS", "/workspace/FABRICA_CORRIDAS"))
CANONICOS = {
    "motor/Engine_V5_CANONICO_SOLO.py": "665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082",
    "motor/patterns_final_v14.json": "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1",
}
P_MIN, P_MAX = 0.60, 0.84
PROHIBIDAS = ("desenlace", "outcome", "resultado_real", "ground_truth", "label_real")
COLS = ["lote", "case_id", "sujeto", "tipo", "freeze", "input_sha256", "desenlace_sha256", "returncode",
        "H1", "H2", "apuesta_estado", "escenario_principal", "acierto_H1", "acierto_H2", "acierto_set",
        "acierto_apuesta", "familias_desenlace", "fuente_desenlace", "engine_ok_antes", "engine_ok_despues", "fecha",
        "destino_real", "apuesta_destino", "acierto_destino", "acierto_destino_polaridad"]  # PATCH 022


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def candados(base: Path) -> dict:
    return {rel: (sha(base / rel) == h if (base / rel).is_file() else False) for rel, h in CANONICOS.items()}


def _buscar_fila_caldero(o):
    if isinstance(o, dict):
        if o.get("componente") == "sidecar_caldero_busqueda_arquetipos.py" and "estado_busqueda_externa" in o:
            return o
        for v in o.values():
            r = _buscar_fila_caldero(v)
            if r: return r
    elif isinstance(o, list):
        for v in o:
            r = _buscar_fila_caldero(v)
            if r: return r
    return None


def _corridas_caso(corridas_dir: Path):
    """Solo las salidas del motor por caso; excluye sidecars del arnés (RECIBO_EJECUCION, CEB_LEDGER_MANIFIESTO),
    que no son casos y antes daban FALLO_EJECUCION_CALDERO falso (SIN_RECIBO_CEB)."""
    return [fp for fp in sorted(Path(corridas_dir).glob("*.json"))
            if not (fp.stem.endswith("_RECIBO_EJECUCION") or "_CEB_LEDGER" in fp.stem)]


def compuerta_caldero(corridas_dir: Path, requerido: bool) -> dict:
    """REGLA_MJ_20261025: en la fábrica de calibración Caldero DEBE buscar en vivo. Fixture/no invocado/fallido = incumplimiento.
    Sin fila CEB = SIN_RECIBO_CEB (también incumplimiento: no se puede probar que corrió)."""
    por_caso = {}
    for fp in _corridas_caso(corridas_dir):
        try:
            fila = _buscar_fila_caldero(json.loads(fp.read_text(encoding="utf-8")))
        except Exception as ex:
            fila = {"estado_busqueda_externa": "SIN_RECIBO_CEB", "motivo": f"no legible: {ex}"}
        est = (fila or {}).get("estado_busqueda_externa", "SIN_RECIBO_CEB")
        permitido = bool((fila or {}).get("incumplimiento") is False)
        por_caso[fp.stem] = {"estado": est, "incumplimiento": requerido and not (est == "EJECUTADO" or (est == "OMITIDO_POR_CONDICION" and permitido)),
                             "accion": (fila or {}).get("accion") or "sin fila CEB de Caldero: averiguar por qué no se registró"}
    malos = {k: v for k, v in por_caso.items() if v["incumplimiento"]}
    return {"requerido_vivo": requerido, "por_caso": por_caso, "incumplimientos": sorted(malos),
            "veredicto": "OK" if not malos else "FALLO_EJECUCION_CALDERO"}


def _filas_fallo(o, acc):
    if isinstance(o, dict):
        if o.get("severidad") in ("FALLO_EJECUCION", "REQUIERE_CONTRATO") and (o.get("pieza") or o.get("componente")):
            n = str(o.get("pieza") or o.get("componente")).replace("verificado:", "")
            acc.setdefault(n, {"estado": o.get("estado_verificado") or o.get("estado_busqueda_externa") or o.get("estado"),
                               "severidad": o["severidad"], "accion": o.get("accion")})
        for v in o.values(): _filas_fallo(v, acc)
    elif isinstance(o, list):
        for v in o: _filas_fallo(v, acc)
    return acc


def compuerta_piezas(corridas_dir: Path, requerido: bool = True) -> dict:
    """REGLA_MJ_20261025 generalizada: junta TODAS las piezas en FALLO_EJECUCION/REQUIERE_CONTRATO de cada caso del lote."""
    por_caso, por_pieza = {}, {}
    for fp in _corridas_caso(corridas_dir):
        try:
            f = _filas_fallo(json.loads(fp.read_text(encoding="utf-8")), {})
        except Exception as ex:
            f = {"(corrida ilegible)": {"estado": "SIN_RECIBO_CEB", "severidad": "FALLO_EJECUCION", "accion": f"no legible: {ex}"}}
        por_caso[fp.stem] = f
        for n, v in f.items():
            por_pieza.setdefault(n, {**v, "casos": []})["casos"].append(fp.stem)
    fallo = {n: v for n, v in por_pieza.items() if v["severidad"] == "FALLO_EJECUCION"}
    contrato = {n: v for n, v in por_pieza.items() if v["severidad"] == "REQUIERE_CONTRATO"}
    return {"requerido": requerido, "por_caso": por_caso, "por_pieza": por_pieza, "fallos_ejecucion": sorted(fallo),
            "requiere_contrato": sorted(contrato),
            "veredicto": "OK" if not (fallo or contrato) else ("FALLO_EJECUCION_PIEZAS" if fallo else "REQUIERE_CONTRATO"),
            "playbook": "docs/CEB_INVESTIGAR_Y_RESOLVER.md"}


def vocab() -> set:
    d = json.loads((MOTOR_REPO / "motor/patterns_final_v14.json").read_text(encoding="utf-8"))
    return set(t for p in d.values() for k in ("tokens_favor", "tokens_contra") for t in p.get(k, {})), set(d)


def hashes_previos() -> set:
    s = set()
    for f in ("casos/HASHES_ENTRADAS.json", "casos/HISTORIAL_HASHES.json", "casos/resultados/resultados.jsonl"):
        p = REPO / f
        if p.is_file():
            import re
            s |= set(re.findall(r"[0-9a-f]{64}", p.read_text(encoding="utf-8")))
    if CSV.is_file():
        s |= {r["input_sha256"] for r in csv.DictReader(CSV.open(encoding="utf-8"))}
    return s


def _tiene(o):
    if isinstance(o, dict):
        return any(str(k).lower() in PROHIBIDAS for k in o) or any(_tiene(v) for v in o.values())
    return any(_tiene(v) for v in o) if isinstance(o, list) else False


def preparar(semillas: Path) -> int:
    spec = importlib.util.spec_from_file_location("semillas", semillas); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    V, FAM = vocab(); previos = hashes_previos(); errores = []
    for sid, persona, tipo, freeze, q, cuts, src, fams, fuente in m.SUJETOS:
        cs = []
        for cid, fecha, hecho, P, A, C in cuts:
            if fecha > freeze: errores.append(f"{sid}: corte {cid} posterior al freeze")
            for t, w in P + A + C:
                if t not in V: errores.append(f"{sid}: token fuera de vocabulario {t}")
                if not (P_MIN <= w <= P_MAX): errores.append(f"{sid}: peso fuera de contrato {t}={w}")
            cs.append({"id": cid, "corte": cid, "cut_id": cid, "date": fecha, "fecha_corte": fecha, "hecho": hecho,
                       "P": [list(x) for x in P], "A": [list(x) for x in A], "C": [list(x) for x in C]})
        for f in fams:
            if f not in FAM: errores.append(f"{sid}: familia de desenlace fuera del catálogo {f}")
        entrada = {"case_id": f"CAL_{sid}", "question": q, "person": persona, "tipo_sujeto": tipo, "freeze": freeze,
                   "random_seed": 20261024, "z_work_kind": "CASE_CUTOFF", "z_work_date": cuts[-1][0], "cuts": cs, "source_notes": src}
        if _tiene(entrada): errores.append(f"{sid}: la entrada trae campo de desenlace")
        d = COLA / f"CAL_{sid}"
        if d.exists(): print(f"ya en cola: {d.name}"); continue
        d.mkdir(parents=True)
        (d / "entrada.json").write_text(json.dumps(entrada, ensure_ascii=False, indent=1), encoding="utf-8")
        (d / "desenlace_sellado.json").write_text(json.dumps({"familias": fams, "fuente": fuente}, ensure_ascii=False, indent=1), encoding="utf-8")
        if sha(d / "entrada.json") in previos: errores.append(f"{sid}: entrada duplicada (hash ya registrado)")
    if errores:
        print("\n".join(errores)); return 1
    print("preparado OK"); return 0


def _gate():
    spec = importlib.util.spec_from_file_location("gate_z90", MOTOR_REPO / "calibracion" / "gate_z90.py")
    g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g); return g


def _validar_pistas_llm(pistas, persona, familias):
    """A5_20261107: carga casos/fabrica/pistas_llm_caldero_v1.py (mismo patrón que _gate())."""
    spec = importlib.util.spec_from_file_location("pistas_llm_caldero_v1", AQUI / "pistas_llm_caldero_v1.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.validar_pistas_llm(pistas, persona, familias, MOTOR_REPO)


def preparar_z(semillas: Path, destinos: Path) -> int:
    """COMPUERTA Z_TRABAJO + preparación ciega. Dos archivos SEPARADOS:
       semillas (SEMILLAS_Z, lo escribe quien NO conoce el final) y destinos (DESTINOS, lo escribe el custodio).
       Si UNA entrada viola la compuerta, falla TODO el lote y no se escribe nada."""
    load = lambda f, n: (lambda sp: (lambda m: (sp.loader.exec_module(m), m)[1])(importlib.util.module_from_spec(sp)))(importlib.util.spec_from_file_location(n, f))
    S, D = load(semillas, "semillas_z").SEMILLAS_Z, load(destinos, "destinos_z").DESTINOS
    V, FAM = vocab(); previos = hashes_previos(); g = _gate(); errores = []; listos = []
    for sm in S:
        sid = sm["id"]; pc = sm.get("preparacion_ciega") or {}; dz = D.get(sid)
        if not dz: errores.append(f"{sid}: sin destino sellado en {destinos.name}"); continue
        if (dz.get("custodio") or "") != (pc.get("custodio_destino") or ""): errores.append(f"{sid}: el custodio del destino no coincide con preparacion_ciega")
        cs = []
        for c in sm["cuts"]:
            for t, w in c["P"] + c["A"] + c["C"]:
                if t not in V: errores.append(f"{sid}: token fuera de vocabulario {t}")
                if not (P_MIN <= w <= P_MAX): errores.append(f"{sid}: peso fuera de contrato {t}={w}")
            cs.append({"id": c["id"], "corte": c["id"], "cut_id": c["id"], "date": c["date"], "fecha_corte": c["date"], "hecho": c["hecho"],
                       "P": [list(x) for x in c["P"]], "A": [list(x) for x in c["A"]], "C": [list(x) for x in c["C"]], "evidencia": c["evidencia"]})
        familias = dz.get("familias")
        if not isinstance(familias, list) or not familias:
            errores.append(f"{sid}: falta 'familias' (lista no vacía de familias del catálogo 244); completar por el custodio antes de preparar-z")
        elif len(familias) != len(set(familias)):
            errores.append(f"{sid}: 'familias' contiene duplicados")
        else:
            for familia in familias:
                if familia not in FAM:
                    errores.append(f"{sid}: familia de desenlace fuera del catálogo {familia}")
        entrada = {"case_id": f"CAL_{sid}", "question": sm["question"], "person": sm["person"], "tipo_sujeto": sm["tipo"],
                   "freeze": sm["z_trabajo"], "z_trabajo": sm["z_trabajo"], "modo_z": sm["modo_z"], "gate_z": g.VERSION,
                   "preparacion_ciega": pc, "random_seed": 20261024, "z_work_kind": "CASE_CUTOFF", "z_work_date": cs[-1]["date"] if cs else "",
                   "cuts": cs, "source_notes": sm.get("source_notes", "")}
        # A5_20261107: la fábrica llena caldero_llm_neighbor_hints desde `pistas_llm`
        # de la semilla (opcional). Sin pistas, el campo queda [] y el guardián del
        # runner no tiene nada que filtrar; con pistas, solo entran las validadas.
        _pistas, _aud_pistas, _err_pistas = _validar_pistas_llm(sm.get("pistas_llm"), sm["person"], FAM)
        errores += [f"{sid}: {x}" for x in _err_pistas]
        entrada["caldero_llm_neighbor_hints"] = _pistas
        entrada["caldero_llm_neighbor_hints_audit"] = _aud_pistas
        if _tiene(entrada): errores.append(f"{sid}: la entrada trae campo de desenlace")
        errores += [f"{sid}: {x}" for x in g.validar_entrada(entrada, dz.get("prohibidas_post_Z"))]
        listos.append((sid, entrada, dz))
    if errores:
        print("LOTE RECHAZADO por la compuerta Z_trabajo (no se escribió nada):\n" + "\n".join(errores)); return 1
    for sid, entrada, dz in listos:
        d = COLA / f"CAL_{sid}"
        if d.exists(): print(f"ya en cola: {d.name}"); continue
        d.mkdir(parents=True)
        (d / "entrada.json").write_text(json.dumps(entrada, ensure_ascii=False, indent=1), encoding="utf-8")
        if sha(d / "entrada.json") in previos: print(f"{sid}: entrada duplicada"); shutil.rmtree(d); return 1
        (d / "desenlace_sellado.json").write_text(json.dumps({"familias": dz["familias"], "fuente": dz["fuente"],
            "prohibidas_post_Z": dz.get("prohibidas_post_Z", []), "custodio": dz.get("custodio")}, ensure_ascii=False, indent=1), encoding="utf-8")
        if dz.get("destino"):
            (d / "destino_sellado.json").write_text(json.dumps({"destino": dz["destino"], "porque": dz.get("porque", ""), "fuente": dz["fuente"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"preparado OK (compuerta {g.VERSION})"); return 0


def pendientes() -> list:
    hechos = {r["case_id"] for r in csv.DictReader(CSV.open(encoding="utf-8"))} if CSV.is_file() else set()
    return [d for d in sorted(COLA.iterdir()) if d.is_dir() and d.name not in hechos]


def _migrar_csv():
    """PATCH 022: si el CSV existe con columnas viejas, se reescribe con las nuevas (filas viejas quedan en blanco)."""
    if not CSV.is_file(): return
    with CSV.open(encoding="utf-8") as fh:
        r = csv.DictReader(fh); viejas = list(r); cab = r.fieldnames
    if cab != COLS:
        with CSV.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows([{k: f.get(k, "") for k in COLS} for f in viejas])


POL = lambda x: "abajo" if x in ("caida", "ruptura") else "arriba_o_igual"


def correr(lote: str, n: int, rehacer: list | None = None) -> int:
    _migrar_csv()
    # --rehacer ID1,ID2: vuelve a correr casos ya evaluados con sus MISMOS sellos (para un parche nuevo; no se reetiqueta nada)
    casos = [COLA / c for c in rehacer] if rehacer else pendientes()[:n]
    g = _gate()
    for d in casos:  # COMPUERTA Z_TRABAJO otra vez justo antes del motor (por si alguien editó la cola a mano)
        e = json.loads((d / "entrada.json").read_text(encoding="utf-8"))
        if e.get("gate_z"):
            pz = json.loads((d / "desenlace_sellado.json").read_text(encoding="utf-8")).get("prohibidas_post_Z")
            bad = g.validar_entrada(e, pz)
            if bad: print(f"GATE_Z_TRABAJO_RECHAZADO {d.name}: " + "; ".join(bad[:10])); return 8
    if not casos: print("sin casos pendientes en cola/"); return 0
    ok_antes = candados(MOTOR_REPO)
    if not all(ok_antes.values()): print(json.dumps({"error": "CANDADO_ROTO_ANTES", "detalle": ok_antes})); return 3
    LOTES.mkdir(exist_ok=True); salida = CORRIDAS / lote
    if salida.exists(): print(f"ya existe {salida}: el sello no se reescribe; use otro --lote"); return 3
    # 1) Compromiso: hashes de entradas y desenlaces ANTES de correr (los desenlaces no se leen).
    comp = {"lote": lote, "fecha_local": datetime.now().isoformat(timespec="seconds"), "candados_antes": ok_antes,
            "casos": {d.name: {"input_sha256": sha(d / "entrada.json"), "desenlace_sha256": sha(d / "desenlace_sellado.json"),
                         **({"destino_sha256": sha(d / "destino_sellado.json")} if (d / "destino_sellado.json").is_file() else {})} for d in casos}}
    (LOTES / f"{lote}_COMPROMISO.json").write_text(json.dumps(comp, ensure_ascii=False, indent=1), encoding="utf-8")
    # 2) Copia temporal del motor y corrida con el arnés existente (sin LLM).
    tmp = Path(tempfile.mkdtemp(prefix="fabrica_motor_"))
    mcopy = tmp / "motor"
    shutil.copytree(MOTOR_REPO, mcopy, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    entradas = tmp / "casos"; entradas.mkdir()
    for d in casos: shutil.copy(d / "entrada.json", entradas / f"{d.name}.json")
    sb_root = os.environ.get("STINKBOX_STORAGE_ROOT") or str(Path.home() / "STINKBOX_PERSISTENTE" / "STINKBOX_STORAGE")  # persistente entre lotes
    env = {**os.environ, "STINKBOX_STORAGE_ROOT": sb_root, "CALDERO_BUSQUEDA_VIVA": os.environ.get("CALDERO_BUSQUEDA_VIVA", "1"), "CALDERO_BUSCADOR": os.environ.get("CALDERO_BUSCADOR", "auto")}
    pr = subprocess.run([sys.executable, "-B", "calibracion/arnes_calibracion.py", "correr", str(entradas), str(salida), "--pesos", "0"],
                        cwd=str(mcopy), env=env, text=True, capture_output=True)
    print(pr.stdout[-2000:], pr.stderr[-2000:])
    ok_despues = {**candados(MOTOR_REPO), **{f"copia::{k}": v for k, v in candados(mcopy).items()}}
    reg_p = salida / "REGISTRO_CALIBRACION.json"
    if not reg_p.is_file(): print("sin registro sellado"); return 4
    reg = json.loads(reg_p.read_text(encoding="utf-8"))
    # 3) Abrir desenlaces SOLO ahora, comprobando el compromiso.
    des = {}
    for d in casos:
        if sha(d / "desenlace_sellado.json") != comp["casos"][d.name]["desenlace_sha256"]:
            print(f"DESENLACE_ALTERADO {d.name}"); return 5
        des[d.name] = json.loads((d / "desenlace_sellado.json").read_text(encoding="utf-8"))
        if (d / "destino_sellado.json").is_file():  # PATCH 022: destino personal sellado aparte
            if sha(d / "destino_sellado.json") != comp["casos"][d.name].get("destino_sha256"):
                print(f"DESTINO_ALTERADO {d.name}"); return 5
            des[d.name]["destino"] = json.loads((d / "destino_sellado.json").read_text(encoding="utf-8"))["destino"]
    (salida / "desenlaces.json").write_text(json.dumps(des, ensure_ascii=False, indent=1), encoding="utf-8")
    subprocess.run([sys.executable, "-B", "calibracion/arnes_calibracion.py", "evaluar", str(reg_p), str(salida / "desenlaces.json")], cwd=str(mcopy), check=False)
    # 4) Filas acumuladas.
    nuevo = not CSV.is_file(); filas = []
    errs = {e["caso"].removesuffix(".json"): e.get("returncode") for e in reg.get("errores", [])}
    for d in casos:
        e = json.loads((d / "entrada.json").read_text(encoding="utf-8")); fams = set(des[d.name]["familias"])
        r = (reg["casos"].get(d.name) or {}).get("por_peso", {}).get("0")
        f = {"lote": lote, "case_id": d.name, "sujeto": e["person"], "tipo": e["tipo_sujeto"], "freeze": e["freeze"],
             "input_sha256": comp["casos"][d.name]["input_sha256"], "desenlace_sha256": comp["casos"][d.name]["desenlace_sha256"],
             "familias_desenlace": "|".join(sorted(fams)), "fuente_desenlace": des[d.name]["fuente"],
             "engine_ok_antes": all(ok_antes.values()), "engine_ok_despues": all(ok_despues.values()), "fecha": datetime.now().date().isoformat()}
        if r:
            hs = [h["familia"] for h in r["hipotesis"]]
            f.update(returncode=r["returncode"], H1=r["H1"], H2=r["H2"], apuesta_estado=r["apuesta_estado"], escenario_principal=r["escenario_principal"],
                     acierto_H1=int(r["H1"] in fams), acierto_H2=int(r["H2"] in fams), acierto_set=int(bool(fams & set(hs))),
                     acierto_apuesta=int(bool(fams & set(r["hipotesis_escenario_principal"]))))
            dr, pd = des[d.name].get("destino"), r.get("apuesta_destino_personal")
            f.update(destino_real=dr or "", apuesta_destino=pd or "",
                     acierto_destino=(int(pd == dr) if dr else ""), acierto_destino_polaridad=(int(bool(pd) and POL(pd) == POL(dr)) if dr else ""))
        else:
            f.update(returncode=errs.get(d.name, "?"), H1="NO_SELLADO", H2="", apuesta_estado="NO_SELLADA", escenario_principal="",
                     acierto_H1="", acierto_H2="", acierto_set="", acierto_apuesta="")
        filas.append(f)
    with CSV.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        if nuevo: w.writeheader()
        w.writerows(filas)
    req = os.environ.get("CALDERO_BUSQUEDA_VIVA", "1") == "1" and os.environ.get("FABRICA_CALDERO_REQUERIDO", "1") != "0"
    gc = compuerta_caldero(salida / "corridas", req); comp["compuerta_caldero"] = gc
    if gc["incumplimientos"]:
        print(f"FALLO_EJECUCION_CALDERO (lote marcado, no es éxito): {gc['incumplimientos']}")
    gp = compuerta_piezas(salida / "corridas", os.environ.get("FABRICA_PIEZAS_REQUERIDAS", "1") != "0"); comp["compuerta_piezas"] = gp
    for n, v in gp["por_pieza"].items():
        print(f"[CEB] {v['severidad']} {n} estado={v['estado']} casos={len(v['casos'])} -> {v['accion']}")
    comp["candados_despues"] = ok_despues; comp["sha256_registro_sellado"] = reg.get("sha256_registro")
    (LOTES / f"{lote}_RESUMEN.json").write_text(json.dumps({**comp, "filas": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
    resumen_md()
    # 5) StinkBox -> GitHub (solo stinkbox/tokens.jsonl + casos/resultados/resultados.jsonl). FABRICA_SYNC=0 lo apaga.
    if os.environ.get("FABRICA_SYNC", "1") != "0" and all(ok_despues.values()):
        sy = subprocess.run([sys.executable, "-B", str(REPO / "scripts" / "sincronizar_storage.py"), "despues", "--corrida", str(salida),
                             "--repo", str(REPO), "--stinkbox", sb_root, "--modelo", os.environ.get("FABRICA_MODELO", "GrokBot_fabrica")],
                            text=True, capture_output=True)
        print("[sync StinkBox]", sy.stdout[-1500:], sy.stderr[-800:])
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({"lote": lote, "casos": len(filas), "candados_antes": ok_antes, "candados_despues": ok_despues}, ensure_ascii=False))
    if not all(ok_despues.values()): return 6
    return 9 if (gc["incumplimientos"] or (gp["requerido"] and gp["fallos_ejecucion"])) else 0


def resumen_md():
    filas = list(csv.DictReader(CSV.open(encoding="utf-8")))
    ev = [f for f in filas if f["acierto_H1"] != ""]
    evd = [f for f in filas if f.get("acierto_destino", "") != ""]
    def tasad(k):
        a = sum(int(f[k]) for f in evd); m_ = len(evd); return f"{a}/{m_} (Laplace {((a + 1) / (m_ + 2)):.2f})"
    n = len(ev)
    def tasa(k):
        a = sum(int(f[k]) for f in ev); return f"{a}/{n} ({(a / n * 100 if n else 0):.0f} %; Laplace {((a + 1) / (n + 2)):.2f})"
    L = ["# Calibración acumulada — fábrica de casos", "",
         f"Casos en la tabla: {len(filas)} · evaluados (sellados): {n} · no sellados: {len(filas) - n}", "",
         f"- Acierto H1: {tasa('acierto_H1')}", f"- Acierto H2: {tasa('acierto_H2')}",
         f"- Acierto set abierto (alguna hipótesis): {tasa('acierto_set')}", f"- Acierto apuesta (escenario principal): {tasa('acierto_apuesta')}",
         f"- Acierto apuesta de destino personal (PATCH 022, exacta auge/meseta/caida/ruptura): {tasad('acierto_destino')}" if evd else "",
         f"- Acierto destino por polaridad (arriba/igual vs abajo): {tasad('acierto_destino_polaridad')}" if evd else "",
         "", "Aviso: con menos de 30 casos evaluados la tasa es muy ruidosa." if n < 30 else "", "",
         "| Lote | Caso | Tipo | H1 | H2 | Escenario | H1 | H2 | Set | Apuesta | Destino apostado | Destino real | Destino | Engine OK |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    m = lambda v: {"1": "sí", "0": "no", "": "—"}.get(str(v), str(v))
    for f in filas:
        L.append(f"| {f['lote']} | {f['sujeto']} ({f['freeze']}) | {f['tipo']} | {f['H1']} | {f['H2']} | {f['escenario_principal']} | "
                 f"{m(f['acierto_H1'])} | {m(f['acierto_H2'])} | {m(f['acierto_set'])} | {m(f['acierto_apuesta'])} | {f.get('apuesta_destino') or '—'} | {f.get('destino_real') or '—'} | {m(f.get('acierto_destino', ''))} | {f['engine_ok_antes']}/{f['engine_ok_despues']} |")
    MD.write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    a = sys.argv
    if len(a) >= 4 and a[1] == "preparar-z": sys.exit(preparar_z(Path(a[2]).resolve(), Path(a[3]).resolve()))
    if len(a) >= 3 and a[1] == "preparar":
        print("AVISO: 'preparar' (formato viejo, sin compuerta Z_trabajo) queda solo para lotes ya sellados (F001). Lotes nuevos: preparar-z.")
        if os.environ.get("FABRICA_PERMITIR_SIN_GATE") != "1": sys.exit(7)
        sys.exit(preparar(Path(a[2]).resolve()))
    if len(a) >= 2 and a[1] == "correr":
        lote = a[a.index("--lote") + 1] if "--lote" in a else datetime.now().strftime("F%Y%m%d")
        n = int(a[a.index("--n") + 1]) if "--n" in a else 5
        reh = a[a.index("--rehacer") + 1].split(",") if "--rehacer" in a else None
        sys.exit(correr(lote, n, reh))
    print(__doc__); sys.exit(2)
