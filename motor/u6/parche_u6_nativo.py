#!/usr/bin/env python3
"""U6 #3 (desempate del cuello por evidencia) + A7 (alias) sobre motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py y la llamada en UNICO."""
from pathlib import Path
M = Path(__file__).resolve().parent.parent / "motor"
def patch(path, pairs):
    s = path.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, s.count(old), old[:100]); s = s.replace(old, new)
    path.write_text(s, encoding="utf-8"); print("OK", path.name)

patch(M / "MOTOR_V15_3_NATIVO_V0_9_UNICO.py", [
("import hashlib\n", "import hashlib\nimport os  # U6\n"),
('''    "plugin_embudo_clinico.py",
    "plugin_pregunta_detras.py",
    "plugin_metodo_rigor.py",
    "plugin_arquetipos_dinamicos.py",''',
'''    "plugin_embudo_clinico.py",
    "plugin_pregunta_detras_v2.py",  # U6 A7: alias (MAPA_NOMBRES) de plugin_pregunta_detras.py, que no existe
    "plugin_metodo_rigor.py",
    "plugin_arquetipos_dinamicos.py",'''),
('''    "plugin_aquiles_h.py",
    "plugin_wroas.py",
''', '''    "plugin_aquiles_h.py",
    # U6 A7: "plugin_wroas.py" quitado de la lista OFF: el archivo no existe en ningún pack y nadie lo carga (referencia muerta).
'''),
('''    "plugin_embudo_clinico.py",
    "plugin_pregunta_detras.py",
    "plugin_metodo_rigor.py",
)''', '''    "plugin_embudo_clinico.py",
    "plugin_pregunta_detras_v2.py",  # U6 A7: alias
    "plugin_metodo_rigor.py",
)'''),
('''                "file": "MOTOR_V15_3_NATIVO.py",''', '''                "file": "MOTOR_V15_3_NATIVO_V0_9_UNICO.py",  # U6 A7: antes nombraba MOTOR_V15_3_NATIVO.py (inexistente)'''),
('''                "luego por peso descendente; a igual peso decide la posición en el input (la primera gana); se pasan en su orden original. "''',
'''                "luego por peso descendente; a igual peso (U6) decide la EVIDENCIA observada hasta ese corte: 1) frecuencia en cortes previos, "
                "2) racha de presencia inmediatamente anterior (recencia), 3) apoyo en otros ejes del mismo corte; solo si todo empata decide la posición. "
                "No usa cortes posteriores (sin mirar el futuro). Se pasan en su orden original. "'''),
('''def cuello_top_k(cid: str, eje: str, rows: Eje, canonical: set, k: int = CUELLO_K):
    rows = list(rows)
    if len(rows) <= k:
        return rows, None
    orden = sorted(range(len(rows)), key=lambda i: (0 if rows[i][0] in canonical else 1, -float(rows[i][1]), i))''',
'''def _evidencia_desempate_u6(token: str, eje: str, previos, corte_actual) -> Tuple[int, int, int]:
    """U6: evidencia real y determinista para desempatar a igual peso. Solo cortes ANTERIORES y el corte actual."""
    def toks(c):
        return {str(r[0] if isinstance(r, (list, tuple)) else r) for e in ("P", "A", "C") for r in (c.get(e) or [])}
    pres = [token in toks(c) for c in (previos or [])]
    frecuencia = sum(pres)
    racha = 0
    for p in reversed(pres):
        if not p: break
        racha += 1
    apoyo = 0
    if corte_actual:
        apoyo = sum(1 for e in ("P", "A", "C") if e != eje and any(str(r[0] if isinstance(r, (list, tuple)) else r) == token for r in (corte_actual.get(e) or [])))
    return frecuencia, racha, apoyo


def cuello_top_k(cid: str, eje: str, rows: Eje, canonical: set, k: int = CUELLO_K, previos=None, corte_actual=None):
    rows = list(rows)
    if len(rows) <= k:
        return rows, None
    _pos = os.environ.get("U6_DESEMPATE_CUELLO", "evidencia").strip().lower() == "posicion"
    ev = {i: ((0, 0, 0) if _pos else _evidencia_desempate_u6(str(rows[i][0]), eje, previos, corte_actual)) for i in range(len(rows))}
    orden = sorted(range(len(rows)), key=lambda i: (0 if rows[i][0] in canonical else 1, -float(rows[i][1]), -ev[i][0], -ev[i][1], -ev[i][2], i))
    # registro de cómo se resolvió cada empate en el borde (entra vs queda fuera con el mismo peso)
    _wk = float(rows[orden[k - 1]][1]); _borde = [i for i in orden if float(rows[i][1]) == _wk and rows[i][0] in canonical]
    _dentro = [i for i in _borde if i in orden[:k]]; _fuera = [i for i in _borde if i not in orden[:k]]
    _decision = []
    for a in _dentro:
        for b in _fuera:
            crit = next((n for n, x, y in zip(("frecuencia_previa", "racha_previa", "apoyo_otros_ejes"), ev[a], ev[b]) if x != y), "posicion")
            _decision.append(crit)'''),
('''        "empates_en_el_borde": sum(1 for i in fuera if float(rows[i][1]) == wk and rows[i][0] in canonical),''',
'''        "empates_en_el_borde": sum(1 for i in fuera if float(rows[i][1]) == wk and rows[i][0] in canonical),
        "desempate_U6": {"regla": "posicion (legado, U6_DESEMPATE_CUELLO=posicion)" if _pos else "peso > frecuencia_previa > racha_previa > apoyo_otros_ejes > posicion",
                         "pares_borde": len(_decision), "decididos_por": {c: _decision.count(c) for c in sorted(set(_decision))},
                         "evidencia": {str(rows[i][0]): list(ev[i]) for i in _borde}},'''),
('''    for raw in cuts:
        cid = raw["id"]
        P, A, C = raw.get("P") or [], raw.get("A") or [], raw.get("C") or []
        holes_all[cid] = validar_corte(cid, P, A, C, canonical)
        P5, lgP = cuello_top_k(cid, "P", P, canonical)
        A5, lgA = cuello_top_k(cid, "A", A, canonical)
        C5, lgC = cuello_top_k(cid, "C", C, canonical)''',
'''    for _iu6, raw in enumerate(cuts):
        cid = raw["id"]
        P, A, C = raw.get("P") or [], raw.get("A") or [], raw.get("C") or []
        holes_all[cid] = validar_corte(cid, P, A, C, canonical)
        _prev_u6 = list(cuts[:_iu6])
        P5, lgP = cuello_top_k(cid, "P", P, canonical, previos=_prev_u6, corte_actual=raw)
        A5, lgA = cuello_top_k(cid, "A", A, canonical, previos=_prev_u6, corte_actual=raw)
        C5, lgC = cuello_top_k(cid, "C", C, canonical, previos=_prev_u6, corte_actual=raw)'''),
])
patch(M / "MOTOR_V15_3_UNICO_20260927.py", [
('''        _cu4=(lambda cid,e,rows: native.cuello_top_k(cid,e,rows,_canon_u4)[0]) if _canon_u4 is not None else (lambda cid,e,rows: rows)
        try:
            for c, raw in zip(motor.get("cuts") or [], case["cuts"]):
                c["P_FULL_244"]=native._board(eng_emit, ep, c["corte"]+"_P_EMIT", _cu4(c["corte"],"P",raw.get("P") or []))
                c["A_FULL_244"]=native._board(eng_emit, ea, c["corte"]+"_A_EMIT", _cu4(c["corte"],"A",raw.get("A") or []))
                c["C_FULL_244"]=native._board(eng_emit, ec, c["corte"]+"_C_EMIT", _cu4(c["corte"],"C",raw.get("C") or []))''',
'''        # U6 #3: mismo desempate por evidencia que el núcleo nativo (cortes previos + corte actual; nunca posteriores).
        _cu4=(lambda cid,e,rows,prev=None,cur=None: native.cuello_top_k(cid,e,rows,_canon_u4,previos=prev,corte_actual=cur)[0]) if _canon_u4 is not None else (lambda cid,e,rows,prev=None,cur=None: rows)
        try:
            for _iu6,(c, raw) in enumerate(zip(motor.get("cuts") or [], case["cuts"])):
                _pv6=case["cuts"][:_iu6]
                c["P_FULL_244"]=native._board(eng_emit, ep, c["corte"]+"_P_EMIT", _cu4(c["corte"],"P",raw.get("P") or [],_pv6,raw))
                c["A_FULL_244"]=native._board(eng_emit, ea, c["corte"]+"_A_EMIT", _cu4(c["corte"],"A",raw.get("A") or [],_pv6,raw))
                c["C_FULL_244"]=native._board(eng_emit, ec, c["corte"]+"_C_EMIT", _cu4(c["corte"],"C",raw.get("C") or [],_pv6,raw))'''),
])
