#!/usr/bin/env python3
"""Barrido de mortalidad (2026-11-12, orden de Marco).

Pregunta: ¿el motor nota/siente la mortalidad por la matematica, sin que
lo hayamos notado verbalmente? Premisa: todos los casos terminan en
muerte (el final). Se revisa si la geometria muestra la aproximacion al
final antes del ultimo corte.

Hecho previo: con 3 cortes NO se puede definir un margen de radio (el
margen necesita un prefijo). Solo Mozart y Napoleon tienen 9-10 cortes.
Por eso el barrido en los 35 casos F001-F004 mide la APROXIMACION, no la
ruptura: (1) tendencia del radio (¿crece hacia afuera o se contrae hacia
el centro al acercarse al final?), (2) aceleracion del ultimo paso
(dX del ultimo paso / dX del anterior; el marcador de limite ya lo
calcula por corte), (3) regimen del marcador en el ultimo corte.
Contra eso: el desenlace sellado de cada caso (¿trae fatalidad/desastre?).

El radio se mide en el plano PC1-PC2 del tablero P (3 puntos), desde el
centroide. Limitacion honesta: con 3 cortes la tendencia es solo 2 pasos;
el barrido busca un patron en 35 casos, no una prueba por caso.
Mozart y Napoleon (10 cortes) entran como referencia con lo ya medido
en la sonda v2 (ruptura de margen / aceleracion).

Salidas: barrido_mortalidad_reporte.json (+ figura si el patron lo amerita).
"""
import json, glob
from pathlib import Path
import numpy as np

BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo")
OUT = Path("/home/hatch/workspace/u6-alterno")

FATALIDAD = {
    "17_fatal_imprudencia", "6_desastre", "36_perdida_de_los_seres_queridos",
    "22_todo_sacrificado_por_una_pasion", "31_conflicto_con_un_dios",
    "16_locura", "cliodinamica_03_fase_crisis_colapso",
    "frye_mythos_tragedia", "20_sacrificio_por_un_ideal",
    "21_sacrificio_por_los_parientes", "19_asesinato_de_un_pariente_no_reconocido",
}


def tableros_p(result_path):
    d = json.load(open(result_path))
    cuts = d["motor"]["cuts"]
    fams = sorted(cuts[0]["P_FULL_244"].keys())
    X = np.array([[c["P_FULL_244"][f] for f in fams] for c in cuts], dtype=float)
    return d, fams, X


def main():
    filas = []
    for rp in sorted(glob.glob(str(BASE / "motor/RESULT_CAL_F00*.json"))):
        if "LEDGER" in rp or "RECIBO" in rp:
            continue
        nombre = Path(rp).stem.replace("RESULT_", "")
        d, fams, X = tableros_p(rp)
        n = X.shape[0]
        # PCA sobre los 3 puntos; radio desde el centroide en PC1-PC2.
        mu = X.mean(axis=0)
        U, S, Vt = np.linalg.svd(X - mu, full_matrices=False)
        sc = (X - mu) @ Vt.T[:, :2]
        r = np.linalg.norm(sc, axis=1)
        dx = np.array(d["motor"]["R732"]["dX_norm"], dtype=float)
        ratio_ultimo = float(dx[-1] / dx[0]) if dx[0] > 1e-12 else None
        marcador = (d["motor"]["R732"].get("marcador_limite_geometrico") or {})
        per_cut = marcador.get("per_cut") or []
        regimen_ultimo = per_cut[-1].get("regime") if per_cut else None
        # Desenlace sellado.
        caso_dir = BASE / "casos/fabrica/cola" / nombre
        desen = {}
        dp = caso_dir / "desenlace_sellado.json"
        if dp.exists():
            desen = json.load(open(dp))
        fams_des = desen.get("familias") or []
        fatal = [f for f in fams_des if f in FATALIDAD]
        filas.append({
            "caso": nombre,
            "n_cortes": n,
            "radio_por_corte": [round(float(v), 3) for v in r],
            "radio_crece_hacia_final": bool(r[-1] > r[0]),
            "radio_monotono_creciente": bool(r[0] < r[1] < r[2]) if n == 3 else None,
            "radio_contrae_hacia_final": bool(r[-1] < r[0]),
            "aceleracion_ultimo_paso_ratio": round(ratio_ultimo, 2) if ratio_ultimo else None,
            "ultimo_paso_acelera": bool(ratio_ultimo and ratio_ultimo > 1.25),
            "regimen_marcador_ultimo_corte": regimen_ultimo,
            "desenlace_familias": fams_des,
            "desenlace_con_fatalidad": bool(fatal),
            "desenlace_fatalidad_cuales": fatal,
        })

    # Referencia: Mozart y Napoleon (sonda v2, 10 cortes).
    ref = {
        "MOZART_Z90": {"radio_rompe_margen": True, "fase_se_invierte": True,
                       "ultimo_paso_acelera": False, "regimen_marcador_ultimo_corte": "GIRO_FUERTE",
                       "desenlace_con_fatalidad": None},
        "NAPOLEON_Z90": {"radio_rompe_margen": False, "fase_se_invierte": False,
                         "ultimo_paso_acelera": True, "regimen_marcador_ultimo_corte": "MOVIMIENTO_ACELERADO",
                         "desenlace_con_fatalidad": True},
    }
    n = len(filas)
    crece = sum(1 for f in filas if f["radio_crece_hacia_final"])
    contrae = sum(1 for f in filas if f["radio_contrae_hacia_final"])
    mono = sum(1 for f in filas if f["radio_monotono_creciente"])
    acel = sum(1 for f in filas if f["ultimo_paso_acelera"])
    fatal = sum(1 for f in filas if f["desenlace_con_fatalidad"])
    crece_y_fatal = sum(1 for f in filas if f["radio_crece_hacia_final"] and f["desenlace_con_fatalidad"])
    crece_sin_fatal = sum(1 for f in filas if f["radio_crece_hacia_final"] and not f["desenlace_con_fatalidad"])
    no_crece_y_fatal = sum(1 for f in filas if not f["radio_crece_hacia_final"] and f["desenlace_con_fatalidad"])
    acel_y_fatal = sum(1 for f in filas if f["ultimo_paso_acelera"] and f["desenlace_con_fatalidad"])
    resumen = {
        "n_casos_F": n,
        "radio_crece_hacia_final": crece,
        "radio_contrae_hacia_final": contrae,
        "radio_monotono_creciente": mono,
        "ultimo_paso_acelera": acel,
        "desenlace_con_fatalidad": fatal,
        "crece_Y_fatalidad": crece_y_fatal,
        "crece_sin_fatalidad": crece_sin_fatal,
        "no_crece_Y_fatalidad": no_crece_y_fatal,
        "acelera_Y_fatalidad": acel_y_fatal,
        "referencia_10_cortes": ref,
    }
    reporte = {"resumen": resumen, "casos": filas}
    (OUT / "barrido_mortalidad_reporte.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    print("--- casos donde el radio crece y hay fatalidad:")
    for f in filas:
        if f["radio_crece_hacia_final"] and f["desenlace_con_fatalidad"]:
            print(" ", f["caso"], "radio:", f["radio_por_corte"], "acelera:", f["ultimo_paso_acelera"],
                  "regimen:", f["regimen_marcador_ultimo_corte"], "fatal:", f["desenlace_fatalidad_cuales"])


if __name__ == "__main__":
    main()
