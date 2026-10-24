#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""autoevidencia_stores_011.py — PATCH 011 (2026-10-06). Regla Mj: la autoevidencia no cuenta; ciego ≈ vivo.

Helpers de solo lectura para los stores persistentes (vecinos Caldero y StinkBox):
  - sha_entrada(case): huella del INPUT congelado (sin rutas del runner) -> procedencia/idempotencia.
  - memoria_vecinos_sin_propios(root, case_id, input_sha): memoria de vecinos Caldero que EXCLUYE los eventos
    del mismo case_id (y del mismo input sha si el evento lo trae). Los propios quedan como traza (conteo).
  - evento_vecinos_ya_registrado(root, case_id, input_sha, query, tokens): idempotencia del append.
  - clasificar_pendientes(vivos, input_sha): mismo_input / otra_version / sin_procedencia.

PATCH 012 (2026-10-06): un token del vocabulario de vecinos VOTA solo con soporte de >=2 case_id AJENOS distintos
  (nunca del mismo case_id / mismo input sha; case_ids que comparten input sha cuentan como uno). Un token con
  soporte de un solo caso ajeno queda como traza/luz 'ilumina' (no suma score), regla de luces de Mj.

PATCH 014 (2026-10-06): con sujeto_actual/sujeto_evento la identidad de soporte es el SUJETO (no el case_id):
  un sujeto cuenta una vez; eventos del mismo sujeto que el caso actual son propios (no se apoya a sí mismo);
  los nombres propios de sujetos (nombres_no_votan) no votan: quedan como traza `nombres_sujeto_015`.
PATCH 015 (2026-10-06): política explícita — nombres_no_votan es GLOBAL (todos los sujetos de TABLA, no solo el actual);
  lectura intencional 'nombres propios de sujetos no votan en otros casos' (no sobre-filtrado). Años léxicos fuera del voto
  vía filtro_relleno_013 (traza `anos_015`).

Contrato: no escribe nada, no decide H, no toca Engine/patterns/244.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

VERSION = "AUTOEVIDENCIA_STORES_011_20261006+SOPORTE_012_20261006+SUJETO_014_20261006+AGNOSTICO_015_20261006"
MIN_CASOS_AJENOS_012 = 2
# Claves que pone el runner/entorno (rutas, ids de ledger): no son parte del input congelado.
CLAVES_NO_INPUT = ("stinkbox_root", "biblioteca_usuario_root", "model_user_library", "caldero_neighbor_store_root",
                   "ceb_root", "ceb_run_id")


def _norm(t: Any) -> str:
    return str(t if t is not None else "").strip().casefold()


def sha_entrada(case: Mapping[str, Any]) -> str:
    """sha256 del input congelado: JSON canónico del caso sin las claves de ruta del runner."""
    limpio = {k: v for k, v in dict(case).items() if k not in CLAVES_NO_INPUT}
    raw = json.dumps(limpio, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _eventos(root: Path) -> Optional[List[Dict[str, Any]]]:
    ev = Path(root) / "neighbor_events.jsonl"
    if not ev.is_file():
        return None
    out = []
    for line in ev.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if isinstance(o, dict):
            out.append(o)
    return out


def _sha_evento(o: Mapping[str, Any]) -> Optional[str]:
    meta = o.get("audit_meta") or {}
    return meta.get("input_sha_011") if isinstance(meta, Mapping) else None


def memoria_vecinos_sin_propios(root: Any, case_id: str, input_sha: Optional[str], min_casos_ajenos: int = 1,
                                sujeto_actual: Optional[str] = None, sujeto_evento: Any = None,
                                nombres_no_votan: Iterable[str] = ()) -> Dict[str, Any]:
    """Misma forma que _load_auxiliary_neighbor_memory (status/unique_tokens/observations/cases/store) + traza 011.

    Un token cuenta solo si lo aportaron eventos de OTROS case_id (con otro input sha). PATCH 012: con
    min_casos_ajenos=2 hacen falta >=2 identidades ajenas distintas; con 1 solo caso ajeno el token 'ilumina'.
    """
    min_casos_ajenos = max(1, int(min_casos_ajenos or 1))
    root = Path(root)
    cid = str(case_id)
    evs = _eventos(root)
    if evs is None:
        idx = root / "neighbor_index.json"
        if not idx.is_file():
            return {"status": "ABSENT", "unique_tokens": [], "observations": 0, "cases": 0, "version_011": VERSION,
                    "propios_excluidos": 0, "fuente": "sin_store"}
        try:
            data = json.loads(idx.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"status": "ERROR", "unique_tokens": [], "observations": 0, "cases": 0,
                    "error": f"{type(exc).__name__}:{exc}", "version_011": VERSION}
        nb = data.get("neighbors") or {}
        ajenos_idx = {t: {str(c) for c in (v.get("cases") or []) if str(c) != cid} for t, v in nb.items()}
        ok = {t: nb[t] for t, cs in ajenos_idx.items() if len(cs) >= min_casos_ajenos}
        ilu_idx = sorted(t for t, cs in ajenos_idx.items() if cs and len(cs) < min_casos_ajenos)
        propios = sorted(t for t, cs in ajenos_idx.items() if not cs)
        cases = set()
        for v in ok.values():
            cases.update(str(c) for c in (v.get("cases") or []) if str(c) != cid)
        return {"status": "PRESENT", "unique_tokens": sorted(ok), "observations": None, "cases": len(cases),
                "store": str(idx), "fuente": "neighbor_index.json(cases)", "version_011": VERSION,
                "propios_excluidos": None, "tokens_solo_propios_excluidos": len(propios),
                "min_casos_ajenos": min_casos_ajenos,
                "ilumina_012": {"n_tokens": len(ilu_idx), "tokens": ilu_idx, "efecto": "traza/luz; no vota ni suma score"}}
    propios_tok: set = set(); n_prop = 0; n_prop_sha = 0; n_prop_suj = 0; n_otros = 0
    ajenos = []  # (identidad, sha, tokens, filas, case_id)
    nombres = {_norm(x) for x in (nombres_no_votan or ())} - {""}
    def _suj(o):  # PATCH 014: identidad = sujeto (si hay resolvedor), si no case_id
        if callable(sujeto_evento):
            try:
                return str(sujeto_evento(o.get("case_id"), o.get("audit_meta"))[0])
            except Exception:
                return "caso:" + str(o.get("case_id"))
        return str(o.get("case_id"))
    for o in evs:
        filas = [r for r in (o.get("tokens_neighbors") or []) if isinstance(r, Mapping) and _norm(r.get("token"))]
        toks = {_norm(r.get("token")) for r in filas}
        mismo_caso = str(o.get("case_id")) == cid
        mismo_sha = bool(input_sha) and _sha_evento(o) == input_sha
        ident = _suj(o)
        mismo_suj = bool(sujeto_actual) and callable(sujeto_evento) and ident == str(sujeto_actual)
        if mismo_caso or mismo_sha or mismo_suj:
            n_prop += 1
            n_prop_sha += int(mismo_sha and not mismo_caso)
            n_prop_suj += int(mismo_suj and not mismo_caso and not mismo_sha)
            propios_tok |= toks
            continue
        n_otros += 1
        ajenos.append((ident, _sha_evento(o), toks, filas, str(o.get("case_id"))))
    # PATCH 012: identidad ajena = case_id; case_ids que comparten input sha se funden en una sola identidad.
    padre: Dict[str, str] = {}
    def _raiz(x: str) -> str:
        while padre.setdefault(x, x) != x:
            x = padre[x]
        return x
    por_sha: Dict[str, str] = {}
    for c, sh, _t, _f, _cid in ajenos:
        _raiz(c)
        if sh:
            if sh in por_sha:
                a, b = _raiz(c), _raiz(por_sha[sh])
                if a != b:
                    padre[max(a, b)] = min(a, b)
            else:
                por_sha[sh] = c
    soporte: Dict[str, set] = {}
    casos_tok: Dict[str, set] = {}
    for c, _sh, toks, _f, _cid in ajenos:
        for t in toks:
            soporte.setdefault(t, set()).add(_raiz(c))
            casos_tok.setdefault(t, set()).add(_cid)
    permitidos = {t for t, ids in soporte.items() if len(ids) >= min_casos_ajenos}
    nombres_fuera = sorted(permitidos & nombres) if nombres else []  # PATCH 014: nombres propios -> solo traza
    permitidos -= set(nombres_fuera)
    ilumina = sorted(t for t in soporte if t not in permitidos and t not in nombres)
    ilu_por_caso: Dict[str, int] = {}
    for t in ilumina:
        for c in casos_tok.get(t, ()):
            ilu_por_caso[c] = ilu_por_caso.get(c, 0) + 1
    cases: set = set(); obs = 0
    for c, _sh, toks, filas, _cid in ajenos:
        if toks & permitidos:
            cases.add(_cid)
        obs += sum(int(r.get("coactivation_frequency", 1) or 1) for r in filas if _norm(r.get("token")) in permitidos)
    return {"status": "PRESENT" if permitidos else "PRESENT_SIN_AJENOS", "unique_tokens": sorted(permitidos),
            "observations": obs, "cases": len(cases), "store": str(root / "neighbor_events.jsonl"),
            "fuente": "neighbor_events.jsonl", "version_011": VERSION,
            "eventos_total": len(evs), "eventos_ajenos": n_otros,
            "propios_excluidos": n_prop, "propios_excluidos_por_sha": n_prop_sha,
            "tokens_solo_propios_excluidos": len(propios_tok - set(soporte)),
            "min_casos_ajenos": min_casos_ajenos,
            "identidades_ajenas": len({_raiz(c) for c, _s, _t, _f, _cid in ajenos}),
            "propios_excluidos_por_sujeto_014": n_prop_suj, "sujeto_actual_014": sujeto_actual if callable(sujeto_evento) else None,
            "nombres_sujeto_015": {"n_votarian": len(nombres_fuera), "tokens": nombres_fuera,
                                   "n_en_store": len(set(soporte) & nombres) if nombres else 0,
                                   "efecto": "nombre propio de sujeto (global TABLA): solo traza, no vota; política intencional 015"},
            "ilumina_012": {"n_tokens": len(ilumina), "por_caso": dict(sorted(ilu_por_caso.items())), "tokens": ilumina,
                            "efecto": "traza/luz; no vota ni suma score (soporte de un solo caso ajeno)"},
            "regla": "autoevidencia_no_cuenta: eventos del mismo case_id o mismo input sha no votan; quedan como traza. "
                     "PATCH 012: token vota solo con soporte de >=%d case_id ajenos distintos; con menos, 'ilumina'" % min_casos_ajenos}


def evento_vecinos_ya_registrado(root: Any, case_id: str, input_sha: Optional[str], query: str,
                                 tokens_neighbors: Iterable[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    """Devuelve el evento existente si esta corrida es repetición del mismo input (no se vuelve a escribir).

    Coincide si: mismo case_id y (mismo input_sha_011, o evento legado sin sha con misma query y mismos tokens).
    """
    evs = _eventos(Path(root)) or []
    toks = json.dumps(list(tokens_neighbors or []), ensure_ascii=False, sort_keys=True, default=str)
    for o in evs:
        if str(o.get("case_id")) != str(case_id):
            continue
        s = _sha_evento(o)
        if s and input_sha and s == input_sha:
            return {"event_id": o.get("event_id"), "timestamp_utc": o.get("timestamp_utc"), "criterio": "mismo_input_sha"}
        if not s and str(o.get("query", "")) == str(query or "") and \
                json.dumps(list(o.get("tokens_neighbors") or []), ensure_ascii=False, sort_keys=True, default=str) == toks:
            return {"event_id": o.get("event_id"), "timestamp_utc": o.get("timestamp_utc"), "criterio": "legado_sin_sha_mismo_contenido"}
    return None


def clasificar_pendientes(vivos: Iterable[Mapping[str, Any]], input_sha: Optional[str]) -> Dict[str, Any]:
    mismo, otra, sin = [], [], []
    for v in vivos or []:
        s = v.get("input_sha") or ((v.get("procedencia_011") or {}).get("input_sha") if isinstance(v.get("procedencia_011"), Mapping) else None)
        fid = v.get("front_id")
        if s is None:
            sin.append(fid)
        elif input_sha and s == input_sha:
            mismo.append(fid)
        else:
            otra.append(fid)
    return {"mismo_input": mismo, "otra_version_input": otra, "sin_procedencia": sin,
            "n_mismo_input": len(mismo), "n_otra_version_input": len(otra), "n_sin_procedencia": len(sin),
            "regla": "pendientes del mismo input = solo traza/latencia (no suman, no bloquean); otra versión = contexto de latencia, marcado"}
