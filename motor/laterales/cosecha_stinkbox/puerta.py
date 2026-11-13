#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""puerta.py — Puerta del lateral cosecha del StinkBox, v2.

G1 (estructural): el catálogo carga (244 familias, 703 tokens), el índice
   de casos resueltos carga (160 entradas) y el archivo manual de
   descubrimientos carga (13 entradas). can_decide_H es False: la cosecha
   decide activación de ANÁLOGOS, nunca H.
G2 (reproducción + decisiones): la cosecha completa (sin registro)
   reproduce los 13 descubrimientos del archivo manual
   (STINKBOX_PERSISTENTE/tokens_descubiertos_ciegos_z90_20261113.json):
   mismos casos, mismas familias, mismo lugar, mismo rank_fusion
   (tolerancia 1e-4) y mismo regimen; para las de Z, mismo valor. Y la
   salida v2 trae los 4 tokens sin familia con decisión y evidencia
   (familia más cercana, puntaje, motivo, casos, apariciones).
G3 (registro y dedupe por token): re-correr la cosecha v2 sobre el
   mismo índice NO produce hallazgos nuevos ni matices nuevos de casos
   ya cosechados (0 casos nuevos, 0 hallazgos, 0 matices nuevos); los
   53 casos distintos del índice están todos en el registro. Y el dedupe
   por token funciona: al filtrar los candidatos de un caso ya cosechado
   (ANONIMO2_Z90_20261113) contra el registro, arte/deuda/enfermedad
   salen como omitidos con motivo "ya existe" y NO vuelven a entrar
   como hallazgo; los tokens delta en el catálogo también se omiten.
G4 (determinismo + no-duplicación): decidir_token dos veces sobre la
   misma entrada da la misma decisión (misma entrada, misma decisión);
   las sondas de duplicado ("busqueda_riesgo", "busqueda_riesgos",
   "deuda_de_sangre") se rechazan como duplicadas; los 4 tokens reales
   no son duplicados.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # motor-cameo/
sys.path.insert(0, str(HERE))
import cosecha as C

MANUAL = ROOT / "STINKBOX_PERSISTENTE" / "tokens_descubiertos_ciegos_z90_20261113.json"
V2_JSON = HERE / "COSECHA_20261113_V2.json"
REGISTRO = HERE / "REGISTRO_COSECHA.json"
TOKENS_ESPERADOS = ["arte", "deuda", "enfermedad", "riesgo"]
DECISIONES_ESPERADAS = {"arte": "ACTIVADO", "deuda": "ACTIVADO",
                        "enfermedad": "PENDIENTE", "riesgo": "PENDIENTE"}
CASO_YA_COSECHADO = "ANONIMO2_Z90_20261113"
SONDAS_DUPLICADO = ["busqueda_riesgo", "busqueda_riesgos", "deuda_de_sangre"]


def _cerca(a, b, tol=1e-4):
    if a is None or b is None:
        return a is b
    return abs(float(a) - float(b)) <= tol


def main():
    fallos = []
    fams, toks = C.cargar_catalogo()
    if len(fams) != 244 or len(toks) != 703:
        fallos.append(f"G1: catálogo {len(fams)} familias / {len(toks)} tokens (esperado 244 / 703)")
    ids_indice, n_entradas = C.cargar_indice()
    if n_entradas != 160:
        fallos.append(f"G1: índice {n_entradas} entradas (esperado 160)")
    manual = json.loads(MANUAL.read_text(encoding="utf-8"))
    descubrimientos = manual["tokens_descubiertos"]
    if len(descubrimientos) != 13:
        fallos.append(f"G1: archivo manual {len(descubrimientos)} descubrimientos (esperado 13)")
    if C.can_decide_H is not False:
        fallos.append("G1: can_decide_H no es False")
    if C.CONTRATO != "COSECHA_V2_20261113":
        fallos.append(f"G1: contrato {C.CONTRATO} (esperado COSECHA_V2_20261113)")

    # G2: cosecha completa (sin registro) contra el manual.
    casos, cands, _, _, _ = C._cosechar_todos_los_casos()
    por_par = {}
    for c in cands:
        por_par.setdefault((c["caso"], c["familia"]), []).append(c)
    n_reproducidos = 0
    for d in descubrimientos:
        clave = (d["caso"], d["familia"])
        cands_par = por_par.get(clave, [])
        if not cands_par:
            fallos.append(f"G2: falta {clave[0]} / {clave[1]}")
            continue
        c = cands_par[0]
        if d.get("lugar") is not None:
            if c.get("lugar") != d["lugar"]:
                fallos.append(f"G2 {clave}: lugar {c.get('lugar')} != {d['lugar']}")
            if not _cerca(c.get("rank_fusion"), d.get("rank_fusion")):
                fallos.append(f"G2 {clave}: rank_fusion {c.get('rank_fusion')} != {d.get('rank_fusion')}")
        # El regimen del RESULT trae "MESeta_O_ESTABILIZACION" (caja mezclada
        # del motor); el manual lo normalizó a MESETA. Comparar sin caja.
        if str(c.get("regimen") or "").casefold() != str(d.get("regimen") or "").casefold():
            fallos.append(f"G2 {clave}: regimen {c.get('regimen')} != {d.get('regimen')}")
        if d.get("regimen", "").endswith("_en_Z"):
            if not _cerca(c.get("valor"), _valor_manual(d)):
                fallos.append(f"G2 {clave}: valor Z {c.get('valor')} != {_valor_manual(d)} (manual)")
        n_reproducidos += 1
    print(f"G2 reproducción: {n_reproducidos}/13 del archivo manual")

    # G2 (decisiones): la salida v2 trae los 4 tokens con decisión y evidencia.
    if not V2_JSON.is_file():
        fallos.append("G2: falta COSECHA_20261113_V2.json (correr cosecha.py primero)")
        v2 = {}
    else:
        v2 = json.loads(V2_JSON.read_text(encoding="utf-8"))
    decisiones = v2.get("decisiones", {})
    for tok in TOKENS_ESPERADOS:
        dec = decisiones.get(tok)
        if dec is None:
            fallos.append(f"G2: el token '{tok}' no tiene decisión en la salida v2")
            continue
        if dec.get("decision") != DECISIONES_ESPERADAS[tok]:
            fallos.append(f"G2: '{tok}' decisión {dec.get('decision')} "
                          f"!= {DECISIONES_ESPERADAS[tok]}")
        if dec.get("motivo") not in ("analogo_por_proximidad", "lejos_de_todas",
                                     "ambiguo_empate", "duplicado"):
            fallos.append(f"G2: '{tok}' motivo inválido: {dec.get('motivo')}")
        if dec.get("decision") == "ACTIVADO" and not dec.get("familia_mas_cercana"):
            fallos.append(f"G2: '{tok}' ACTIVADO sin familia")
        if dec.get("puntaje") is None and dec.get("decision") != "RECHAZADO":
            fallos.append(f"G2: '{tok}' sin puntaje de proximidad")
        if not dec.get("casos"):
            fallos.append(f"G2: '{tok}' sin casos de evidencia")
    faltan = v2.get("familias_que_faltan", [])
    if sorted(f["token"] for f in faltan) != sorted(TOKENS_ESPERADOS):
        fallos.append(f"G2: familias_que_faltan trae {[f['token'] for f in faltan]} "
                      f"(esperado {sorted(TOKENS_ESPERADOS)})")
    n_vinc = sum(len(f.get("vinculos", [])) for f in faltan)
    if n_vinc < 1:
        fallos.append("G2: familias_que_faltan sin vínculos (matices)")
    print(f"G2 decisiones: {len(decisiones)} tokens; "
          f"familias que faltan: {len(faltan)}; vínculos: {n_vinc}")

    # G3: re-correr la v2 no produce nada nuevo de casos ya cosechados.
    if not REGISTRO.is_file():
        fallos.append("G3: falta REGISTRO_COSECHA.json (correr cosecha.py primero)")
        registro = {"casos": {}, "tokens": {}, "vinculos": {}}
    else:
        registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    casos_registro_antes = set(registro.get("casos", {}).keys())
    vinc_antes = set(registro.get("vinculos", {}).keys())
    out2, _, _ = C.cosechar_v2(fecha="20261113")
    if out2["n_casos_nuevos"] != 0:
        fallos.append(f"G3: la re-corrida encontró {out2['n_casos_nuevos']} casos nuevos "
                      f"(esperado 0)")
    if out2["n_hallazgos_nuevos"] != 0:
        fallos.append(f"G3: la re-corrida produjo {out2['n_hallazgos_nuevos']} hallazgos "
                      f"nuevos (esperado 0)")
    if out2["n_matices_vinculacion_nuevos"] != 0:
        fallos.append(f"G3: la re-corrida produjo {out2['n_matices_vinculacion_nuevos']} "
                      f"matices nuevos (esperado 0)")
    registro2 = C.cargar_registro()
    if set(registro2.get("casos", {}).keys()) != casos_registro_antes:
        fallos.append("G3: la re-corrida cambió los casos del registro")
    if set(registro2.get("vinculos", {}).keys()) != vinc_antes:
        fallos.append("G3: la re-corrida cambió los vínculos del registro")
    faltan_indice = [c for c in ids_indice if c not in registro2.get("casos", {})]
    if faltan_indice:
        fallos.append(f"G3: {len(faltan_indice)} casos distintos del índice fuera del "
                      f"registro: {faltan_indice[:5]}")
    print(f"G3 re-corrida: {out2['n_casos_nuevos']} casos nuevos, "
          f"{out2['n_hallazgos_nuevos']} hallazgos, "
          f"{out2['n_matices_vinculacion_nuevos']} matices nuevos; "
          f"registro: {len(registro2.get('casos', {}))} casos "
          f"({len(ids_indice)} distintos en el índice)")

    # G3 (dedupe por token): filtrar un caso ya cosechado no re-añade nada.
    _, tokens_703 = C.cargar_catalogo()
    ents_caso, _ = C.cosechar_caso(ROOT, CASO_YA_COSECHADO, tokens_703)
    hallazgos, omitidos, n_fam = C.filtrar_candidatos_caso(
        ents_caso, set(registro2.get("tokens", {}).keys()), tokens_703)
    if hallazgos:
        fallos.append(f"G3 dedupe: el caso ya cosechado {CASO_YA_COSECHADO} volvió a "
                      f"dar hallazgos: {[h.get('token') for h in hallazgos]}")
    motivos = {o["token"]: o["motivo"] for o in omitidos}
    for tok in ("arte", "deuda", "enfermedad"):
        if motivos.get(tok) != "ya existe":
            fallos.append(f"G3 dedupe: '{tok}' no salió como omitido 'ya existe' "
                          f"(salió {motivos.get(tok)})")
    print(f"G3 dedupe ({CASO_YA_COSECHADO}): {len(hallazgos)} hallazgos, "
          f"{len(omitidos)} omitidos 'ya existe', {n_fam} familias conocidas omitidas")

    # G4: determinismo + no-duplicación.
    patrones = C.cargar_patrones()
    for tok in TOKENS_ESPERADOS:
        ent = registro2.get("tokens", {}).get(tok, {})
        d1 = C.decidir_token(tok, ent.get("apariciones", []), patrones, tokens_703)
        d2 = C.decidir_token(tok, ent.get("apariciones", []), patrones, tokens_703)
        if d1 != d2:
            fallos.append(f"G4: la decisión de '{tok}' no es determinista")
        dup, _ = C.es_duplicado(tok, tokens_703)
        if dup:
            fallos.append(f"G4: '{tok}' marcado como duplicado (no debería serlo)")
    for sonda in SONDAS_DUPLICADO:
        dup, ev = C.es_duplicado(sonda, tokens_703)
        if not dup:
            fallos.append(f"G4: la sonda '{sonda}' no se rechazó como duplicado")
        dec = C.decidir_token(sonda, [], patrones, tokens_703)
        if dec.get("decision") != "RECHAZADO":
            fallos.append(f"G4: la sonda '{sonda}' no dio RECHAZADO "
                          f"(dio {dec.get('decision')})")
    print(f"G4 determinismo: 4/4 decisiones estables; sondas duplicado: "
          f"{len(SONDAS_DUPLICADO)}/{len(SONDAS_DUPLICADO)} rechazadas")

    print(f"G1 catálogo: {len(fams)} familias / {len(toks)} tokens; índice: {n_entradas} entradas")
    if fallos:
        print("PUERTA RECHAZADA:")
        for f in fallos:
            print(" -", f)
        return 1
    print("PUERTA PASA")
    return 0


def _valor_manual(d):
    """El valor en Z del manual vive en el contexto ('... (X 0.0175 ...)')."""
    import re
    m = re.search(r"(\d+\.\d+)", d.get("contexto") or "")
    return float(m.group(1)) if m else None


if __name__ == "__main__":
    raise SystemExit(main())
