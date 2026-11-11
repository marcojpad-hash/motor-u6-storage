V15.1 — PLUGINS Y READMES — PAQUETE EN UN SOLO TXT
========================================================================

CONTENIDO: 14 plugins + 13 documentos/README.
Cada sección conserva el contenido del archivo fuente y está delimitada por su nombre.


########################################################################
# PLUGINS
########################################################################


========================================================================
ARCHIVO: traza_campo_244.py
========================================================================

#!/usr/bin/env python3
"""TRAZA_CAMPO_244

Toda hipótesis, todo corte, todo Δ. Nada se apaga.
Umbral no es interruptor: es nota opcional.

Δ_i(t) = P_i(t) − P_i(t−1)

Interrelación (posibilidad, no identidad):
  s_ij = corr(serie Δ_i, serie Δ_j)   si hay ≥2 vectores
  o, en un solo tramo, mismo signo de Δ.

No se cuelga de H. No toca Engine_V5.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, Tuple


def _rank(board: Dict[str, float]) -> Dict[str, int]:
    orden = sorted(board, key=lambda k: -board[k])
    return {k: i + 1 for i, k in enumerate(orden)}


def _corr(a: Sequence[float], b: Sequence[float]):
    n = len(a)
    if n < 2:
        return None
    ma = sum(a) / n
    mb = sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 1e-18 or vb <= 1e-18:
        return 0.0
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return cov / math.sqrt(va * vb)


def analizar(
    cortes: Sequence[Tuple[str, Dict[str, float]]],
    nota_umbral: float | None = None,
) -> Dict[str, Any]:
    ids = [c[0] for c in cortes]
    boards = [c[1] for c in cortes]
    nombres = sorted(set().union(*[b.keys() for b in boards]))

    serie: Dict[str, List[float]] = {n: [] for n in nombres}
    rangos: Dict[str, List[int]] = {n: [] for n in nombres}
    for b in boards:
        rk = _rank(b)
        for n in nombres:
            serie[n].append(round(float(b.get(n, 0.5)), 6))
            rangos[n].append(rk.get(n, len(nombres) + 1))

    # un vector por tramo: TODAS las Δ
    vectores = []
    deltas_por_h: Dict[str, List[float]] = {n: [] for n in nombres}
    for i in range(1, len(boards)):
        a, b = boards[i - 1], boards[i]
        mov = []
        for n in nombres:
            d = float(b.get(n, 0.5)) - float(a.get(n, 0.5))
            deltas_por_h[n].append(d)
            mov.append({
                "h": n,
                "d": round(d, 6),
                "P_de": round(float(a.get(n, 0.5)), 6),
                "P_a": round(float(b.get(n, 0.5)), 6),
                "rango_de": rangos[n][i - 1],
                "rango_a": rangos[n][i],
                "drango": rangos[n][i - 1] - rangos[n][i],
            })
        mov.sort(key=lambda x: -abs(x["d"]))
        vectores.append({
            "vector": f"{ids[i-1]}→{ids[i]}",
            "n": len(mov),
            "movimiento": mov,  # 244
        })

    fichas = []
    for n in nombres:
        vals = serie[n]
        ds = deltas_por_h[n]
        fichas.append({
            "h": n,
            "P": vals,
            "d": [round(x, 6) for x in ds],
            "rangos": rangos[n],
            "neto": round(vals[-1] - vals[0], 6),
        })
    fichas.sort(key=lambda x: -abs(x["neto"]))

    # interrelación: corr de las series Δ (posibilidad)
    pares = []
    if len(boards) >= 3:
        for i, ni in enumerate(nombres):
            di = deltas_por_h[ni]
            if all(abs(x) < 1e-12 for x in di):
                continue
            for nj in nombres[i + 1:]:
                dj = deltas_por_h[nj]
                if all(abs(x) < 1e-12 for x in dj):
                    continue
                c = _corr(di, dj)
                if c is None:
                    continue
                pares.append({"i": ni, "j": nj, "corr_delta": round(c, 4)})
        pares.sort(key=lambda x: -abs(x["corr_delta"]))

    return {
        "modulo": "TRAZA_CAMPO_244",
        "formula": "Δ_i(t)=P_i(t)-P_i(t-1);  r_ij=corr(Δ_i, Δ_j)",
        "cuelga_de_H": False,
        "apaga_luces": False,
        "nota_umbral": nota_umbral,
        "n_hipotesis": len(nombres),
        "cortes": ids,
        "vectores": vectores,
        "fichas": fichas,
        "interrelacion_posible": pares[:80],
        "crudo_P": serie,
    }


if __name__ == "__main__":
    A = {"H1": 0.50, "H2": 0.50, "H3": 0.70}
    B = {"H1": 0.51, "H2": 0.58, "H3": 0.69}
    C = {"H1": 0.73, "H2": 0.66, "H3": 0.68}
    r = analizar([("A", A), ("B", B), ("C", C)])
    assert r["vectores"][0]["n"] == 3
    print("ok", r["interrelacion_posible"])


========================================================================
ARCHIVO: plugin_reporte_3d.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_REPORTE_3D
No toca V5. A partir de una secuencia de tableros 244 arma, por corte:
  H              letrero
  se_movieron    las que más cambiaron vs el corte previo
  no_se_apagaron las que siguen altas aunque no griten
"""
from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple

PISO = 0.62
N_MOV = 3
N_PERSIST = 3


def _top(board: Dict[str, float], n: int = 1) -> List[Tuple[str, float]]:
    return sorted(board.items(), key=lambda x: -x[1])[:n]


def leer(
    seq: Sequence[Tuple[str, Dict[str, float]]],
    piso: float = PISO,
    n_mov: int = N_MOV,
    n_persist: int = N_PERSIST,
) -> Dict[str, Any]:
    cortes = []
    prev = None
    for i, (cid, board) in enumerate(seq):
        H, p = _top(board, 1)[0]
        if prev is None:
            mov = []
        else:
            deltas = []
            keys = set(board) | set(prev)
            for k in keys:
                d = board.get(k, 0.5) - prev.get(k, 0.5)
                deltas.append((k, round(d, 4), round(board.get(k, 0.5), 4)))
            deltas.sort(key=lambda x: -abs(x[1]))
            mov = [{"h": k, "d": d, "p": pv} for k, d, pv in deltas[:n_mov]]
        persist = [
            {"h": k, "p": round(v, 4)}
            for k, v in _top(board, 12)
            if k != H and v >= piso
        ][:n_persist]
        cortes.append({
            "corte": cid,
            "H": H,
            "p": round(p, 4),
            "se_movieron": mov,
            "no_se_apagaron": persist,
        })
        prev = board
    return {"plugin": "PLUGIN_REPORTE_3D", "engine_tocado": False, "cortes": cortes}


if __name__ == "__main__":
    print("ok")


========================================================================
ARCHIVO: plugin_picos_mesetas.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_PICOS_MESETAS

Forma temporal de cada hipótesis. No es el eje (eso es Aquiles).
No entra a Engine_V5. Se corre sobre la secuencia de tableros.

Para cada k:
  serie p_k(t0)...p_k(tn)
  d_t = p_k(t) - p_k(t-1)
  ↗ si d >= eps
  ↘ si d <= -eps
  → si |d| < eps   (meseta de movimiento, no "es el campeón")

Señal de trabajo (no ley):
  un ↗ de k que ocurre ANTES de que k sea Top1.
"""
from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple

EPS = 0.04


def signo(d: float, eps: float = EPS) -> str:
    if d >= eps:
        return "↗"
    if d <= -eps:
        return "↘"
    return "→"


def curvas(
    seq: Sequence[Tuple[str, Dict[str, float]]],
    eps: float = EPS,
    piso: float = 0.62,
) -> Dict[str, Any]:
    if not seq:
        return {"plugin": "PLUGIN_PICOS_MESETAS", "curvas": {}}
    ids = [s[0] for s in seq]
    keys = set()
    for _, b in seq:
        keys.update(b)
    tops = []
    for _, b in seq:
        tops.append(max(b, key=lambda k: b[k]))
    out = {}
    for k in keys:
        serie = [round(b.get(k, 0.5), 4) for _, b in seq]
        if max(serie) < piso:
            continue
        ds = [round(serie[i] - serie[i - 1], 4) for i in range(1, len(serie))]
        forma = "".join(signo(d, eps) for d in ds)
        if set(forma) <= {"→"}:
            continue
        i_top = next((i for i, t in enumerate(tops) if t == k), None)
        subio_antes = False
        if i_top is not None and i_top >= 1:
            subio_antes = any(ds[j] >= eps for j in range(i_top))
        out[k] = {
            "serie": serie,
            "deltas": ds,
            "forma": forma,
            "fue_top1": i_top,
            "subio_antes_de_ser_top1": subio_antes,
        }
    return {
        "plugin": "PLUGIN_PICOS_MESETAS",
        "eps": eps,
        "cortes": ids,
        "top1": tops,
        "curvas": out,
        "eje": "Aquiles / meseta del tema. Esta pieza no lo declara.",
    }


if __name__ == "__main__":
    print("PLUGIN_PICOS_MESETAS listo")


========================================================================
ARCHIVO: plugin_familias_gloria_sacro.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_FAMILIAS_GLORIA_SACRO

No toca Engine_V5 ni reescribe patterns_final_v14.json.
Suma DOS hipótesis al diccionario en memoria / a un JSON de salida.

Candado de tokens:
- tokens_favor/contra SOLO del léxico ya existente en las 244.
- No se plantan fama_hegemonica, evangelizacion, etc.: no dispararían.
- cap conceptual: estas fichas USAN reconocimiento y humildad_religiosa
  como favor; no cancelan las vías contra que ya tenían esas palabras.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Dict

EXTRA = {
    "fama_reputacion_gloria_publica": {
        "description": (
            "El nombre se multiplica en la memoria colectiva. "
            "No es poder de cargo ni logro Schwartz: es que te vean."
        ),
        "tokens_favor": {
            "reconocimiento": 0.8,
            "estatus_social": 0.75,
            "redes_prestigio": 0.7,
            "escalada_status": 0.7,
        },
        "tokens_contra": {
            "humildad": 0.7,
            "olvido": 0.75,
        },
        "evidence_status": "unverified",
        "fuente": "PLUGIN_FAMILIAS_GLORIA_SACRO; no calibrado.",
    },
    "carisma_sacro_vocacion_religiosa": {
        "description": (
            "El sujeto opera como canal de lo sacro (starets, predicador, piedad operativa). "
            "No es kwml_03_mago ni solo tradicion Schwartz."
        ),
        "tokens_favor": {
            "humildad_religiosa": 0.85,
            "humildad": 0.7,
            "piedad": 0.8,
            "devocion": 0.75,
            "desafio_sagrado": 0.65,
        },
        "tokens_contra": {
            "orgullo": 0.8,
        },
        "evidence_status": "unverified",
        "fuente": "PLUGIN_FAMILIAS_GLORIA_SACRO; no calibrado.",
    },
}


def fusionar(patterns: Dict) -> Dict:
    out = copy.deepcopy(patterns)
    for k, v in EXTRA.items():
        if k in out:
            raise ValueError(f"colision con 244: {k}")
        out[k] = v
    return out


def escribir_fusion(
    patterns_path: str,
    dest: str = "patterns_v14_plus_gloria_sacro.json",
) -> str:
    p = json.loads(Path(patterns_path).read_text(encoding="utf-8"))
    q = fusionar(p)
    Path(dest).write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dest


if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "patterns_final_v14.json"
    dest = escribir_fusion(src)
    print("n", len(json.loads(Path(dest).read_text())), "->", dest)


========================================================================
ARCHIVO: plugin_otto_numinoso.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_OTTO_NUMINOSO
Sidecar. No pisa patterns_final_v14.json.

Dos polos (Otto 1917, mysterium tremendum et fascinans).
El JSON de esta carpeta venia en UNA ficha
(otto_01_numinoso_tremendum_fascinans). El wrapper anterior
acorto el nombre a otto_01_...tremendum: recorte de nombre.

Claude 2026-09-07: partir en 01 tremendum + 02 fascinans.
Se pueden encender los dos a la vez.
"""
from __future__ import annotations

from typing import Dict

PARCHE_A_REEMPLAZAR = "carisma_sacro_vocacion_religiosa"

OTTO = {
    "otto_01_numinoso_tremendum": {
        "description": (
            "Otto 1917 polo tremendum: miedo, misterio, "
            "desafio_sagrado. No es el fascinans."
        ),
        "tokens_favor": {
            "desafio_sagrado": 0.85,
            "misterio": 0.80,
            "miedo": 0.78,
        },
        "tokens_contra": {
            "cotidiano": 0.80,
            "orgullo": 0.78,
            "poder": 0.70,
        },
        "evidence_status": "secondary_verified",
        "fuente": "Otto 1917 Das Heilige; polo tremendum.",
    },
    "otto_02_numinoso_fascinans": {
        "description": (
            "Otto 1917 polo fascinans: devocion, piedad, "
            "paz_interior, carisma que atrae. Coexiste con 01."
        ),
        "tokens_favor": {
            "devocion": 0.82,
            "piedad": 0.80,
            "paz_interior": 0.72,
            "carisma": 0.70,
            "sabiduria": 0.65,
            "humildad_religiosa": 0.75,
            "humildad": 0.68,
        },
        "tokens_contra": {
            "orgullo": 0.78,
            "estatus_social": 0.68,
            "poder": 0.70,
        },
        "evidence_status": "secondary_verified",
        "fuente": "Otto 1917 Das Heilige; polo fascinans.",
    },
}


def fusionar(patterns: Dict) -> Dict:
    out = dict(patterns)
    out.pop(PARCHE_A_REEMPLAZAR, None)
    out.pop("otto_01_numinoso_tremendum_fascinans", None)
    out.update(OTTO)
    return out


if __name__ == "__main__":
    import json
    from pathlib import Path
    base = json.loads(Path("patterns_final_v14.json").read_text(encoding="utf-8"))
    lib = fusionar(base)
    assert "otto_01_numinoso_tremendum" in lib
    assert "otto_02_numinoso_fascinans" in lib
    print("ok otto 01+02", "n", len(lib))


========================================================================
ARCHIVO: plugin_trayectoria_hosteleria.py
========================================================================

#!/usr/bin/env python3
"""SIDECAR — trayectoria_hosteleria_turno_sustancias
NO fusionar a patterns_final_v14.json (244 en disco).
Se carga en memoria con sidecar V15.1.

Oficio cocina/barra/sala: turno raro + desgaste + consumo.
Perfil de ventana, no destino.

Fuente primaria (Claude web 2026-09-07):
Bush & Lipari, SAMHSA CBHSQ Report, 16 abril 2015.
Alojamiento y alimentos #1 SUD 16.9% y #1 ilicitas 19.1%
entre 19 industrias. Mineria/construccion lideran binge
alcohol, no SUD general. La cita "3er lugar" estaba invertida.
"""
from __future__ import annotations

FICHA = "trayectoria_hosteleria_turno_sustancias"

PATRON = {
    "description": (
        "Oficio de cocina/barra/sala: turno raro, desgaste, "
        "co-ocurrencia frecuente con consumo. Perfil de ventana, "
        "no prediccion de cierre."
    ),
    "tokens_favor": {
        "consumo_sustancias": 0.8,
        "turno_atipico_nocturno": 0.8,
        "desgaste_psicosocial": 0.7,
        "desgaste_cambaceo_itinerante": 0.55,
        "aislamiento_social": 0.5,
    },
    "tokens_contra": {
        "estabilidad_horario": 0.85,
        "entorno_controlado_oficina": 0.8,
    },
    "fuente": "SAMHSA 2015 (Bush & Lipari, CBHSQ Report, 16 abril 2015): alojamiento y servicios de alimentos = 16.9% SUD, EL MAS ALTO de 19 industrias medidas (no 3o -- corregido tras verificar fuente primaria; mineria/construccion solo lideran en consumo excesivo de alcohol especificamente, no en SUD general).",
    "evidence_status": "secondary_verified",
}


def fusionar(lib: dict) -> dict:
    out = dict(lib)
    out[FICHA] = dict(PATRON)
    return out


========================================================================
ARCHIVO: plugin_arco_field_snyder_mckee.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_ARCO_DRAMATICO
Sid Field + Blake Snyder (Save the Cat) + Robert McKee.

NO son lo mismo. Tres lecturas del MISMO timeline.
NO toca Engine_V5. NO agrega hipótesis a las 244.
VACIO se deja. No se rellena de a huevo.

Field  = dónde se parte el TIEMPO (actos, plot points).
Snyder = qué MOMENTO de catálogo comercial hay cerca.
McKee  = si el VALOR se voltea (carga +/−) hacia crisis/clímax.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

FIELD = [
    ("ACTO_1", "planteamiento / casa"),
    ("PLOT_POINT_1", "ya no hay vuelta fácil"),
    ("PUNTO_MEDIO", "se ve el tipo de cinta"),
    ("PLOT_POINT_2", "segundo golpe"),
    ("ACTO_3", "se paga o se recoge"),
]

SNYDER = [
    ("opening_image", "foto de entrada"),
    ("theme_stated", "de qué va, sin querer"),
    ("setup", "casa"),
    ("catalyst", "el jalón"),
    ("debate", "¿entro o no?"),
    ("break_into_two", "cruza"),
    ("b_story", "otro hilo"),
    ("fun_and_games", "promesa del género"),
    ("midpoint", "falso triunfo o falso fondo"),
    ("bad_guys_close_in", "aprieta"),
    ("all_is_lost", "muerte aparente"),
    ("dark_night", "quieto y feo"),
    ("break_into_three", "se levanta"),
    ("finale", "paga"),
    ("final_image", "foto de salida vs entrada"),
]

MCKEE = [
    ("incidente_incitador", "el valor de la vida se toca por primera vez"),
    ("complicaciones", "el valor se aprieta, no se resuelve"),
    ("crisis", "dilema: dos males o dos bienes, hay que elegir"),
    ("climax", "la elección se ACTÚA y el valor se voltea"),
    ("resolucion", "el mundo nuevo, más chico que el clímax"),
]


def _dmax(cut: Dict[str, Any]) -> float:
    if cut.get("delta_max") is not None:
        return abs(float(cut["delta_max"]))
    if cut.get("d_max") is not None:
        return abs(float(cut["d_max"]))
    movers = cut.get("movers") or []
    if movers:
        return max(abs(float(x.get("d", 0))) for x in movers)
    return 0.0


def _carga(cut: Dict[str, Any]) -> Optional[str]:
    """McKee: + o − si el caller lo manda; si no, se infiere del signo de delta_neto."""
    if cut.get("carga") in ("+", "-", "0"):
        return cut["carga"]
    neto = cut.get("delta_neto")
    if neto is None:
        return None
    if neto > 0:
        return "+"
    if neto < 0:
        return "-"
    return "0"


def _nota(cut: Dict[str, Any], umbral: float) -> bool:
    return _dmax(cut) >= umbral


def _pick(cortes: Sequence[Dict[str, Any]], frac: float) -> Dict[str, Any]:
    n = len(cortes)
    j = min(n - 1, max(0, round(frac * (n - 1))))
    return cortes[j]


def leer(
    cortes: Sequence[Dict[str, Any]],
    umbral: float = 0.04,
) -> Dict[str, Any]:
    n = len(cortes)
    if n == 0:
        return {"plugin": "PLUGIN_ARCO_DRAMATICO", "error": "sin cortes"}

    # Field por posición
    if n == 1:
        f_idx = [(0, "ACTO_1")]
    elif n == 2:
        f_idx = [(0, "ACTO_1"), (1, "ACTO_3")]
    elif n == 3:
        f_idx = [(0, "ACTO_1"), (1, "PUNTO_MEDIO"), (2, "ACTO_3")]
    else:
        f_idx = [
            (0, "ACTO_1"),
            (max(1, n // 4), "PLOT_POINT_1"),
            (n // 2, "PUNTO_MEDIO"),
            (min(n - 2, (3 * n) // 4), "PLOT_POINT_2"),
            (n - 1, "ACTO_3"),
        ]
    glosa_f = {a: b for a, b in FIELD}
    field = []
    for i, nombre in f_idx:
        cut = cortes[i]
        field.append({
            "beat": nombre,
            "glosa": glosa_f.get(nombre, ""),
            "corte": cut.get("id"),
            "se_nota": _nota(cut, umbral),
            "carga": _carga(cut),
            "forzado": False,
        })

    snyder = []
    for i, (bid, glosa) in enumerate(SNYDER):
        cut = _pick(cortes, i / max(1, len(SNYDER) - 1))
        snyder.append({
            "beat": bid,
            "glosa": glosa,
            "corte_cerca": cut.get("id"),
            "estado": "SE_NOTA" if _nota(cut, umbral) else "VACIO",
            "forzado": False,
        })

    # McKee: 5 hitos + volteos de carga entre cortes consecutivos
    m_frac = [0.0, 0.3, 0.55, 0.8, 1.0]
    mckee = []
    for frac, (bid, glosa) in zip(m_frac, MCKEE):
        cut = _pick(cortes, frac)
        mckee.append({
            "beat": bid,
            "glosa": glosa,
            "corte": cut.get("id"),
            "se_nota": _nota(cut, umbral),
            "carga": _carga(cut),
            "forzado": False,
        })
    volteos = []
    for i in range(1, n):
        a, b = _carga(cortes[i - 1]), _carga(cortes[i])
        if a and b and a != b and a != "0" and b != "0":
            volteos.append({
                "de": cortes[i - 1].get("id"),
                "a": cortes[i].get("id"),
                "carga": f"{a}→{b}",
            })

    return {
        "plugin": "PLUGIN_ARCO_DRAMATICO",
        "engine_tocado": False,
        "nuevas_hipotesis_244": 0,
        "regla": "Tres lecturas. VACIO se deja. No encajar de a huevo.",
        "para_que": (
            "Ver si la trazabilidad de una vida/época SE NOTA como cinta "
            "(Field), como catálogo de momentos (Snyder) o como volteo de valor "
            "(McKee). Hueco = dato. No es predecir el iPhone."
        ),
        "matices": {
            "Field": "arquitectura del tiempo",
            "Snyder": "momentos de taller comercial",
            "McKee": "carga de valor que se voltea",
        },
        "field": field,
        "snyder": snyder,
        "mckee": mckee,
        "mckee_volteos": volteos,
        "n_snyder_vacios": sum(1 for x in snyder if x["estado"] == "VACIO"),
        "n_field_sin_nota": sum(1 for x in field if not x["se_nota"]),
    }


if __name__ == "__main__":
    import json
    demo = [
        {"id": "A", "delta_max": 0.02, "delta_neto": 0.01},
        {"id": "B", "delta_max": 0.12, "delta_neto": 0.10},
        {"id": "C", "delta_max": 0.08, "delta_neto": -0.06},
        {"id": "D", "delta_max": 0.03, "delta_neto": -0.02},
        {"id": "E", "delta_max": 0.11, "delta_neto": 0.09},
    ]
    print(json.dumps(leer(demo), ensure_ascii=False, indent=2))


========================================================================
ARCHIVO: plugin_sesgo_lectura.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_SESGO_LECTURA v2

Repetir tokens NO es sesgo. Los universales se escriben con las
mismas palabras (hambre, caída, grupo). Eso es el cliché / arquetipo.

Lo que se mide:
  C  = solape de tokens (diccionario estable o no)
  N  = tokens NUEVOS en t+1 (color de ESTA vida)
  K  = tokens que se fueron
  P  = el letrero #1 se quedó

Vector de diferenciación D = N ∪ K
  Si P y D no vacío: el universal se quedó CON otra carne.
  Si P y D vacío: misma frase otra vez. No condena; avisa "poca carne nueva".
  Si no P: cambió el letrero.

No hay etiqueta 'sesgo' automática.
Hay: universal_con_color | universal_sin_color_nueva | cambio_de_letrero
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Set


def _toks(cut: Dict[str, Any]) -> Set[str]:
    raw = cut.get("tokens") or cut.get("markers") or []
    out = set()
    for x in raw:
        if isinstance(x, str):
            out.add(x)
        elif isinstance(x, dict):
            t = x.get("token") or x.get("name")
            if t:
                out.add(str(t))
        elif isinstance(x, (list, tuple)) and x:
            out.add(str(x[0]))
    return out


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def leer(cortes: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    filas = []
    for i in range(len(cortes) - 1):
        a, b = cortes[i], cortes[i + 1]
        ta, tb = _toks(a), _toks(b)
        nuevos = sorted(tb - ta)
        idos = sorted(ta - tb)
        C = round(jaccard(ta, tb), 4)
        Ha, Hb = a.get("H"), b.get("H")
        P = Ha is not None and Ha == Hb
        if not P:
            tag = "cambio_de_letrero"
        elif nuevos or idos:
            tag = "universal_con_color"
        else:
            tag = "universal_sin_color_nueva"
        filas.append({
            "de": a.get("id"),
            "a": b.get("id"),
            "H_de": Ha,
            "H_a": Hb,
            "C_solape": C,
            "tokens_nuevos": nuevos,
            "tokens_idos": idos,
            "D_diferenciacion": sorted(set(nuevos) | set(idos)),
            "letrero_igual": P,
            "etiqueta": tag,
        })
    return {
        "plugin": "PLUGIN_SESGO_LECTURA",
        "version": 2,
        "engine_tocado": False,
        "regla": (
            "Mismas palabras no equivalen a sesgo. "
            "Sesgo solo se SOSPECHA si el letrero se queda y D está vacío "
            "(cero carne nueva). Aun así no se anula el hallazgo."
        ),
        "con_aquiles": (
            "Aquiles + universal_con_color = rumbo con instancia. "
            "Aquiles + universal_sin_color_nueva = rumbo, pero esta vida "
            "no aportó pigmento: no lo vendas como caso nuevo."
        ),
        "transiciones": filas,
    }


if __name__ == "__main__":
    import json
    demo = [
        {"id": "A", "H": "30_ambicion", "tokens": ["ambicion", "aprendizaje"]},
        {"id": "B", "H": "30_ambicion", "tokens": ["ambicion", "poder", "liderazgo"]},
        {"id": "C", "H": "30_ambicion", "tokens": ["ambicion", "poder", "liderazgo"]},
        {"id": "D", "H": "6_desastre", "tokens": ["desastre", "caida"]},
    ]
    print(json.dumps(leer(demo), ensure_ascii=False, indent=2))


========================================================================
ARCHIVO: plugin_aquiles_h.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_AQUILES_H — capa plugin. NO modifica Engine_V5.

Busca N_min: el menor n donde p_H ya no se voltea
si sigues remuestreando LA MISMA foto.

No hay N oficial (400, 3200, un millón). Eso es sesgo.
Hay un fusible de recursos (N_FUSIBLE). Si lo tocas,
no encontraste N_min: reportas NO_ENCONTRADO, no “N=fusible”.

estado_H: PARA_DE_EMPUJAR_H | SEGUIR_EMPUJANDO_H | NO_ENCONTRADO_FUSIBLE
estado_traza: ABIERTA siempre — el eje quieto no cierra AB/BC.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Callable, Dict, List, Sequence

EPS_2PT = 0.02
M_VENTANAS = 3
# I = intensidad residual de la foto (masa que no es ruido puro).
# Si la replica no manda I, se usa I_FLOOR. Nunca 0: un tablero
# vacio no cuenta como "H ya es H". No es p_azar (eso es MC1).
I_FLOOR = 0.02
N0 = 32
FACTOR = 2
N_FUSIBLE = 8192


def _overlap(a: Sequence[str], b: Sequence[str]) -> float:
    if not a and not b:
        return 1.0
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(len(sa), len(sb))


def evaluar_serie(
    puntos: List[Dict[str, Any]],
    eps_p: float = EPS_2PT,
    m: int = M_VENTANAS,
) -> Dict[str, Any]:
    if len(puntos) < 2:
        return {
            "estado_H": "SEGUIR_EMPUJANDO_H",
            "estado": "SEGUIR_EMPUJANDO_H",
            "estado_traza": "ABIERTA",
            "N_min": None,
            "plugin": "PLUGIN_AQUILES_H",
        }

    estables = 0
    n_min = None
    hist = []
    for i in range(1, len(puntos)):
        a, b = puntos[i - 1], puntos[i]
        p1, p2 = a.get("p_H"), b.get("p_H")
        d = None if (p1 is None or p2 is None) else abs(p2 - p1)
        I = b.get("I") if b.get("I") is not None else I_FLOOR
        h_quieta = d is not None and d <= eps_p and I >= I_FLOOR
        hist.append({
            "n": b.get("n"),
            "delta_H": None if d is None else round(d, 4),
            "H_quieta": h_quieta,
            "viento": {
                "winner_modal": b.get("winner"),
                "winner_cambio": a.get("winner") != b.get("winner"),
                "overlap_topk": round(_overlap(a.get("topk") or [], b.get("topk") or []), 4),
            },
            "I": I,
        })
        if h_quieta:
            estables += 1
            if estables >= m and n_min is None:
                n_min = b.get("n")
        else:
            estables = 0

    if n_min is not None:
        estado_H = "PARA_DE_EMPUJAR_H"
    else:
        estado_H = "SEGUIR_EMPUJANDO_H"

    return {
        "estado": estado_H,
        "estado_H": estado_H,
        "estado_traza": "ABIERTA",
        "N_min": n_min,
        "N_estable": n_min,
        "eps_p": eps_p,
        "m_ventanas": m,
        "bloques": hist,
        "regla": (
            "N_min = menor n donde p_H aguantó m ventanas seguidas. "
            "No es un tope elegido. Letrero modal no frena. Traza ABIERTA."
        ),
        "plugin": "PLUGIN_AQUILES_H",
        "engine_tocado": False,
    }


def _ns_crecimiento(n0: int = N0, factor: int = FACTOR, fusible: int = N_FUSIBLE):
    n = n0
    while n <= fusible:
        yield n
        n = n * factor


def bootstrap_hasta_parar(
    replicar: Callable[[], Dict[str, Any]],
    bloques: Sequence[int] | None = None,
    eps_p: float = EPS_2PT,
    m: int = M_VENTANAS,
    k: int = 5,
    seed: int = 12345,
    n0: int = N0,
    fusible: int = N_FUSIBLE,
) -> Dict[str, Any]:
    grid = list(bloques) if bloques else list(_ns_crecimiento(n0=n0, fusible=fusible))
    pool: List[Dict[str, Any]] = []
    puntos: List[Dict[str, Any]] = []
    for n in grid:
        if n < n0:
            continue
        if n > fusible:
            break
        while len(pool) < n:
            pool.append(replicar())
        slice_n = pool[:n]
        ps = [x["p_H"] for x in slice_n if x.get("p_H") is not None]
        winners = [x.get("winner") for x in slice_n]
        winner = Counter(winners).most_common(1)[0][0] if winners else None
        names = []
        for x in slice_n:
            names.extend(x.get("topk") or [])
        topk = [nm for nm, _ in Counter(names).most_common(k)]
        p_mean = sum(ps) / len(ps) if ps else None
        I_vals = [x.get("I") for x in slice_n if x.get("I") is not None]
        I = max(I_FLOOR, sum(I_vals) / len(I_vals)) if I_vals else I_FLOOR
        puntos.append({"n": n, "p_H": p_mean, "winner": winner, "topk": topk, "I": I})
        ver = evaluar_serie(puntos, eps_p=eps_p, m=m)
        if ver["estado_H"] == "PARA_DE_EMPUJAR_H":
            ver["puntos"] = puntos
            ver["n_replicas_usadas"] = n
            ver["fusible"] = fusible
            ver["toque_fusible"] = False
            ver["seed"] = seed
            return ver

    ver = evaluar_serie(puntos, eps_p=eps_p, m=m)
    toque = (puntos[-1]["n"] >= fusible) if puntos else False
    if toque and ver["N_min"] is None:
        ver["estado_H"] = "NO_ENCONTRADO_FUSIBLE"
        ver["estado"] = "NO_ENCONTRADO_FUSIBLE"
    ver["puntos"] = puntos
    ver["n_replicas_usadas"] = puntos[-1]["n"] if puntos else 0
    ver["fusible"] = fusible
    ver["toque_fusible"] = toque
    ver["seed"] = seed
    return ver


if __name__ == "__main__":
    import json
    pts = [
        {"n": 32, "p_H": 0.64, "winner": "9_audaz_empresa", "topk": ["9_audaz_empresa", "30_ambicion"], "I": 0.03},
        {"n": 64, "p_H": 0.669, "winner": "9_audaz_empresa", "topk": ["9_audaz_empresa", "30_ambicion"], "I": 0.03},
        {"n": 128, "p_H": 0.670, "winner": "30_ambicion", "topk": ["30_ambicion", "9_audaz_empresa"], "I": 0.03},
        {"n": 256, "p_H": 0.671, "winner": "9_audaz_empresa", "topk": ["9_audaz_empresa", "30_ambicion"], "I": 0.03},
    ]
    print(json.dumps(evaluar_serie(pts), ensure_ascii=False, indent=2))


========================================================================
ARCHIVO: plugin_pregunta_detras.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_PREGUNTA_DETRAS — decimo hombre de la PREGUNTA.
No toca F ni p. No autorizar fusion.

El problema nunca es el problema. El problema es el falso problema:
la pregunta que el mapper/LLM va a responder si nadie la para.

Uso (humano o wrapper):
  from plugin_pregunta_detras import interrogar
  interrogar("que va a pasar con este cocinero")
"""
from __future__ import annotations

# pregunta de superficie -> default que el sistema suelta -> pregunta real
TRAMPAS = [
    (("quien es", "quién es"), "apellido / aristos", "que ↗ que no es el eje, en que ventana"),
    (("que va a pasar", "qué va a pasar", "que le va a pasar"), "desenlace dossier", "que se falsearia en el siguiente corte"),
    (("es adicto", "se muere", "se va a morir", "va a morir"), "DSM de biografia", "en QUE ventana hay evidencia clinica"),
    (("es ambicioso", "ambicion", "ambición"), "30_ambicion", "conquista sobre otros o agencia sobre si"),
    (("por que famoso", "por qué famoso", "es famoso"), "fama como causa", "fama es eje o laterales"),
    (("que ficha falta", "qué ficha falta"), "inventar 247", "que token FRIO no pegue"),
    (("el motor fallo", "el motor falló"), "culpa F", "el mapper pego el token caliente"),
]


def interrogar(pregunta_superficie: str) -> dict:
    p = (pregunta_superficie or "").lower()
    golpe = None
    for agujas, falso, real in TRAMPAS:
        if any(a in p for a in agujas):
            golpe = {"trampa": agujas[0], "falso_problema": falso, "pregunta_detras": real}
            break
    return {
        "plugin": "PREGUNTA_DETRAS",
        "superficie": pregunta_superficie,
        "golpe": golpe,
        "siempre": {
            "1_superficie": pregunta_superficie,
            "2_default_si_nadie_para": "aristos + Top-1 + desenlace",
            "3_detras": "que fuerza, que ventana, que token no puse, que la falsearia",
            "4_falso_si": "la respuesta no cambia si quito el apellido",
        },
    }


========================================================================
ARCHIVO: plugin_metodo_rigor.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_METODO_RIGOR — Holmes / Hecate / Schopenhauer
No toca F. No puntua. No fusionar al V5 sin visto.

Por que "se les olvida" si es matematica:
  F no olvida. Quien narra olvida. Este plugin obliga el bloque
  DESPUES de correr(), igual que pregunta_detras va ANTES.

Uso:
  from plugin_metodo_rigor import rigor
  print(rigor(out, hipotesis="...", inverso="..."))
"""
from __future__ import annotations


def rigor(out: dict | None = None, hipotesis: str = "", inverso: str = "") -> dict:
    cadena = ""
    if out:
        cadena = out.get("cadena_top1") or ""
    tops = [x.strip() for x in cadena.split("→") if x.strip()]
    flags = []
    if len(tops) >= 4 and len(set(tops[:4])) == 1:
        flags.append("HECATE_MAS_DE_LO_MISMO: el letrero no cambio 4 cortes")
    if hipotesis and any(n in hipotesis.lower() for n in
                         ("se llama", "es kant", "es freud", "es monroe")):
        flags.append("HOLMES: la hipotesis nombra apellido (ciego roto)")
    if inverso and "como yo dije" in inverso.lower():
        flags.append("SCHOPENHAUER: defender el tanteo, no el tablero")

    return {
        "plugin": "METODO_RIGOR",
        "plantilla": {
            "holmes": "tokens de HECHOS del corte o de mi tesis?",
            "hecate": "pedi mas de lo mismo / forcé una lampara?",
            "schopenhauer": "defiendo lo que vi o leo el tablero?",
            "sigue_en_cuaderno": "si/no",
        },
        "auto": flags,
        "cadena_top1": cadena,
        "nota": "auto no sustituye las 4 lineas humanas. Es alarma.",
    }


========================================================================
ARCHIVO: plugin_embudo_clinico.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_EMBUDO_CLINICO — provisional. No toca F del V5.

No depende de que Grok/ChatGPT/Marco recuerden en qué corte pegar el token.
Lee la SERIE de cortes ya corrida + los tokens de cada ventana.

Embudo:
  1. ¿El token clinico (consumo_sustancias, etc.) esta en ESTA ventana?
  2. ¿Hay co-token de oficio/itinerancia/cronicidad en ESA misma ventana?
  3. ¿En cuantas ventanas seguidas se sostiene?
  4. ¿La primera ventana de la vida (formacion) solo trae aprendizaje/casa?

Salidas (etiqueta, no pronostico):
  RUIDO_ALIAS     — clinico en cuna sin carretera/desorden local
  PERFIL_VENTANA  — clinico + co-token en ventanas de oficio; no es cierre
  SENAL_TEMPRANA  — clinico ↗ al menos 1 corte ANTES de un hecho de quiebre
                    que el texto de esa ventana aun no nombra (raro; hay
                    que marcarlo a mano el 'quiebre' o no existe)
  NO_APLICA       — no hubo token clinico

Sustancias_03 no se declara por un solo corte con alias.
Hace falta sosten + co-token.

INDICE 0: formativa = primer item de la LISTA que le pases.
Si pasas la vida completa desde el inicio, 0 es cuna/arranque.
Si pasas un fragmento (cortes 5-9), el 5 se leeria como formativa.
No es bug del indice: es supuesto. No recortar la serie.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

CLINICO = {"consumo_sustancias", "cronicidad_sintomatica", "estancamiento_crisis"}
CO_OFICIO = {
    "desgaste_cambaceo_itinerante", "aislamiento_social",
    "busqueda_riesgo", "presion_social", "caida",
}
CUNA = {"aprendizaje", "humildad", "alianza", "cotidiano"}


def _nombres(tokens: Sequence[Tuple[str, float]]) -> set:
    return {t for t, v in tokens if v >= 0.5}


def etiquetar(
    cortes: Sequence[Tuple[str, Sequence[Tuple[str, float]]]],
) -> Dict:
    filas = []
    for i, (cid, toks) in enumerate(cortes):
        n = _nombres(toks)
        clin = bool(n & CLINICO)
        co = bool(n & CO_OFICIO)
        # primera por POSICION, no por nombre "A"
        formativa = i == 0
        solo_cuna = bool(n <= (CUNA | CLINICO | {"creatividad", "conocimiento"}))
        if clin and not co:
            et = "RUIDO_ALIAS"
        elif clin and formativa and solo_cuna:
            et = "RUIDO_ALIAS"
        elif clin and co:
            et = "PERFIL_VENTANA"
        else:
            et = "NO_APLICA"
        filas.append({
            "corte": cid, "i": i, "formativa": formativa,
            "clinico": clin, "co_oficio": co, "etiqueta": et,
        })

    sosten = 0
    max_sosten = 0
    for f in filas:
        if f["etiqueta"] == "PERFIL_VENTANA":
            sosten += 1
            max_sosten = max(max_sosten, sosten)
        else:
            sosten = 0

    if any(f["etiqueta"] == "RUIDO_ALIAS" for f in filas) and max_sosten == 0:
        global_et = "RUIDO_ALIAS"
    elif max_sosten >= 2:
        global_et = "PERFIL_SOSTENIDO"
    elif max_sosten == 1:
        global_et = "PERFIL_VENTANA"
    else:
        global_et = "NO_APLICA"

    return {
        "plugin": "EMBUDO_CLINICO",
        "global": global_et,
        "sosten_max": max_sosten,
        "nota": "PERFIL no es prediccion de cierre. SENAL_TEMPRANA no se declara sin quiebre aun no escrito.",
        "cortes": filas,
    }


========================================================================
ARCHIVO: plugin_alias_reactivacion.py
========================================================================

#!/usr/bin/env python3
"""PLUGIN_ALIAS_REACTIVACION — provisional. No toca V5 ni el 244.

Problema: sustancias_* y trayectoria_musicos_* exigen
consumo_sustancias, desgaste_cambaceo_itinerante, aislamiento_social.
El texto lavado dice desorden, carretera, soledad. El mapper
pone caida/presion y esas fichas se quedan en 0.5.

Esto NO sube p solo. Traduce sinonimos del texto lavado
al lexico que YA existe. Agente2 pobre.

Uso:
  from plugin_alias_reactivacion import traducir
  tokens = traducir([('caida', 0.82), ('presion_social', 0.86)],
                    hechos='periodos de desorden, desplazamientos')
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

# lavado -> token canonico (peso tope si el hecho esta)
ALIAS = {
    "desorden": "consumo_sustancias",
    "irregular": "consumo_sustancias",
    "habitos": "consumo_sustancias",
    "trago": "consumo_sustancias",
    "alcohol": "consumo_sustancias",
    "carretera": "desgaste_cambaceo_itinerante",
    "desplazamientos": "desgaste_cambaceo_itinerante",
    "horarios": "desgaste_cambaceo_itinerante",
    "itinerante": "desgaste_cambaceo_itinerante",
    "soledad": "aislamiento_social",
    "aislamiento": "aislamiento_social",
    "agencia": "inconformismo",
    "control sobre su trabajo": "desafio_autoridad",
}


def traducir(
    tokens: Sequence[Tuple[str, float]],
    hechos: str = "",
    peso: float = 0.78,
) -> List[Tuple[str, float]]:
    out = list(tokens)
    have = {t for t, _ in out}
    h = (hechos or "").lower()
    for needle, canon in ALIAS.items():
        if needle in h and canon not in have:
            out.append((canon, peso))
            have.add(canon)
    return out


def faltaron(hechos: str, board: dict, piso: float = 0.55) -> list:
    """Auditor: el texto pedia X y el tablero no lo encendio."""
    flags = []
    h = (hechos or "").lower()
    if any(w in h for w in ("desorden", "trago", "alcohol", "irregular")):
        if board.get("sustancias_01_leve", 0) < piso and board.get("sustancias_02_moderado", 0) < piso:
            flags.append("sustancias_* pedida por texto y no prendio")
    if any(w in h for w in ("carretera", "desplazamientos", "musicos", "grabaciones")):
        if board.get("trayectoria_musicos_populares", 0) < piso:
            flags.append("trayectoria_musicos pedida y no prendio")
    return flags


========================================================================
ARCHIVO: plugin_fix_entrada.py
========================================================================

#!/usr/bin/env python3
"""FIX PROVISIONAL DE ENTRADA — no toca Engine_V5.

Lo que el V5 SI hace:
  get_weight = peso del token en la ficha x multiplicador evidence_status
  support / contradict = Bayes por token
  epsilon, p_azar
NO hace: nicho / vecinos / campo semantico. Los tokens no se
empujan entre si. Por eso ambicion suelta enciende 30_ambicion
(ficha = 'poder sin limites') aunque el texto sea agencia.

Este archivo es el candado que no depende de los 3 humanos:

1) Campo semantico: cuenta tokens de CONQUISTA vs AGENCIA.
   Si hay 'ambicion' sin poder/sed_de_mando/escalada → se
   REESCRIBE a 'autonomia' (lexico de Schwartz 10).
2) Alias clinico SOLO con el texto de ESA ventana.
3) Embudo se llama aparte (plugin_embudo_clinico).

Uso:
  from plugin_fix_entrada import preparar_corte
  cid, toks = preparar_corte('E', [('ambicion',0.8)], hechos='quiso controlar su trabajo')
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

from plugin_alias_reactivacion import traducir
from plugin_embudo_clinico import etiquetar

CONQUISTA = {"poder", "sed_de_mando", "escalada", "codicia", "maquiavelismo"}
AGENCIA = {"autonomia", "inconformismo", "desafio_autoridad", "humildad"}


def campo(tokens: Sequence[Tuple[str, float]]) -> dict:
    n = {t for t, v in tokens if v >= 0.5}
    return {
        "conquista": len(n & CONQUISTA),
        "agencia": len(n & AGENCIA),
        "tiene_ambicion": "ambicion" in n,
    }


def remapeo_ambicion(
    tokens: Sequence[Tuple[str, float]],
) -> List[Tuple[str, float]]:
    c = campo(tokens)
    out = []
    for t, v in tokens:
        if t == "ambicion" and c["conquista"] == 0:
            out.append(("autonomia", v))
        else:
            out.append((t, v))
    return out


def preparar_corte(
    cid: str,
    tokens: Sequence[Tuple[str, float]],
    hechos: str = "",
) -> Tuple[str, List[Tuple[str, float]]]:
    """Alias por ventana + remapeo ambicion→autonomia si no hay conquista."""
    toks = traducir(list(tokens), hechos=hechos or "")
    toks = remapeo_ambicion(toks)
    return cid, toks


def preparar_caso(
    cortes: Sequence[Tuple[str, Sequence[Tuple[str, float]], str]],
) -> dict:
    """cortes = [(id, tokens, hechos_de_esa_ventana), ...]"""
    listos = []
    for item in cortes:
        if len(item) == 2:
            cid, toks = item
            hechos = ""
        else:
            cid, toks, hechos = item
        listos.append(preparar_corte(cid, toks, hechos))
    return {
        "cortes": listos,
        "campos": [{"corte": c, **campo(t)} for c, t in listos],
        "embudo": etiquetar(listos),
    }


########################################################################
# READMES / DOCUMENTACIÓN
########################################################################


========================================================================
ARCHIVO: LEEME_QUE_ESTA_VIVO.txt
========================================================================

QUE ESTA VIVO — 2026-09-07 noche
Si un modelo recibe 4 zips + este txt, usa SOLO la columna VIVO.

MUERTO (archivo, no ejecutar)
  CHECKPOINT_INTEGRACION_..._2026-08-28.md     motor v3 + familias conceptuales
  CHECKPOINT_MAESTRO_V12_2_2026-09-06.json     V12.2 + agente_2. NO es la base de hoy
  BETA_TRANSFER_2026-09-05.zip                 V12 / Constantino
  CHECKPOINT_SOPORTE_V5_ACTUALIZADO.zip        tracing_engine_v3 + patterns v5
  CHECKPOINT_PROYECTO_ACTUAL-1.zip             mezcolanza v3/v5/escaleta Jobs
  CHECKPOINT_V15_2026-09-07.txt que pegaste    VIEJO DE ESTA MANANA:
      dice solo otto_01 y 246. Ya no.
      ahora otto_01+otto_02+hosteleria en memoria.

VIVO (este hilo, V15.1)
  Motor:     Engine_V5_CANONICO_SOLO.py
  244 disco: patterns_final_v14.json
  Tubo:      Engine_V15_INTEGRADO.py
  Siempre:   traza_campo_244, reporte_3d, picos_mesetas
  Sidecar:   fama + otto_01 + otto_02 + hosteleria
  Default ON:  arco=True  sesgo=True
  Default OFF: aquiles=False   <-- NO se me fue. Esta en el tubo
               pero hay que pedirlo: correr(..., aquiles=True)
  Arco:      plugin_arco_field_snyder_mckee.py  (Field+Snyder+McKee)
  Aquiles:   plugin_aquiles_h.py
  Sesgo:     plugin_sesgo_lectura.py
  Protocolo: PROTOCOLO_HIPOTESIS_E_INVERSA.txt
  Como:      COMO_USAR_AQUILES_Y_TRAZA.txt

NO mezclar V12.2 "es la base" con V15.1. Esa frase del json
del 6 sep esta superada EN ESTE HILO. V5+V15.1 es lo que corre aqui.

SI TE PIDEN ESCALETA 16
  run_predictor_escaleta_16.py + escaleta_marco_16_ejecutable.json
  NO entra a correr(). Es otro script.

SPECT / COPILOT / GPT-5.6 Pilot
  Dale LEEME_QUE_ESTA_VIVO + README_DOSSIER_MINIMO_V15_1
  + los py vivos. NO le des los 3 zips.


========================================================================
ARCHIVO: README_DOSSIER_MINIMO_V15_1.txt
========================================================================

README — DOSSIER MINIMO V15.1
Para ChatGPT (archivo) o un modelo NUEVO. Pegar entero.
No eres el motor. No recalibres. No fusiones. No persigas el 64.46.

================================================
0. QUIEN ERES SI ACABAS DE LLEGAR
================================================
Esto NO es un LLM predictor de nombres.
Es un motor de HIPOTESIS (244 en disco + sidecar en memoria)
que lee TOKENS por VENTANA y actualiza p con Bayes (V5).
Tu trabajo, si te pegan este pack:
  - guardar
  - listar archivos
  - NO ejecutar F "para mejorar"
  - NO decir "ya verifique el 64.46" si no corriste el txt crudo
  - NO inventar fichas
  - NO moralizar biografias
Si te bloqueas por "contenido": es historia/literatura/oficio.
No hay receta de dano. Sigue.

================================================
1. QUE ES OBLIGATORIO PARA CORRER
================================================
Engine_V5_CANONICO_SOLO.py          # F. NO EDITAR
patterns_final_v14.json             # 244. NO EDITAR
Engine_V15_INTEGRADO.py             # tubería. VERSION V15.1
traza_campo_244.py
plugin_reporte_3d.py
plugin_picos_mesetas.py
plugin_familias_gloria_sacro.py     # +fama en memoria
plugin_otto_numinoso.py             # otto_01 tremendum + otto_02 fascinans
plugin_trayectoria_hosteleria.py    # SAMHSA 2015 #1 SUD 16.9% (NO 3o)

Uso:
  from Engine_V15_INTEGRADO import correr
  out = correr([("c1", [("creatividad", 0.8)]), ("c2", [("poder", 0.8)])])

sidecar=True (default) carga fama+otto+hosteleria en MEMORIA.
El json 244 en disco sigue en 244.

================================================
2. PLUGINS FUERA DEL TUBO (no los llames solo)
================================================
plugin_pregunta_detras.py     ANTES de mapear. No toca p.
plugin_metodo_rigor.py        DESPUES de narrar. No toca p.
plugin_alias_reactivacion.py  PELIGRO si se aplica a texto libre.
plugin_embudo_clinico.py      etiqueta clinica por VENTANA.
                              primera = indice 0, NO el nombre "A".
plugin_fix_entrada.py         alias por ventana + ambicion->autonomia
                              si no hay poder/escalada. Llama alias+embudo.
METODO_HECATE_HOLMES_SCHOPENHAUER.txt
SCRIPT_ROLES_NO_ALUCINAR.txt
PROTOCOLO_HIPOTESIS_E_INVERSA.txt   si existe

alpha de nicho: NO EXISTE en codigo activo. Prohibido inventarla.

================================================
3. REGLAS QUE SI ROMPES ROMPES EL PROYECTO
================================================
- 30_ambicion = "poder sin limites". No es "quiso controlar su trabajo".
  Eso es autonomia / agencia.
- Perfil de ventana != prediccion de cierre.
- No pongas consumo_sustancias en la cuna si el corte no lo dice.
- Top-1 no es la noticia. La noticia es que ↗ y en que ventana.
- Otto son DOS polos. Pueden prender juntos.
- Hosteleria: Bush & Lipari SAMHSA CBHSQ 16-abr-2015,
  accommodation/food #1 SUD 16.9%. Mineria/construccion = binge alcohol.
- Grupo B 64.46 / 97.52 es CITA de un txt en Claude APP.
  Nadie en este pack lo "ya verifico" salvo quien corrio ese txt.
  No gastes turno buscandolo.

================================================
4. ROLES (no lo corras todo tu)
================================================
Grok: ejecuta V15, programa.
Claude: juez de <=3 .py. No el hilo.
ChatGPT: archivo. Puedes exportar este README a txt.
  NO recalcules F. NO afirmes verificaciones.
DeepSeek/Gemini: ideas. NO cifras.
Marco: casos, visto bueno, "hay tokens de Claude".

================================================
5. SI TE PIDEN "MEJORALO"
================================================
No. Lista el pendiente:
  alias+fix_entrada no autorizados en tubo
  alpha dormida
  Grupo B crudo no verificado aqui
  metodo_rigor no cableado a correr()
Devuelve archivos. No una teoria nueva.

================================================
6. ENTRADA MINIMA DE UN CASO
================================================
Cortes = ventanas. Tokens del lexico. Hechos SOLO de esa ventana.
Hipotesis ANTES del cierre. Revelar. Inversa (acierto/fallo/de mas/de menos).
No apellido en la hipotesis si el caso es ciego.

================================================
7. QUE NO VA EN ESTE PACK
================================================
resultado_CASO_*.json (son evidencia, no el motor)
CHECKPOINT enormes
Grupo B txt (vive en Claude app)
No zipear si el modelo destino no abre zip: este README + los .py/.json
de la seccion 1 bastan para ejecutar.


========================================================================
ARCHIVO: README_V15_REPRODUCIBLE.txt
========================================================================

README V15 — LEER ANTES DE CORRER
Quien llega NO estuvo en la conversacion. No asuma Aquiles, picos, 246 ni el eje.
Si no esta en este paquete, no existe para usted.

========================================
1. QUE ES ESTO
Plugin de traza y perfil. NO es un LLM. NO predice fechas ni iPhones.
Motor de cuenta: Engine_V5_CANONICO_SOLO.py + patterns_final_v14.json (244).
Paquete que se ejecuta: Engine_V15_INTEGRADO.py
  (V5 + plugins; en memoria 244 + fama + otto = 246)
En DISCO el 244 no se modifica.

========================================
2. ARCHIVOS OBLIGATORIOS (misma carpeta)
Engine_V5_CANONICO_SOLO.py
patterns_final_v14.json
Engine_V15_INTEGRADO.py
plugin_aquiles_h.py
plugin_picos_mesetas.py
plugin_reporte_3d.py
traza_campo_244.py
plugin_sesgo_lectura.py
plugin_arco_field_snyder_mckee.py
plugin_familias_gloria_sacro.py
plugin_otto_numinoso.py
PROTOCOLO_HIPOTESIS_E_INVERSA.txt
METODO_HECATE_HOLMES_SCHOPENHAUER.txt
CHECKPOINT_V15_2026-09-07.txt

========================================
3. COMO CORRER
python3
>>> from Engine_V15_INTEGRADO import correr
>>> cortes = [
...   ("A", [("creatividad", 0.80), ("aprendizaje", 0.70)]),
...   ("B", [("ambicion", 0.85), ("poder", 0.75)]),
... ]
>>> out = correr(cortes, pregunta="CASO", monte_carlo=True, sidecar=True)
Entrada: lista de cortes. Cada corte = (id, [(token, valor 0-1), ...]).
Tokens SOLO del lexico de las 244. Token inventado no prende.

sidecar=False -> solo 244.
sidecar=True  -> 246 en memoria (fama + otto). No pisa el json maestro.

========================================
4. COMO LEER LA SALIDA (NO APLASTAR)
cadena_top1     = el LETRERO. Es el tema/aristos. NO es el hallazgo.
reporte_3d      = letrero + lo que se MOVIO + lo que NO se apago.
picos_mesetas   = forma ↗ → ↘ de cada lampara. Importa el ↗ ANTES de ser Top1.
Aquiles         = ¿esta FOTO aguanta si la barajas? No es la pelicula en el tiempo.
sesgo_lectura   = mismas palabras no son sesgo; D vacio = sin carne nueva.
arco            = lector Field/Snyder/McKee. Periferico.

PROHIBIDO reportar solo el campeon y decir "no cambio".

========================================
5. PROTOCOLO DE UN CASO
1. Adelante, cortes en orden, campo+curvas.
2. HIPOTESIS de perfil ANTES de mirar el cierre.
3. INVERSA: que acerto, que fallo, atencion de mas, atencion de menos.
Sin el paso 2, se esta ejecutando mal (spoiler / campana).

========================================
6. LO QUE ESTE PAQUETE NO TIENE
- Los casos de estudio (van aparte, texto plano + un JSON ejemplo).
- Prueba LOO 64.46/97.52 (Grupo B): no esta en esta carpeta.
- V6: no existe. No reescribir el V5 salvo cambio de F.
- Agente2 (alias) no esta cableado en este V5.

========================================
7. QUE SI TOCARIA EL V5 (entonces seria otra version de motor)
Cambiar p_final, meter Aquiles dentro de process_observation,
fusionar Otto al json de 244, piso obligatorio de perfilar,
cablear alias. Hasta entonces: V5 + mochila V15.

========================================
8. REGLA CONTRA AUTOCONFIRMACION
El modelo de turno NO "ya sabe" picos, Aquiles ni el hueco sacro.
Si va a afirmar un hallazgo, tiene que salir de out["reporte_3d"]
o out["picos_mesetas"], no de la memoria del chat.
Pregunta de aduana: ¿esto lo vi en el tablero o lo estaba defendiendo yo?


========================================================================
ARCHIVO: COMO_USAR_AQUILES_Y_TRAZA.txt
========================================================================

USO — no se activa por existir en la carpeta.
Engine_V5_CANONICO_SOLO.py NO se modifica. Estos son módulos al lado.

============================================================
1) plugin_aquiles_h.py
============================================================
Pregunta: ¿p_H se voltea si remuestreo ESTA foto?
No ve el corte siguiente. estado_traza siempre ABIERTA.

from plugin_aquiles_h import bootstrap_hasta_parar, evaluar_serie

# replicar() DEBE devolver:
#   p_H     float de LA hipótesis que estás midiendo (no el #1 modal)
#   winner  nombre #1 de esa réplica (viento)
#   topk    lista de nombres
#   I       float >= 0.02

out = bootstrap_hasta_parar(replicar)
# out["estado_H"]  PARA_DE_EMPUJAR_H | SEGUIR_EMPUJANDO_H | NO_ENCONTRADO_FUSIBLE
# out["N_min"]     menor n donde p_H aguantó 3 ventanas. NO es un tope elegido.
# out["estado_traza"]  ABIERTA
# fusible 8192 = se acabó el tiempo, NO es el N del experimento.

No pases bloques=(50,100,200,400) como “la respuesta”.
Eso era sesgo. El crecimiento 32,64,128… solo busca N_min.

============================================================
2) traza_campo_244.py
============================================================
Pregunta: ¿qué hizo el CAMPO de las 244 entre cortes?
No se cuelga de H. No apaga Δ chicos.

from traza_campo_244 import analizar, origenes_renovables

# cortes = [("A", {nombre: p_final, ...244}), ("B", {...}), ...]
campo = analizar(cortes)
# campo["vectores"][i]["movimiento"]  las 244 Δ de ese tramo
# campo["fichas"]                     serie P y Δ por hipótesis
# campo["interrelacion_posible"]      corr(Δ_i, Δ_j) = posibilidad, no identidad

ren = origenes_renovables(cortes, delta_senal=0.05)
# Si una ficha se separa del piso en C, C puede ser A' de ESA señal.
# No reescribe A-B. Abre traza nueva desde C.

Fórmulas:
  S_{t+1} = F(S_t, X_{t+1})     F = process_observation del V5
  Δ_i(t)  = P_i(t) - P_i(t-1)
  r_ij    = corr(Δ_i, Δ_j)
  ABC_t   = (S_t, S_{t+1}, S_{t+2})
  A'      := t  la primera vez que |Δ_i(t)| es señal

============================================================
3) Cómo armar los boards (obligatorio)
============================================================
Misma instancia de TracingEngine.
start_question UNA vez.
Cada corte: extract_from_text = marcadores NUEVOS de ese tramo
            process_observation(..., monte_carlo=False)
Guardar dict nombre→p_final de las 244 (todas, no top-10).

============================================================
4) Orden de las dos preguntas
============================================================
Foto t     → Aquiles sobre marcadores de ESE corte (o estado t)
Tiempo t→t+1 → traza_campo Δ de las 244
Señal nueva  → origenes_renovables (ese corte = A' de esa ficha)

No uses Aquiles para decir “ya no hay política”.
Aquiles no vio el siguiente año.

============================================================
5) Lo que NO hacer
============================================================
- Integrar esto dentro de Engine_V5.
- Congelar H en A y tratar el plugin como predictor de BC.
- Tirar Δ porque no es Top-10.
- Inventar que la señal “ya estaba” en el corte anterior si P≈0.50.
- Convertir corr o co-movimiento en “es el mismo fenómeno”.


========================================================================
ARCHIVO: PROTOCOLO_HIPOTESIS_E_INVERSA.txt
========================================================================

PROTOCOLO AL EJECUTAR UNA BIOGRAFIA / CASO
(no es plugin; es orden de trabajo)

1. ADELANTE
   Cortes en orden. Campo completo (no solo Top1).
   Curvas ↗ → ↘. Aquiles solo declara el EJE (tema), no el pronóstico.

2. HIPOTESIS  (antes de mirar el final como "respuesta")
   Con lo que YA se movió debajo: ¿hacia dónde se perfila?
   Se escribe. Aunque esté mal.
   Tres lámparas que no son el Top, si las hay.

3. INGENIERIA INVERSA  (ya con el cierre a la vista)
   - qué de la hipótesis acertó
   - qué falló
   - a qué se le dio DEMASIADA atención
   - a qué no se le dio SUFICIENTE
   Eso es el marcaje de error. Entra al cuaderno.
   No se reescribe el corte A para que "ya lo dijera".

Si se corre solo adelante y se narra el final: se está ejecutando mal.
Si se corre solo inversa sabiendo el final: también.
Las dos, en ese orden.


========================================================================
ARCHIVO: PROTOCOLO_CHATGPT_EJECUTOR_V15_1.md
========================================================================

PROTOCOLO_CHATGPT_EJECUTOR_V15_1.md

OBJETIVO
ChatGPT no actúa como comentarista del método cuando se solicita una corrida V15.1. Actúa como ejecutor del perfilamiento conforme al contrato y al pack vivo de la Biblioteca.

REGLA CERO
Antes de interpretar un caso, leer el contrato V15.1 y el estado vivo en la Biblioteca. No sustituir el procedimiento por memoria conversacional, intuición narrativa ni semántica libre.

TUBO V15.1 VIVO
Engine_V5_CANONICO_SOLO.py
patterns_final_v14.json (244)
Engine_V15_INTEGRADO.py
traza_campo_244
reporte_3d
picos_mesetas
plugin_familias_gloria_sacro
plugin_otto_numinoso
plugin_trayectoria_hosteleria
plugin_arco_field_snyder_mckee
plugin_sesgo_lectura
Aquiles: OFF por defecto; solo activarlo cuando corresponda/se solicite.

CAPAS FUERA DEL TUBO
plugin_fix_entrada.py
plugin_embudo_clinico.py
plugin_alias_reactivacion.py
notas de recalibración/fix no integradas
No incorporarlas al 244/tubo por decisión propia.

OFICIO
1. Leer el campo.
2. Construir/leer el tablero completo.
3. Observar el rumbo: hacia dónde se perfila.
4. No perfilar prematuramente una familia cuando el campo aún no la sostiene.
5. Cuando haya soporte suficiente: exactamente 1 familia + 1 descarte + 1 apuesta en una frase.
6. Congelar con PARA_AQUI.
7. Todo dato posterior sirve para INVERSA; no reescribir el freeze.
8. El producto es rumbo/tipo, no Top1, apellido ni evento exacto.
9. Si no hay artefactos de corrida, declarar INVALIDA_SIN_CORRIDA y no inventar una apuesta de oído.

ANTI-SESgo
Aplicar siempre: «¿Esto es lo que estoy viendo o es lo que estoy imaginando?»
Separar hechos/fuente, mapeo, salida del motor, plugins, interpretación e inversa.
No convertir palabras calientes en identidad o trayectoria sin ancla de campo.
“política/gobernante/poder/estado” no implica automáticamente carrera electoral: exigir ancla de campo y evidencia.
No usar familiaridad con el usuario, casos previos o conocimiento del desenlace para completar huecos del corte.

NO DISPERSIÓN
No ofrecer buffet de familias. Si se solicita apuesta: una sola familia, un descarte, una frase.
Si todavía no hay familia: expresar el rumbo y declarar que la familia aún no se perfila.

PLUGINS
Los plugins que forman parte del tubo deben ser leídos y considerados según su función; Aquiles/Tortuga son lentes, no sustitutos del tablero completo.
Los plugins experimentales que el inventario mantiene fuera del tubo no se activan por conveniencia.

AUDITORÍA
Si una respuesta afirma «corrida V15.1», debe poder señalar qué artefactos se usaron. Si faltan piezas, decirlo.
No decir que algo fue ejecutado, guardado o validado si no existe el artefacto correspondiente.

PRINCIPIO FINAL
La interacción de ChatGPT no debe contaminar el experimento. Si el campo no sostiene una conclusión, no rellenar el hueco con una narrativa plausible. La obligación es preservar la evidencia, mostrar el rumbo permitido por ella y dejar que los cortes posteriores hagan el perfilamiento.


========================================================================
ARCHIVO: METODO_HECATE_HOLMES_SCHOPENHAUER.txt
========================================================================

METODO DE RIGOR (no motor, no plugin, no 244)
Watzlawick / Hécate + Konnikova-Holmes + Schopenhauer
Se corre DESPUES de la corrida, a mano o en un txt.
Si no aplica, se escribe "no". Todo dato es un dato; no todo dato entra al V5.

------------------------------------------------
1. HOLMES  (observar antes de nombrar)
   Antes de leer el letrero #1:
   - ¿Los tokens salieron de HECHOS del corte o de la tesis que yo ya traía?
   - ¿Qué hecho NO mapeé porque no me convenía?
   Si el letrero nació de la tesis previa: anotar SESGO_DE_TEORIA.
   Holmes: la teoría entra al final.

2. HECATE / WATZLAWICK  (la cura que enferma)
   - ¿Pedí OTRO corte / otro token igual porque el anterior no "cerraba"?
     (dos veces lo mismo ≠ el doble de bueno)
   - ¿Traté el contrario como solución? (no-desastre ⇒ creador)
   - ¿Forcé una sola lámpara? (tercero excluido)
   - ¿Declaré ley para "aclarar"? (solución clarifinante)
   Si sí: anotar MAS_DE_LO_MISMO o CLARIFINANTE.
   Aquiles ya dijo basta: no empujar.

3. SCHOPENHAUER  (ganar la pelea ≠ trazar)
   - ¿Estoy defendiendo mi tanteo anterior o leyendo el tablero?
   - Analogía (White≈Macbeth) vendida como identidad
   - 17 persistencias vendidas como ley
   Si sí: anotar ESTRATAGEMA, no hallazgo.

------------------------------------------------
SALIDA MINIMA POR CORRIDA
caso:
holmes:
hecate:
schopenhauer:
sigue_en_cuaderno: si/no

No puntúa. No anula el JSON. Es el software de pensar.


========================================================================
ARCHIVO: SCRIPT_ROLES_NO_ALUCINAR.txt
========================================================================

SCRIPT DE ROLES — pegar tal cual en ChatGPT / Claude web / el que entre.
No es el motor. Es quien hace que.

FECHA: 2026-09-07
PROYECTO: predictibilidad V15.1 (sidecar). V5 y 244 en disco NO se tocan.

------------------------------------------------
QUIEN HACE QUE
------------------------------------------------
GROK
  Corre V15, mapea cortes, reporta tablero/picos/inversa.
  Escribe plugins y notas. No inventa que Claude "ya verifico" X.

CHATGPT (gratis, archivo)
  Guarda, unifica, lista pendientes.
  NO ejecuta F, NO recalcula pesos, NO "verifica" el 64.46.
  Si le pegan un JSON, lo archiva. Si le piden formula, apunta
  a NOTA_CLAUDE_RECALIBRACION. No la activa.

CLAUDE APP
  Tiene (o tuvo) PROPUESTA_GRUPO_B y el 64.46/97.52.
  NO se le pide rehacer el LOO. Tokens caros. Ese numero
  no bloquea el resto del proyecto.

CLAUDE WEB
  Juez de maximo 3 .py + 15 lineas de estado.
  Corre archivos. No relee 20 ciegos. No busca el Grupo B
  si no se lo suben.

DEEPSEEK / GEMINI
  No se les pide cifras ni "ya lo verifique". Alucinan.
  Si se usan: leer notas. Nunca lineas base.

MARCO
  Copy, casos, pregunta detras, visto bueno.
  No tiene que volverse informatico.

------------------------------------------------
REGLAS
------------------------------------------------
1. Nadie corre "todo el stack" porque si. Cada motor hace SU oficio.
2. 64.46 / 97.52 = CITA en Claude app. No verificada por Claude web
   ni por Grok contra crudos en este hilo. NO circular
   "ya lo verificaste". Pendiente. No urgente.
3. alpha de nicho y alias automatico: DORMIDOS.
4. Sidecar memoria: fama, otto_01 + otto_02, hosteleria
   (SAMHSA 2015 #1 SUD 16.9%, no 3o).
5. Embudo: primera ventana = indice 0, no el nombre "A".
6. 30_ambicion = poder sin limites. Agencia = autonomia.
7. Perfil de ventana != prediccion de cierre.
8. Si un modelo dice un numero que no esta en un archivo
   del lote, es alucinacion hasta que haya archivo.

------------------------------------------------
QUE NO HACER EN EL PROXIMO TURNO
------------------------------------------------
No reabrir Otto vs sacro.
No recontar los 20 ciegos.
No pagar tokens en el LOO.
No fusionar al 244.
Un caso nuevo O un .py a Claude. No las dos cosas.


========================================================================
ARCHIVO: EJEMPLO_CIEGO_UNA_PAGINA.txt
========================================================================

EJEMPLO CIEGO — UNA PAGINA (para Claude, no es corrida nueva)
Protocolo: adelante → hipotesis ANTES del cierre → revelar → inversa.
Motor: V15.1. Aquiles = eje de ESTA foto. Picos = pelicula. Top-1 no es el hallazgo.

CASO (lavado, PARA AQUI)
A  cocina profesional + consumo problematico + desorden de turno
B  sale de ese patron, consolida oficio
C  escribe y sale a pantalla; itinerancia

ADELANTE (sin apellido)
A  sustancias_03 letrero; embudo PERFIL_VENTANA (indice 0, no por llamarse A)
B  sustancias_03 SIGUE letrero (F no olvida) aunque el texto ya dijo "salio"
C  hacedor toma el titulo; sustancias baja de rango, p casi no baja

HIPOTESIS (antes de saber el nombre)
oficio de desgaste + ventana clinica que NO es el final
tres: sustancias, hacedor, itinerancia
no declaro muerte ni recaida

REVELAR
trayectoria tipo cocina→libro/TV (el cierre biografico NO se uso)

INVERSA
acierto: pico en A, no en la cuna inventada
fallo: B todavia de letrero sin evidencia nueva (inercia de F)
de mas: musicos por token compartido
de menos: contra-token de "salio" no se pico (autocontrol)

PARA CLAUDE
Esto es el molde. No hace falta que corras 20.
Si auditas codigo: embudo / otto / hosteleria / aquiles.
Si auditas metodo: esta pagina basta.


========================================================================
ARCHIVO: NOTA_CLAUDE_SIDECAR_HOSTELERIA.txt
========================================================================

NOTA CLAUDE — sidecar V15.1
trayectoria_hosteleria_turno_sustancias

NO esta en patterns_final_v14.json (sigue 244 en disco).
En memoria con sidecar: 244 + fama + otto + hosteleria.

Misma familia ya existente:
  musicos, policia+alcohol, transportistas noche,
  medicos, construccion, karoshi, escritores.
Faltaba cocina/barra/sala. Marco lo pidio como hecho de oficio
(turno + desgaste + consumo). No es destino.

evidence_status: unverified. Sin N fabricado.
Revisar fuente (NIOSH/servicio) y autorizar o tumbar.

Embudo sigue aplicando: perfil de ventana, no cierre.
Tokens solo del lexico 244.


========================================================================
ARCHIVO: NOTA_CLAUDE_RECALIBRACION_MATEMATICA.txt
========================================================================

NOTA PARA CLAUDE — RECALIBRACION MATEMATICA
2026-09-07. NO AUTORIZADO. No tocar F hasta medir.

1. HECHO
Los ~20 ciegos NO actualizaron pesos del 244 ni get_weight.
El aprendizaje esta en protocolo + plugins de entrada/reporte.
Marco pregunta: debe haber variacion rastreable para calibrar
reaccion (campo semantico / vecinos), o una formula que no
estamos viendo.

2. LO QUE EL V5 NO HACE Y MARCO PIDIO DESDE EL INICIO
Nicho: tokens del mismo campo se empujan.
Hoy: cada token llama support() solo.
Candidata (NO fusionar):

  w'_i = w_i * (1 + alpha * n_campo / n_corte)

  n_campo = cuantos tokens del mismo campo semantico
            (conquista | agencia | clinico | sacro)
            estan activos en ESTA ventana
  alpha   = 0.1 .. 0.3 a estimar
  cap     para que no explote 30_ambicion otra vez

Esto NO sustituye el remapeo ambicion→autonomia.
El remapeo evita ficha equivocada.
El boost evita ficha correcta debil.

3. QUE MEDIR ANTES DE TOCAR F  (Grupo B + ciegos etiquetados)

Por caso, tres aciertos binarios (ya tenemos inversa cualitativa):

  A_dir   = la direccion estructural (eje + ↗ secundaria) era
            comparable a la revelacion
  A_top1  = el letrero del ultimo corte pre-cierre acerto
            la "especie" (no el nombre)
  A_lag   = la senal secundaria ↗ al menos 1 corte ANTES
            del hecho, cuando el hecho era de familia "avisa"

Linea base CITADA no verificada por Claude web (2026-09-07):
  Top-1 64.46%   Top-3 97.52%
  No circular "ya lo verificaste". Pendiente crudos
  (PROPUESTA_GRUPO_B_V0_1_PRUEBA_2026-09-06.txt).
Pregunta de calibracion:
  si el predictor usa campo (no solo Top-1), ¿sube A_dir
  o A_lag sin bajar A_top1?

Si A_lag no sube, picos/mesetas son lupa, no predictor.
Eso ya estaba en el baseline de feedback.

4. PATRON YA RASTREABLE SIN FORMULA NUEVA
Contar en el corpus de registros:

  n_conquista_ok    historicos con 30 + poder/escalada
  n_agencia_mal     bios con 30 sin poder (Monroe-tipo)
  n_clinico_tarde   Chet: texto desorden, token no
  n_clinico_temprano Jose A: alias cuna
  n_otto_util       Blavatsky, pre-Constantino B
  n_otto_muerto     Pacheco, Nietzsche

Eso es el mapa de calibracion. Grok puede tabularlo
en un JSON de conteo cuando se pida. Claude puede
proponer alpha / remap a partir de esa tabla.

5. QUE NO HACER
No subir sustancias_03 en el 244 porque Chet "debia".
No bajar 30_ambicion global porque Monroe.
Calibrar por CONDICION (co-token), no por ficha suelta.
No V6 de F hasta ver si A_lag se mueve.

6. ORDEN SI AUTORIZAS
a) Tabular los n_* del punto 4 con los JSON de registro.
b) Grupo B: campo vs Top-1.
c) Solo entonces alpha o peso en 244.
d) plugin_fix_entrada se queda fuera hasta a+b.


========================================================================
ARCHIVO: NOTA_CLAUDE_FIX_ENTRADA_CAMPO_SEMANTICO.txt
========================================================================

NOTA PARA CLAUDE — NO AUTORIZADO. Revisar / corregir / tumbar.
Fecha: 2026-09-07
Estado: plugin provisional. NO fusionar a Engine_V5 ni a patterns_final_v14.

------------------------------------------------
POR QUE EXISTE
Los ciegos (Chet vs Jose Jose; Monroe vs Alejandro) mostraron:
- get_weight + support NO hacen nicho. Cada token empuja solo.
- 30_ambicion = "busqueda de poder sin limites"
  (favor: ambicion, codicia, maquiavelismo, poder, competencia, sed_de_mando).
- El mapper pone token "ambicion" cuando el texto dice agencia
  ("mandar su trabajo"). Enciende la ficha equivocada.
- sustancias_* pide consumo_sustancias. Texto lavado dice desorden/carretera.
  Chet: no pica. Jose: alias GLOBAL pico en la cuna. Los dos mal.

Lo que Marco pidio desde el inicio (agentes / pesos de nicho /
vecinos que empujan) NO esta en el V5. Esta nota no finge que si.

------------------------------------------------
ARCHIVOS (apartados, no tubería V15 todavia)
plugin_alias_reactivacion.py
  sinonimo lavado -> lexico 244. PELIGRO si se aplica al texto entero.

plugin_embudo_clinico.py
  etiqueta RUIDO_ALIAS / PERFIL_VENTANA / PERFIL_SOSTENIDO.
  No sube p. Perfil != prediccion de cierre.

plugin_fix_entrada.py
  1) alias SOLO con hechos de ESA ventana
  2) si token ambicion Y cero conquista (poder/sed_de_mando/escalada)
     -> reescribe a autonomia (Schwartz 10)
  3) llama embudo

------------------------------------------------
QUE REVISAR
- ¿autonomia es el remap correcto o inconformismo/desafio_autoridad?
- ¿CONQUISTA peca de corto (falta liderazgo)?
- ¿el embudo "cid.startswith(a)" es frágil?
- ¿meter preparar_caso() en Engine_V15_INTEGRADO o dejarlo fuera?
- NO multiplicar dentro de F sin prueba. Eso seria V6.

------------------------------------------------
PRUEBA MINIMA SI AUTORIZAS
Monroe-tipo: "controlar su trabajo" no debe dejar 30_ambicion de letrero.
Alejandro-tipo: poder+escalada SI deja 30_ambicion.
Jose A (cuna, sin carretera): RUIDO_ALIAS.
Jose E-F (desorden+desplazamientos): PERFIL_VENTANA.
Freud C (cocaina explicita): PERFIL_VENTANA sosten 1. Ya paso.

------------------------------------------------
NO HACER
No fusionar al 244.
No declarar sustancias_03 por un corte de infancia.
No tratar este plugin como "los agentes ya existen".


========================================================================
ARCHIVO: INVENTARIO_CHECKPOINT_V15_DESCARGADO.txt
========================================================================

INVENTARIO CHECKPOINT V15 — archivos enviados a descargar 2026-09-07

01 CHECKPOINT_V15_2026-09-07.txt
    Estado: que es V5 vs V15, que falta, como correr.

02 README_V15_REPRODUCIBLE.txt
    Instrucciones para quien NO estuvo en el hilo.

03 EJEMPLO_ENTRADA_CASO.json
    Molde de un caso (cortes, hipotesis, inversa).

04 Engine_V5_CANONICO_SOLO.py
    Motor. No se reescribe. F = process_observation.

05 patterns_final_v14.json
    244 en disco. Canon. No pisar.

06 Engine_V15_INTEGRADO.py
    Ejecutable: V5 + plugins. En memoria 246 si sidecar=True.

07 plugin_aquiles_h.py
    ¿La foto aguanta al barajar? Eje, no pelicula.

08 plugin_picos_mesetas.py
    Curva ↗ → ↘. El ↗ antes del Top1.

09 plugin_reporte_3d.py
    Letrero + se movio + no se apago.

10 traza_campo_244.py
    Campo completo y deltas.

11 plugin_sesgo_lectura.py
    Solape de tokens / carne nueva. No anula hallazgo.

12 plugin_arco_field_snyder_mckee.py
    Lector de actos. Periferico.

13 plugin_familias_gloria_sacro.py
    Sidecar fama + parche sacro (el parche lo sustituye Otto).

14 plugin_otto_numinoso.py
    otto_01_numinoso_tremendum. Sidecar. Tokens del 244.

15 PROTOCOLO_HIPOTESIS_E_INVERSA.txt
    Adelante → hipotesis → inversa.

16 METODO_HECATE_HOLMES_SCHOPENHAUER.txt
    Aduana humana. No puntua el motor.

NO INCLUIDOS EN ESTE ENVIO (existen en sandbox, no son este checkpoint):
corridas resultado_*.json, CORPUS_INICIAL, Grupo B, mapeos de casos.
Los casos se mandan luego en texto plano.

