#!/usr/bin/env python3
"""
V15.3 UNIFICADO ALTERNO V0.9

Motor alterno, case-agnostic.
- No modifica Engine_V5_CANONICO_SOLO.py ni patterns_final_v14.json.
- Conserva el corpus de 17 fórmulas como contrato documental.
- Ejecuta primero el motor canónico V15.3 y después las capas funcionales
  disponibles: geometría, Polti/Caldero, traza, Otto, embudo, hostelería,
  estabilidad y Aquiles.
- Las salidas de esas capas se convierten en features trazables y SÍ llegan
  al predictor; no se cuentan solamente como "feeds_predictor".
- No incorpora ningún caso histórico en el código.
- FREEZE es frontera de información; la predicción ocurre DESPUÉS.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math, re, sys, random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Optional
import numpy as np

BASE = Path(__file__).resolve().parent

class _CierreModo016(Exception):
    """UNIFICADO_20261011: selector de cierre terminal 016."""


def _STINKBOX_STORAGE_ROOT() -> Path:
    """Stable cross-run storage; explicit user/device path wins over package-local fallback."""
    configured = _oscat.getenv("STINKBOX_STORAGE_ROOT") or _oscat.getenv("STINKBOX_STORAGE")
    return Path(configured).expanduser() if configured else (BASE.parent.parent / "STINKBOX_STORAGE")

VERSION = "V15.3_UNICO_WORKING_OPEN_HYPOTHESES_20261020_R1"  # motor de trabajo: set abierto + geometría multicapas + apuesta multiescenario
# UNICO_20260927 = ESTRICTO (456c7e9f) + (1) catálogo de patrones configurable (MOTOR_PATTERNS_PATH; default
# patterns_final_v14.json d827dcc3; nada asume 244: se usa len() del catálogo cargado; sha y n registrados;
# puentes validados contra el catálogo cargado) + (2) Aquiles con claves correctas (p_H/n) + (3) HUB
# laterales_unico_v1: VOTO negativo Ricci–Forman vs billar (siempre-on, independiente de MODO_ESTRICTO),
# VOTO familias de tokens (EXPERIMENTAL, un voto por candidato; FAMILIAS_TOKENS=0 lo apaga), sensores de todas
# las líneas (Memento, matriz_corrida, luces, amantes, trazabilidad, integración, interrelación, alias, fix_entrada,
# gloria/sacro, Souriau, Z-RI, Tusi, Schrödinger, perfil del narrador, contraste formular_h, Aquiles bootstrap)
# + (4) protocolo_kernel orden 0 + (5) monomito v2 + (6) guardianes V1.2 con detrás v2 2.3.3.
# Laterales/sensores: can_decide_H=False; nunca escriben H ni el catálogo. MODO_ESTRICTO=0 apaga el cierre estricto.
# GUARDIANES_TROPOS_20260927 = GUARDIANES (3281c062) + guardián 9 TROPOS_BERISTAIN (vecino de falacias/Copi)
# + ruta de cierre latente: todo NO_RESUELTO o DOBLE_NEGACION_LITOTE de un guardián pone el CIERRE en
# LATENTE (motivo trazable, vía control_latencia_decimo_hombre), escribe el evento en StinkBox y corre
# tortugas (_resolution_pass con borroso=True) sobre esos cortes partidos más fino. H1/H2/top1 NO cambian.
# WORKING_OPEN_HYPOTHESES: cardinalidad variable, vectorización multiescala en fusión, apuesta por escenarios.
# H1/H2 conservados solo como alias de compatibilidad; salida primaria = hipotesis_trayectoria_abierta.
# GUARDIANES_20260927 = CONSOLIDADO (6f5174e6) + bloque "guardianes" al final de run():
# pruebas de control estructural siempre-on (décimo hombre/latencia, pregunta detrás v2,
# pregunta dirigida + post hoc, falacias 0.5.1, Copi, polaridad, hombre de acero, Sherlock/rigor
# con cadena_top1). can_decide_H=False: se verifica por hash que el predictor no cambia.
# CONSOLIDADO = V0.16.4 (compuerta + StinkBox v0.2 + Frye fix) + dynamis (V0.17, por candidato, catalogo cargado)
# + arco analogico pre-H (V0.18, bytes originales + limpieza) + (a) lentes por candidato (b) guardia de dimensiones
# constantes/duplicadas + empates por rango promedio + desempate sin nombre + EMPATE explicito (c) solo numericos
# al orden (d) puente de nombres/alias con log (g) Acero/zoomout y Capa2 cableados. Canon 244/Engine sin tocar.
# V0.16.4 = V0.16.3_E_LENTES + (a) latencia por frente escrita en StinkBox DESPUES de
# information_state; (b) COMPUERTA DE CIERRE (regla Mj): antes de cualquier cierre
# (DETERMINADO/H/apuesta) se revisan los pendientes vivos con la evidencia actual;
# si hay objeciones, la resolución operativa terminal activa tortugas y evidencia de casos semejantes.
# La latencia intermedia no se conserva como estado final; solo tokens nuevos quedan en memoria activa.
GATE_SEPARATION = 1.0     # == separated en _information_state
GATE_DISCARD_GAP = 2.0    # frente no-top a >= 2.0 del top1 -> resuelto en contra
GATE_ABSENT_LIMIT = 3     # cortes revisados sin el frente -> resuelto en contra
GATE_PENDING_TOPK = 10    # candidatos vivos considerados para abrir latencia por frente
DEFAULT_SEED = 20260924
CANON_HASH = "48333cd11b9234f1"
PATTERNS_SHA = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"  # sha del catálogo DEFAULT (v14); no es condición
PATTERNS_SHA_DEFAULT = PATTERNS_SHA
N_CANON = 244  # solo informativo (v14). El motor usa _n_patrones() = len(catálogo cargado).
import os as _oscat
def _PATTERNS_PATH() -> Path:
    """Ruta del catálogo de patrones: MOTOR_PATTERNS_PATH o patterns_final_v14.json junto al motor."""
    return Path(_oscat.environ.get("MOTOR_PATTERNS_PATH") or (BASE / "patterns_final_v14.json"))
def _n_patrones() -> int:
    p = _patterns()
    return len(p) if isinstance(p, (dict, list)) else 0

def _verify_patterns_contract() -> Dict[str, Any]:
    """Pin the default canonical catalogue; explicit overrides remain opt-in and auditable."""
    path = _PATTERNS_PATH()
    if not path.is_file():
        raise FileNotFoundError(f"CANONICAL_PATTERNS_MISSING:{path}")
    actual = _sha(path)
    custom = bool(_oscat.environ.get("MOTOR_PATTERNS_PATH"))
    expected = (_oscat.environ.get("MOTOR_PATTERNS_SHA256") if custom else PATTERNS_SHA)
    data = json.loads(path.read_text(encoding="utf-8"))
    count = len(data) if isinstance(data, (dict, list)) else -1
    if not custom and actual != PATTERNS_SHA:
        raise RuntimeError(f"CANONICAL_PATTERNS_HASH_MISMATCH:expected={PATTERNS_SHA}:actual={actual}")
    if not custom and count != N_CANON:
        raise RuntimeError(f"CANONICAL_PATTERNS_COUNT_MISMATCH:expected={N_CANON}:actual={count}")
    if custom and expected and actual != expected:
        raise RuntimeError(f"CUSTOM_PATTERNS_HASH_MISMATCH:expected={expected}:actual={actual}")
    return {"path": str(path), "sha256": actual, "n_patterns": count,
            "canonical_default": not custom, "hash_verified": bool(expected and actual == expected),
            "expected_sha256": expected,
            "status": "CANONICAL_VERIFIED" if (not custom and actual == PATTERNS_SHA and count == N_CANON)
                      else ("CUSTOM_HASH_VERIFIED" if custom and expected and actual == expected else "CUSTOM_HASH_UNPINNED")}
M = 0.998

# Corpus/contrato: no son decoración; se conservan como parte de la ejecución.
FORMULA_CORPUS = "Corpus_Final_Unificado_17_Formulas.txt"
FORMULAS = tuple(range(1, 18))

CORE_COMPONENTS = (
    "Engine_V5_CANONICO_SOLO.py", "patterns_final_v14.json", "MOTOR_V15_3_NATIVO_V0_9.py",
    "traza_campo_244.py", "sidecar_geometria.py", "sidecar_polti_caldero.py",
    "plugin_otto_numinoso.py", "plugin_embudo_clinico.py", "plugin_reporte_3d.py",
    "plugin_trayectoria_hosteleria.py", "estabilidad_vectorial_h.py", "plugin_aquiles_h.py",
    "motor_interrelacion_extensible_v0_1.py", "stinkbox_transport_v0_2.py", "plugin_sombrero_blanco_token.py", "sidecar_caldero_busqueda_arquetipos.py",
    "metacognition_v0_1.py",
    "tokens_laterales/dynamis_dramatica_sistemica_v0_1.json",
)
OPTIONAL_COMPONENTS = (
    "plugin_arquetipos_dinamicos.py", "plugin_guardia_no_cruce.py",
    "plugin_arco_field_snyder_mckee.py", "plugin_picos_mesetas.py",
    "plugin_familias_gloria_sacro.py", "plugin_sesgo_lectura.py",
    "plugin_alias_reactivacion.py", "plugin_fix_entrada.py",
    "plugin_pregunta_detras_v2.py", "plugin_metodo_rigor.py",
    "plugin_capa2_antecedentes_arquetipos.py", "plugin_circulo_monomito_v2.py",  # PATCH 006: antes plugin_circulo_monomito.py (v1 ausente)
    "plugin_pregunta_dirigida.py", "sidecar_caldero_busqueda_arquetipos.py", "predictor_vecinos_prefijo_v1.py",  # PATCH 006: antes caldero_run.py (SUPERADA por cuadrantes)
    "caldero_zoomout_acero_v0_1.py", "catalogo_capa2_familias_semilla.json",
    "billar_circular_convergencia_v0_2.py", "ricci_forman_coocurrencia_v0_1.py", "lente_lateral_metrics_v1_1_galileo.py",
    "autoevidencia_stores_011.py",  # PATCH 011
    "filtro_relleno_013.py",  # PATCH 013
    "sujetos_014.py",  # PATCH 014
)
GUARDIAN_COMPONENTS = (
    "guardianes_control_v1.py", "control_latencia_decimo_hombre.py", "plugin_pregunta_detras_v2.py",
    "plugin_pregunta_dirigida_v0_5_1.py", "guardian_logica_copi_v1.py", "plugin_polaridad_causal.py",
    "sidecar_ablacion_hombre_acero.py", "guardian_acero_rival_v1.py", "plugin_metodo_rigor.py",
    "guardian_tropos_beristain_v1.py", "decimo_hombre_esteroides_mayeutica_v1.py",
)


def _h_snapshot(pred):
    """Huella del predictor (H1/H2/candidatos/estado) para probar que los guardianes no lo tocan."""
    return hashlib.sha256(json.dumps(pred, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def _load(name: str, filename: str):
    p = BASE / filename
    if not p.exists():
        p = BASE / "plugins" / filename
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, str(p))
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(name, None)
        return None
    return mod


def _prefijo_monomito(cuts, vocab):
    """PATCH 005: prefijo de estados monomíticos SOLO desde el input (sin inferencia).
    Por corte: clave explícita (estado_monomito|monomito|etapa_monomito|stage) o un único token P/A/C
    idéntico (casefold) a un estado del vocabulario del corpus. 0 o >1 estados => se corta el prefijo."""
    voc={str(v).casefold():v for v in vocab}; pref=[]; det=[]
    for i,c in enumerate(cuts or []):
        cid=c.get("id") or c.get("corte") or i
        exp=next((c.get(k) for k in ("estado_monomito","monomito","etapa_monomito","stage") if c.get(k)),None)
        if exp is not None and str(exp).casefold() in voc:
            det.append({"corte":cid,"estado":voc[str(exp).casefold()],"fuente":"clave_explicita"}); pref.append(voc[str(exp).casefold()]); continue
        hits=sorted({voc[str(t[0] if isinstance(t,(list,tuple)) else t).strip().casefold()] for e in ("P","A","C") for t in (c.get(e) or [])
                     if str(t[0] if isinstance(t,(list,tuple)) else t).strip().casefold() in voc})
        if len(hits)==1:
            det.append({"corte":cid,"estado":hits[0],"fuente":"token_exacto_PAC"}); pref.append(hits[0]); continue
        det.append({"corte":cid,"estado":None,"fuente":"ambiguo" if hits else "sin_estado","candidatos":hits})
        break
    return pref,det


def _sha(p: Path) -> Optional[str]:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None




# --- PROTOCOLO TRANSVERSAL ABSORBIDO (guardia / rigor / pregunta / sombrero blanco) ---
# Estas funciones se recuperan/adaptan de implementaciones V15.1 anteriores.
# No modifican 244, Engine_V5 ni R732; controlan frontera, contaminación y trazabilidad.
CAMPOS_PROHIBIDOS = {"probability","probabilidad","weight","peso","confidence","confianza","prob"}

class ContaminacionBayesianaError(Exception):
    pass

class CampoProbabilisticoProhibidoError(Exception):
    pass

class GuardiaNoCruce:
    """Protege el estado del motor mientras se ejecutan lentes laterales."""
    def __init__(self, hypotheses_state, corte_id):
        self.hypotheses_state = hypotheses_state
        self.corte_id = corte_id
        self._snapshot_antes = None
    def __enter__(self):
        import copy
        self._snapshot_antes = copy.deepcopy(self.hypotheses_state)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        for hid, before in self._snapshot_antes.items():
            after = self.hypotheses_state.get(hid)
            if after != before:
                raise ContaminacionBayesianaError(
                    f"corte={self.corte_id} hipotesis={hid} cambio durante lente lateral"
                )
        return False
    def validar_output_lente(self, output, ruta=""):
        if isinstance(output, dict):
            for k,v in output.items():
                r = f"{ruta}.{k}" if ruta else k
                if k.lower() in CAMPOS_PROHIBIDOS:
                    raise CampoProbabilisticoProhibidoError(
                        f"corte={self.corte_id} campo probabilistico prohibido: {r}"
                    )
                self.validar_output_lente(v, r)
        elif isinstance(output, list):
            for i,item in enumerate(output):
                self.validar_output_lente(item, f"{ruta}[{i}]")


PROTOCOL_NOISE_RE = re.compile(
    r"(?i)\b(juicio\s+est[eé]tico|fecha\s+de\s+protocolo|sombrero\s+blanco|"
    r"recorte\s+de\s+protocolo|metadato\s+de\s+protocolo)\b"
)

def _protocol_quality(case):
    """Sombrero blanco + rigor de entrada: datos observables pasan; metadatos de protocolo no crean evidencia."""
    q = str(case.get("question", case.get("case_id", "")))
    facts=[]
    for c in case.get("cuts") or []:
        facts.append({"id":c.get("id"),"P":len(c.get("P") or []),"A":len(c.get("A") or []),"C":len(c.get("C") or [])})
    return {
        "status":"PASS",
        "sombrero_blanco":"ENFORCED",
        "question_present":bool(q),
        "protocol_noise_in_question":bool(PROTOCOL_NOISE_RE.search(q)),
        "facts_only_boundary":True,
        "no_probabilistic_fields_in_input":not any(
            any(str(k).lower() in CAMPOS_PROHIBIDOS for k in c.keys()) for c in case.get("cuts") or []
        ),
        "observed_cut_shape":facts,
    }

def _run_transversal_guards(case, motor, features):
    """Run absorbed controls after native engine and before predictor."""
    q=_protocol_quality(case)
    # Snapshot the native candidate boards. Validate all lateral outputs without allowing them to mutate boards.
    boards_state={}
    for c in motor.get("cuts") or []:
        cid=c.get("corte")
        boards_state[cid]={
            "P":tuple(c.get("P_top5_ANEXO") or []),
            "A":tuple(c.get("A_top5_ANEXO") or []),
            "C":tuple(c.get("C_top5_ANEXO") or []),
        }
    guard=GuardiaNoCruce(boards_state,"ALL_CUTS")
    with guard:
        for name,out in features.items():
            guard.validar_output_lente(out, name)
    rigor={
        "input_schema":"PASS",
        "canonical_244":len(motor.get("cuts") or [])>0 and motor.get("n_canon") is not None and len(((motor.get("cuts") or [{}])[-1].get("P_FULL_244") or {}))==_n_patrones(),
        "R732":bool((motor.get("R732") or {}).get("X_shape")),
        "no_lateral_bayes_write":True,
        "no_rewrite_prior_cut":True,
        "candidate_fallback":"PROHIBITED",
        "inverse_engineering":"DEFERRED_UNTIL_FUTURE_REVEAL",
    }
    return {"question_white_hat":q,"guardia_no_cruce":{"status":"PASS","scope":"features_before_predictor"},"metodo_rigor":rigor}


def _validate_case(case: Dict[str, Any]) -> None:
    if not isinstance(case, dict) or not case.get("cuts"):
        raise ValueError("INPUT_INVALIDO: falta cuts")
    if not case.get("case_id"):
        raise ValueError("INPUT_INVALIDO: falta case_id")
    z90 = case.get("z90_date")
    for c in case["cuts"]:
        if not c.get("id"):
            raise ValueError("INPUT_INVALIDO: corte sin id")
        if z90 and c.get("date") and str(c["date"]) > str(z90):
            raise ValueError(f"POST_Z90_EN_INPUT: {c['id']}")
        for eje in ("P", "A", "C"):
            for pair in c.get(eje) or []:
                if len(pair) != 2:
                    raise ValueError(f"TOKEN_INVALIDO {c['id']} {eje}")
                if not (0.60 <= float(pair[1]) <= 0.84):
                    raise ValueError(f"PESO_FUERA_DE_CONTRATO {c['id']} {eje} {pair}")


def _run_module_features(cuts, motor: Dict[str, Any], question: str = "", ceb=None) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Run available native/lateral modules without modifying canonical 244/PAC/R732/FREEZE.
    Optional modules are now distinguished from missing files; no module is silently labeled OFF.
    """
    features: Dict[str, Any] = ceb.observable({}, "features") if ceb else {}
    status: List[Dict[str, Any]] = []

    def run(name, fn):
        if _off(name):
            status.append({"component": name, "status": "APAGADO_ABLACION", "feeds_predictor": False}); return
        try:
            def _ceb_body():
                out = fn()
                features[name] = out
                return out
            out = ceb.call(name, _ceb_body, shared=[features, motor]) if ceb else _ceb_body()
            _d6=_decl_u6(name)
            status.append({"component": name, "status": "EXECUTED",
                           "feeds_predictor": (_d6 is None or _d6[0] in ("ACTIVA","CABLEADA_SIN_SENAL_EN_CASO")),
                           **({"declaracion_U6": _d6[0], "motivo_declaracion_U6": _d6[1]} if _d6 else {})})
        except Exception as e:
            status.append({"component": name, "status": "ERROR", "feeds_predictor": False,
                           "error": f"{type(e).__name__}:{e}"})

    # Native core lenses already part of V0.7
    geo = _load("u_geo", "sidecar_geometria.py")
    if geo and hasattr(geo, "observar_corrida"):
        run("geometria", lambda: geo.observar_corrida(motor))
    polti = _load("u_polti", "sidecar_polti_caldero.py")
    if polti and hasattr(polti, "observar_corrida"):
        run("polti_caldero", lambda: polti.observar_corrida(motor))
    annex = motor.get("annex") or {}
    if annex.get("traza_P") not in (None, "plugin ausente") and not _off("traza_campo_244"):
        # PATCH 010b: una sola clave en features (antes "traza_campo_244" + "traza_campo_244.py" con el MISMO
        # contenido -> el puente de nombres sumaba la señal dos veces en rank_fusion).
        run("traza_campo_244", lambda: annex["traza_P"])
        if status and status[-1].get("component") == "traza_campo_244":
            status[-1]["archivo"] = "traza_campo_244.py"; status[-1]["nota"] = "PATCH 010b: clave única (antes duplicada)"
    rep=_load("u_rep3d","plugin_reporte_3d.py")
    if rep and hasattr(rep,"leer"):
        seq=[(c.get("corte"), dict(c.get("P_top5_ANEXO") or [])) for c in motor.get("cuts") or []]
        run("plugin_reporte_3d", lambda: rep.leer(seq))

    toks=[]; per_cut=[]
    for c in cuts:
        ct=[]
        for eje in ("P","A","C"):
            ct.extend(str(t) for t,_ in (c.get(eje) or []))
        per_cut.append((c["id"],ct)); toks.extend(ct)
    tokset=set(toks)

    otto=_load("u_otto","plugin_otto_numinoso.py")
    if otto and hasattr(otto,"OTTO"):
        def do_otto():
            out={}
            for name,f in (getattr(otto,"OTTO",{}) or {}).items():
                fav=set(f.get("tokens_favor") or {}); con=set(f.get("tokens_contra") or {})
                out[name]={"favor":sorted(fav&tokset),"contra":sorted(con&tokset),"neto":round(len(fav&tokset)-len(con&tokset),6)}
            return out
        run("otto_numinoso",do_otto)
    emb=_load("u_emb","plugin_embudo_clinico.py")
    if emb and hasattr(emb,"CLINICO"):
        run("embudo_clinico", lambda: [{"corte":cid,"clinico":sorted(set(ts)&set(emb.CLINICO)),"co_oficio":sorted(set(ts)&set(getattr(emb,"CO_OFICIO",set())))} for cid,ts in per_cut])
    hotel=_load("u_hotel","plugin_trayectoria_hosteleria.py")
    if hotel:
        def do_hotel():
            pat=getattr(hotel,"PATRON",{}) or {}; fav=set(pat.get("tokens_favor") or {}); con=set(pat.get("tokens_contra") or {})
            return {"favor":sorted(fav&tokset),"contra":sorted(con&tokset),"neto":len(fav&tokset)-len(con&tokset)}
        run("trayectoria_hosteleria",do_hotel)
    stab=_load("u_stab","estabilidad_vectorial_h.py")
    if stab and hasattr(stab,"evaluar"):
        rows=[((c.get("P_top5_ANEXO") or [None,None])[0][0],float((c.get("P_top5_ANEXO") or [None,None])[0][1])) for c in motor.get("cuts") or [] if c.get("P_top5_ANEXO")]
        if rows: run("estabilidad_vectorial", lambda: stab.evaluar(rows[-2][1],rows[-1][1],rows[-2][0],rows[-1][0]) if len(rows)>1 else stab.evaluar(rows[0][1],rows[0][1],None,rows[0][0]))
    aq=_load("u_aq","plugin_aquiles_h.py")
    if aq and hasattr(aq,"evaluar_serie"):
        def do_aq():
            pts=[]
            for c in motor.get("cuts") or []:
                top=c.get("P_top5_ANEXO") or []
                # UNICO: claves correctas del plugin (p_H, n, winner, topk). Antes 'p'/'corte' -> salida siempre nula.
                pts.append({"n":len(pts)+1,"corte":c.get("corte"),"winner":top[0][0] if top else None,"p_H":float(top[0][1]) if top else None,"topk":[x[0] for x in top[:3]]})
            out=aq.evaluar_serie(pts)
            out={k:v for k,v in out.items()}
            out["lectura"]="serie por cortes: p_H = p del top P de cada corte; winner = top P del corte (claves p_H/n corregidas)"
            return out
        run("aquiles_h",do_aq)

    # V0.16.3-E: lateral lenses Billar v0.2 (corte2), Ricci-Forman v0.1, lateral_metrics v1.1.
    # Feed lateral convergence/ranking only via per-family "score" share in [0,1]; never write H.
    bil=_load("u_billar_v02","billar_circular_convergencia_v0_2.py")
    if bil and hasattr(bil,"correr_cuts"):
        def do_billar():
            o=bil.correr_cuts(motor.get("cuts") or [], "motor_run")
            n=max(1,o["v0_2"]["N_real"]); cnt={}
            for e in o["convergencias_v0_2"]:
                for f in e["familias"]: cnt[f]=cnt.get(f,0)+1
            return {"lens":"billar_circular_v0_2","Alimenta_H":"NO","writes_H":False,
                    "N_real_v0_1":o["v0_1"]["N_real"],"z_v0_1":o["v0_1"]["null"]["z_score"],
                    "N_real_v0_2":o["v0_2"]["N_real"],"null_v0_2":o["v0_2"]["null"],
                    "excluded_both_empty":o["v0_2"]["excluded_both_empty_convergences"],
                    "both_present_vivo":o["v0_2"]["both_present_vivo"],
                    "por_familia":{f:{"score":round(c/n,6),"n_conv":c} for f,c in sorted(cnt.items())}}
        run("billar_circular_v0_2",do_billar)
    ric=_load("u_ricci_v01","ricci_forman_coocurrencia_v0_1.py")
    if ric and hasattr(ric,"correr_cuts"):
        def do_ricci():
            o=ric.correr_cuts(motor.get("cuts") or [], "motor_run")
            strength={}
            for k,w in (o.get("flujo_un_paso_w") or {}).items():
                a,b=k.split("|"); strength[a]=strength.get(a,0.0)+w; strength[b]=strength.get(b,0.0)+w
            tot=sum(strength.values()) or 1.0
            return {"lens":"ricci_forman_v0_1","Alimenta_H":"NO","writes_H":False,"gamma":o["gamma"],
                    "curvature_method":o.get("curvature_method","UNSPECIFIED"),
                    "forman_ricci_verified":bool(o.get("forman_ricci_verified",False)),
                    "graph_topology":o.get("graph_topology","UNSPECIFIED"),
                    "note_method":o.get("note_method","No method note supplied by sidecar."),
                    "media_Ric":o["ricci"]["media"],"null":o["nulo"],"z_media_Ric":o["z_media_Ric"],
                    "top3_abs_Ric":o["ricci"]["aristas"][:3],
                    "por_familia":{f:{"score":round(v/tot,6)} for f,v in sorted(strength.items())}}
        run("ricci_forman_v0_1",do_ricci)
    lmet=_load("u_lateral_metrics_v11","lente_lateral_metrics_v1_1_galileo.py")
    if lmet and hasattr(lmet,"correr_motor"):
        run("lateral_metrics_v1_1",lambda: lmet.correr_motor(motor))

    # CONSOLIDADO (g): Acero/zoom-out (proxy sobre traza_P) y Capa 2 (antecedentes). Laterales, nunca H.
    acero=_load("u_acero","caldero_zoomout_acero_v0_1.py")
    if acero and hasattr(acero,"run") and annex.get("traza_P") not in (None,"plugin ausente"):
        run("acero_zoomout", lambda: acero.run({"annex":{"traza_P":annex["traza_P"]}}, str(BASE/"MOTOR_V15_3_NATIVO_V0_9.py")))
    else:
        status.append({"component":"caldero_zoomout_acero_v0_1.py","status":"PLUGIN_SALTADO","reason":"archivo_o_traza_no_disponible","effect":"sin_ejecucion"})
    capa2=_load("u_capa2","plugin_capa2_antecedentes_arquetipos.py")
    cat2=BASE/"catalogo_capa2_familias_semilla.json"
    if capa2 and hasattr(capa2,"leer") and cat2.is_file():
        run("capa2_antecedentes", lambda: capa2.leer({cid:ts for cid,ts in per_cut}, catalogo_path=str(cat2)))
    else:
        status.append({"component":"plugin_capa2_antecedentes_arquetipos.py","status":"PLUGIN_SALTADO","reason":"archivo_o_catalogo_no_disponible","effect":"sin_ejecucion"})

    # Optional/lateral modules that were previously only listed in inventory.
    seq=[(c["id"], dict((motor.get("cuts") or [])[i].get("P_top5_ANEXO") or {})) for i,c in enumerate(cuts)]
    # PATCH18: el sensor de sesgo necesita comparar el letrero #1 entre cortes.
    # El ranking P por corte ya lo emite el motor; antes el adaptador descartaba
    # ese dato y solo pasaba tokens, provocando H_de/H_a ausentes en todas las transiciones.
    mcuts = motor.get("cuts") or []
    dx = ((motor.get("R732") or {}).get("dX_norm") or [])
    cuts_dict=[]
    for i,c in enumerate(cuts):
        mc = mcuts[i] if i < len(mcuts) and isinstance(mcuts[i], dict) else {}
        ptop = mc.get("P_top5_ANEXO") or []
        h_cut = ptop[0][0] if ptop and isinstance(ptop[0], (list, tuple)) and ptop[0] else None
        row = {
            "id": c.get("id") or mc.get("corte") or f"C{i+1}",
            "tokens": sum(([t for t,_ in (c.get(e) or [])] for e in ("P","A","C")),[]),
            "H": h_cut,
            "H_fuente": "motor.cuts[].P_top5_ANEXO[0]",
        }
        # PLUGIN_ARCO uses delta_max only to detect whether a beat is noticeable.
        # Use the real R732 transition norm for cuts with a predecessor; do not
        # fabricate delta_neto/sign (that would falsely imply a McKee value flip).
        if i > 0 and i - 1 < len(dx):
            row["delta_max"] = float(dx[i - 1])
            row["delta_max_fuente"] = "motor.R732.dX_norm[cut_index-1]"
        cuts_dict.append(row)
    for fn, api, payload in [
        ("plugin_picos_mesetas.py","curvas",seq),
        ("plugin_arco_field_snyder_mckee.py","leer",cuts_dict),
        ("plugin_sesgo_lectura.py","leer",cuts_dict),
    ]:
        mod=_load("opt_"+fn.replace('.','_'),fn)
        if mod is None:
            status.append({"component":fn,"status":"PLUGIN_SALTADO","reason":"archivo_no_disponible","effect":"sin_ejecucion"})
        elif hasattr(mod,api):
            if fn=="plugin_picos_mesetas.py" and not _off("picos_score_u6"):
                def _picos_u6(mod=mod,api=api,payload=payload):
                    o=getattr(mod,api)(payload)
                    for _k,_c in ((o or {}).get("curvas") or {}).items():
                        _fz=str(_c.get("forma") or "")
                        # U6: misma lectura del plugin (signo con su eps); fracción de ↗ en la serie. No usa datos post-Z.
                        _c["score"]=round(_fz.count("↗")/len(_fz),6) if _fz else 0.0
                    if isinstance(o,dict): o["score_u6"]="score=fracción de transiciones ↗ (eps del plugin) por familia; señal lateral can_decide_H=False"
                    return o
                run(fn,_picos_u6)
            else:
                run(fn,lambda mod=mod,api=api,payload=payload:getattr(mod,api)(payload))
        else:
            status.append({"component":fn,"status":"CABLEADO_NO_EJECUTADO","reason":"API_no_encontrada","effect":"sin_ejecucion"})

    # Question/rigor controls are observational and do not alter H.
    qd=_load("opt_qd","plugin_pregunta_detras_v2.py")
    if qd and hasattr(qd,"interrogar"): run("plugin_pregunta_detras",lambda:qd.interrogar(question))
    else: status.append({"component":"plugin_pregunta_detras_v2.py","status":"PLUGIN_SALTADO","reason":"archivo_no_disponible","effect":"sin_ejecucion"})
    rigor=_load("opt_rigor","plugin_metodo_rigor.py")
    # PATCH 010b: rigor() lee out["cadena_top1"]; antes se le pasaba motor (sin esa clave) -> salida constante.
    if rigor and hasattr(rigor,"rigor"): run("plugin_metodo_rigor",lambda:rigor.rigor({"cadena_top1":" → ".join(str(((c.get("P_top5_ANEXO") or [[None]])[0][0])) for c in motor.get("cuts") or [])}))
    else: status.append({"component":"plugin_metodo_rigor.py","status":"PLUGIN_SALTADO","reason":"archivo_no_disponible","effect":"sin_ejecucion"})
    # U6 #2: semiotica_deriva_v0_1 cableada como TRAZA_SOLO (antes 0 llamadas). Marca SIGNIFICANTE_SIN_OBJETO / SIGNO_AISLADO.
    #   Su 'por_familia' suma también tokens CONTRA como apoyo: por eso NO entra al puente de nombres (BRIDGE_EXCLUDE).
    sem=_load("opt_sem","semiotica_deriva_v0_1.py")
    if sem and hasattr(sem,"revisar") and not _off("semiotica_deriva"):
        def _sem_u6():
            o=dict(sem.revisar({"cuts":cuts},{}))
            o["feeds_predictor"]=False; o["can_decide_H"]=False; o["rol_U6"]="TRAZA_SOLO"
            return o
        run("semiotica_deriva",_sem_u6)
        if status and status[-1].get("component")=="semiotica_deriva":
            status[-1].update({"feeds_predictor":False,"declaracion_U6":"TRAZA_SOLO","motivo_declaracion_U6":"traza semiótica; por_familia cuenta tokens contra como apoyo -> no apta como señal de ranking"})
    dyn=_load("opt_dyn","plugin_arquetipos_dinamicos.py")
    if dyn and hasattr(dyn,"info"): run("plugin_arquetipos_dinamicos",dyn.info)
    guard=_load("opt_guard","plugin_guardia_no_cruce.py")
    if guard and hasattr(guard,"GuardiaNoCruce"):
        status.append({"component":"plugin_guardia_no_cruce.py","status":"ABSORBIDO_EN_GUARDIA_TRANSVERSAL","feeds_predictor":False,"role":"control_only",
                       "reason":"absorbido: la lógica corre en GuardiaNoCruce dentro de _run_transversal_guards (protocol_controls); el archivo no se invoca como API","execution_note":"La lógica efectiva corre en GuardiaNoCruce absorbido dentro de _run_transversal_guards; el archivo se carga como artefacto auxiliar, no se invoca como API independiente."})
    # Monomito se ejecuta después del Caldero para que su resolución Q1-Q4
    # reciba la pregunta activa y los vecinos Caldero CURRENT del run.
    # La memoria persistente no se inyecta como evidencia corriente por sí sola.
    qdir=_load("opt_qdir","plugin_pregunta_dirigida.py")
    if qdir and hasattr(qdir,"detectar_pregunta_dirigida"):
        run("plugin_pregunta_dirigida",lambda:qdir.detectar_pregunta_dirigida(question))
        # PATCH 010b: 0 hallazgos != ACTIVA. Estado explícito con motivo (la salida vacía queda tal cual).
        if status and status[-1].get("component")=="plugin_pregunta_dirigida" and status[-1].get("status")=="EXECUTED" and not features.get("plugin_pregunta_dirigida"):
            status[-1]["status"]="EXECUTED_SIN_HALLAZGOS"
            status[-1]["reason"]="pregunta es un identificador (sin lenguaje natural)" if (" " not in str(question).strip()) else "pregunta neutral: 0 estructuras dirigidas detectadas"
    # These are real artifacts but may be unavailable or inapplicable; never claim execution without a successful call.
    # PATCH 006 (2026-10-06): Caldero II ya no usa escaleta lineal externa; la escaleta fue sustituida por
    # cuadrantes circulares (plugin_circulo_monomito_v2: Q1-Q4 por co-ocurrencia de tokens P/A/C del corte
    # + vecinos Caldero del run, ver bloque MONOMITO + CALDERO en run()). La fila caldero_run.py era un gate
    # fijo que reportaba PLUGIN_SALTADO sin intentar nada.
    _circ_chk=_load("opt_circ_chk","plugin_circulo_monomito_v2.py")
    if _circ_chk is not None and hasattr(_circ_chk,"posicion_por_corte"):
        status.append({"component":"caldero_run.py","status":"SUPERADA","superada_por":"plugin_circulo_monomito_v2.py",
                       "reason":"escaleta lineal (Marco-16 / Caldero II 2.0 f670b872) sustituida por cuadrantes circulares Q1-Q4 derivados de los cortes; ver fila plugin_circulo_monomito_v2.py",
                       "effect":"sin_ejecucion_propia","feeds_H":False,"can_decide_H":False})
    else:
        status.append({"component":"caldero_run.py","status":"PLUGIN_SALTADO","reason":"ni caldero_run.py ni plugin_circulo_monomito_v2.py disponibles","effect":"sin_ejecucion"})
    # PATCH 005 (2026-10-06): predictor_vecinos_prefijo_v1 trae su corpus (15 biografías codificadas) dentro del
    # archivo; lo único que necesita es el PREFIJO de estados monomíticos del caso. Antes: gate fijo
    # CABLEADO_NO_EJECUTADO sin intentar. Ahora: se intenta con el input real (clave explícita por corte o token
    # P/A/C que coincida EXACTO con el vocabulario del corpus). No se infiere etapa desde cuadrante ni sinónimos.
    _vp=_load("opt_vecpref","predictor_vecinos_prefijo_v1.py")
    if _vp is None or not hasattr(_vp,"predict_next"):
        status.append({"component":"predictor_vecinos_prefijo_v1.py","status":"PLUGIN_SALTADO","reason":"archivo_o_API_no_disponible","effect":"sin_ejecucion"})
    else:
        _vocab={x for _seq in getattr(_vp,"BIOGRAFIAS",{}).values() for x in _seq}
        _pref,_det=_prefijo_monomito(cuts,_vocab)
        if _pref:
            try:
                _r=_vp.predict_next(list(_pref),top_n=5)
                status.append({"component":"predictor_vecinos_prefijo_v1.py","status":"EXECUTED","feeds_predictor":False,"feeds_H":False,"can_decide_H":False,
                               "prefijo":_pref,"prefijo_detalle":_det,"resultado":{k:_r.get(k) for k in ("eligible_reference_count","transition_candidates","selected_neighbors") if k in _r},
                               "nota":"voto t+1 lateral (Caldero B); no es probabilidad poblacional; no entra al ranking"})
            except Exception as _e:
                status.append({"component":"predictor_vecinos_prefijo_v1.py","status":"ERROR","error":f"{type(_e).__name__}:{_e}","prefijo":_pref})
        else:
            status.append({"component":"predictor_vecinos_prefijo_v1.py","status":"SIN_PREFIJO_EN_INPUT","feeds_predictor":False,"feeds_H":False,"can_decide_H":False,
                           "reason":"ningún corte inicial trae estado monomítico (clave estado_monomito/monomito/etapa_monomito o token exacto del vocabulario de las 15 biografías); no se rellena",
                           "prefijo_detalle":_det,"effect":"sin_voto"})

    return features,status


def _extract_named_hits(obj: Any, candidate: str) -> float:
    """Candidate-specific lateral evidence. Only explicit name matches count."""
    if isinstance(obj, dict):
        s=0.0
        for k,v in obj.items():
            if k == candidate:
                if isinstance(v,(int,float)): s += float(v)
                elif isinstance(v,dict):
                    for z in ("neto","score","p","delta"):
                        if isinstance(v.get(z),(int,float)): s += abs(float(v[z]))
            s += _extract_named_hits(v,candidate)
        return s
    if isinstance(obj,list):
        return sum(_extract_named_hits(v,candidate) for v in obj)
    return 0.0


def _load_auxiliary_neighbor_memory(features: Dict[str, Any]) -> Dict[str, Any]:
    """Read persisted Caldero neighbors as auxiliary evidence only.

    This is deliberately outside canonical 244/P-A-C/H. It makes the persistence
    layer actually reusable by later cuts/cases without converting lateral tokens
    into canonical patterns.
    """
    explicit = features.get("caldero_neighbor_memory")
    if isinstance(explicit, dict):
        return explicit
    # PATCH 011: memoria sin eventos del mismo case_id / mismo input sha (autoevidencia no cuenta).
    _m011 = _RUN_CTX.get("vecinos_011")
    if isinstance(_m011, dict) and _m011.get("status") != "ERROR":
        return _m011
    root = features.get("caldero_neighbor_store_root") or (BASE / "vecinos_caldero")
    idx = Path(root) / "neighbor_index.json"
    if not idx.is_file():
        return {"status":"ABSENT", "unique_tokens":[], "observations":0, "cases":0}
    try:
        data=json.loads(idx.read_text(encoding="utf-8"))
        neighbors=data.get("neighbors") or {}
        observations=sum(int(v.get("observations",0) or 0) for v in neighbors.values())
        cases=set()
        for v in neighbors.values(): cases.update(v.get("cases") or [])
        return {"status":"PRESENT", "unique_tokens":sorted(neighbors),
                "observations":observations, "cases":len(cases),
                "store":str(idx)}
    except Exception as exc:
        return {"status":"ERROR", "unique_tokens":[], "observations":0,
                "cases":0, "error":f"{type(exc).__name__}:{exc}"}


def _relational_activity(features: Dict[str,Any]) -> float:
    """Normalized relational signal; never selects or writes H directly."""
    inter=features.get("interrelation") or {}
    hyper=len(inter.get("hyperrelations") or [])
    movement=len(inter.get("movement") or [])
    tokens=len(inter.get("unique_tokens") or [])
    cuts=max(1, len(features.get("cuts") or []))
    # Bound the signal so relation count cannot dominate the rank-fusion engine.
    raw=float(hyper + movement + tokens)
    capacity=float(cuts*3)
    return float(raw/(raw+capacity)) if raw>0 else 0.0


# --- CAPA ESTRUCTURAL LATERAL: Propp + Booker + Greimas + Frye ---
# No añade fichas al canon 244. Los pesos son calibración lateral, no pesos canónicos.
STRUCTURAL_CALIBRATION = {
    "propp": {"propp_02_prohibicion_guardrail":0.85,"propp_03_transgresion_bifurcacion":0.89,"propp_08_dano_atricion":0.92,"propp_14_recibir_agente_auxilio":-0.84},
    "booker": {"booker_overcoming_monster":0.78,"booker_rags_to_riches":0.83,"booker_voyage_return":0.75,"booker_tragedy_collapse":0.91},
    "greimas": {"actante_sujeto_operador":1.0,"actante_objeto_meta":1.0,"actante_destinador_origen":1.0,"actante_oponente_friccion":0.76},
    "frye": {"frye_modo_mitico":0.95,"frye_alto_mimetico":0.72,"frye_bajo_mimetico":0.50,"frye_modo_ironico":0.88},
}

def _clip01(x): return max(0.0,min(1.0,float(x)))

# ===================== CONSOLIDADO 20260927: helpers =====================
import os as _os, unicodedata as _ud
DYNAMIS_CATALOG = "tokens_laterales/dynamis_dramatica_sistemica_v0_1.json"
TIE_EPS = 1e-12
EMPATE_EPS = 1e-9

def _off_set():
    """Ablation switches (diagnostic only): env CONSOLIDADO_OFF or case['consolidado_off']."""
    s=set(x.strip() for x in (_os.environ.get("CONSOLIDADO_OFF","") or "").split(",") if x.strip())
    s|=set(_RUN_CTX.get("case_off") or [])
    return s
_RUN_CTX={}
def _off(name): return name in _off_set()

# U6 #1 (2026-10-12): declaración VERAZ de cada componente frente al ranking (rank_fusion).
#   ACTIVA                       -> su salida llega a rank_fusion como señal lateral o dimensión (can_decide_H=False siempre)
#   CABLEADA_SIN_SENAL_EN_CASO   -> hay vía real al ranking; en este caso la entrada está vacía o es igual para todas las candidatas
#   TRAZA_SOLO                   -> salida de nivel caso (sin campo por candidata): por construcción no puede ordenar candidatas
#   ACTIVA_MUDA_SIN_MAPEO        -> salida por entidad, pero en un espacio de nombres fuera del 244 sin puente aprobado (no se inventa mapeo)
#   FILTRO_AGUAS_ARRIBA          -> no produce dimensión: filtra/condiciona la entrada de otra pieza que sí llega
_DECL_U6={
 "geometria":("TRAZA_SOLO","lee R732 (dX_norm, persist_cos, kappa_dir) del motor; la misma señal R732 entra al vector de candidata por vía directa (geometric_inertia_alignment, geometric_direction_change; PATCH11). El sidecar no se suma dos veces"),
 "otto_numinoso":("ACTIVA_MUDA_SIN_MAPEO","neto por familias otto_* que no están en el 244 ni en PUENTE_244_FAMILIAS; mapearlas sería inventar familias"),
 "embudo_clinico":("TRAZA_SOLO","listas clínicas / co-oficio por corte (nivel caso), sin campo por candidata"),
 "trayectoria_hosteleria":("ACTIVA_MUDA_SIN_MAPEO","favor/contra de la plantilla hostelería (no es familia del 244); sin puente aprobado"),
 "estabilidad_vectorial":("TRAZA_SOLO","estado de estabilidad de la H ya calculada (post-ranking); control de cierre, no ordena candidatas"),
 "aquiles_h":("TRAZA_SOLO","SEGUIR/PARAR por ventanas sobre la H (nivel caso); control de cierre, no ordena candidatas"),
 "capa2_antecedentes":("ACTIVA_MUDA_SIN_MAPEO","estereotipos/prototipos capa2 (estereo_*, alianza_*...) fuera del 244; el propio plugin declara que SUGIERE luces, no apuesta"),
 "plugin_arco_field_snyder_mckee.py":("TRAZA_SOLO","beats Field/Snyder/McKee por corte (nivel caso)"),
 "plugin_sesgo_lectura.py":("TRAZA_SOLO","transiciones de letrero entre cortes (nivel caso); sospecha de sesgo, no ordena"),
 "plugin_pregunta_detras":("TRAZA_SOLO","control de la pregunta (marcajes ETIQUETA_SUJETO); no tiene salida por candidata"),
 "plugin_metodo_rigor":("TRAZA_SOLO","alarma HECATE sobre la cadena top1 por corte (nivel caso)"),
 "plugin_pregunta_dirigida":("TRAZA_SOLO","hallazgos sobre la pregunta (nivel caso)"),
 "plugin_arquetipos_dinamicos":("ACTIVA_MUDA_SIN_MAPEO","info() devuelve 3 claves PROPUESTAS fuera del 244, sin valor por caso"),
 "plugin_circulo_monomito_v2.py":("TRAZA_SOLO","posición/cuadrante por corte en tokens, sin nombres de candidata; recibe vecinos Caldero"),
 "plugin_arcos_emocionales_laterales.py":("ACTIVA_MUDA_SIN_MAPEO","arcos del catálogo lateral (no 244); sus arcos ACTIVOS siembran la consulta ciega pre-H (aguas arriba), no el ranking"),
 "sujetos_014.py":("FILTRO_AGUAS_ARRIBA","identidad de sujeto: condiciona autoevidencia_stores_011 (un sujeto cuenta una vez); no es dimensión"),
 "filtro_relleno_013.py":("FILTRO_AGUAS_ARRIBA","saca relleno/años del voto de vecinos (caldero_neighbor_*); lo consume el predictor vía _RUN_CTX"),
 "plugin_cameo_institucional.py":("CABLEADA_SIN_SENAL_EN_CASO","dims cameo_activity/cameo_profile_activity son de nivel caso (iguales para todas); sus tokens explícitos van al bus de luces -> interrelation -> relational_alignment"),
 "sidecar_caldero_busqueda_arquetipos.py":("CABLEADA_SIN_SENAL_EN_CASO","vía caldero_neighbor_alignment; sin fuentes de búsqueda (offline / input sin caldero_search_sources) no hay vecinos"),
 "vecinos_caldero/neighbor_store.py":("CABLEADA_SIN_SENAL_EN_CASO","vía caldero_neighbor_memory/alignment; store vacío en la corrida estándar"),
 "motor_interrelacion_extensible_v0_1.py":("CABLEADA_SIN_SENAL_EN_CASO","vía relational_alignment; solo trabaja sobre external_lights/external_activations, ausentes en el input"),
 "stinkbox_to_light_bus_v1":("CABLEADA_SIN_SENAL_EN_CASO","vía relational_alignment; sin luces persistentes registradas"),
 "stinkbox_transport_v0_2.py":("CABLEADA_SIN_SENAL_EN_CASO","vía stinkbox_support (candidate_support); con stores vacíos el soporte es 0 para todas"),
 "hub:negativo_ricci_vs_billar":("CABLEADA_SIN_SENAL_EN_CASO","voto del hub por el puente de nombres; llega a candidatas pero no discrimina en este caso"),
 "lateral_metrics_v1_1":("CABLEADA_SIN_SENAL_EN_CASO","vía puente de nombres (node_mass_pairs de curvatura negativa); sin masa incidente no nombra candidatas"),
 "plugin_picos_mesetas.py":("ACTIVA","U6: score = fracción de transiciones ↗ (eps del plugin) de la serie P_top5 por corte; señal lateral por candidata"),
}
def _decl_u6(name):
    return _DECL_U6.get(str(name)) or _DECL_U6.get(str(name).replace("hub:",""))

_PAT_CACHE={}
def _patterns():
    if "p" not in _PAT_CACHE:
        try: _PAT_CACHE["p"]=json.loads((_PATTERNS_PATH()).read_text(encoding="utf-8"))
        except Exception: _PAT_CACHE["p"]={}
    return _PAT_CACHE["p"]

def _is_num(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))

# ---------- (a) evidencia propia del candidato ----------
def _candidate_token_evidence(candidate, cuts, last_k=3):
    """Hits of the candidate's OWN 244 pattern (tokens_favor/contra) in the observed cuts."""
    pv=_patterns().get(candidate,{}) if isinstance(_patterns(),dict) else {}
    favor=dict(pv.get("tokens_favor") or {}); contra=dict(pv.get("tokens_contra") or {})
    per_cut=[]
    for c in cuts or []:
        obs={}
        for e in ("P","A","C"):
            for pair in c.get(e) or []:
                t=str(pair[0]); obs[t]=max(obs.get(t,0.0),float(pair[1]))
        per_cut.append({"favor":{t:w for t,w in obs.items() if t in favor},
                        "contra":{t:w for t,w in obs.items() if t in contra}})
    recent=per_cut[-last_k:]
    fav=set(); con=set()
    for x in recent: fav|=set(x["favor"]); con|=set(x["contra"])
    return {"favor_tokens":sorted(fav),"contra_tokens":sorted(con),
            "favor_mass":[round(sum(x["favor"].values()),6) for x in per_cut],
            "contra_mass":[round(sum(x["contra"].values()),6) for x in per_cut],
            "n_favor_pattern":len(favor),"n_contra_pattern":len(contra)}

def _load_dynamis_catalog():
    p=BASE/DYNAMIS_CATALOG
    if not p.is_file(): return None
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return None

DYN_FAVOR_BUCKETS=(("vector_prosecucion_propulsor",("accion","prosec","avance","impul","objetivo","ambicion","conquista","expan")),
                   ("bucle_limites_al_exito",("limite","restric","constraint","guardrail","barrera","meseta")),
                   ("bucle_desplazamiento_carga",("desplaz","carga","deuda","compens","sintoma","parche","aplaz")),
                   ("fuerza_desvio_contagonista",("desvio","contagon","rival","alternat","bifurc","ruido")),
                   ("oscilacion_emocional_caotica",("emoc","ansiedad","ira","miedo","euforia","oscil","volatil")),
                   ("atricion_tragedia_comunes",("comun","tragedia","sobreexplot","recurso","atric")))
DYN_CONTRA_BUCKETS=(("fuerza_evitacion_resistencia",("evit","resistencia","retirada","prudencia","cautela")),
                    ("vector_razon_homeostatica",("razon","logica","homeostat","equilibr","verific","escept")),
                    ("fuerza_guardian_atenuacion",("guardian","atenu","amort","proteccion","filtro","defensa")),
                    ("verificacion_esceptica_guardrails",("verific","escept","audit","guardrail","control")),
                    ("retroalimentacion_balance_sigma",("balance","sigma","estabil","amort","homeostat")))
DYN_DEFAULT_W={"vector_prosecucion_propulsor":0.86,"bucle_limites_al_exito":0.83,"bucle_desplazamiento_carga":0.80,
               "fuerza_desvio_contagonista":0.76,"oscilacion_emocional_caotica":0.72,"atricion_tragedia_comunes":0.65,
               "fuerza_evitacion_resistencia":0.88,"vector_razon_homeostatica":0.84,"fuerza_guardian_atenuacion":0.79,
               "verificacion_esceptica_guardrails":0.75,"retroalimentacion_balance_sigma":0.70}

def _dynamis_bucket_counts(pool, extra_lateral_tokens=()):
    low=[str(x).casefold() for x in pool]
    lat={str(x).casefold() for x in extra_lateral_tokens}
    out={}
    for name,words in DYN_FAVOR_BUCKETS+DYN_CONTRA_BUCKETS:
        out[name]=sum(1 for x in low if any(w in x for w in words)) + (1 if name in lat else 0)
    return out

def _dynamis_evidence(candidate, boards, histories, features, cand_ev=None):
    """Dynamis per candidate: buckets counted on the candidate's OWN observed favor/contra tokens
    (legacy V0.17 counted board keys = the 244 family names, identical for every candidate).
    Weights come from the Dynamis catalog when present (same values as V0.17 hardcode)."""
    cat=_load_dynamis_catalog()
    W=dict(DYN_DEFAULT_W)
    if cat:
        for k,v in (cat.get("tokens_favor") or {}).items(): W[k]=abs(float(v))
        for k,v in (cat.get("tokens_contra") or {}).items(): W[k]=abs(float(v))
    lateral_tokens=(features.get("pre_h_lateral_tokens") or {}).get("unique_tokens") or []
    if _off("lentes_por_candidato") or cand_ev is None:
        pool=set()
        for b in boards[-3:]:
            for a in ("P","A","C"): pool.update(b[a].keys())
        fav_pool=pool; con_pool=set()
    else:
        fav_pool=set(cand_ev["favor_tokens"]); con_pool=set(cand_ev["contra_tokens"])
    cf=_dynamis_bucket_counts(fav_pool, lateral_tokens)
    cc=_dynamis_bucket_counts(con_pool)
    # A bucket hit on a CONTRA token of the candidate counts against the favor side.
    net={k:max(0,cf[k]-cc[k]) for k in cf}
    fnames=[n for n,_ in DYN_FAVOR_BUCKETS]; cnames=[n for n,_ in DYN_CONTRA_BUCKETS]
    fraw=sum(net[n]*W[n] for n in fnames); craw=sum(net[n]*W[n] for n in cnames)
    den=max(1,sum(net.values()))
    balance=(fraw-craw)/den
    shared=_clip01(0.5+0.5*balance)
    vals=[float(np.mean([b[a].get(candidate,0.0) for a in ("P","A","C")])) for b in boards]
    slope=float(np.polyfit(np.arange(len(vals)),np.asarray(vals),1)[0]) if len(vals)>1 else 0.0
    acceleration=_clip01(0.5+3.0*slope)
    p,l,d,dv,e,cm=(net[n] for n in fnames); av,rz,gd,sk,sg=(net[n] for n in cnames)
    limit_pressure=_clip01((p*W[fnames[0]]+l*W[fnames[1]])/max(1,p+l))
    load_loop=_clip01((d*W[fnames[2]]+dv*W[fnames[3]])/max(1,d+dv))
    oscillation=_clip01(e/max(1,e+av))
    containment=_clip01((rz*W[cnames[1]]+gd*W[cnames[2]]+sk*W[cnames[3]]+sg*W[cnames[4]])/max(1,rz+gd+sk+sg))
    contribution=_clip01(0.35*shared+0.25*limit_pressure+0.20*load_loop+0.10*oscillation+0.10*acceleration)
    return {"dynamis_shared_evidence":shared,"dynamis_prosecution":_clip01(p/max(1,p+av)),
            "dynamis_success_limit_loop":limit_pressure,"dynamis_load_shift_loop":load_loop,
            "dynamis_diversion":_clip01(dv/max(1,dv+p)),"dynamis_emotional_oscillation":oscillation,
            "dynamis_commons_attrition":_clip01(cm/max(1,cm+rz+gd)),
            "dynamis_avoidance_resistance":_clip01(av/max(1,av+p)),"dynamis_homeostatic_reason":_clip01(rz/max(1,rz+e)),
            "dynamis_guardian_attenuation":_clip01(gd/max(1,gd+dv)),"dynamis_skeptical_guardrails":_clip01(sk/max(1,sk+p)),
            "dynamis_sigma_balance":_clip01(sg/max(1,sg+d)),"dynamis_acceleration":acceleration,
            "dynamis_containment":containment,"dynamis_structural_contribution":contribution,
            # non-numeric metadata: never enters the numeric rank sort (fix c)
            "dynamis_tokens_active":sorted(fav_pool|con_pool)[:40],
            "dynamis_catalog_status":"LOADED" if cat else "ABSENT_DEFAULT_WEIGHTS"}

def _dynamis_case_summary(cuts):
    """Case-level Dynamis context (observed tokens only). Used only to seed the pre-H blind query."""
    toks=set()
    for c in cuts or []:
        for e in ("P","A","C"): toks.update(str(p[0]) for p in (c.get(e) or []))
    cnt=_dynamis_bucket_counts(toks)
    return {k:v for k,v in cnt.items() if v>0}

# ---------- (d) puente de nombres ----------
_NAME_FIELDS=("h","familia","family","name","id","top","candidate","candidato","hipotesis")
_NUM_FIELDS=("neto","score","p","delta","d","P_a","value","valor","mass","n_conv")

def _norm_name(s):
    s=_ud.normalize("NFKD",str(s)).encode("ascii","ignore").decode().casefold().strip()
    return re.sub(r"[^a-z0-9]+","_",s).strip("_")

def _alias_table():
    fams=list(_patterns().keys()) if isinstance(_patterns(),dict) else []
    forms={}
    for f in fams:
        n=_norm_name(f); fs={n, re.sub(r"^\d+_","",n)}
        for pre in ("arquetipo_el_","arquetipo_la_","arquetipo_los_","arquetipo_"):
            if n.startswith(pre): fs.add(n[len(pre):])
        for x in fs: forms.setdefault(x,set()).add(f)
    uniq={k:next(iter(v)) for k,v in forms.items() if len(v)==1}
    amb={k:sorted(v) for k,v in forms.items() if len(v)>1}
    return uniq,amb

BRIDGE_EXCLUDE={"semiotica_deriva","laterales_unico_detalle","stinkbox_transport","caldero_neighbor_memory","cuts","pre_h_analogical_search","pre_h_lateral_tokens",
                "dynamis_dramatica_sistemica","post_h_analogical_contrast","personajes_corte_016"}

def _bridge_matrix(features, candidates):
    """Per module, candidate-specific magnitude found in the module output.
    Exact keys (legacy) + [name, value] pairs + dicts with a name field + alias-normalized names.
    Unmatched names (in name slots) are logged, never guessed."""
    legacy=_off("puente_nombres")
    cset=set(candidates); uniq,amb=_alias_table()
    fam244=set(_patterns().keys()) if isinstance(_patterns(),dict) else set()
    def resolve(k):
        if not isinstance(k,str): return None,None
        if k in cset: return k,"exact"
        if legacy: return None,None
        n=_norm_name(k)
        f=uniq.get(n)
        if f is None: return None,("ambiguous" if n in amb else "unmatched")
        return (f,"alias") if f in cset else (None,"family_not_candidate")
    matrix={}; log={}
    for mname,out in features.items():
        if mname in BRIDGE_EXCLUDE: continue
        acc={c:0.0 for c in candidates}; lg={"exact":0,"alias":0,"family_not_candidate":0,"unmatched":0,"ambiguous":0,"unmatched_sample":set(),"alias_examples":set()}
        def add(fam,how,val,raw):
            if fam is not None:
                acc[fam]+=abs(float(val)) if val is not None else 0.0
                lg[how]+=1
                if how=="alias": lg["alias_examples"].add(f"{raw}->{fam}")
            elif how:
                lg[how]+=1
                if how in ("unmatched","ambiguous") and len(lg["unmatched_sample"])<25: lg["unmatched_sample"].add(str(raw))
        def walk(o):
            if isinstance(o,dict):
                if not legacy:
                    for nf in _NAME_FIELDS:
                        if isinstance(o.get(nf),str):
                            fam,how=resolve(o[nf])
                            num=next((o[z] for z in _NUM_FIELDS if _is_num(o.get(z))),None)
                            if how in ("exact","alias","family_not_candidate","unmatched","ambiguous"): add(fam,how,num,o[nf])
                            break
                for k,v in o.items():
                    fam,how=resolve(k)
                    if fam is not None:
                        if _is_num(v): add(fam,how,v,k)
                        elif isinstance(v,dict):
                            add(fam,how,sum(abs(float(v[z])) for z in ("neto","score","p","delta") if _is_num(v.get(z))),k)
                    walk(v)
            elif isinstance(o,(list,tuple)):
                if not legacy and len(o)==2 and isinstance(o[0],str) and _is_num(o[1]):
                    fam,how=resolve(o[0])
                    if how in ("exact","alias","family_not_candidate","unmatched","ambiguous"): add(fam,how,o[1],o[0])
                    return
                for v in o: walk(v)
        walk(out)
        matrix[mname]=acc
        lg["unmatched_sample"]=sorted(lg["unmatched_sample"]); lg["alias_examples"]=sorted(lg["alias_examples"])[:10]
        vals=list(acc.values())
        lg["reaches_candidates"]=any(v>0 for v in vals)
        lg["discriminates"]=(max(vals)-min(vals))>TIE_EPS if vals else False
        log[mname]=lg
    return matrix,log

def _bridge_candidate_features(matrix, candidates):
    active=[m for m,acc in matrix.items() if (max(acc.values())-min(acc.values()))>TIE_EPS]
    out={}
    for c in candidates:
        if not active:
            out[c]={"lateral_candidate_specific":0.0,"lateral_breadth":0.0}; continue
        shares=[matrix[m][c]/max(matrix[m].values()) for m in active]
        out[c]={"lateral_candidate_specific":float(np.mean(shares)),
                "lateral_breadth":float(np.mean([1.0 if matrix[m][c]>0 else 0.0 for m in active]))}
    return out,active


def _lateral_signal_contributions(matrix, candidates, active_modules):
    """Keep lateral bridge signals separate at ranking time.
    Only candidate-discriminating modules are rank-eligible; no aggregate lateral vote is used.
    """
    out={c:{} for c in candidates}; registry=[]
    for m in active_modules:
        acc=matrix.get(m) or {}
        vals=[float(acc.get(c,0.0)) for c in candidates]
        if not vals or (max(vals)-min(vals))<=TIE_EPS:
            continue
        mx=max(vals); denom=mx if abs(mx)>TIE_EPS else 1.0
        row={c:max(0.0,min(1.0,float(acc.get(c,0.0))/denom)) for c in candidates}
        registry.append({"signal":m,"discriminates":True,"candidate_values":row,
                         "range":float(max(vals)-min(vals)),"rank_eligible":True,"can_decide_H":False})
        for c,v in row.items(): out[c][m]=v
    return out,registry

# ---------- (b) guardia de constantes, rangos con empates, desempate sin nombre ----------
def _frac_scores(rows,k):
    """Rank score in [0,1]; equal values share the average rank (no name ordering)."""
    vals=sorted(((float(f[k]),n) for n,f in rows), key=lambda z:-z[0])
    N=len(vals); out={}; i=0
    while i<N:
        j=i
        while j+1<N and abs(vals[j+1][0]-vals[i][0])<=TIE_EPS: j+=1
        avg=(i+j)/2.0
        for t in range(i,j+1): out[vals[t][1]]=1.0-avg/max(1,N-1)
        i=j+1
    return out

def _legacy_scores(rows,k):
    ordered=sorted(rows,key=lambda z:(-z[1][k],z[0]))
    return {n:1.0-r/max(1,len(ordered)-1) for r,(n,_) in enumerate(ordered)}

def _tb_key(n,f,score):
    """Deterministic tie-break, not by name: score, core board mean, trajectory slope, hash(candidate) last."""
    if _off("desempate_no_nombre"):
        return (-score, n)
    return (-score, -float(f.get("state",0.0)), -float(f.get("_tb_slope",0.0)), hashlib.sha256(n.encode("utf-8")).hexdigest())

_CONST_U6_CASO=("relational_activity","caldero_neighbor_activity","caldero_neighbor_memory","cameo_activity","cameo_profile_activity",
                "geometric_persistence_context","geometric_turn_context","geometric_latest_movement")
_CONST_U6_ENTRADA=("relational_alignment","caldero_neighbor_alignment","stinkbox_support","lateral_shared_evidence","analog_alignment")
def _motivo_constante_u6(k):
    if k in _CONST_U6_CASO: return "NIVEL_CASO_POR_CONSTRUCCION: el valor no depende de la candidata (contexto); no es bug"
    if k in _CONST_U6_ENTRADA: return "ENTRADA_VACIA: depende de external_lights / fuentes Caldero / stores, ausentes o vacíos en esta corrida"
    if k.startswith("dynamis_") or k.startswith("propp_") or k.startswith("booker_") or k.startswith("greimas_"):
        return "SIN_ACIERTOS_DE_PALABRA_CLAVE: los tokens propios de las candidatas no contienen las raíces del bucket (igual valor para todas)"
    if k=="frye_support": return "SATURACION (corregido en U6 con normalización); si sigue constante, todas las candidatas tienen el mismo poder relativo"
    return "CONSTANTE_EN_ESTE_CASO"

def _dimension_guard(rows, keys):
    excluded_const=[]; excluded_dup=[]; kept=[]; seen_vecs=[]
    for k in keys:
        vec=[float(f[k]) for _,f in rows]
        if not _off("guardia_constantes") and (max(vec)-min(vec))<=TIE_EPS:
            excluded_const.append(k); continue
        if not _off("guardia_constantes"):
            dup=next((kk for kk,vv in seen_vecs if all(abs(a-b)<=TIE_EPS for a,b in zip(vec,vv))),None)
            if dup is not None:
                excluded_dup.append({"dimension":k,"duplicate_of":dup}); continue
        kept.append(k); seen_vecs.append((k,vec))
    return kept,excluded_const,excluded_dup

def _empates(fused):
    groups=[]; i=0
    top=fused[:10]
    while i<len(top):
        j=i
        while j+1<len(top) and abs(top[j+1][1]["rank_fusion"]-top[i][1]["rank_fusion"])<=EMPATE_EPS: j+=1
        if j>i: groups.append([x[0] for x in top[i:j+1]])
        i=j+1
    return {"top1_top2_empate":bool(len(fused)>1 and abs(fused[0][1]["rank_fusion"]-fused[1][1]["rank_fusion"])<=EMPATE_EPS),
            "grupos_empate_top10":groups,"eps":EMPATE_EPS}

# ---------- (f) V0.18 pre-H blind analogical search (bytes originales V0.18 + limpieza) ----------
def _case_identity(case):
    """Identity used only by the external self-match filter, never by the blind query."""
    raw=case.get("caldero_identity") or case.get("identity") or {}
    raw=dict(raw) if isinstance(raw,dict) else {}
    if case.get("person") and not raw.get("name") and not raw.get("nombre"):
        raw["name"]=case.get("person")
    for dest, keys in (("birth_date",("birth_date","fecha_nacimiento")), ("death_date",("death_date","fecha_muerte"))):
        if not any(raw.get(k) for k in keys):
            for key in keys:
                if case.get(key): raw[dest]=case[key]; break
    return raw


def _identity_terms(case):
    raw=_case_identity(case)
    terms=set()
    for k,v in (raw.items() if isinstance(raw,dict) else []):
        vals=v if isinstance(v,(list,tuple)) else [v]
        for x in vals:
            if x is None: continue
            s=str(x).strip().casefold()
            if not s: continue
            terms.add(s)
            if k in ("name","nombre","aliases","alias"):
                terms.update(w for w in re.split(r"\W+",s) if len(w)>=4)
    return terms

def _normalizar_fecha_corte(valor):
    """A5_20261107: normaliza una fecha de corte a YYYY-MM-DD (o None).

    Acepta YYYY-MM-DD, YYYY-MM-DDTHH:MM..., YYYY-MM y YYYY (parcial -> día 1).
    Las fechas parciales se marcan con fecha_parcial en el filtro que las usa.
    """
    if valor is None:
        return None
    s = str(valor).strip()
    if not s:
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r"^(\d{4})-(\d{2})$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-01"
    m = re.match(r"^(\d{4})$", s)
    if m:
        return f"{m.group(1)}-01-01"
    return None


def _resolver_z_corte(case):
    """A5_20261107: Z del caso para el corte temporal del Caldero.

    Z := case["freeze"] (equivale a case["z_trabajo"]), con fallback z90_date.
    NUNCA z_work_date sin normalizar: en entradas viejas es el id de un corte
    ("C3_1895B"), no una fecha. Sin Z (LIVE_PRESENT) devuelve None: sin corte.
    """
    fr = case.get("freeze")
    if isinstance(fr, dict):
        fr = fr.get("z_work") or fr.get("z_trabajo") or fr.get("freeze")
    return _normalizar_fecha_corte(fr) or _normalizar_fecha_corte(case.get("z_trabajo")) or _normalizar_fecha_corte(case.get("z90_date"))


def _cargar_filtro_017():
    """A5_20261107: carga filtro_entrada_dirigida_017 por ruta explícita.

    La capa LLM vive en motor/capa_llm/, fuera del motor. En la corrida estándar
    el runner corre desde runs/ESTANDAR__<nombre>/ (copia plana de motor/motor/),
    así que capa_llm está en BASE.parent.parent/capa_llm; en uso directo desde
    el repo está en BASE.parent/capa_llm. CAPA_LLM_DIR la fija explícitamente.
    Devuelve el módulo o None si no está en el pack.
    """
    import os as _os_f017
    cands = []
    env = _os_f017.environ.get("CAPA_LLM_DIR")
    if env:
        cands.append(Path(env))
    cands.append(BASE.parent.parent / "capa_llm")
    cands.append(BASE.parent / "capa_llm")
    for d in cands:
        fp = Path(d) / "filtro_entrada_dirigida_017.py"
        if fp.is_file():
            spec = importlib.util.spec_from_file_location("filtro_entrada_dirigida_017", str(fp))
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
            except Exception:
                return None
            return mod
    return None


def _aplicar_filtro_017(case):
    """A5_20261107: compuerta 017 al entrar a run(). Devuelve (caso_a_usar, traza).

    Modo por env FILTRO_017: traza (defecto, analiza sin modificar el caso),
    activo (neutraliza identidad/obra/calendario en el payload), off (apagado).
    El catálogo se pasa explícito: el fallback del filtro apunta a una ruta que
    no existe en el pack y devolvería un catálogo vacío en silencio.
    Si el módulo no está en el pack o la compuerta falla, la traza dice
    NO_DISPONIBLE/ERROR y la corrida sigue con el caso crudo (la capa LLM es
    opcional; no es compuerta de decisión). La consulta_dirigida NO se cablea
    aquí: ya vive en correr_estandar.py y duplicarla aplicaría sus preguntas
    dos veces en la corrida estándar; el filtro 017 sí va en run() porque es
    una compuerta pura de entrada, idempotente, y debe cubrir también las
    llamadas directas a run().
    """
    import os as _os_f017
    modo = (_os_f017.environ.get("FILTRO_017", "traza") or "traza").strip().lower()
    _base = {"version": "FILTRO_ENTRADA_DIRIGIDA_017_20261007", "contrato": "CONTRATO_TRADUCCION_LLM_017",
             "modo": modo, "status": "NO_CONFIGURADO", "n_aplicadas": 0}
    if modo == "off":
        return case, {**_base, "nota": "FILTRO_017=off"}
    mod = _cargar_filtro_017()
    if mod is None:
        return case, {**_base, "status": "NO_DISPONIBLE",
                      "nota": "capa_llm/filtro_entrada_dirigida_017.py no está en el pack; corrida con caso crudo"}
    try:
        cat = json.loads((BASE / "patterns_final_v14.json").read_text(encoding="utf-8"))
    except Exception:
        cat = {}
    try:
        payload, traza = mod.compuerta(case, modo, cat)
    except Exception as exc:
        return case, {**_base, "status": "ERROR", "error": f"{type(exc).__name__}:{exc}",
                      "nota": "la compuerta falló; corrida con caso crudo"}
    traza = dict(traza or {})
    traza["payload_aplicado"] = bool(modo == "activo")
    return payload, traza


def _build_pre_h_blind_input(case: Dict[str,Any], motor: Dict[str,Any], features: Dict[str,Any]) -> Dict[str,Any]:
    """PATCH13: semilla ciega estable construida solo desde los cortes congelados.

    No usa unique_tokens de interrelation ni familias laterales calculadas durante
    la propia corrida: pueden variar o contener vocabulario de infraestructura y
    causar que la solicitud del puente no coincida con la respuesta.
    Familias extra solo se admiten si el caso las declara explícitamente en
    `caldero_search_families`, antes de la búsqueda.
    """
    tokens=[]
    for c in case.get("cuts") or []:
        for eje in ("P","A","C"):
            for pair in c.get(eje) or []:
                if pair and pair[0] is not None:
                    tokens.append(str(pair[0]))
    ident=_identity_terms(case)
    def clean(vals):
        seen=set(); out=[]
        for v in vals:
            z=str(v).strip().casefold()
            if z and z not in seen and not any(t in z for t in ident):
                seen.add(z); out.append(z)
        return out
    families=case.get("caldero_search_families") or []
    if isinstance(families,str): families=[families]
    return {"tokens":clean(tokens)[:40],"patterns":[],"families":clean(families)[:20]}

def _run_pre_h_analogical_search(case: Dict[str,Any], motor: Dict[str,Any], features: Dict[str,Any]) -> Dict[str,Any]:
    """V0.18 original (sidecar_caldero_busqueda_arquetipos). Offline: only case['analogical_search_sources'];
    never calls the web. identity_exposed / future_outcome_exposed are now CHECKED, not asserted."""
    mod=_load("caldero_pre_h", "sidecar_caldero_busqueda_arquetipos.py")
    base={"can_decide_H":False,"writes_canonical":False,"writes_H":False}
    if mod is None:
        return {**base,"status":"NOT_AVAILABLE","activated":False,"reason":"sidecar_missing"}
    raw_identity=_case_identity(case)
    identity=mod.SelfMatchIdentity.from_mapping(raw_identity)
    blind_raw=_build_pre_h_blind_input(case,motor,features)
    blind=mod.ArchetypeInput.from_mapping(blind_raw)
    if not (blind.tokens or blind.patterns or blind.families):
        return {**base,"status":"NOT_ACTIVATED","activated":False,"reason":"no_observable_seed"}
    ident=_identity_terms(case)
    # A5_20261107: corte temporal del Caldero (vecinos <= Z) también en pre-H.
    _z_corte=_resolver_z_corte(case)
    import os as _os_pre
    _corte_modo=_os_pre.environ.get("CALDERO_CORTE_TEMPORAL","leniente").strip().lower()
    if _corte_modo not in ("leniente","estricto","off"): _corte_modo="leniente"
    future_keys=[k for k in ("future_outcome","outcome","resultado_futuro","t1_resultado") if k in case]
    # Un solo bus de búsqueda: el resultado externo ya obtenido por la capa
    # Caldero (`caldero_search_sources`) es reutilizable aquí. La ruta antigua
    # `analogical_search_sources` queda como alias de compatibilidad.
    prior=features.get("caldero_busqueda_arquetipos") or {}
    # FIX_20261025: el sidecar no emite 'status'; la reutilización nunca disparaba (PRE-H quedaba API_PENDING aunque
    # el Caldero hubiera buscado en vivo). Aceptar recibo de proveedor vivo (no fixture) como EXECUTED.
    _rcpt=(prior.get("audit") or {}).get("provider_receipt") or {}
    _prior_ok=prior.get("status")=="EXECUTED" or (_rcpt.get("status")=="EXECUTED" and _rcpt.get("provider") not in (None,"static_fixture","provided_fixture"))
    if _prior_ok and prior.get("caldero_input"):
        cal=prior.get("caldero_input") or {}
        return {**base,
                "status":"EXECUTED","activated":True,"reason":"pre_h_orientation_reused_caldero_search",
                "phase":"PRE_H_ORIENTATION","query_blind":True,"identity_exposed":False,"future_outcome_exposed":False,
                "future_keys_present_not_read":future_keys,
                "query":prior.get("audit",{}).get("query_exact",""),
                "raw_source_count":len(prior.get("audit",{}).get("raw_sources_before_self_match") or []),
                "discarded_self_match_count":len(prior.get("audit",{}).get("discarded_by_self_match") or []),
                "analog_token_count":len(cal.get("tokens_neighbors") or []),
                "tokens_neighbors":cal.get("tokens_neighbors") or [],
                "raw_sources":prior.get("audit",{}).get("raw_sources_before_self_match") or [],
                "discarded":prior.get("audit",{}).get("discarded_by_self_match") or [],
                "provider_receipt":_rcpt,"feeds":"stinkbox_and_lateral_alignment_only"}
    # PATCH19: el orden del runner ejecuta esta etapa antes del Caldero principal.
    # Si existe un puente de herramienta conectada ya registrado, consumirlo aquí
    # directamente (sin red) para que la búsqueda PRE-H no quede API_PENDING.
    # Se repiten los candados de procedencia y query ciega del consumidor principal.
    bridge=case.get("caldero_search_bridge")
    if isinstance(bridge,dict) and bridge.get("status")=="EXECUTED" and bridge.get("origin")=="connected_tool_call":
        rows=bridge.get("results") or []
        expected_query=mod.build_blind_query(blind)
        expected_hash=hashlib.sha256(expected_query.encode("utf-8")).hexdigest()
        submitted_query=str(bridge.get("submitted_query") or "")
        identity_terms=[str(t).casefold() for t in ident if str(t).strip()]
        if bridge.get("blind_query_sha256") != expected_hash:
            return {**base,"status":"BRIDGE_REJECTED","activated":True,"reason":"SEARCH_BRIDGE_QUERY_MISMATCH",
                    "phase":"PRE_H_ORIENTATION","query_blind":True,"identity_exposed":False,"future_outcome_exposed":False,
                    "future_keys_present_not_read":future_keys,"raw_source_count":0,"discarded_self_match_count":0,
                    "analog_token_count":0,"tokens_neighbors":[],"feeds":"stinkbox_and_lateral_alignment_only"}
        if not submitted_query.strip() or any(t and t in submitted_query.casefold() for t in identity_terms):
            return {**base,"status":"BRIDGE_REJECTED","activated":True,"reason":"SEARCH_BRIDGE_SUBMITTED_QUERY_INVALID_OR_EXPOSES_IDENTITY",
                    "phase":"PRE_H_ORIENTATION","query_blind":True,"identity_exposed":False,"future_outcome_exposed":False,
                    "future_keys_present_not_read":future_keys,"raw_source_count":0,"discarded_self_match_count":0,
                    "analog_token_count":0,"tokens_neighbors":[],"feeds":"stinkbox_and_lateral_alignment_only"}
        if not rows or any(not isinstance(r,dict) or not str(r.get("url") or "").startswith(("https://","http://")) for r in rows):
            return {**base,"status":"BRIDGE_REJECTED","activated":True,"reason":"SEARCH_BRIDGE_RESULTS_INVALID",
                    "phase":"PRE_H_ORIENTATION","query_blind":True,"identity_exposed":False,"future_outcome_exposed":False,
                    "future_keys_present_not_read":future_keys,"raw_source_count":0,"discarded_self_match_count":0,
                    "analog_token_count":0,"tokens_neighbors":[],"feeds":"stinkbox_and_lateral_alignment_only"}
        sources=[mod.SearchSource.from_mapping(r) for r in rows]
        adapter=mod.StaticSearchAdapter(sources)
        adapter.last_receipt={"provider":str(bridge.get("provider") or "connected_tool_bridge"),"status":"EXECUTED",
                              "query_count":int(bridge.get("query_count") or 1),"result_count":len(sources),
                              "query_sha256":expected_hash,"submitted_query_sha256":hashlib.sha256(submitted_query.encode("utf-8")).hexdigest(),
                              "bridge_id":str(bridge.get("bridge_id") or ""),"tool_name":str(bridge.get("tool_name") or "connected_search_tool"),
                              "origin":"connected_tool_call","reused_bridge":True}
        result=mod.CalderoArchetypeSearchSidecar(adapter,mod.SelfMatchFilter(identity)).run(blind,cutoff_date=_z_corte,corte_modo=_corte_modo)
        cal=result.get("caldero_input") or {}; audit=result.get("audit") or {}
        return {**base,"status":"EXECUTED","activated":True,"reason":"pre_h_orientation_reused_connected_bridge",
                "phase":"PRE_H_ORIENTATION","query_blind":True,"identity_exposed":False,"future_outcome_exposed":False,
                "future_keys_present_not_read":future_keys,"query":audit.get("query_exact",expected_query),
                "adapter":"caldero_search_bridge/connected_tool_call (reused; no live search in Python runner)",
                "raw_source_count":len(audit.get("raw_sources_before_self_match") or []),
                "discarded_self_match_count":len(audit.get("discarded_by_self_match") or []),
                "analog_token_count":len(cal.get("tokens_neighbors") or []),"tokens_neighbors":cal.get("tokens_neighbors") or [],
                # Las fuentes completas y su metadata viven en el audit del Caldero principal.
                # No duplicarlas aquí: en el puente metadata ausente es ausencia real, no un objeto vacío.
                "discarded_self_match_count":len(audit.get("discarded_by_self_match") or []),
                "provider_receipt":adapter.last_receipt,"feeds":"stinkbox_and_lateral_alignment_only"}
    # No reciclar fuentes bibliográficas como si fueran resultados de búsqueda.
    supplied = case.get("caldero_search_fixture") if case.get("allow_static_search_fixture") is True else None
    if supplied is None:
        q=" ".join(list(blind.tokens)+list(blind.families))
        return {**base,"status":"API_PENDING","activated":True,"reason":"pre_h_orientation_required",
                "query_blind":True,"identity_exposed":any(t in q.casefold() for t in ident),"future_outcome_exposed":False,
                "future_keys_present_not_read":future_keys,
                "query_terms":list(blind.tokens)+list(blind.families),"raw_source_count":0,"discarded_self_match_count":0,
                "analog_token_count":0,"adapter":"caldero_search_sources/analogical_search_sources absent; search provider not injected"}
    sources=[mod.SearchSource.from_mapping(x) if isinstance(x,dict) and hasattr(mod.SearchSource,"from_mapping") else (mod.SearchSource(**x) if isinstance(x,dict) else x) for x in supplied]
    result=mod.CalderoArchetypeSearchSidecar(mod.StaticSearchAdapter(sources),mod.SelfMatchFilter(identity)).run(blind,cutoff_date=_z_corte,corte_modo=_corte_modo)
    cal=result.get("caldero_input") or {}
    query=result.get("audit",{}).get("query_exact","")
    exposed=any(t in query.casefold() for t in ident)
    return {**base,
        # A5_20261107: fuente estática explícita (fixture) != búsqueda ejecutada.
        # Antes decía EXECUTED y la fila de componente mentía; el estado honesto
        # solo vivía en el CEB. Ahora EXECUTED_FIXTURE (=> SIMULADO_FIXTURE en CEB).
        "status":"EXECUTED_FIXTURE","provider":"provided_fixture","activated":True,"reason":"pre_h_orientation_required","phase":"PRE_H_ORIENTATION",
        "query_blind":not exposed,"identity_exposed":exposed,"future_outcome_exposed":False,
        "future_keys_present_not_read":future_keys,
        "query":query,
        "raw_source_count":len(result.get("audit",{}).get("raw_sources_before_self_match") or []),
        "discarded_self_match_count":len(result.get("audit",{}).get("discarded_by_self_match") or []),
        "analog_token_count":len(cal.get("tokens_neighbors") or []),
        "tokens_neighbors":cal.get("tokens_neighbors") or [],
        "raw_sources":result.get("audit",{}).get("raw_sources_before_self_match") or [],
        "discarded":result.get("audit",{}).get("discarded_by_self_match") or [],
        "feeds":"stinkbox_and_lateral_alignment_only"}
# =================== fin helpers CONSOLIDADO ===================


def _structural_evidence(candidate, boards, histories, features, cand_ev=None):
    """Structural lenses (Propp/Booker/Greimas/Frye). CONSOLIDADO: Propp/Greimas read the candidate's OWN
    observed favor/contra tokens (legacy read the 244 board keys: identical for every candidate). Frye fixed."""
    vals=[float(np.mean([b[a].get(candidate,0.0) for a in ('P','A','C')])) for b in boards]
    latest=vals[-1] if vals else 0.5
    prev=vals[-2] if len(vals)>1 else latest
    delta=latest-prev
    diffs=np.diff(vals) if len(vals)>1 else np.array([])
    legacy=_off("lentes_por_candidato") or cand_ev is None
    if legacy:
        active=set()
        for b in boards[-3:]:
            for a in ('P','A','C'): active.update(b[a].keys())
        fav_pool=active; con_pool=set()
    else:
        fav_pool=set(cand_ev["favor_tokens"]); con_pool=set(cand_ev["contra_tokens"])
    pool=fav_pool|con_pool
    def hit(words, p=None): return sum(1 for x in (pool if p is None else p) if any(w in x.lower() for w in words))
    prohibition=hit(('prohib','restric','guardrail','limit','constraint'))
    transgression=hit(('transgres','rebel','desaf','ruptur','violat'))
    damage=hit(('daño','dano','atric','crisis','colap','destruc','caida','stress','fatiga'))
    aid=hit(('auxil','alian','soporte','ayuda','recomp','rescat'))
    propp=(0.85*prohibition + 0.89*transgression + 0.92*damage - 0.84*aid)/max(1,prohibition+transgression+damage+aid)
    propp_signal=_clip01(0.5+0.5*propp)
    slope=float(np.polyfit(np.arange(len(vals)),np.asarray(vals),1)[0]) if len(vals)>1 else 0.0
    rise=_clip01(0.5+4*slope); fall=_clip01(0.5-4*slope)
    reversals=sum(1 for a,b in zip(diffs[:-1],diffs[1:]) if a*b<0)/max(1,len(diffs)-1)
    tragedy=_clip01(0.55*fall+0.45*(1-reversals))
    voyage_return=_clip01(reversals)
    overcoming=_clip01(0.5*rise+0.5*max(0,latest-0.5)*2)
    booker=_clip01(0.91*tragedy + 0.78*overcoming - 0.75*voyage_return)
    booker_signal=_clip01(0.5+0.5*booker)
    if legacy:
        total=max(1.0,len(pool)); contra=hit(('conflic','obstac','opon','restric','crisis','enem','caida','persec'))
        opponent=_clip01(contra/total)
    else:
        # Greimas opponent = share of the candidate's observed evidence that is CONTRA its own pattern.
        opponent=_clip01(len(con_pool)/max(1,len(pool))) if pool else 0.0
    subject=_clip01(latest)
    obj=_clip01(0.5+delta*3)
    destinator=_clip01(0.5+3*(vals[1]-vals[0])) if len(vals)>1 else 0.5
    greimas_support=_clip01(0.30*subject+0.25*obj+0.20*destinator+0.25*(1-0.76*opponent))
    # Frye (fix V0.16.1): relative power of candidate vs the active environment.
    env=[float(np.mean([b[x].get(n,0.0) for x in ('P','A','C')])) for b in boards for n in b['P'].keys()]
    env_med=float(np.median(env)) if env else latest
    relative=_clip01(0.5+2*(latest-env_med))
    ironic=_clip01(1-relative)
    frye_mythic=_clip01(relative)
    frye_high_mimetic=_clip01(1-abs(relative-0.72))
    frye_low_mimetic=_clip01(1-abs(relative-0.50))
    frye_iron_atrition=_clip01(0.88*ironic)
    if _off("frye_normalizado_u6"):
        frye_support=_clip01(0.95*frye_mythic + 0.72*frye_high_mimetic + 0.50*frye_low_mimetic - frye_iron_atrition)
    else:
        # U6 BUG FIX: misma combinación lineal dividida por su máximo positivo (0.95+0.72+0.50=2.17); antes saturaba en 1.0.
        frye_support=_clip01((0.95*frye_mythic + 0.72*frye_high_mimetic + 0.50*frye_low_mimetic - frye_iron_atrition)/2.17)
    iron_tragedy_gate=_clip01(ironic*tragedy)
    shared=_clip01(0.25*propp_signal+0.25*booker_signal+0.25*greimas_support+0.25*frye_support)
    contribution=_clip01(0.70*shared+0.30*(1-iron_tragedy_gate))*0.35
    return {"propp_signal":propp_signal,"booker_signal":booker_signal,"greimas_support":greimas_support,
            "frye_support":frye_support,"frye_relative_power":relative,"frye_ironic":ironic,
            "propp_transgression":_clip01(transgression/max(1,transgression+prohibition+damage+aid)),
            "propp_damage":_clip01(damage/max(1,transgression+prohibition+damage+aid)),
            "booker_tragedy":tragedy,"booker_voyage_return":voyage_return,
            "greimas_opponent_friction":opponent,"greimas_subject_density":subject,"greimas_object_attraction":obj,"greimas_destinator_impulse":destinator,
            "frye_mythic":frye_mythic,"frye_high_mimetic":frye_high_mimetic,"frye_low_mimetic":frye_low_mimetic,"frye_iron_atrition":frye_iron_atrition,
            "coupling_iron_tragedy":iron_tragedy_gate,"coupling_opponent":opponent,
            "structural_shared_evidence":shared,"structural_contribution":contribution}

def _feature_vector(candidate: str, histories, boards, motor, features, ctx=None) -> Dict[str,Any]:
    ctx=ctx or {}
    cand_ev=(ctx.get("cand_ev") or {}).get(candidate)
    vals=[boards[-1][a].get(candidate,0.0) for a in ("P","A","C")]
    structural={} if _off("estructural") else _structural_evidence(candidate, boards, histories, features, cand_ev)
    dynamis={} if _off("dynamis") else _dynamis_evidence(candidate, boards, histories, features, cand_ev)
    state=float(np.mean(vals))
    seen=[candidate in {x["familia"] for x in h} for h in histories]
    continuity=sum(seen)/max(1,len(seen))
    recency=sum(seen[-3:])/max(1,min(3,len(seen)))
    prev=np.mean([boards[-2][a].get(candidate,0.0) for a in ("P","A","C")]) if len(boards)>1 else state
    delta=state-prev
    bridge=(ctx.get("bridge") or {}).get(candidate,{"lateral_candidate_specific":0.0,"lateral_breadth":0.0})
    named_specific=float(bridge["lateral_candidate_specific"])
    breadth=float(bridge["lateral_breadth"])
    spread=float(np.std(vals))
    convergence=max(0.0,1.0-min(1.0,spread*4.0))
    inter=features.get("interrelation") or {}
    observed=set(inter.get("unique_tokens") or [])
    pv=_patterns().get(candidate,{}) if isinstance(_patterns(),dict) else {}
    favor=set((pv.get("tokens_favor") or {}).keys()); contra=set((pv.get("tokens_contra") or {}).keys())
    denom=max(1,len(favor|contra))
    relation_alignment=max(0.0,min(1.0,0.5+0.5*(len(observed & favor)-len(observed & contra))/denom))
    caldero=features.get("caldero_busqueda_arquetipos") or {}
    current_neighbors={str(x.get("token","")).strip().casefold() if isinstance(x,dict) else str(x).strip().casefold() for x in ((caldero.get("caldero_input") or {}).get("tokens_neighbors") or [])}; current_neighbors.discard("")
    current_neighbors-=set(_RUN_CTX.get("filtro_013_actuales_fuera") or ())  # PATCH 013: relleno/ids de fuente no votan
    memory=_load_auxiliary_neighbor_memory(features)
    persisted_neighbors=set(memory.get("unique_tokens") or [])
    neighbor_activity=float(1.0-math.exp(-math.log1p(len(current_neighbors)))) if current_neighbors else 0.0
    memory_activity=float(1.0-math.exp(-math.log1p(len(persisted_neighbors)))) if persisted_neighbors else 0.0
    neighbor_alignment=max(0.0,min(1.0,0.5+0.5*(len((current_neighbors|persisted_neighbors)&favor)-len((current_neighbors|persisted_neighbors)&contra))/denom))
    stink=features.get("stinkbox_transport") or {}
    support=(stink.get("candidate_support") or {}).get(candidate,0.0)
    stink_support=max(0.0,min(1.0,0.5+0.5*float(support)))
    analog=set(str(x).casefold() for x in ((features.get("pre_h_lateral_tokens") or {}).get("unique_tokens") or []))
    shared_terms=[_relational_activity(features), relation_alignment, neighbor_activity, memory_activity, neighbor_alignment, stink_support]
    analog_alignment=None
    if analog:
        analog_alignment=max(0.0,min(1.0,0.5+0.5*(len(analog&favor)-len(analog&contra))/denom))
        shared_terms.append(analog_alignment)
    lateral_shared=max(0.0,min(1.0,float(np.mean(shared_terms))))
    # Own-evidence core: candidate's own pattern hits in the latest cut (fix a).
    own_fav=(cand_ev or {}).get("favor_mass") or [0.0]; own_con=(cand_ev or {}).get("contra_mass") or [0.0]
    own_evidence=_clip01(0.5+0.25*(own_fav[-1]-own_con[-1]))
    core_support=float(np.mean([state, continuity, recency, max(0.0,min(1.0,0.5+delta)), breadth, convergence]))
    structural_contribution=float(structural.get("structural_contribution",0.0))
    dynamis_contribution=float(dynamis.get("dynamis_structural_contribution",0.0))
    lateral_contribution=max(0.0,min(1.0,0.45*lateral_shared*core_support + 0.30*named_specific + 0.15*structural_contribution + 0.10*dynamis_contribution))
    bvals=[float(np.mean([b[a].get(candidate,0.0) for a in ("P","A","C")])) for b in boards]
    tb_slope=float(np.polyfit(np.arange(len(bvals)),np.asarray(bvals),1)[0]) if len(bvals)>1 else 0.0
    # WORKING PATCH: trayectoria vectorizada multiescala. La inercia no decide por sí sola;
    # entra como evidencia candidata en la fusión junto a las señales P/A/C y laterales.
    step_deltas=np.diff(np.asarray(bvals,dtype=float)) if len(bvals)>1 else np.asarray([],dtype=float)
    def _support_slope(vals):
        if len(vals)<2: return 0.5
        slope=float(np.polyfit(np.arange(len(vals)),np.asarray(vals,dtype=float),1)[0])
        return _clip01(0.5+0.5*math.tanh(8.0*slope))
    trajectory_micro=_support_slope(bvals[-2:])
    trajectory_meso=_support_slope(bvals[-min(4,len(bvals)):])
    trajectory_macro=_support_slope(bvals)
    last_delta=float(step_deltas[-1]) if len(step_deltas) else 0.0
    prev_delta=float(step_deltas[-2]) if len(step_deltas)>1 else last_delta
    trajectory_accel=_clip01(0.5+0.5*math.tanh(8.0*(last_delta-prev_delta)))
    scale_supports=[trajectory_micro,trajectory_meso,trajectory_macro]
    trajectory_convergence=_clip01(1.0-(max(scale_supports)-min(scale_supports)))
    # PATCH11 + WORKING PATCH: la persistencia geométrica modula la continuidad; κ atenúa cuando hay giro.
    # It informs H; it does not determine H by itself. Use only observed cuts (no future data).
    r732=(motor or {}).get("R732") or {}
    geom_persist=list(r732.get("persist_cos") or [])
    geom_kappa=list(r732.get("kappa_dir") or [])
    geom_dx=list(r732.get("dX_norm") or [])
    persist_last=float(geom_persist[-1]) if geom_persist and _is_num(geom_persist[-1]) else 0.0
    kappa_last=float(geom_kappa[-1]) if geom_kappa and _is_num(geom_kappa[-1]) else 0.0
    dX_last=float(geom_dx[-1]) if geom_dx and _is_num(geom_dx[-1]) else 0.0
    candidate_steps=np.diff(np.asarray(bvals,dtype=float)) if len(bvals)>1 else np.asarray([],dtype=float)
    last_candidate_step=float(candidate_steps[-1]) if len(candidate_steps) else 0.0
    previous_candidate_step=float(candidate_steps[-2]) if len(candidate_steps)>1 else last_candidate_step
    # Persistence carries direction; curvature attenuates extrapolation when the path is turning.
    geom_trust=max(0.0,min(1.0,1.0-0.5*max(0.0,min(1.0,kappa_last))))
    geom_direction=_clip01(0.5+0.5*math.tanh(25.0*last_candidate_step)*persist_last*geom_trust)
    geom_change=_clip01(0.5+0.5*math.tanh(25.0*(last_candidate_step-previous_candidate_step))*geom_trust)
    cameo=features.get("cameo_lateral") or {}
    cameo_activity=_clip01(float(cameo.get("selected_code_count",0))/max(1.0,float(cameo.get("available_codes",1))))
    cameo_profile_activity=_clip01(float(len(cameo.get("profiles") or []))/2.0)
    out={"state":state,"continuity":continuity,"recency":recency,"delta":max(0.0,min(1.0,0.5+delta)),
         "lateral_breadth":breadth,"axis_convergence":convergence,
         "relational_activity":_relational_activity(features),
         "relational_alignment":relation_alignment,
         "caldero_neighbor_activity":neighbor_activity,"caldero_neighbor_memory":memory_activity,
         "caldero_neighbor_alignment":neighbor_alignment,"stinkbox_support":stink_support,
         "own_pattern_evidence":own_evidence,
         "lateral_shared_evidence":lateral_shared,"lateral_candidate_specific":named_specific,
         "lateral_contribution":lateral_contribution,"cameo_activity":cameo_activity,"cameo_profile_activity":cameo_profile_activity,
         "geometric_inertia_alignment":geom_direction,"geometric_direction_change":geom_change,
         "geometric_persistence_context":_clip01(0.5+0.5*persist_last),
         "geometric_turn_context":_clip01(kappa_last),"geometric_latest_movement":dX_last,
         "trajectory_micro_support":trajectory_micro,"trajectory_meso_support":trajectory_meso,
         "trajectory_macro_support":trajectory_macro,"trajectory_acceleration_support":trajectory_accel,
         "trajectory_multiscale_convergence":trajectory_convergence,
         "trajectory_inertia_alignment":_clip01(0.5+(trajectory_micro-0.5)*persist_last*geom_trust),
         "trajectory_curvature_response":_clip01(0.5+(trajectory_accel-0.5)*(1.0-min(1.0,max(0.0,kappa_last)))),
         "_tb_slope":tb_slope,
         **structural, **dynamis}
    if analog_alignment is not None: out["analog_alignment"]=analog_alignment
    return out

def _resolution_pass(boards, histories, features, ordered, native_tortugas=None):
    """Resolve ambiguity by re-reading the SAME frozen input at three resolutions.

    This is not a closure mechanism and never writes H. Each level uses a different
    observable representation: micro=local axis motion, meso=relational coactivation,
    macro=whole-trajectory persistence/turning. A level may add evidence; it may not
    change a family by fiat. The returned values are evidence for the predictor.
    """
    if not ordered:
        return {"status":"NO_CANDIDATES","levels":[]}
    names=[x[0] for x in ordered]
    # Initial ambiguity: close candidates or native trajectory blur.
    initial_margin=float(ordered[0][1].get("rank_fusion",0.0) - (ordered[1][1].get("rank_fusion",0.0) if len(ordered)>1 else 0.0))
    native_blur=bool((native_tortugas or {}).get("borroso"))
    trigger = initial_margin < 1.0 or native_blur
    if not trigger:
        return {"status":"NOT_NEEDED","trigger":False,"levels":[]}

    levels=[]
    current=set(names)

    # MICRO: local trajectory direction and axis agreement, using the latest two cuts.
    micro={}
    for n in names:
        seq=[]
        for b in boards[-3:]:
            vals=[float(b[a].get(n,0.0)) for a in ("P","A","C")]
            seq.append(float(np.mean(vals)))
        if len(seq)>=2:
            d=seq[-1]-seq[-2]
            local=max(0.0,min(1.0,0.5+2.0*d))
        else: local=0.5
        last=[float(boards[-1][a].get(n,0.0)) for a in ("P","A","C")]
        spread=float(np.std(last))
        axis=max(0.0,1.0-min(1.0,spread*4.0))
        micro[n]=0.65*local+0.35*axis
    levels.append({"level":1,"name":"micro","reason":"resolver_arista_local","evidence":micro})

    # MESO: relations already extracted by interrelation/Caldero, measured as
    # candidate-neutral context plus named hits; no source can directly select H.
    inter=features.get("interrelation") or {}
    relations=(inter.get("hyperrelations") or [])+(inter.get("movement") or [])
    observed_rel_tokens=set(inter.get("unique_tokens") or [])
    # Candidate-specific meso reading comes from the canonical pattern's own token
    # relations against what the frozen input actually activated. No neighbor is
    # mapped directly to a hypothesis.
    try:
        pat=json.loads((_PATTERNS_PATH()).read_text(encoding="utf-8"))
    except Exception:
        pat={}
    meso={}
    for n in names:
        pv=pat.get(n,{}) if isinstance(pat,dict) else {}
        favor=set((pv.get("tokens_favor") or {}).keys())
        contra=set((pv.get("tokens_contra") or {}).keys())
        f_hits=0; c_hits=0; f_total=max(1,len(favor)); c_total=max(1,len(contra))
        for b in boards:
            active=set()
            for a in ("P","A","C"):
                active.update(b[a].keys())
            f_hits += len(active & favor)/f_total
            c_hits += len(active & contra)/c_total
        temporal_f=f_hits/max(1,len(boards)); temporal_c=c_hits/max(1,len(boards))
        relation_bonus=len((favor|contra)&observed_rel_tokens)/max(1,len(favor|contra))
        # Favor/contra remain signed evidence; relation bonus only resolves
        # whether the pattern's relational vocabulary is actually present.
        meso[n]=max(0.0,min(1.0,0.65*temporal_f-0.25*temporal_c+0.10*relation_bonus+0.15))
    levels.append({"level":2,"name":"meso","reason":"resolver_arista_relacional","evidence":meso})

    # MACRO: persistence and whole-trajectory shape, not another copy of local delta.
    macro={}
    for n in names:
        vals=[]
        for b in boards:
            vals.append(float(np.mean([b[a].get(n,0.0) for a in ("P","A","C")])))
        if not vals:
            macro[n]=0.5; continue
        # Persistence = fraction of cuts in which candidate is above its own median.
        med=float(np.median(vals))
        persistence=sum(v>=med for v in vals)/len(vals)
        # Shape = normalized net displacement + directional persistence, so
        # candidates with genuinely different long trajectories can separate.
        diffs=np.diff(vals)
        if len(vals)>1:
            slope=float(np.polyfit(np.arange(len(vals)),np.asarray(vals),1)[0])
        else: slope=0.0
        slope_norm=max(0.0,min(1.0,0.5+5.0*slope))
        sign_cons=sum(1 for d in diffs if d>0)/max(1,len(diffs))
        macro[n]=0.45*persistence+0.35*slope_norm+0.20*sign_cons
    levels.append({"level":3,"name":"macro","reason":"resolver_arista_trayectoria_total","evidence":macro})

    # The three readings become additional equal-vote evidence dimensions.
    # They do not select a family directly; predictor re-ranks all candidates.
    return {"status":"RESOLVED_INPUT_RESCAN","trigger":True,"initial_margin":round(initial_margin,6),
            "native_blur":native_blur,"levels":levels,
            "contract":"same_frozen_input; micro->meso->macro; no family switch; no direct H feed"}



def _tortuga_traza(boards):
    """Remide el mismo input partiendo cada tramo. No inventa familia."""
    if len(boards)<2:
        return {"traza_legible": False, "cortes": [], "razon": "sin_tramo"}
    fino=[boards[0]]
    for a,b in zip(boards, boards[1:]):
        mid={ax:{k:(float(a[ax].get(k,0.0))+float(b[ax].get(k,0.0)))/2.0 for k in set(a[ax])|set(b[ax])} for ax in ("P","A","C")}
        fino.extend([mid, b])
    moves=[]
    for i in range(1, len(fino)):
        prev=float(sum(float(sum(fino[i-1][ax].values())/max(1,len(fino[i-1][ax]))) for ax in ("P","A","C"))/3)
        cur=float(sum(float(sum(fino[i][ax].values())/max(1,len(fino[i][ax]))) for ax in ("P","A","C"))/3)
        moves.append({"de": i-1, "a": i, "d": round(cur-prev, 6)})
    return {"traza_legible": len(moves)>=2, "n_cortes": len(fino), "cortes": moves, "razon": "remedido_mismo_input"}

def _information_state(rows, histories, motor=None, resolution=None):
    """Determine whether information is sufficient AFTER exhausting input resolution.

    LATENCIA is a state of unresolved information, not permission to stop processing.
    """
    if not rows:
        return {"state":"LATENCIA_INFORMACIONAL", "reason":"sin_candidatos", "evidence_sufficient":False}
    ordered=list(rows)  # CONSOLIDADO: already ordered by _tb_key (no name ordering)
    top=ordered[0][1]["rank_fusion"]
    second=ordered[1][1]["rank_fusion"] if len(ordered)>1 else 0.0
    margin=float(top-second)
    top_name=ordered[0][0]
    seen=sum(top_name in {x["familia"] for x in h} for h in histories)
    separated = margin >= 1.0
    repeated = seen >= 2
    r732=(motor or {}).get("R732") or {}
    dx=list(r732.get("dX_norm") or [])
    latest_dX=float(dx[-1]) if dx else 0.0
    new_signal=latest_dX >= 0.1
    resolution_exhausted=bool(resolution and resolution.get("status") in {"RESOLVED_INPUT_RESCAN","NOT_NEEDED"})
    # New trajectory is necessary, but it is never sufficient by itself.
    sufficient = bool(new_signal and resolution_exhausted and separated)
    reason="informacion_resuelta" if sufficient else ("resolucion_agotada_sin_separacion" if resolution_exhausted else "resolucion_pendiente")
    return {"state":"DETERMINADO" if sufficient else "LATENCIA_INFORMACIONAL",
            "reason":reason,"evidence_sufficient":sufficient,"top_margin":round(margin,6),
            "top_neighbor_support":seen,"latest_dX_norm":round(latest_dX,6),"new_vector_signal":new_signal,
            "resolution_exhausted":resolution_exhausted,
            "closure_rule":"cerrar_solo_si_la_informacion_disponible_fue_resuelta_y_hay_separacion; latencia_no_detiene_la_ejecucion",
            "rule":"LATENCIA = estado informacional, no permiso para dejar de explorar el input congelado"}


def _gate_rows(fused, histories):
    return [{"family":n,"rank_fusion":float(f["rank_fusion"]),
             "seen":int(sum(n in {x["familia"] for x in h} for h in histories))} for n,f in fused]


def _compuerta_cierre(fused, histories, motor, info, gate_ctx):
    """COMPUERTA DE CIERRE (regla Mj). Control de cierre, no lateral: nunca elige H.

    1) Carga pendientes_vivos del StinkBox (cortes/corridas previas).
    2) Los re-evalua con la evidencia actual (review_pending).
    3) Si algun pendiente vivo contradice el cierre propuesto -> no cierra
       (LATENCIA con lista explicita); la ejecucion continua.
    """
    closure_proposed=bool(info.get("evidence_sufficient"))
    top1=fused[0][0] if fused else None
    block={"version":"COMPUERTA_CIERRE_V0.1","cierre_propuesto":closure_proposed,
           "candidato_cierre":top1 if closure_proposed else None,
           "estado_pre_compuerta":info.get("state"),
           "feeds_H":False,"can_decide_H":False,"can_only_withhold_closure":True,
           "regla":"antes_de_cerrar_volver_a_revisar_pendientes; pendiente_vivo_contradictorio=>LATENCIA; latencia_no_detiene_ejecucion"}
    if not gate_ctx or gate_ctx.get("box") is None:
        block.update({"status":"NO_DISPONIBLE","pendientes_revisados":[],"resueltos":[],"siguen_latentes":[],
                      "contradice_cierre":False,
                      "decision":"CIERRE_PERMITIDO_SIN_COMPUERTA" if closure_proposed else "SIN_CIERRE_PROPUESTO"})
        return block
    box=gate_ctx["box"]
    vivos_antes=[v["front_id"] for v in box.pendientes_vivos()]
    r732=(motor or {}).get("R732") or {}
    dx=list(r732.get("dX_norm") or [])
    latest_dX=float(dx[-1]) if dx else 0.0
    rep_=box.review_pending(_gate_rows(fused,histories), gate_ctx["cut_id"],
                            closing_candidate=top1 if closure_proposed else None,
                            latest_dX=latest_dX, separation=GATE_SEPARATION,
                            discard_gap=GATE_DISCARD_GAP, absent_limit=GATE_ABSENT_LIMIT)
    # PATCH 011: pendientes del mismo input = solo traza/latencia; no pueden bloquear ni sumar.
    _ae=gate_ctx.get("ae011"); _cls011=None
    if _ae is not None:
        _cls011=_ae.clasificar_pendientes(box.pendientes_vivos(), gate_ctx.get("input_sha_011"))
        _mismo=set(_cls011["mismo_input"])
        rep_={**rep_,"contradicen_cierre":[f for f in (rep_.get("contradicen_cierre") or []) if f not in _mismo]}
    contradice=bool(closure_proposed and rep_["contradicen_cierre"])
    if not closure_proposed: decision="SIN_CIERRE_PROPUESTO_LATENCIA_PREVIA"
    elif contradice: decision="CIERRE_BLOQUEADO_LATENCIA"
    else: decision="CIERRE_PERMITIDO"
    block.update({"status":"EJECUTADA","cut_id":gate_ctx["cut_id"],"pending_case_id":box.case_id,
                  "pendientes_vivos_cargados":vivos_antes,
                  "pendientes_revisados":rep_["revisados"],
                  "resueltos":{"a_favor":rep_["resueltos_a_favor"],"en_contra":rep_["resueltos_en_contra"]},
                  "siguen_latentes":rep_["siguen_latentes"],
                  "pendientes_que_contradicen":rep_["contradicen_cierre"],
                  "contradice_cierre":contradice,"decision":decision,
                  "detalle_revision":rep_["detalle"],
                  "autoevidencia_011":_cls011})
    return block


def _registrar_latencia_por_frente(fused, histories, motor, info, gate_ctx, gate):
    """Escribe latencia run-global + por frente DESPUES de information_state/compuerta.
    Frentes vivos sin separacion suficiente quedan LATENTE (no descartados)."""
    if not gate_ctx or gate_ctx.get("box") is None or not fused:
        return {"status":"NO_DISPONIBLE","abiertos":[]}
    box=gate_ctx["box"]; cut=gate_ctx["cut_id"]
    rows=_gate_rows(fused,histories)
    # PATCH 011: procedencia en cada pendiente nuevo; si el input ya estaba registrado (repetición), no se suman latency_events.
    _sha011=gate_ctx.get("input_sha_011"); _rep011=bool(gate_ctx.get("repeticion_011"))
    import datetime as _dt011
    _prov011={"input_sha":_sha011,"registrado_utc":_dt011.datetime.now(_dt011.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),"motor":VERSION}
    _lat=(lambda **_k: None) if _rep011 else box.record_latency
    top=rows[0]; margin=top["rank_fusion"]-(rows[1]["rank_fusion"] if len(rows)>1 else 0.0)
    r732=(motor or {}).get("R732") or {}
    dx=list(r732.get("dX_norm") or []); latest_dX=float(dx[-1]) if dx else 0.0
    new_signal=latest_dX>=0.1
    opened=[]
    def miss_for(row, is_top):
        m=[]
        if is_top:
            if margin<GATE_SEPARATION: m.append(f"margen_separacion>={GATE_SEPARATION}")
        else:
            m.append(f"separacion_top1_vs_frente>={GATE_DISCARD_GAP}_o_frente_como_top1_con_margen>={GATE_SEPARATION}")
        if row["seen"]<2: m.append("soporte_repetido(seen>=2)")
        if not new_signal: m.append("senal_vectorial_nueva(dX>=0.1)")
        return m
    if margin<GATE_SEPARATION:
        ev={"rank_pos":1,"rank_fusion":round(top["rank_fusion"],6),"top_margin":round(margin,6),"seen":top["seen"],"latest_dX_norm":round(latest_dX,6)}
        box.record_pending(front_id=top["family"],cut_id=cut,reason="top1_sin_separacion_suficiente",missing=miss_for(top,True),evidence=ev,save=False,input_sha=_sha011,procedencia_011=_prov011)
        _lat(state="LATENTE",reason="top1_sin_separacion_suficiente",cut_id=cut,front_id=top["family"],detail=ev,save=False)
        opened.append(top["family"])
    for i,row in enumerate(rows[1:GATE_PENDING_TOPK],start=2):
        gap=top["rank_fusion"]-row["rank_fusion"]
        ev={"rank_pos":i,"rank_fusion":round(row["rank_fusion"],6),"gap_to_top":round(gap,6),"seen":row["seen"],"latest_dX_norm":round(latest_dX,6)}
        if gap<GATE_DISCARD_GAP:
            reason=("H2_" if i==2 else "")+("rival_vivo_sin_separacion" if gap<GATE_SEPARATION else "rival_en_banda_intermedia")
            box.record_pending(front_id=row["family"],cut_id=cut,reason=reason,missing=miss_for(row,False),evidence=ev,save=False,input_sha=_sha011,procedencia_011=_prov011)
            _lat(state="LATENTE",reason=reason,cut_id=cut,front_id=row["family"],detail=ev,save=False)
            opened.append(row["family"])
        elif i==2:
            # H2 always leaves a trace per front, even when already separated.
            _lat(state="SEPARADO",reason="H2_separado_gap>=discard_gap",cut_id=cut,front_id=row["family"],detail=ev,save=False)
    _lat(state=info.get("state","UNKNOWN"),reason=info.get("reason",""),cut_id=cut,
                       detail={"top1":top["family"],"top_margin":round(margin,6),"compuerta":gate.get("decision"),
                               "pendientes_bloqueantes":gate.get("pendientes_que_contradicen",[])},save=False)
    box._touch(); box._save()
    cbox=gate_ctx.get("case_box")
    if cbox is not None and cbox.case_id!=box.case_id and not _rep011:
        # the case vault also receives the run-global latency (fix: 0 latency_events)
        cbox.data=cbox._load_or_create()
        cbox.record_latency(state=info.get("state","UNKNOWN"),reason=info.get("reason",""),cut_id=cut,
                            detail={"top1":top["family"],"top_margin":round(margin,6),"compuerta":gate.get("decision"),
                                    "pending_case_id":box.case_id,"fronts_latentes":opened})
    return {"status":"ESCRITO","cut_id":cut,"pending_case_id":box.case_id,"abiertos_o_reafirmados":opened,
            "pendientes_vivos_despues":[v["front_id"] for v in box.pendientes_vivos()],
            "pending_fronts_sha256":box.pending_digest(),
            "idempotencia_011":{"input_sha":_sha011,"repeticion":_rep011,"pendientes_deduplicados":int(getattr(box,"pending_dedup_011",0)),
                                "latency_events_omitidos":_rep011}}


def _candidate_history_for_cut(cut):
    """Universo de candidatas del corte: unión PAC, con ejes de procedencia."""
    by_family = {}
    for axis, key in (("P", "P_candidatos_0a3"), ("A", "A_candidatos_0a3"), ("C", "C_candidatos_0a3")):
        for item in (cut.get(key) or []):
            if isinstance(item, dict) and item.get("familia"):
                family = str(item["familia"])
                row = by_family.setdefault(family, {"familia": family, "ejes": []})
                if axis not in row["ejes"]:
                    row["ejes"].append(axis)
    return list(by_family.values())


def _candidate_histories_from_cuts(cuts):
    """Misma construcción PAC para corrida principal y contrafactuales."""
    return [_candidate_history_for_cut(cut) for cut in (cuts or [])]


def _predict(boards, histories, motor, features, gate_ctx=None, adversarial_exclude_dimensions=()):
    names=set()
    for h in histories: names.update(x["familia"] for x in h)
    candidates=sorted(names)
    if not candidates: return {"status":"INDETERMINADO","candidates":[]}
    cuts=features.get("cuts") or []
    cand_ev={n:_candidate_token_evidence(n,cuts) for n in candidates}
    matrix,bridge_log=_bridge_matrix(features,candidates)
    bridge_feats,bridge_active=_bridge_candidate_features(matrix,candidates)
    ctx={"cand_ev":cand_ev,"bridge":bridge_feats}
    rows=[(n,_feature_vector(n,histories,boards,motor,features,ctx)) for n in candidates]
    lateral_signal_map,lateral_signal_registry=_lateral_signal_contributions(matrix,candidates,bridge_active)
    for n,f in rows:
        f["lateral_signal_contributions"]=dict(lateral_signal_map.get(n) or {})
    # (c) only finite numeric fields enter the rank sort; lists/strings (e.g. dynamis_tokens_active) never do.
    all_keys=list(rows[0][1])
    numeric_keys=[k for k in all_keys if not k.startswith("_") and k != "lateral_contribution" and k not in set(adversarial_exclude_dimensions or ()) and all(_is_num(f.get(k)) for _,f in rows)]
    # PATCH 02: when each discriminating bridge signal is added separately below,
    # do not also rank the two aggregates derived from that same bridge matrix.
    # Keep them in features for diagnostics and for the non-additive ablation path.
    if not _off("contribucion_lateral_aditiva"):
        numeric_keys=[k for k in numeric_keys if k not in {"lateral_candidate_specific", "lateral_breadth"}]
    non_numeric=[k for k in all_keys if k not in numeric_keys and not k.startswith("_")]
    # (b) constant / duplicate dimensions are excluded from fusion (logged, not deleted).
    keys,excl_const,excl_dup=_dimension_guard(rows,numeric_keys)
    scorer=_legacy_scores if _off("desempate_no_nombre") else _frac_scores
    ranks={n:0.0 for n,_ in rows}
    for k in keys:
        sc=scorer(rows,k)
        for n in ranks: ranks[n]+=sc[n]
    if not _off("contribucion_lateral_aditiva"):
        # Distinct lateral signals remain separate. Only discriminating signals enter rank_fusion.
        for n,f in rows:
            for signal_value in (f.get("lateral_signal_contributions") or {}).values():
                ranks[n]+=float(signal_value)
    ordered=sorted(rows,key=lambda z:_tb_key(z[0],z[1],ranks[z[0]]))
    fused=[(n,{**f,"rank_fusion":ranks[n]}) for n,f in ordered]
    native_tortugas=(((motor.get("protocolo") or {}).get("tortugas") or motor.get("tortugas")) if isinstance(motor,dict) else None) or {}
    resolution={"status":"ABLATED","levels":[]} if _off("resolucion") else _resolution_pass(boards,histories,features,fused,native_tortugas)
    if isinstance(resolution, dict):
        resolution={**resolution, **_tortuga_traza(boards)}
    res_excl=[]
    if resolution.get("levels"):
        levelmap={x["name"]:x["evidence"] for x in resolution["levels"]}
        for n,f in fused:
            f["resolution_micro"]=levelmap["micro"].get(n,0.5)
            f["resolution_meso"]=levelmap["meso"].get(n,0.5)
            f["resolution_macro"]=levelmap["macro"].get(n,0.5)
        r2={n:ranks[n] for n in names}
        rk,rc,rd=_dimension_guard(fused,["resolution_micro","resolution_meso","resolution_macro"])
        res_excl=rc+[d["dimension"] for d in rd]
        for k in rk:
            sc=scorer(fused,k)
            for n in r2: r2[n]+=sc[n]
        ordered=sorted(fused,key=lambda z:_tb_key(z[0],z[1],r2[z[0]]))
        fused=[(n,{**f,"rank_fusion":r2[n]}) for n,f in ordered]
        keys_used=keys+rk
    else:
        keys_used=list(keys)
    # PATCH 03: zero-based, group-balanced potential index + normalized entropy diagnostic.
    # This is structural calibration of the score, not empirical hit-rate calibration.
    def _cal_group(k):
        if k in {"state", "continuity", "delta", "axis_convergence", "own_pattern_evidence"}: return "trayectoria_estado"
        if k.startswith("booker_"): return "booker"
        if k.startswith("greimas_"): return "greimas"
        if k.startswith("frye_"): return "frye"
        if k.startswith("coupling_"): return "acoplamiento"
        if k.startswith("structural_"): return "estructura"
        if k.startswith("dynamis_"): return "dynamis"
        if k.startswith("resolution_"): return "resolucion"
        if k.startswith("geometric_"): return "geometria_inercia"
        return "otras_dimensiones"
    group_dims={}
    dim_scores={}
    for k in keys_used:
        sc=scorer(fused,k)
        grp=_cal_group(k)
        group_dims.setdefault(grp,[]).append(k)
        for n in dim_scores.keys() | {name for name,_ in fused}:
            dim_scores.setdefault(n,{})[k]=float(sc.get(n,0.0))
    lateral_names=sorted({sig for _,f in fused for sig in (f.get("lateral_signal_contributions") or {})})
    if lateral_names:
        group_dims["puente_lateral"] = lateral_names
    active_groups=sorted(group_dims)
    calibrated_by_candidate={}
    for n,f in fused:
        group_detail={}; fractions=[]
        for grp in active_groups:
            dims=group_dims[grp]
            if grp=="puente_lateral":
                vals=[float((f.get("lateral_signal_contributions") or {}).get(sig,0.0)) for sig in dims]
            else:
                vals=[float(dim_scores.get(n,{}).get(k,0.0)) for k in dims]
            subtotal=sum(vals); maximum=float(len(dims))
            frac=(subtotal/maximum) if maximum>0 else 0.0
            frac=max(0.0,min(1.0,frac))
            group_detail[grp]={"aporte":round(subtotal,6),"maximo":maximum,"fraccion_0_1":round(frac,6),"porcentaje_del_maximo":round(frac*100.0,4),"n_componentes":len(dims)}
            fractions.append(frac)
        idx=(sum(fractions)/len(fractions)) if fractions else 0.0
        calibrated_by_candidate[n]={"indice_potencial_equilibrado_0_1":round(idx,8),"indice_potencial_equilibrado_pct":round(idx*100.0,6),"grupos":group_detail}
    # Entropy is calculated over the normalized distribution of these structural indices.
    # It measures dispersion/uncertainty among candidates, not probability of a correct answer.
    import math as _math
    idx_vals=[max(0.0,float(calibrated_by_candidate[n]["indice_potencial_equilibrado_0_1"])) for n,_ in fused]
    total_idx=sum(idx_vals); n_candidates=len(idx_vals)
    if n_candidates>1:
        probs=([v/total_idx for v in idx_vals] if total_idx>0 else [1.0/n_candidates]*n_candidates)
        entropy=-sum(q*_math.log(q) for q in probs if q>0)
        max_entropy=_math.log(n_candidates)
        entropy_norm=max(0.0,min(1.0,entropy/max_entropy))
        entropy_diag={"entropia_normalizada_0_1":round(entropy_norm,8),"entropia_relativa_pct":round(entropy_norm*100.0,6),"concentracion_complementaria_pct":round((1.0-entropy_norm)*100.0,6),"entropia_maxima_nats":round(max_entropy,8),"n_candidatos":n_candidates,"distribucion_indices_no_probabilistica":True}
    else:
        entropy_diag={"entropia_normalizada_0_1":None,"entropia_relativa_pct":None,"concentracion_complementaria_pct":None,"entropia_maxima_nats":None,"n_candidatos":n_candidates,"distribucion_indices_no_probabilistica":True}
    for n,f in fused:
        f.update(calibrated_by_candidate[n])
        f["entropia_relativa_candidatos_pct"]=entropy_diag["entropia_relativa_pct"]
        f["concentracion_complementaria_candidatos_pct"]=entropy_diag["concentracion_complementaria_pct"]
    emp=_empates(fused)
    info=_information_state(fused,histories,motor,resolution)
    if emp["top1_top2_empate"]:
        info={**info,"state":"EMPATE","reason":"empate_exacto_top1_top2_no_se_ordena_en_silencio","evidence_sufficient":False,
              "empate":emp["grupos_empate_top10"][0] if emp["grupos_empate_top10"] else [fused[0][0],fused[1][0]]}
    gate=_compuerta_cierre(fused,histories,motor,info,gate_ctx)
    if gate.get("decision")=="CIERRE_BLOQUEADO_LATENCIA":
        info={**info,"state":"LATENCIA_INFORMACIONAL","reason":"compuerta_cierre_pendientes_vivos_contradicen",
              "evidence_sufficient":False,"state_pre_compuerta":"DETERMINADO",
              "pendientes_bloqueantes":list(gate.get("pendientes_que_contradicen") or [])}
    latency_write=_registrar_latencia_por_frente(fused,histories,motor,info,gate_ctx,gate)
    gate["latencia_escrita"]=latency_write
    def pub(f): return {k:v for k,v in f.items() if not k.startswith("_")}
    payload={"status":"OK" if info["evidence_sufficient"] else ("EMPATE" if info["state"]=="EMPATE" else "LATENCIA_INFORMACIONAL"),
             "method":"rank_fusion_fractional_ties_constant_guard_plus_bounded_lateral_plus_resolution_rescan",
             "dimensions":keys_used,
             "dimension_guard":{"n_numeric":len(numeric_keys),"used":len(keys_used),
                                "excluded_constant":excl_const,"excluded_constant_motivo_U6":{k:_motivo_constante_u6(k) for k in excl_const},"excluded_duplicate":excl_dup,
                                "excluded_resolution":res_excl,"non_numeric_never_sorted":non_numeric,
                                "tie_rule":"legacy_name_order" if _off("desempate_no_nombre") else "average_rank_on_ties; final: score,-state,-slope,sha256(candidate)"},
             "name_bridge":{"legacy_exact_only":_off("puente_nombres"),"modules":bridge_log,"modules_discriminating":bridge_active},
             "lateral_signal_registry":lateral_signal_registry,
             "own_evidence":{n:{k:cand_ev[n][k] for k in ("favor_tokens","contra_tokens","favor_mass","contra_mass")} for n,_ in fused},
             "empates":emp,
             "ablation_off":sorted(_off_set()),
             "resolution":resolution,
             "calibracion_estructural":{"metodo":"promedio_equilibrado_de_fraccion_del_maximo_por_grupo_activo","cero":"sin aporte en los grupos activos","techo_teorico_pct":100.0,"grupos_activos":active_groups,"maximo_por_grupo":{g:len(v) for g,v in group_dims.items()},"entropia":entropy_diag,"advertencia":"índice estructural; no es probabilidad ni tasa de acierto. La entropía máxima (100%) significa máxima dispersión/incertidumbre entre candidatos, no máximo acierto."},
             "candidates":[{"family":n,"rank_fusion":round(f["rank_fusion"],6),"indice_fusion_relativo_0_1":round(float(f["rank_fusion"])/max(1,len(keys_used)+max((len(ff.get("lateral_signal_contributions") or {}) for _,ff in fused), default=0)),6),
                         "indice_fusion_relativo_pct":round(100.0*float(f["rank_fusion"])/max(1,len(keys_used)+max((len(ff.get("lateral_signal_contributions") or {}) for _,ff in fused), default=0)),6),
                         "features":pub(f)} for n,f in fused],
             "techo_rank":len(keys_used)+max((len(ff.get("lateral_signal_contributions") or {}) for _,ff in fused), default=0),
             # U3_021: aporte de rango (0..1) de cada dimensión usada, sobre las N candidatas de la fusión (ya calculado arriba; solo se expone).
             "aporte_por_dimension_021":{n:dict(dim_scores.get(n,{})) for n,_ in fused},
             "information_state":info,
             "compuerta_cierre":gate,
             "ranking_top2_sin_cierre":[fused[0][0], fused[1][0] if len(fused)>1 else None]}
    if info["evidence_sufficient"]:
        h1=fused[0]; h2=fused[1] if len(fused)>1 else None
        payload["H1"]={"family":h1[0],"features":pub(h1[1])}
        payload["H2"]={"family":h2[0],"features":pub(h2[1])} if h2 else None
    else: payload["H1"]=None; payload["H2"]=None
    payload["hipotesis_abiertas_contract"]={"cardinalidad_fija":False,"maximo":None,"universo_candidatas_completo":True,
        "geometria_multiescala_en_rank_fusion":["trajectory_micro_support","trajectory_meso_support","trajectory_macro_support",
        "trajectory_acceleration_support","trajectory_multiscale_convergence","trajectory_inertia_alignment","trajectory_curvature_response"],
        "H1_H2_son_alias_compatibilidad":True}
    return payload


def _cortes_finos(boards, histories, idxs):
    """Parte en cortes más finos el tramo alrededor de cada corte marcado: inserta el punto medio entre
    el corte anterior y el marcado, y entre el marcado y el siguiente. Solo interpola lo ya observado
    (mismo input congelado): no agrega tokens ni fuerza. Devuelve (boards_finos, histories_finos, mapa)."""
    idxs=set(i for i in idxs if 0<=i<len(boards))
    out_b=[]; out_h=[]; mapa=[]
    def mid(b1,b2):
        return {ax:{k:0.5*float(b1[ax].get(k,0.0))+0.5*float(b2[ax].get(k,0.0)) for k in set(b1[ax])|set(b2[ax])} for ax in ("P","A","C")}
    for i,b in enumerate(boards):
        if i in idxs and i>0:
            out_b.append(mid(boards[i-1],b)); out_h.append(list(histories[i]) if i<len(histories) else []); mapa.append(f"{i-1}.5")
        out_b.append(b); out_h.append(list(histories[i]) if i<len(histories) else []); mapa.append(str(i))
        if i in idxs and i+1<len(boards):
            out_b.append(mid(b,boards[i+1])); out_h.append(list(histories[i]) if i<len(histories) else []); mapa.append(f"{i}.5")
    return out_b,out_h,mapa


def _tortugas_guardianes(boards, histories, features, pred, motor, ruta):
    """Re-mide con borroso=True sobre cortes subdivididos y devuelve soporte por candidata.
    La capa terminal usa ese soporte para una selección operacional trazable; no inventa evidencia."""
    cands=pred.get("candidates") or []
    if len(cands)<2:
        return {"status":"SIN_CANDIDATOS"}
    ordered=[(c["family"],{"rank_fusion":float(c["rank_fusion"])}) for c in cands]
    top1=cands[0]["family"]
    nat=dict((((motor.get("protocolo") or {}).get("tortugas") or motor.get("tortugas")) if isinstance(motor,dict) else None) or {})
    nat.update({"borroso":True,"origen":"guardianes_no_resuelto","accion":"remedir_mas_fino_no_cambiar_familia"})
    idxs=list(ruta.get("cortes_a_remedir_idx") or [])
    fb,fh,mapa=_cortes_finos(boards,histories,idxs)
    def leer(res):
        niveles={}
        for lv in res.get("levels") or []:
            ev=lv["evidence"]; vmax=max(float(v) for v in ev.values())
            arg=sorted(k for k,v in ev.items() if abs(float(v)-vmax)<=1e-9)
            niveles[lv["name"]]={"argmax":arg[0] if len(arg)==1 else f"EMPATE({len(arg)})","empatados":arg if len(arg)>1 else [],
                                 "valor_argmax":round(vmax,6),"valor_top1":round(float(ev.get(top1,0.0)),6),
                                 "top1_es_argmax":len(arg)==1 and arg[0]==top1}
        return niveles
    base_res=_resolution_pass(boards,histories,features,ordered,nat)
    fino_res=_resolution_pass(fb,fh,features,ordered,nat)
    nb=leer(base_res); nf=leer(fino_res)
    sost=sum(1 for v in nf.values() if v["top1_es_argmax"])
    # Candidate-level evidence from every available tortugas scale. These are
    # diagnostic measurements, not probabilities. They may resolve an operational
    # tie at the terminal stage; raw rank_fusion is retained unchanged.
    support={n:{"votos_argmax":0,"n_mediciones":0,"suma_evidencia":0.0,"evidencia_media":0.0} for n,_ in ordered}
    for res in (base_res,fino_res):
        for lv in res.get("levels") or []:
            ev=lv.get("evidence") or {}
            if not ev: continue
            vals={n:float(v) for n,v in ev.items() if n in support and _is_num(v)}
            if not vals: continue
            mx=max(vals.values())
            winners=[n for n,v in vals.items() if abs(v-mx)<=1e-9]
            for n,v in vals.items():
                support[n]["n_mediciones"]+=1; support[n]["suma_evidencia"]+=v
                if n in winners and len(winners)==1: support[n]["votos_argmax"]+=1
    for n,row in support.items():
        row["evidencia_media"]=round(row["suma_evidencia"]/row["n_mediciones"],8) if row["n_mediciones"] else 0.0
        row["suma_evidencia"]=round(row["suma_evidencia"],8)
    veredicto="TORTUGAS_SOSTIENE_TOP1" if sost>=2 else "TORTUGAS_NO_SEPARA_TOP1"
    return {"status":"EJECUTADO","disparado_por":ruta.get("guardianes_que_objetan"),"native_tortugas":nat,
            "cortes_marcados_idx":idxs,"cortes_marcados":ruta.get("cortes_a_remedir"),"n_cortes_original":len(boards),
            "n_cortes_finos":len(fb),"mapa_cortes_finos":mapa,
            "remedicion_misma_resolucion":nb,"remedicion_cortes_finos":nf,
            "niveles_que_sostienen_top1":sost,"veredicto":veredicto,
            "apoyo_por_candidata":support,
            "efecto":"medición tortugas reutilizada en el desempate operativo terminal; rank_fusion original se conserva y no se interpreta como probabilidad",
            "contract":"same_frozen_input; micro->meso->macro; no future facts; operational tie-break only"}

def _protocolo_orden0(case):
    """UNICO: protocolo_kernel_motor (orden 0) antes de todo. Solo registra; no para salvo candado duro (Engine/catálogo/FREEZE/H)."""
    k=_load("protocolo_kernel_orden0","protocolo_kernel_motor.py")
    if k is None: return {"status":"FALTA_ARCHIVO","file":"protocolo_kernel_motor.py"}
    try:
        k.limpiar_bitacora() if hasattr(k,"limpiar_bitacora") else None
        arr=k.arranque_matriz(); q=str(case.get("question",""))
        clas=k.clasificar_para_protocolo(q) if hasattr(k,"clasificar_para_protocolo") else None
        return {"status":"EXECUTED","version":getattr(k,"__version__",None),"arranque":arr,"clasificacion_pregunta":clas,
                "bitacora":k.bitacora() if hasattr(k,"bitacora") else None,"can_decide_H":False}
    except Exception as e:
        return {"status":"ERROR","error":f"{type(e).__name__}:{e}"}

def _run_geometria_multicapa_working(result: Dict[str, Any], case: Dict[str, Any]) -> Dict[str, Any]:
    """Run the previously separate U6 geometry/trajectory sidecars before the open-H set.

    Outputs are compacted to summaries. The sidecars do not rewrite canonical engine,
    patterns, P/A/C, R732, or the already computed predictor ranking. Their candidate-level
    trace links are consumed by the open hypothesis-set builder, not treated as probabilities.
    """
    if case.get("_internal_analysis_no_external_search"):
        return {"status":"SKIPPED_INTERNAL_ANALYSIS", "reason":"subcorrida_interna_T1_no_escribe_ledger_geometrico",
                "feeds_hypothesis_generation":False, "can_decide_H":False}
    import copy as _copy_geo, tempfile as _tempfile
    from pathlib import Path as _PathGeo
    geo_dir = BASE / "geometria_multicapa"
    required = ("sidecar_latentes_v1.py", "adaptador_convergencia_real_v1.py",
                "teseracto_recursivo_geometria_v0_4.py", "v153_convergencia_multinivel_v0_3.py")
    missing = [x for x in required if not (geo_dir / x).is_file()]
    if missing:
        return {"status":"MISSING_REQUIRED_GEOMETRY_MODULES", "missing":missing,
                "feeds_hypothesis_generation":False, "can_decide_H":False}
    import sys as _sys, importlib.util as _importlib
    _sys.path.insert(0, str(geo_dir))
    def load_geo(name, filename):
        path = geo_dir / filename
        spec = _importlib.spec_from_file_location(name, path)
        if spec is None or spec.loader is None: raise RuntimeError(f"GEO_MODULE_LOAD_FAILED:{filename}")
        mod = _importlib.module_from_spec(spec); _sys.modules[name] = mod; spec.loader.exec_module(mod)
        return mod
    try:
        lat_mod = load_geo("u6_geo_sidecar_latentes", "sidecar_latentes_v1.py")
        ad_mod = load_geo("u6_geo_adaptador_convergencia", "adaptador_convergencia_real_v1.py")
        tes_mod = load_geo("u6_geo_teseracto", "teseracto_recursivo_geometria_v0_4.py")
        root = _STINKBOX_STORAGE_ROOT() / "geometria_multicapa"
        root.mkdir(parents=True, exist_ok=True)
        ledger = root / "relaciones_acumulado.jsonl"
        with _tempfile.TemporaryDirectory(prefix="u6_geo_working_") as td:
            td = _PathGeo(td); result_path = td / "result.json"; side_path = td / "sidecar_latentes.json"
            result_path.write_text(json.dumps(result, ensure_ascii=False, allow_nan=False, default=str), encoding="utf-8")
            lat = lat_mod.run(_copy_geo.deepcopy(result), _copy_geo.deepcopy(case), BASE, ledger)
            side_path.write_text(json.dumps(lat, ensure_ascii=False, allow_nan=False, default=str), encoding="utf-8")
            ad = ad_mod.run(result_path, BASE, side_path, geo_dir / "sidecar_latentes_v1.py")
            tes = tes_mod.run(result_path)
        rb = lat.get("ricci_billar_por_prefijo") or {}
        rb_cuts = {}
        for cid, row in (rb.get("por_corte") or {}).items():
            rb_cuts[str(cid)] = {k: row.get(k) for k in ("cortes_usados", "billar_convergencias_en_este_corte",
                "billar_sobre_nulo", "ricci_media", "ricci_sobre_nulo", "ricci_aristas_negativas_n")}
        suma = lat.get("suma_restando") or {}
        trace_counts = {}
        for row in (suma.get("suma_relaciones_omitidas") or []):
            fam = str(row.get("favorece_a") or "").strip()
            if fam: trace_counts[fam] = trace_counts.get(fam, 0) + 1
        for row in (suma.get("resta_explicaciones_de_desaparicion_con_trayectoria_viva") or []):
            rel = str(row.get("relacion") or "")
            for fam in rel.split("|"):
                fam = fam.strip()
                if fam: trace_counts[fam] = trace_counts.get(fam, 0) + 1
        for row in (suma.get("resta_coincidencias_accidentales") or []):
            rel = str(row.get("relacion") or row.get("par") or "")
            for fam in rel.split("|"):
                fam = fam.strip()
                if fam: trace_counts[fam] = trace_counts.get(fam, 0) + 1
        for row in (rb.get("por_corte") or {}).values():
            for pair in row.get("billar_convergencias_en_este_corte") or []:
                for fam in str(pair).split("|"):
                    fam = fam.strip()
                    if fam: trace_counts[fam] = trace_counts.get(fam, 0) + 1
        pac = tes.get("PAC_pattern_trajectories") or {}
        hier = tes.get("recursive_hierarchy") or {}
        helix = tes.get("helical_trace") or {}
        adapter_pairs = {}
        for pair, row in (ad.get("convergencia_pares_tableros") or {}).items():
            adapter_pairs[pair] = {k: row.get(k) for k in ("final_sobre_inicial", "monotone_contraction", "d_full_244_por_corte")}
        return {
            "status":"EXECUTED", "version":"U6_GEOMETRIA_MULTICAPA_INTEGRADA_WORKING_V1",
            "feeds_hypothesis_generation":True, "can_decide_H":False,
            "sidecar_latentes": {"version":lat.get("version"), "n_cortes":len(lat.get("cortes") or []),
                "n_trayectorias_relacionales":len(lat.get("3_trayectorias_relaciones") or []),
                "n_precedencias":len((lat.get("2_convergencia") or {}).get("precede") or []),
                "n_coocurrencias":len((lat.get("2_convergencia") or {}).get("coocurren") or []),
                "n_reconvergencias":len(lat.get("4_reconvergencia") or []),
                "suma_restando_estado":suma.get("estado"),
                "n_relaciones_omitidas":len(suma.get("suma_relaciones_omitidas") or []),
                "n_expulsiones_con_trayectoria_viva":len(suma.get("resta_explicaciones_de_desaparicion_con_trayectoria_viva") or []),
                "ricci_billar_por_prefijo":{"status":rb.get("status"),"por_corte":rb_cuts},
                "verificacion_H_intacto":(lat.get("verificacion_H_intacto") or {}).get("H_intacto"),
                "ledger":lat.get("ledger")},
            "convergencia_multinivel": {"version":ad.get("version"),
                "R732_serialization_audit":ad.get("chequeo_R732"),
                "jerarquia_recursiva":ad.get("jerarquia_recursiva"),
                "pares_tableros":adapter_pairs,
                "helice_por_tablero":{k:{"eje_pca":(v.get("eje_pca") or {}).get("helix_like"),
                    "drift_axis":(v.get("eje_deriva_primer_ultimo_corte") or {}).get("helix_like"),
                    "nulo_orden_permutado":{q:(v.get("nulo_orden_permutado") or {}).get(q) for q in ("n","frac_helix_like_pct","radius_cv_mediana")}}
                    for k,v in (ad.get("helice_por_tablero") or {}).items()},
                "Tusi": {"motor_median":(ad.get("tusi") or {}).get("lectura"), "n_pairs":len((ad.get("tusi") or {}).get("a_entrada_motor_P_top5") or [])}},
            "teseracto": {"version":tes.get("version"), "n_cortes":tes.get("n_cuts"),
                "R732_serialization_audit":(tes.get("R732_serialization_audit") or {}).get("status"),
                "PAC_pattern_trajectories":{k:pac.get(k) for k in ("coordinate_space","n_patterns","mean_path_length","mean_net_displacement",
                    "n_pair_trajectories_with_endpoint_contraction","n_pair_trajectories_monotone_contraction")},
                "recursive_hierarchy":{k:hier.get(k) for k in ("status","levels","n_levels","n_points","warning","interpretation")},
                "helical_trace":{"status":helix.get("status"),"minimum_cuts":helix.get("minimum_cuts"),
                    "not_physical_validation":helix.get("not_physical_validation"),
                    "n_fits":len(helix.get("fits") or []),
                    "n_helix_like":sum(bool(x.get("helix_like")) for x in (helix.get("fits") or [])),
                    "time_order_null_control":{k:(helix.get("time_order_null_control") or {}).get(k) for k in ("status","n_perm","seed","n_real_helix_like_patterns","empirical_p_one_sided","interpretation")}},
                "execution_controls":tes.get("execution_controls")},
            "candidate_trace_support":dict(sorted(trace_counts.items(), key=lambda x:(-x[1],x[0]))),
            "interpretation_contract":"R732 and candidate multiscale features influence predictor; these external geometric diagnostics enrich traceability and candidate-set inclusion. Descriptive geometry is not physical proof or calibrated probability.",
        }
    except Exception as exc:
        return {"status":"ERROR", "error":f"{type(exc).__name__}:{exc}",
                "feeds_hypothesis_generation":False, "can_decide_H":False}


def run(case: Dict[str,Any], monte_carlo: bool=True) -> Dict[str,Any]:
    catalog_integrity = _verify_patterns_contract()
    _validate_case(case)
    # A5_20261107: filtro 017 cableado al runner único (ver _aplicar_filtro_017).
    case, _f017_traza = _aplicar_filtro_017(case)
    _orden0=_protocolo_orden0(case)
    _RUN_CTX.clear(); _RUN_CTX["case_off"]=list(case.get("consolidado_off") or [])
    # PATCH 011: huella del input congelado (sin rutas del runner) para procedencia e idempotencia de stores.
    _ae011=_load("autoevidencia_stores_011","autoevidencia_stores_011.py")
    _RUN_CTX["input_sha_011"]=_ae011.sha_entrada(case) if _ae011 is not None else None
    _s014=_load("sujetos_014","sujetos_014.py")  # PATCH 014: un sujeto cuenta una vez en el soporte de vecinos
    seed = int(case.get("random_seed", DEFAULT_SEED))
    random.seed(seed)
    z90=case.get("z90_date")
    z_work_kind=case.get("z_work_kind") or ("BIOGRAPHY_Z90" if z90 else "LIVE_PRESENT")
    z_work=case.get("z_work_date") or z90 or (datetime.now().astimezone().date().isoformat() if z_work_kind == "LIVE_PRESENT" else None)
    # FREEZE is an information boundary, not the end of computation.
    freeze={"status":"FROZEN","z_work":z_work,"z90":z90,"z_work_kind":z_work_kind,"future_accessed_during_freeze":False,
            "information_boundary":"all input facts/cuts through Z de trabajo only"}

    ceb = None; ceb_ledger = None; ceb_mod = None
    try:
        # Retained-cut T+1 subruns are auxiliary measurements. They run in isolated
        # subprocesses and do not install process-wide CEB hooks; the primary run keeps
        # full CEB provenance and its complete ledger.
        if not case.get("_internal_analysis_no_external_search"):
            ceb_mod = _load("ceb_runtime_v03", "ceb_runtime_v0_6_flow.py")
            if ceb_mod is not None:
                ceb_root = Path(case.get("ceb_root") or _oscat.environ.get("CEB_ROOT") or (BASE / "ceb_runs"))
                ceb_run_id = str(case.get("ceb_run_id") or f"{case.get('case_id','run')}_{int(datetime.now().timestamp()*1000)}")
                ceb_ledger = ceb_mod.FlowLedger(ceb_root, ceb_run_id)
                ceb = ceb_mod.FlowTracer(ceb_ledger)
                case = ceb.observable(case, "case")
                ceb.ledger.register("run", "motor_run", metadata={"case_id":str(case.get("case_id")),"version":VERSION})
    except Exception:
        ceb = None; ceb_ledger = None; ceb_mod = None

    # Runtime provenance is recorded by CEB from the exact loaded files.
    # This makes motor/copy/capability attribution an execution fact, not a
    # filename-level assertion made after the run.
    native=_load("v153_native_v09","MOTOR_V15_3_NATIVO_V0_9_UNICO.py") or _load("v153_native_v09","MOTOR_V15_3_NATIVO_V0_9.py")
    if native is None: raise RuntimeError("Falta MOTOR_V15_3_NATIVO_V0_9.py")
    execution_identity=None
    if ceb and ceb_ledger:
        _loaded_motor_path=Path(__file__).resolve()
        _native_path=Path(getattr(native,'__file__','')).resolve() if getattr(native,'__file__',None) else None
        _eng_path=(BASE / "Engine_V5_CANONICO_SOLO.py").resolve()
        _pat_path=Path(_PATTERNS_PATH()).resolve()
        _artifacts={"motor":_loaded_motor_path,"native":_native_path,"canonical_engine":_eng_path,"patterns":_pat_path}
        execution_identity=ceb_ledger.record_execution_identity(_artifacts, source_module=_loaded_motor_path)
        # PATCH09: auditar artefactos activos del directorio motor; runs/ contiene
        # snapshots históricos que deliberadamente conservan el hash de su versión.
        _integrity=ceb_ledger.audit_artifact_integrity(
            BASE,
            authorized=_artifacts)
        if not _integrity.get("ok"):
            raise RuntimeError("EXECUTION_INTEGRITY_FAILURE:"+json.dumps(_integrity.get("anomalies"),ensure_ascii=False,sort_keys=True))
    def _native_call():
        try:
            return native.correr_5x3(case["cuts"],pregunta=case.get("question",case["case_id"]),
                                     annex_traza=True,obstaculo=case.get("obstaculo"),texto_polaridad=case.get("texto_polaridad"),
                                     monte_carlo=monte_carlo,
                                     marcador_limite=case.get("marcador_limite_geometrico") or {"modo":"ESTIMADO_DESDE_PREFIJO"})
        finally:
            # The native routine closes on its normal path; this second guard also
            # closes every tracked SQLite engine if an exception interrupts it.
            close_all=getattr(native,"_close_all_engines",None)
            if callable(close_all): close_all()
    motor=ceb.call("native_core", _native_call, shared=[case]) if ceb else _native_call()
    if ceb:
        motor=ceb.observable(motor, "motor")
        _native_sid=ceb.latest_id("native_core")
        if _native_sid: ceb.ledger.seed_mapping("motor", motor, _native_sid)
    # Non-mutating emission adapter: downstream predictor receives exact 244-dimensional boards.
    if not all((c.get("P_FULL_244") is not None and c.get("A_FULL_244") is not None and c.get("C_FULL_244") is not None)
               for c in motor.get("cuts") or []):
        eng_emit=_load("eng_emit_v09", "Engine_V5_CANONICO_SOLO.py")
        if eng_emit is None:
            raise RuntimeError("Falta Engine_V5_CANONICO_SOLO.py para emission adapter")
        pat_path=str(_PATTERNS_PATH())
        q=str(case.get("question", case.get("case_id", "")))
        ep=native._engine(eng_emit, pat_path, q+"_P_EMIT")
        ea=native._engine(eng_emit, pat_path, q+"_A_EMIT")
        ec=native._engine(eng_emit, pat_path, q+"_C_EMIT")
        # U4_todos_tokens: el tablero canónico que alimenta H usa el mismo cuello top-5 por eje que el núcleo nativo.
        _canon_u4=native.load_canonical()[1] if hasattr(native,"cuello_top_k") else None
        # U6 #3: mismo desempate por evidencia que el núcleo nativo (cortes previos + corte actual; nunca posteriores).
        _cu4=(lambda cid,e,rows,prev=None,cur=None: native.cuello_top_k(cid,e,rows,_canon_u4,previos=prev,corte_actual=cur)[0]) if _canon_u4 is not None else (lambda cid,e,rows,prev=None,cur=None: rows)
        try:
            for _iu6,(c, raw) in enumerate(zip(motor.get("cuts") or [], case["cuts"])):
                _pv6=case["cuts"][:_iu6]
                c["P_FULL_244"]=native._board(eng_emit, ep, c["corte"]+"_P_EMIT", _cu4(c["corte"],"P",raw.get("P") or [],_pv6,raw))
                c["A_FULL_244"]=native._board(eng_emit, ea, c["corte"]+"_A_EMIT", _cu4(c["corte"],"A",raw.get("A") or [],_pv6,raw))
                c["C_FULL_244"]=native._board(eng_emit, ec, c["corte"]+"_C_EMIT", _cu4(c["corte"],"C",raw.get("C") or [],_pv6,raw))
            dims=[(len(c.get("P_FULL_244") or {}),len(c.get("A_FULL_244") or {}),len(c.get("C_FULL_244") or {})) for c in motor.get("cuts") or []]
            if not all(a==b==c==_n_patrones() for a,b,c in dims):
                raise RuntimeError(f"EMISSION_ADAPTER_DIMENSION_ERROR:{dims[:3]}")
            motor["emission_adapter"]={"used":True,"mutates_canonical":False,"source":"native._engine + native._board","verified_dim":_n_patrones()}
        finally:
            if hasattr(native, "_close_all_engines"):
                native._close_all_engines()
    else:
        motor["emission_adapter"]={"used":False,"mutates_canonical":False,"source":"native_output","verified_dim":_n_patrones()}

    features,status=_run_module_features(case["cuts"],motor, str(case.get("question", case.get("case_id", ""))), ceb=ceb)
    features["cuts"] = case["cuts"]
    features["marcador_limite_geometrico"] = ((motor.get("R732") or {}).get("marcador_limite_geometrico") or {
        "status":"MISSING", "can_decide_H":False, "feeds_H":False, "rank_effect":"NONE"})
    def _ceb_stage(name, fn, shared=None):
        return ceb.call(name, fn, shared=(shared or [case, motor, features])) if ceb else fn()
    # CAMEO: question-conditioned institutional event taxonomy; lateral only.
    try:
        cameo_mod=_load("cameo_institucional", "plugin_cameo_institucional.py")
        cameo_texts=[str(case.get("question", ""))]
        for cc in case.get("cuts") or []:
            cameo_texts += [str(x) for x in (cc.get("facts") or [])]
        for cc in case.get("cuts") or []:
            for ax in ("P","A","C"):
                cameo_texts += [str(x[0]) for x in (cc.get(ax) or []) if isinstance(x,(list,tuple)) and x]
        def _do_cameo():
            out = cameo_mod.evaluate(case.get("question", case.get("case_id", "")), cameo_texts) if cameo_mod else {"status":"PLUGIN_SALTADO","reason":"archivo_no_disponible"}
            if isinstance(out, dict) and "feeds_H" in out:
                # PATCH 010b: feeds_H coherente con la fila (= discriminates); la declaración original del módulo queda aparte.
                out["feeds_H_declarado_modulo"] = out.get("feeds_H"); out["feeds_H"] = bool(out.get("discriminates", False))
            features["cameo_lateral"] = out
            return out
        cameo = _ceb_stage("plugin_cameo_institucional", _do_cameo)
    except Exception as exc:
        cameo={"status":"ERROR","reason":f"{type(exc).__name__}:{exc}"}
        features["cameo_lateral"] = cameo
    cameo_discriminates=bool(cameo.get("discriminates",False))
    status.append({"component":"plugin_cameo_institucional.py","status":cameo.get("status"),"feeds_predictor":True,"feeds_H":cameo_discriminates,"can_decide_H":False,"mutates_canonical":False,"selected_profiles":cameo.get("profiles",[]),"discriminates":cameo_discriminates})
    # CAMEO -> existing 703-token vocabulary -> existing interrelation/lights bus.
    cameo703_mod=_load("cameo_to_703_lateral_v1", "cameo_to_703_lateral_v1.py")
    if cameo703_mod is not None:
        try:
            cameo703=_ceb_stage("plugin_cameo_to_703_lateral", lambda: cameo703_mod.run(case.get("cuts") or [], list(_patterns().keys()), _patterns()))
        except Exception as exc:
            cameo703={"status":"ERROR","reason":f"{type(exc).__name__}:{exc}","events":[],"candidate_scores":{},"feeds_H":False}
    else:
        cameo703={"status":"PLUGIN_SALTADO","events":[],"candidate_scores":{},"feeds_H":False}
    def _store_cameo703():
        features["cameo_703_lateral"] = cameo703
        toks = sorted({str(e.get("token")) for e in (cameo703.get("events") or []) if e.get("token")})
        features["cameo_activated_tokens_703"] = toks
        return cameo703
    cameo703 = _ceb_stage("cameo_to_703_lateral_v1.output", _store_cameo703, shared=[cameo703])
    cameo_tokens=sorted({str(e.get("token")) for e in (cameo703.get("events") or []) if e.get("token")})
    cameo703_discriminates=bool(cameo703.get("discriminates",False))
    status.append({"component":"cameo_to_703_lateral_v1.py","status":cameo703.get("status"),
                   "feeds_predictor":bool(cameo_tokens),"feeds_H":cameo703_discriminates,"can_decide_H":False,
                   "mutates_canonical":False,"events_n":len(cameo703.get("events") or []),
                   "event_tokens":cameo_tokens,"mapping":cameo703.get("mapping"),"new_weights":False,
                   "discriminates":cameo703_discriminates})
    transversal=_ceb_stage("plugin_guardia_no_cruce.absorbed", lambda: _run_transversal_guards(case,motor,features), shared=[motor,features])

    # CALDERO SEARCH: OPTIONAL external-search stage; lateral evidence/context only, never writes H1/H2.
    # El motor es AGNOSTICO: la busqueda usa proveedores libres primero (ORDEN_AUTO de
    # caldero_buscadores: ddgs, ddg, bing, searx, wiki, google; Exa/Brave/Serper/Tavily
    # solo si hay clave) y nunca es puerta de la corrida. Sin red ni clave corre offline
    # y la corrida completa (exit 0). Exa es un proveedor opcional mas, nunca un requisito.
    caldero_mod=_load("caldero_search", "sidecar_caldero_busqueda_arquetipos.py")
    _neighbor_persistence_010b={"status":"SEARCH_NOT_EXECUTED","required":False,"reason":"no result yet"}
    _caldero_attempt={"required":False,"status":"NOT_RUN","provider":"auto","query_count":0,"result_count":0}
    if case.get("_internal_analysis_no_external_search"):
        _caldero_attempt={"required":False,"status":"SKIPPED_INTERNAL_ANALYSIS","provider":"none","query_count":0,"result_count":0,
                          "reason":"subcorrida_interna_para_comparacion_de_corte; la búsqueda externa pertenece a la corrida primaria"}
        features["caldero_busqueda_arquetipos"]={"status":"SKIPPED_INTERNAL_ANALYSIS","required":False,"can_decide_H":False}
        status.append({"component":"sidecar_caldero_busqueda_arquetipos.py","status":"SKIPPED_INTERNAL_ANALYSIS","required":False,
                       "reason":"internal_cut_comparison","feeds_predictor":False,"feeds_H":False,"can_decide_H":False})
    elif caldero_mod is None:
        _caldero_attempt.update({"status":"FAILED","error":"sidecar_missing"})
        status.append({"component":"sidecar_caldero_busqueda_arquetipos.py","status":"OPTIONAL_STAGE_FAILED","required":False,"reason":"sidecar_missing","feeds_predictor":False,"feeds_H":False,"can_decide_H":False})
    else:
        try:
            identity=caldero_mod.SelfMatchIdentity.from_mapping(_case_identity(case))
            active_raw=case.get("caldero_archetype_input") or _build_pre_h_blind_input(case,motor,features)
            active=caldero_mod.ArchetypeInput.from_mapping(active_raw)
            bridge=case.get("caldero_search_bridge")
            # AGNOSTICO_20261024: CALDERO_BUSQUEDA_VIVA=1 -> ignora el puente grabado (p.ej. chatgpt_connected_tool)
            # y busca en vivo con buscador libre agnóstico (CALDERO_BUSCADOR, default auto). Query ciega y filtro de identidad intactos.
            import os as _os_ag
            _bridge_ignorado=None
            if _os_ag.environ.get("CALDERO_BUSQUEDA_VIVA")=="1" and bridge is not None:
                _bridge_ignorado=str((bridge or {}).get("bridge_id") or "") if isinstance(bridge,dict) else "?"; bridge=None
            # Procedencia bibliográfica del caso NO equivale a una búsqueda ejecutada.
            # Solo fixtures explícitos pueden usar el adaptador estático.
            supplied = case.get("caldero_search_fixture") if case.get("allow_static_search_fixture") is True else None
            if bridge is not None:
                # PATCH13: puente explícito desde una herramienta conectada del host
                # (p. ej. búsqueda MCP/ChatGPT) al proceso Python. No se confunde con fixture.
                if not isinstance(bridge,dict) or bridge.get("status")!="EXECUTED" or bridge.get("origin")!="connected_tool_call":
                    raise RuntimeError("SEARCH_BRIDGE_INVALID_PROVENANCE")
                expected_query=caldero_mod.build_blind_query(active)
                expected_hash=hashlib.sha256(expected_query.encode("utf-8")).hexdigest()
                if bridge.get("blind_query_sha256") != expected_hash:
                    raise RuntimeError("SEARCH_BRIDGE_QUERY_MISMATCH")
                submitted_query=str(bridge.get("submitted_query") or "")
                if not submitted_query.strip():
                    raise RuntimeError("SEARCH_BRIDGE_SUBMITTED_QUERY_MISSING")
                identity_terms=[str(x).casefold() for x in _identity_terms(case) if str(x).strip()]
                if any(t and t in submitted_query.casefold() for t in identity_terms):
                    raise RuntimeError("SEARCH_BRIDGE_QUERY_EXPOSES_CASE_IDENTITY")
                rows=bridge.get("results") or []
                if not rows:
                    raise RuntimeError("SEARCH_BRIDGE_NO_RESULTS")
                sources=[]
                for row in rows:
                    if not isinstance(row,dict) or not str(row.get("url") or "").startswith(("https://","http://")):
                        raise RuntimeError("SEARCH_BRIDGE_RESULT_URL_INVALID")
                    sources.append(caldero_mod.SearchSource.from_mapping(row))
                adapter=caldero_mod.StaticSearchAdapter(sources)
                adapter.last_receipt={
                    "provider":"chatgpt_connected_tool",
                    "status":"EXECUTED",
                    "query_count":int(bridge.get("query_count", 1)),
                    "result_count":len(sources),
                    "query_sha256":expected_hash,
                    "submitted_query_sha256":hashlib.sha256(submitted_query.encode("utf-8")).hexdigest(),
                    "bridge_id":str(bridge.get("bridge_id") or ""),
                    "tool_name":str(bridge.get("tool_name") or "connected_search_tool"),
                    "origin":"connected_tool_call",
                    "provenance_note":"results supplied by host tool orchestration; not a local HTTP request"
                }
                _caldero_provider="chatgpt_connected_tool"
            elif supplied is not None:
                sources=[caldero_mod.SearchSource.from_mapping(x) if isinstance(x,dict) and hasattr(caldero_mod.SearchSource,"from_mapping") else (caldero_mod.SearchSource(**x) if isinstance(x,dict) else x) for x in supplied]
                adapter=caldero_mod.StaticSearchAdapter(sources)
                _caldero_provider="provided_fixture"
            else:
                adapter=caldero_mod.create_search_adapter()
                _caldero_provider=getattr(adapter,"last_receipt",{}).get("provider") or type(adapter).__name__.replace("SearchAdapter", "").casefold()
            # A5_20261107: corte temporal del Caldero (vecinos <= Z). Z := freeze
            # (equivale a z_trabajo), nunca z_work_date sin normalizar. Modo por env
            # CALDERO_CORTE_TEMPORAL: leniente (defecto; descarta solo fuentes con
            # fecha conocida > Z, conserva sin fecha con marca) o estricto
            # (descarta también las sin fecha). Ver sidecar TemporalCutoffFilter.
            _z_corte=_resolver_z_corte(case)
            _corte_modo=_os_ag.environ.get("CALDERO_CORTE_TEMPORAL","leniente").strip().lower()
            if _corte_modo not in ("leniente","estricto","off"): _corte_modo="leniente"
            def _do_caldero():
                # GUARDIAN_PISTAS_LLM_20261025: las pistas LLM pasan por guardián (identidad/futuro/calendario) ANTES del sidecar;
                # antes entraban crudas (las fuentes web sí pasaban SelfMatchFilter).
                _hints=case.get("caldero_llm_neighbor_hints"); _gpl=_load("guardian_pistas_llm_caldero","guardian_pistas_llm_caldero_v1.py")
                if _gpl is None and _hints: raise RuntimeError("GUARDIAN_PISTAS_LLM_AUSENTE")
                _hints,_gpl_audit=(_gpl.filtrar(_hints,_identity_terms(case)) if _gpl is not None else ([],{"guardian":"ausente","entrada":0}))
                # A5_20261107: las pistas aceptadas quedan en la auditoría para que el
                # cierre operativo (llm_hint_scores) use SOLO las que pasaron el guardián
                # y no vuelva a leer el caso crudo.
                _gpl_audit["aceptadas_detalle"]=_hints
                out=caldero_mod.CalderoArchetypeSearchSidecar(adapter,caldero_mod.SelfMatchFilter(identity)).run(active,llm_neighbor_hints=_hints,cutoff_date=_z_corte,corte_modo=_corte_modo)
                out.setdefault("audit",{})["guardian_pistas_llm"]=_gpl_audit
                features["caldero_busqueda_arquetipos"]=out
                return out
            caldero_search=_ceb_stage("sidecar_caldero_busqueda_arquetipos",_do_caldero)
            _provider_receipt=(caldero_search.get("audit") or {}).get("provider_receipt") or getattr(adapter,"last_receipt",{}) or {}
            _caldero_attempt={"required":False,"status":"EXECUTED" if (_provider_receipt.get("status")=="EXECUTED" and _provider_receipt.get("provider") not in ("static_fixture","provided_fixture")) else "EXECUTED_FIXTURE","provider":_provider_receipt.get("provider") or _caldero_provider,"query_count":int(_provider_receipt.get("query_count",1)),"result_count":int(_provider_receipt.get("result_count",len((caldero_search.get("audit") or {}).get("raw_sources_before_self_match") or []))),"query_sha256":_provider_receipt.get("query_sha256"),"raw_sources":len((caldero_search.get("audit") or {}).get("raw_sources_before_self_match") or []),"self_match_discarded":len((caldero_search.get("audit") or {}).get("discarded_by_self_match") or []),"tokens_after_filter":len(((caldero_search.get("caldero_input") or {}).get("tokens_neighbors") or [])),"z_corte":_z_corte,"corte_temporal":((caldero_search.get("audit") or {}).get("corte_temporal") or {})}
            if _bridge_ignorado is not None: _caldero_attempt["bridge_grabado_ignorado"]=_bridge_ignorado
            for _trace_key in ("bridge_id","tool_name","origin","submitted_query_sha256","provenance_note","query","urls","consultado_utc","selector","attempts","llm"):
                if _provider_receipt.get(_trace_key) is not None: _caldero_attempt[_trace_key]=_provider_receipt.get(_trace_key)
            try:
                store_mod=_load("caldero_neighbor_store","vecinos_caldero/neighbor_store.py")
                if store_mod is None: raise RuntimeError("Falta vecinos_caldero/neighbor_store.py")
                store_root=Path(case.get("caldero_neighbor_store_root") or (_STINKBOX_STORAGE_ROOT()/"vecinos_caldero"))
                store=store_mod.NeighborStore(store_root)
                _q011=str((caldero_search.get("audit") or {}).get("query_exact",""))
                _memory_stopwords={"a","an","and","are","as","at","be","by","for","from","in","is","it","of","on","or","the","this","to","under","vs","whether","with","how","may","can","will","that","these","those","their","they","we","our","you","your","between","including","through","online","published","study","article","case"}
                _tn011=[]
                for _tokrow in ((caldero_search.get("caldero_input") or {}).get("tokens_neighbors") or []):
                    if not isinstance(_tokrow,dict): continue
                    _tok=str(_tokrow.get("token") or "").strip().casefold()
                    if len(_tok)>2 and _tok not in _memory_stopwords and not re.fullmatch(r"\d+|(?:19|20)\d{2}",_tok): _tn011.append({**_tokrow,"token":_tok})
                _prev011=_ae011.evento_vecinos_ya_registrado(store_root,str(case["case_id"]),_RUN_CTX.get("input_sha_011"),_q011,_tn011) if _ae011 is not None else None
                _meta011={"raw_sources":_caldero_attempt["raw_sources"],"discarded_self_match":_caldero_attempt["self_match_discarded"],"final_neighbors":len(_tn011),"identity_exposed_to_caldero":False,"provider_receipt":_provider_receipt,"z_corte":_z_corte,"corte_temporal":((caldero_search.get("audit") or {}).get("corte_temporal") or {})}
                if _RUN_CTX.get("input_sha_011"): _meta011["input_sha_011"]=_RUN_CTX.get("input_sha_011")
                if _s014 is not None: _meta011["sujeto_014"]=_s014.sujeto_de_caso(case)[0]
                persist=_ceb_stage("vecinos_caldero/neighbor_store.py",lambda:({"event_id":_prev011.get("event_id"),"tokens_added_or_updated":[],"store":str(store_root),"idempotencia_011":"YA_REGISTRADO:"+str(_prev011.get("criterio"))} if _prev011 else store.append(case_id=str(case["case_id"]),query=_q011,tokens_neighbors=_tn011,audit_meta=_meta011)),shared=[caldero_search])
                caldero_search["persistence"]={"status":"YA_PERSISTIDO_011" if _prev011 else "PERSISTED","store":str(store_root),**persist}
                _neighbor_persistence_010b=dict(caldero_search["persistence"])
                status.append({"component":"vecinos_caldero/neighbor_store.py","status":"EXECUTED","feeds_predictor":True,"feeds_H":True,"can_decide_H":False,"contributes_to_H":True,"contributes_to_apuesta":True,"role":"persistent_lateral_memory"})
            except Exception as exc:
                caldero_search["persistence"]={"status":"PERSISTENCE_ERROR","error":str(exc)}
                status.append({"component":"vecinos_caldero/neighbor_store.py","status":"ERROR","error":str(exc)})
            # A5_20261107: el status de la fila es el del recibo (_caldero_attempt).
            # Antes decía EXECUTED siempre, incluso con fixture (EXECUTED_FIXTURE en
            # el recibo); el estado honesto solo vivía en el CEB.
            status.append({"component":"sidecar_caldero_busqueda_arquetipos.py","status":_caldero_attempt["status"],"required":False,"feeds_predictor":True,"feeds_H":True,"can_decide_H":False,"contributes_to_H":True,"contributes_to_apuesta":True,"role":"lateral_evidence_context","external_search_receipt":_caldero_attempt})
        except Exception as exc:
            _failed_provider_receipt=dict(getattr(locals().get("adapter"),"last_receipt",{}) or {})
            _caldero_attempt={"required":False,"status":"FAILED","provider":_failed_provider_receipt.get("provider") or _os.environ.get("SEARCH_PROVIDER","auto"),"query_count":int(_failed_provider_receipt.get("query_count",0) or 0),"result_count":int(_failed_provider_receipt.get("result_count",0) or 0),"attempts":_failed_provider_receipt.get("attempts",[]),"error":f"{type(exc).__name__}:{exc}"}
            features["caldero_busqueda_arquetipos"]={"status":"OPTIONAL_STAGE_FAILED","error":_caldero_attempt["error"],"required":False,"can_decide_H":False}
            status.append({"component":"sidecar_caldero_busqueda_arquetipos.py","status":"OPTIONAL_STAGE_FAILED","required":False,"error":_caldero_attempt["error"],"feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"contributes_to_H":False,"contributes_to_apuesta":False})
    features["external_archetype_search_receipt"]=_caldero_attempt

    # MONOMITO + CALDERO: puente lateral explícito.
    # El Caldero ya fue ejecutado arriba; solo sus vecinos actuales alimentan
    # la resolución Q1-Q4. La pregunta real viaja al plugin; no se usa "".
    circ=_load("opt_circ","plugin_circulo_monomito_v2.py")  # U6 A7: el fallback al alias v1 (ausente) se quitó; MAPA_NOMBRES: mismo rol
    if circ and hasattr(circ,"posicion_por_corte"):
        _cal_raw=[str(x.get("token")).strip().casefold() for x in ((features.get("caldero_busqueda_arquetipos") or {}).get("caldero_input") or {}).get("tokens_neighbors") or [] if isinstance(x,dict) and str(x.get("token")).strip()]
        _mono_vocab={str(t).strip().casefold() for _q in getattr(circ,"ESTRUCTURAS_CANDIDATAS",{}).values() for t in (_q.get("tokens_candidatos") or [])}
        # CABLEADO_CALDERO_20261112 (5): mapeo por familia, no exact-only.
        # Un vecino mapea si es token favor/contra de alguna familia
        # monomito_XX (vía el catálogo, _patterns()) o si está en el
        # vocabulario de candidatos del plugin (ruta anterior, se conserva).
        # Se registra la ruta por token: familia:cuarto:signo y/o
        # candidato_plugin. El dict del puente dice si lleva o no lleva.
        _mono_fam={}
        try:
            for _fam,_spec in (_patterns().items() if isinstance(_patterns(),dict) else []):
                if not str(_fam).startswith("monomito_"):
                    continue
                try: _n=int(str(_fam).split("_")[1])
                except (ValueError, IndexError): continue
                _q="Q1" if _n<=3 else "Q2" if _n<=6 else "Q3" if _n<=9 else "Q4"
                for _tk in list((_spec.get("tokens_favor") or {})):
                    _mono_fam.setdefault(str(_tk).strip().casefold(),[]).append(f"{_fam}:{_q}:favor")
                for _tk in list((_spec.get("tokens_contra") or {})):
                    _mono_fam.setdefault(str(_tk).strip().casefold(),[]).append(f"{_fam}:{_q}:contra")
        except Exception:
            _mono_fam={}
        _cal_mapa={}
        for _t in sorted(set(_cal_raw)):
            _rutas=[]
            if _t in _mono_vocab:
                _rutas.append("candidato_plugin")
            _rutas.extend(_mono_fam.get(_t,[]))
            if _rutas:
                _cal_mapa[_t]=_rutas
        _cal_current=sorted(_cal_mapa)
        _cal_ignored=sorted({t for t in _cal_raw if t not in _cal_mapa})
        _mono_cuts=[]
        for _raw in (case.get("cuts") or []):
            _cid=str(_raw.get("id") or _raw.get("corte") or "")
            _ts=[]
            for _axis in ("P","A","C"):
                _ts.extend([str(_pair[0]).strip().casefold() for _pair in (_raw.get(_axis) or []) if isinstance(_pair,(list,tuple)) and _pair and str(_pair[0]).strip()])
            _mono_cuts.append((_cid,_ts,str(case.get("question", case.get("case_id", ""))),{}))
        if _mono_cuts:
            # Caldero search is case-level, so current neighbors are attached to
            # the work/final cut only; earlier cuts retain their own frozen tokens.
            # DECISION_MJ_CUARTOS_20261113: el contra CUENTA como evidencia de etapa.
            # Cada cuadrante puede repetirse y llevar varios hilos a la vez (favor y
            # contra son hilos del mismo cuarto); eso no impide ver la transicion.
            # Por eso el puente pasa las RUTAS (familia:cuarto:signo), no solo los
            # nombres: el plugin suma favor y contra como evidencia del cuarto.
            _mono_cuts[-1]=(_mono_cuts[-1][0],_mono_cuts[-1][1],_mono_cuts[-1][2],{"tokens_neighbors":_cal_current,"rutas_vecinos":{t:_cal_mapa.get(t,[]) for t in _cal_current},"source":"caldero_current_run"})
        _mono=_ceb_stage("plugin_circulo_monomito_v2", lambda: circ.posicion_por_corte(_mono_cuts))
        _mono["caldero_bridge"]={"wired":True,"lleva_vecinos":bool(_cal_current),"estado":("CON_VECINOS" if _cal_current else "SIN_VECINOS"),"current_neighbors":_cal_current,"mapeo_por_token":_cal_mapa,"raw_current_neighbors":len(_cal_raw),"ignored_unmapped_neighbors":_cal_ignored,"injected_cut":(_mono_cuts[-1][0] if _mono_cuts and _cal_current else None),"historical_memory_used_as_current":False,"mapping":"familia_monomito_favor_contra_o_candidato_plugin"}
        def _store_mono():
            features["plugin_circulo_monomito"]=_mono
            return _mono
        _ceb_stage("plugin_circulo_monomito_v2.output", _store_mono, shared=[_mono])
        status.append({"component":"plugin_circulo_monomito_v2.py","status":"EXECUTED","feeds_predictor":True,"feeds_H":False,"can_decide_H":False,"caldero_bridge":True,"lleva_vecinos":bool(_cal_current),"current_caldero_neighbors":len(_cal_current),"question_forwarded":True,"role":"lateral_quadrant_resolution"})
    else:
        status.append({"component":"plugin_circulo_monomito_v2.py","status":"PLUGIN_SALTADO","reason":"archivo_o_API_no_disponible","effect":"sin_resolucion_Q1_Q4"})

    # INTERRELACION EXTERNA: se ejecuta dentro del tubo, después del núcleo/laterales
    # y antes del predictor, pero permanece estrictamente fuera de H.
    interrelation_mod=_load("motor_interrelacion_extensible_v0_1","motor_interrelacion_extensible_v0_1.py")
    if interrelation_mod is None:
        interrelation={"status":"PLUGIN_SALTADO","unique_tokens":[],"hyperrelations":[],"movement":[],
                       "feeds_predictor":False,"feeds_H":False,"can_decide_H":False}
        features["interrelation"]=interrelation
        status.append({"component":"motor_interrelacion_extensible_v0_1.py","status":"PLUGIN_SALTADO","reason":"archivo_no_en_este_pack"})
    else:
        # CABLEADO_CALDERO_20261112 (2): las luces del contrato no traen
        # "branch" y run_external lo exige (KeyError: 'branch'). Normalizar:
        # branch = fuente del contrato o "capa2". Se copia cada luz para no
        # mutar el caso sellado; las de Cameo ya traen branch.
        _lights=[]
        for _l0 in (case.get("external_lights", []) or []):
            if isinstance(_l0, dict) and _l0.get("token"):
                _l=dict(_l0)
                if not _l.get("branch"):
                    _l["branch"]=str(_l.get("fuente") or "capa2")
                _lights.append(_l)
        _lights.extend([{"token":t,"branch":"cameo","stereotype":"cameo_institucional","axes":()} for t in cameo_tokens])

        # Persistent Caldero neighbors are part of the reusable light bus.
        # Registration persists across runs; activation requires a current-run
        # observation of the same token, so historical memory is not blindly
        # injected as current evidence.
        _stink_lights=list((features.get("stinkbox_transport") or {}).get("persistent_neighbor_lights") or [])
        _registered={str(x.get("token")).casefold() for x in _lights if isinstance(x,dict) and x.get("token")}
        for _light in _stink_lights:
            _tok=str(_light.get("token","")).casefold()
            if _tok and _tok not in _registered:
                _lights.append({"token":_tok,"branch":"caldero_memory","stereotype":"caldero_neighbor","axes":()})
                _registered.add(_tok)

        _memory_tokens={str(x.get("token")).casefold() for x in _stink_lights if isinstance(x,dict) and x.get("token")}
        _current_memory_hits=set()
        _cal_now=features.get("caldero_busqueda_arquetipos") or {}
        for _row in ((_cal_now.get("caldero_input") or {}).get("tokens_neighbors") or []):
            _tok=str(_row.get("token","")).strip().casefold() if isinstance(_row,dict) else str(_row).strip().casefold()
            if _tok in _memory_tokens: _current_memory_hits.add(_tok)
        _analog_now={str(x).strip().casefold() for x in ((features.get("pre_h_lateral_tokens") or {}).get("unique_tokens") or []) if str(x).strip()}
        _current_memory_hits.update(_analog_now & _memory_tokens)
        _cuts_for_inter=[dict(c) for c in (case.get("cuts", []) or [])]
        if _current_memory_hits and _cuts_for_inter:
            _last=dict(_cuts_for_inter[-1])
            _acts=list(_last.get("external_activations", []) or [])
            _existing_act={str(a.get("token")).casefold() if isinstance(a,dict) else str(a).casefold() for a in _acts}
            for _tok in sorted(_current_memory_hits):
                if _tok not in _existing_act:
                    _acts.append({"token":_tok,"strength":1.0,"source":"persistent_caldero_memory"})
                    try:
                        _sb=features.get("stinkbox_transport") or {}
                        _sb.setdefault("persistent_neighbor_activation_events", []).append({"cut_id":str(_last.get("id") or _last.get("corte") or "Z_TRABAJO"),"token":_tok,"source":"persistent_caldero_memory"})
                    except Exception:
                        pass
            _last["external_activations"]=_acts
            _cuts_for_inter[-1]=_last

        def _do_interrelation():
            out=interrelation_mod.run_external(_lights, _cuts_for_inter) if not _off("interrelation") else {"status":"APAGADO_ABLACION","unique_tokens":[],"hyperrelations":[],"movement":[]}
            out["persistent_caldero_lights_registered"] = len(_stink_lights)
            out["persistent_caldero_lights_activated"] = len(_current_memory_hits)
            out["cameo_tokens_injected"] = cameo_tokens
            out["feeds_predictor"]=True
            out["feeds_H"]=True
            out["can_decide_H"]=False
            out["contributes_to_H"]=True
            out["contributes_to_apuesta"]=True
            out["integration_point"]="post_core_pre_predictor_external"
            features["interrelation"] = out
            return out
        interrelation=_ceb_stage("motor_interrelacion_extensible_v0_1", _do_interrelation)
        status.append({"component":"motor_interrelacion_extensible_v0_1.py","status":"EXECUTED",
                       "feeds_predictor":True,"feeds_H":True,"can_decide_H":False,"contributes_to_H":True,"contributes_to_apuesta":True,"role":"external_relational_layer"})

    # PATCH 011: memoria Caldero sin eventos propios (mismo case_id / mismo input sha). Los propios quedan como traza.
    _ctx014={}
    if _s014 is not None:
        try:
            _o014=_ceb_stage("sujetos_014.py", lambda: _s014.contexto(case)); _RUN_CTX["_o014_obj"]=_o014
            _ctx014=dict(_o014)
            status.append({"component":"sujetos_014.py","status":"EXECUTED","feeds_predictor":True,"declaracion_U6":"FILTRO_AGUAS_ARRIBA","motivo_declaracion_U6":_DECL_U6["sujetos_014.py"][1],"feeds_H":False,"can_decide_H":False,
                           "role":"identidad de sujeto en soporte de vecinos (un sujeto cuenta una vez; nombres propios GLOBALES solo traza, política 015)",
                           "sujeto":_ctx014.get("sujeto"),"fuente":_ctx014.get("fuente")})
        except Exception as _e014:
            _ctx014={"status":"ERROR","error":f"{type(_e014).__name__}:{_e014}"}
            status.append({"component":"sujetos_014.py","status":"ERROR","error":str(_e014)})
    _RUN_CTX["sujetos_014"]=_ctx014
    if _ae011 is not None:
        try:
            _RUN_CTX["vecinos_011"]=dict(_ceb_stage("autoevidencia_stores_011.py", shared=[case,motor,features]+([_RUN_CTX["_o014_obj"]] if _RUN_CTX.get("_o014_obj") is not None else []), fn=lambda: _ae011.memoria_vecinos_sin_propios(case.get("caldero_neighbor_store_root") or (BASE / "vecinos_caldero"),
                                                                      str(case["case_id"]), _RUN_CTX.get("input_sha_011"),
                                                                      min_casos_ajenos=getattr(_ae011,"MIN_CASOS_AJENOS_012",1),  # PATCH 012
                                                                      **({"sujeto_actual":_ctx014.get("sujeto"),"sujeto_evento":_s014.sujeto_de_case_id,
                                                                          "nombres_no_votan":_ctx014.get("nombres_no_votan") or ()} if (_s014 is not None and _ctx014.get("sujeto")) else {}))))  # PATCH 014
        except Exception as _e011:
            _RUN_CTX["vecinos_011"]={"status":"ERROR","error":f"{type(_e011).__name__}:{_e011}"}
    if _off("caldero_memoria"):
        features["caldero_neighbor_memory"]={"status":"APAGADO_ABLACION","unique_tokens":[],"observations":0,"cases":0}
    # EMOTIONAL ARC LATERAL (moved before pre-H so its ACTIVE arcs can seed the blind query).
    emotional_mod=_load("emotional_arcs", "plugin_arcos_emocionales_laterales.py")
    emotional_catalog=BASE / "arcos_emocionales_laterales.json"
    if emotional_mod is None or not emotional_catalog.exists() or _off("arcos_emocionales"):
        status.append({"component":"plugin_arcos_emocionales_laterales.py","status":"APAGADO_ABLACION" if _off("arcos_emocionales") else "PLUGIN_SALTADO","reason":"ablacion" if _off("arcos_emocionales") else "archivo_no_disponible","effect":"sin_ejecucion"})
    else:
        catalog=emotional_mod.load_catalog(emotional_catalog)
        emotional=_ceb_stage("plugin_arcos_emocionales_laterales", lambda: emotional_mod.evaluate(case.get("cuts", []), case.get("external_lights", []), catalog))
        def _store_emotional():
            features["arcos_emocionales_laterales"] = emotional
            return emotional
        _ceb_stage("plugin_arcos_emocionales_laterales.output", _store_emotional, shared=[emotional])
        status.append({"component":"plugin_arcos_emocionales_laterales.py","status":"EXECUTED",
                       "feeds_predictor":True,"feeds_H":False,"can_decide_H":False,"contributes_to_H":True,"contributes_to_apuesta":True,"role":"lateral_emotional_pattern_data",
                       "mutates_canon":False,"crosses_FREEZE":False,"integration_point":"post_freeze_pre_predictor"})
    # DYNAMIS case-level context (observed tokens only; seeds the pre-H query, never ranks by itself).
    def _store_dynamis():
        out=_dynamis_case_summary(case.get("cuts")); features["dynamis_dramatica_sistemica"]=out; return out
    _ceb_stage("dynamis_dramatica_sistemica", _store_dynamis)
    status.append({"component":"dynamis_dramatica_sistemica","status":"EXECUTED","feeds_predictor":True,"feeds_H":True,"can_decide_H":False,
                   "role":"dims dynamis_* del vector de candidato","nota":"PATCH 010b: fila nueva (antes llegaba a H sin fila)"})
    # V0.18 PRE-H ANALOGICAL ARC — CONSOLIDADO: runs BEFORE StinkBox so analog tokens reach the vault
    # and the per-candidate analog_alignment (in V0.18 it ran after StinkBox: tokens reached no ranking path).
    def _do_pre_h():
        if _off("pre_h_analogico"):
            out={"status":"APAGADO_ABLACION","activated":False,"can_decide_H":False,"writes_canonical":False,"writes_H":False}
        else:
            out=_run_pre_h_analogical_search(case,motor,features)
        features["pre_h_analogical_search"]=out
        return out
    pre_h_search=_ceb_stage("pre_h_analogical_search(V0.18)", _do_pre_h)
    status.append({"component":"pre_h_analogical_search(V0.18)","status":pre_h_search.get("status"),"reason":pre_h_search.get("adapter") or pre_h_search.get("reason"),
                   "phase":"PRE_H_ORIENTATION","feeds_predictor":bool(pre_h_search.get("tokens_neighbors")),"feeds_H":False,
                   "can_decide_H":False,"query_blind":pre_h_search.get("query_blind",True),
                   "identity_exposed":pre_h_search.get("identity_exposed",False),
                   "future_outcome_exposed":pre_h_search.get("future_outcome_exposed",False)})
    if pre_h_search.get("tokens_neighbors"):
        def _store_pre_h_tokens():
            features["pre_h_lateral_tokens"]={
                "unique_tokens":sorted({str(x.get("token")) for x in pre_h_search["tokens_neighbors"] if isinstance(x,dict) and x.get("token")}),
                "observations":pre_h_search.get("analog_token_count",0),"source":"blind_analogical_search_pre_H"}
            return features["pre_h_lateral_tokens"]
        _ceb_stage("pre_h_lateral_tokens", _store_pre_h_tokens)
    # STINKBOX: persistent post-FREEZE evidence/transport layer. It records
    # R732 trajectory observations and lateral lights, then exposes bounded
    # candidate-specific support to the predictor. It never mutates canon/H.
    stinkbox_mod=_load("stinkbox_transport_v0_2", "stinkbox_transport_v0_2.py")
    _last_cut=(case.get("cuts") or [{}])[-1]
    gate_cut_id=str(case.get("stinkbox_cut_id") or f"{case['case_id']}::{_last_cut.get('corte', _last_cut.get('id', 'Z'))}")
    if stinkbox_mod is None:
        stinkbox={"status":"PLUGIN_SALTADO","candidate_support":{}}
        features["stinkbox_transport"]=stinkbox
        gate_ctx={"box":None,"cut_id":gate_cut_id,"case_box":None}
        status.append({"component":"stinkbox_transport_v0_2.py","status":"PLUGIN_SALTADO","reason":"archivo_no_en_este_pack"})
    else:
        stink_root=Path(case.get("stinkbox_root") or case.get("biblioteca_usuario_root") or case.get("model_user_library") or _STINKBOX_STORAGE_ROOT())
        pending_case_id=str(case.get("stinkbox_pending_case_id") or case["case_id"])
        stinkbox=_ceb_stage("stinkbox_transport_v0_2", lambda: stinkbox_mod.capture_and_transport(
            case_id=str(case["case_id"]),
            root=stink_root,
            motor_output=motor,
            lateral_features=features,
            patterns_path=_PATTERNS_PATH(),
            external_lights=case.get("external_lights", []),
            pending_case_id=pending_case_id,
            caldero_neighbor_store_root=case.get("caldero_neighbor_store_root") or (_STINKBOX_STORAGE_ROOT() / "vecinos_caldero"),
            input_sha=_RUN_CTX.get("input_sha_011"),
        ))
        if _off("stinkbox_soporte"):
            stinkbox={**stinkbox,"candidate_support":{},"ablation":"candidate_support_apagado"}
        def _store_stink():
            features["stinkbox_transport"] = stinkbox
            return stinkbox
        _ceb_stage("stinkbox_transport.output", _store_stink, shared=[stinkbox])
        gate_ctx={"box":stinkbox_mod.StinkBox(pending_case_id, stink_root),"cut_id":gate_cut_id,
                  "case_box":stinkbox_mod.StinkBox(str(case["case_id"]), stink_root) if pending_case_id!=str(case["case_id"]) else None,
                  "input_sha_011":_RUN_CTX.get("input_sha_011"),"ae011":_ae011,
                  "repeticion_011":bool((stinkbox.get("idempotencia_011") or {}).get("repeticion")) if isinstance(stinkbox,dict) else False}
        status.append({"component":"stinkbox_transport_v0_2.py","status":"EXECUTED",
                       "feeds_predictor":True,"feeds_H":True,"can_decide_H":False,"contributes_to_H":True,"contributes_to_apuesta":True,"role":"persistent_lateral_transport",
                       "mutates_canon":False,"crosses_FREEZE":False,"integration_point":"post_freeze_pre_predictor"})
    # PATCH 013+015: tokens de relleno (stopwords Snowball es/en, src_*, numéricos, <3 car., palabras de año) fuera del voto de vecinos
    # (memoria persistente -> también luces del bus, y vecinos de la corrida actual). Quedan como traza filtrados_013.
    _f013=_load("filtro_relleno_013","filtro_relleno_013.py")
    if _f013 is not None:
        def _filtrar013():
            _v=_RUN_CTX.get("vecinos_011")
            _out={"status":"EXECUTED","version":getattr(_f013,"VERSION",None),"listas":list(getattr(_f013,"FUENTE_LISTAS",())),"can_decide_H":False}
            _anos_all=[]
            if isinstance(_v,dict) and _v.get("status")!="ERROR":
                _ok,_tr=_f013.filtrar(_v.get("unique_tokens") or [])
                _RUN_CTX["vecinos_011"]={**_v,"unique_tokens":sorted(_ok),"filtrados_013":_tr}
                _out["memoria"]={"antes":len(_v.get("unique_tokens") or []),"votan":len(_ok),"filtrados_013":_tr}
                _anos_all.extend(((_tr or {}).get("anos_015") or {}).get("tokens") or [])
            _cal=features.get("caldero_busqueda_arquetipos") or {}
            _act=[x.get("token") if isinstance(x,dict) else x for x in ((_cal.get("caldero_input") or {}).get("tokens_neighbors") or [])]
            _oka,_tra=_f013.filtrar(_act)
            _RUN_CTX["filtro_013_actuales_fuera"]=sorted({str(t).strip().casefold() for t in _act if str(t).strip()}-_oka)
            _out["vecinos_actuales"]={"votan":len(_oka),"filtrados_013":_tra}
            _anos_all.extend(((_tra or {}).get("anos_015") or {}).get("tokens") or [])
            _anos_u=sorted(set(_anos_all))
            _out["anos_015"]={"n":len(_anos_u),"tokens":_anos_u,"efecto":"palabra de año: solo traza, no vota (015)"}
            _RUN_CTX["filtro_013"]=_out
            return _out
        try:
            _RUN_CTX["_o013_obj"]=_ceb_stage("filtro_relleno_013.py", _filtrar013)
            status.append({"component":"filtro_relleno_013.py","status":"EXECUTED","feeds_predictor":True,"declaracion_U6":"FILTRO_AGUAS_ARRIBA","motivo_declaracion_U6":_DECL_U6["filtro_relleno_013.py"][1],"feeds_H":False,"can_decide_H":False,
                           "role":"filtro de relleno + palabras de año 015 en vocabulario de vecinos (no toca favor/contra ni 244)"})
        except Exception as _e013:
            _RUN_CTX["filtro_013"]={"status":"ERROR","error":f"{type(_e013).__name__}:{_e013}"}
            status.append({"component":"filtro_relleno_013.py","status":"ERROR","error":str(_e013)})
    # REWIRE: StinkBox is now upstream of the final light-bus evaluation.
    # The first interrelation pass remains a baseline; this pass incorporates
    # persistent Caldero lights loaded from StinkBox and current-run reactivations.
    if interrelation_mod is not None and not _off("interrelation"):
        # CABLEADO_CALDERO_20261112 (2b): mismo arreglo que en la primera pasada:
        # las luces del contrato no traen "branch" y run_external lo exige.
        _lights2=[]
        for _l0 in (case.get("external_lights", []) or []):
            if isinstance(_l0, dict) and _l0.get("token"):
                _l=dict(_l0)
                if not _l.get("branch"):
                    _l["branch"]=str(_l.get("fuente") or "capa2")
                _lights2.append(_l)
        _lights2.extend([{"token":t,"branch":"cameo","stereotype":"cameo_institucional","axes":()} for t in cameo_tokens])
        _persistent_lights=list((features.get("stinkbox_transport") or {}).get("persistent_neighbor_lights") or [])
        # PATCH 011: solo luces de vecinos aportados por OTROS casos/inputs del store actual (sin propios ni restos ya fuera del store).
        _v011=_RUN_CTX.get("vecinos_011")
        if isinstance(_v011,dict) and _v011.get("status") in ("PRESENT","PRESENT_SIN_AJENOS","ABSENT"):
            _perm011=set(_v011.get("unique_tokens") or []); _antes011=len(_persistent_lights)
            _persistent_lights=[l for l in _persistent_lights if isinstance(l,dict) and str(l.get("token","")).strip().casefold() in _perm011]
            _RUN_CTX["luces_011"]={"registradas_en_vault":_antes011,"usadas":len(_persistent_lights),"excluidas":_antes011-len(_persistent_lights),
                                   "motivo_exclusion":"token sin aporte de otro case_id/input en el store actual (propio o ya fuera del store)",
                                   # PATCH 012: luz de un solo caso ajeno = 'ilumina' (traza), no entra al bus que puntúa.
                                   "min_casos_ajenos_012":_v011.get("min_casos_ajenos"),
                                   "ilumina_012":len(set((_v011.get("ilumina_012") or {}).get("tokens") or []))}
        _reg2={str(x.get("token")).casefold() for x in _lights2 if isinstance(x,dict) and x.get("token")}
        for _light in _persistent_lights:
            _tok=str(_light.get("token","")).strip().casefold() if isinstance(_light,dict) else ""
            if _tok and _tok not in _reg2:
                _lights2.append({"token":_tok,"branch":"caldero_memory","stereotype":"caldero_neighbor","axes":()})
                _reg2.add(_tok)
        _cuts2=[dict(c) for c in (case.get("cuts", []) or [])]
        _memory_tokens2={str(x.get("token")).casefold() for x in _persistent_lights if isinstance(x,dict) and x.get("token")}
        _current_hits2=set()
        _cal2=features.get("caldero_busqueda_arquetipos") or {}
        for _row in ((_cal2.get("caldero_input") or {}).get("tokens_neighbors") or []):
            _tok=str(_row.get("token","")).strip().casefold() if isinstance(_row,dict) else str(_row).strip().casefold()
            if _tok in _memory_tokens2: _current_hits2.add(_tok)
        _current_hits2.update({str(x).strip().casefold() for x in ((features.get("pre_h_lateral_tokens") or {}).get("unique_tokens") or []) if str(x).strip()} & _memory_tokens2)
        if _current_hits2 and _cuts2:
            _last2=dict(_cuts2[-1]); _acts2=list(_last2.get("external_activations",[]) or [])
            _seen2={str(a.get("token")).casefold() if isinstance(a,dict) else str(a).casefold() for a in _acts2}
            for _tok in sorted(_current_hits2):
                if _tok not in _seen2:
                    _acts2.append({"token":_tok,"strength":1.0,"source":"persistent_caldero_memory"})
            _last2["external_activations"]=_acts2; _cuts2[-1]=_last2
        _inter2=_ceb_stage("stinkbox_to_light_bus_v1", lambda: interrelation_mod.run_external(_lights2,_cuts2))
        _inter2["cameo_tokens_injected"]=cameo_tokens
        _inter2["persistent_caldero_lights_registered"]=len(_persistent_lights)
        _inter2["persistent_caldero_lights_activated"]=len(_current_hits2)
        _inter2["light_bus_source"]="StinkBox persistent Caldero memory"
        _inter2["feeds_predictor"]=True; _inter2["feeds_H"]=True; _inter2["can_decide_H"]=False
        _inter2["contributes_to_H"]=True; _inter2["contributes_to_apuesta"]=True
        _inter2["integration_point"]="post_freeze_stinkbox_to_light_bus_pre_predictor"
        def _store_interrelation():
            features["interrelation"]=_inter2
            return _inter2
        _ceb_stage("stinkbox_to_light_bus.output", _store_interrelation, shared=[_inter2])
        interrelation=_inter2
        status.append({"component":"stinkbox_to_light_bus_v1","status":"EXECUTED","feeds_predictor":True,"feeds_H":False,"can_decide_H":False,
                       "persistent_lights_registered":len(_persistent_lights),"persistent_lights_activated":len(_current_hits2),
                       "role":"persistent_caldero_memory_to_light_bus"})

    if ceb: ceb.ledger.checkpoint("protocolo_transversal_absorbido", "protocolo_transversal_absorbido", {"observed":True})
    status.append({"component":"protocolo_transversal_absorbido","status":"EXECUTED","feeds_predictor":False})
    # UNICO: HUB de laterales (votos + sensores) justo antes del predictor. Votos = un módulo más del puente de nombres.
    _hub=_load("laterales_unico_v1","laterales_unico_v1.py"); _hub_reg=[]; _hub_det={}
    if _hub is None:
        status.append({"component":"laterales_unico_v1.py","status":"FALTA_ARCHIVO"})
    else:
        try:
            _votos,_hub_det,_hub_reg=_ceb_stage("laterales_unico_v1.pre_predictor", lambda: _hub.pre_predictor(case,motor,features,BASE,_PATTERNS_PATH(),_patterns()))
            def _store_hub_pre():
                for _k,_v in _votos.items(): features[_k]=_v
                features["laterales_unico_detalle"]=_hub_det
                return _hub_det
            _ceb_stage("laterales_unico_v1.pre_predictor.output", _store_hub_pre, shared=[_hub_det, _votos])
            status.append({"component":"laterales_unico_v1.py(pre)","status":"EXECUTED","feeds_predictor":True,"feeds_H":False,"can_decide_H":False,
                           "votos":sorted(_votos),"n_piezas":len(_hub_reg),"n_piezas_pre":len(_hub_reg),
                           "nota_n_piezas":"PATCH 010b: n_piezas = piezas del PRE; el POST añade más a la misma lista (ver fila (post) n_piezas_total)"})
            # PATCH 010b: filas propias para los votos del hub y las piezas 004-009 que antes solo vivían en registro_piezas
            for _r in _hub_reg:
                if _r.get("pieza") in ("negativo_ricci_vs_billar","familias_tokens_puente","guardian_entrada_autoevidencia","marco_7783_geometria","caldero_ii_cuadrantes","sombrero_blanco_entrada"):
                    status.append({"component":f"hub:{_r.get('pieza')}","status":{"ACTIVA":"HUB_ACTIVA","ACTIVA_MUDA":"HUB_ACTIVA_MUDA"}.get(_r.get("estado"),_r.get("estado")),"reason":_r.get("aporte"),
                                   "feeds_predictor":_r.get("pieza") in ("negativo_ricci_vs_billar","familias_tokens_puente") and _r.get("pieza") in _votos,
                                   "feeds_H":False,"can_decide_H":False,"archivo":_r.get("archivo"),"rol":_r.get("rol")})
        except Exception as e:
            import traceback as _tbh
            status.append({"component":"laterales_unico_v1.py(pre)","status":"ERROR","error":f"{type(e).__name__}:{e}","trace":_tbh.format_exc()[-1500:]})
    boards=[]; histories=[]
    for c in motor.get("cuts") or []:
        boards.append({"P":dict(c.get("P_FULL_244") or {}),"A":dict(c.get("A_FULL_244") or {}),"C":dict(c.get("C_FULL_244") or {})})
        # Universo PAC compartido con las ablaciones adversariales.
        histories.append(_candidate_history_for_cut(c))
    # Legacy CAMEO->244 adapter is audit-only; active path is CAMEO -> 703 -> lateral bus.
    cameo_adapter=_load("cameo_to_244_adapter_v1", "cameo_to_244_adapter_v1.py")
    cameo_244={"status":"AUDIT_ONLY","scores":{},"feeds_H":False,"can_decide_H":False,"mutates_canonical":False}
    _cameo244_raw="NO_CORRIDO"
    if cameo_adapter is not None:
        try:
            cameo_candidates=sorted({str(x.get("familia")) for h in histories for x in h if isinstance(x,dict) and x.get("familia")})
            candidate_texts=case.get("cameo_candidate_texts") or {}
            cameo_244=_ceb_stage("cameo_to_244_adapter_v1", lambda: cameo_adapter.adapt(cameo, {c:list(candidate_texts.get(c, [])) for c in cameo_candidates}, _patterns()))
            _cameo244_raw=cameo_244.get("status")
            cameo_244["status"]="AUDIT_ONLY"; cameo_244["feeds_H"]=False
        except Exception as exc:
            cameo_244={"status":"AUDIT_ERROR","scores":{},"feeds_H":False,"audit":{"error":f"{type(exc).__name__}:{exc}"}}
    def _store_cameo_audit():
        features["cameo_legacy_adapter_audit"] = cameo_244
        return cameo_244
    _ceb_stage("cameo_to_244_adapter_v1.output", _store_cameo_audit, shared=[cameo_244])
    status.append({"component":"cameo_to_244_adapter_v1.py","status":"AUDIT_ONLY" if _cameo244_raw=="EXECUTED" else "NOT_APPLICABLE","estado_crudo_adaptador":_cameo244_raw,
                   "reason":("auditoría CAMEO->244 ejecutada (no alimenta H por diseño)" if _cameo244_raw=="EXECUTED" else
                             f"adaptador devuelve {_cameo244_raw}: {((cameo_244.get('audit') or {}).get('reason')) or 'mapping aprobado cameo_to_244.json ausente'}; no alimenta H por diseño"), "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"mutates_canonical":False,"audit":cameo_244.get("audit")})
    def _matriz():
        base=Path(__file__).resolve().parent
        equiv=base/"MATRIZ_EQUIVALENCIAS_ESCALA.json"
        puente=base/"PUENTE_244_FAMILIAS.json"
        fams=list((base/"familias_tokens").glob("*.json")) if (base/"familias_tokens").is_dir() else []
        if not equiv.is_file() and not puente.is_file() and not fams:
            rec={"status":"AUSENTE","razon":"no_hay_matriz_en_paquete"}
        else:
            try:
                data=json.loads(equiv.read_text(encoding="utf-8")) if equiv.is_file() else {}
                rec={"status":"PRESENTE","fuente":"MATRIZ_EQUIVALENCIAS_ESCALA.json","n_familias":len(data.get("familias") or {}),"n_tokens":data.get("n_tokens"),"puente":puente.is_file(),"familias_tokens":len(fams),"can_decide_H":False}
            except Exception as exc:
                rec={"status":"ERROR","error":type(exc).__name__}
        features["matriz_clases"]=rec
        return rec
    def _marco():
        mod=_load("marco_7783","marco_7783.py")
        fn=features.get("funciones_souriau") or {}
        if mod is None:
            rec={"status":"NO_CORRIDO","razon":"archivo_7783_ausente"}
        else:
            rec=mod.visitar(fn.get("por_corte") or [])
        features["marco_7783"]=rec
        return rec
    def _figura():
        sou=_load("lente_souriau","sidecar_lente_souriau.py")
        if sou is None:
            rec={"status":"ERROR","razon":"sidecar_ausente"}
        else:
            ids=[c.get("id") or str(i) for i,c in enumerate(case.get("cuts") or [])]
            focos=[sou.asignar_focos_por_corte(c, ids, i) for i,c in enumerate(case.get("cuts") or [])]
            ejes={}
            for c in case.get("cuts") or []:
                for ax in ("P","A","C"):
                    ejes[ax]=ejes.get(ax,0)+len(c.get(ax) or [])
            rec={"status":"EXECUTED","focos":len(focos),"conteo_ejes":ejes,"cambio_de_rol":False,"razon":"asigna_foco_no_intercambia_sujeto"}
        features["figura_pac"]=rec
        return rec
    _m=_ceb_stage("matriz_clases", _matriz)
    def _funciones():
        mod=_load("marco_funciones","marco_funciones_souriau.py")
        if mod is None:
            rec={"status":"ERROR","razon":"archivo_ausente"}
        else:
            rec=mod.distribuir(case.get("cuts") or [])
        features["funciones_souriau"]=rec
        return rec
    _fn=_ceb_stage("funciones_souriau", _funciones)
    status.append({"component":"funciones_souriau","status":(_fn or {}).get("status"),"feeds_H":False,"can_decide_H":False,"role":"filtro_antes_de_polti",
                   "modo_016":(_fn or {}).get("modo"),"personajes_016":((_fn or {}).get("personajes") or {}).get("modo_caso")})
    _marker_mod = _load("marcador_limite_geometrico_v01", "marcador_limite_geometrico_v0_1.py")
    if _marker_mod is not None and features.get("marcador_limite_geometrico", {}).get("status") == "EXECUTED_DIAGNOSTIC":
        _marker_enriched = _marker_mod.integrar_funciones_souriau(
            features["marcador_limite_geometrico"], features.get("funciones_souriau") or {})
        features["marcador_limite_geometrico"] = _marker_enriched
        motor.setdefault("R732", {})["marcador_limite_geometrico"] = _marker_enriched
        for _cut_row, _marker_row in zip(motor.get("cuts") or [], _marker_enriched.get("per_cut") or []):
            _cut_row["marcador_limite_geometrico"] = _marker_row
        status.append({"component":"marcador_limite_geometrico_v0_1.py", "status":"EXECUTED_DIAGNOSTIC",
                       "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,
                       "rank_effect":"NONE","integrates":"R732 + Souriau functional recurrence",
                       "per_cut_markers":len(_marker_enriched.get("per_cut") or [])})
    else:
        status.append({"component":"marcador_limite_geometrico_v0_1.py", "status":"MISSING_OR_NO_GEOMETRY",
                       "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"rank_effect":"NONE"})
    _k=_ceb_stage("marco_7783", _marco)
    _f=_ceb_stage("figura_pac", _figura)
    for _nombre,_rec in (("matriz_clases",_m),("marco_7783",_k),("figura_pac",_f)):
        status.append({"component":_nombre,"status":_rec.get("status"),"feeds_H":False,"can_decide_H":False,"razon":_rec.get("razon"),
                       "reason":_rec.get("razon") or {"matriz_clases":"registro de PRESENCIA de MATRIZ/PUENTE/familias_tokens (inventario; no depende del caso); sin nombres de candidato -> no entra al ranking"}.get(_nombre)})
    pred=_ceb_stage("predictor", lambda: _predict(boards,histories,motor,features,gate_ctx),
                    shared=[case,motor,features]+[_RUN_CTX[k] for k in ("_o013_obj",) if _RUN_CTX.get(k) is not None])

    # METACOGNICION: una sola capa para el arco analógico posterior a H y la
    # retrospectiva de calibración. Post-H sólo contrasta; nunca reescribe H/apuesta.
    meta_mod=_load("metacognition_v0_1", "metacognition_v0_1.py")
    if meta_mod is None:
        metacognition={"status":"FALTA_ARCHIVO","model_role":"METACOGNITION","post_H":{"status":"NOT_RUN"},
                       "retrospective":{"status":"WAITING_FOR_FUTURE"}}
        status.append({"component":"metacognition_v0_1.py","status":"FALTA_ARCHIVO","feeds_predictor":False,"feeds_H":False})
    else:
        # Se construye la apuesta antes de cerrar la capa retrospectiva.
        _apuesta_seed=None
        if pred.get("status")=="OK":
            _apuesta_seed={"type":"projection_longitudinal","family":pred["H1"]["family"],
                           "discard":pred["H2"]["family"],"validation":"next_observed_cut_or_external_future",
                           "created_after_freeze":True}
        metacognition=_ceb_stage("metacognition_v0_1.pre_h", lambda: meta_mod.run(features.get("pre_h_analogical_search") or {}, pred, _patterns(), _apuesta_seed, case, z_work))
        features["metacognition"]=metacognition
        features["post_h_analogical_contrast"]=metacognition.get("post_H")
        status.append({"component":"metacognition_v0_1.py","status":"EXECUTED","phase":"POST_H_AND_RETROSPECTIVE",
                       "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"can_rewrite_H":False,
                       "can_rewrite_apuesta":False,"post_H_status":(metacognition.get("post_H") or {}).get("status"),
                       "retrospective_status":(metacognition.get("retrospective") or {}).get("status")})
    if ceb: ceb.ledger.checkpoint("compuerta_cierre_latencia_v0_16_4", "compuerta_cierre_latencia_v0_16_4", {"decision":(pred.get("compuerta_cierre") or {}).get("decision")})
    status.append({"component":"compuerta_cierre_latencia_v0_16_4","status":"EXECUTED",
                   "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"can_only_withhold_closure":True,
                   "role":"closure_gate_control","decision":(pred.get("compuerta_cierre") or {}).get("decision")})
    # APUESTA POST-Z: proyección longitudinal.
    # No decide H ni reordena el rank; proyecta cada rama desde Z usando el
    # desplazamiento observado entre los dos últimos cortes disponibles.
    def _paso(nombre):
        vals=[]
        for b in boards:
            vals.append(float(np.mean([float(b[ax].get(nombre,0.0)) for ax in ("P","A","C")])))
        if len(vals)<2:
            return 0.0, vals
        return vals[-1]-vals[-2], vals
    _cortes=list(case.get("cuts") or [])
    _n=max(1,len(_cortes)-1)
    _horizontes=sorted(set(case.get("horizontes") or [1, _n]))
    _ramas=[]
    for c in (pred.get("candidates") or []):
        _d,_vals=_paso(c.get("family"))
        _proy=[]
        for h in _horizontes:
            _proy.append({"pasos": h, "analogo_a": "tramos_observados" if h!=1 else "siguiente_tramo", "delta": round(_d*h,6), "si_continua": "sigue" if _d>1e-9 else ("frena" if _d<-1e-9 else "plano")})
        _ramas.append({"family": c.get("family"), "rank_en_Z": c.get("rank_fusion"), "es_hecho": False, "serie_hasta_Z": [round(v,6) for v in _vals], "proyeccion": {"desde": "Z", "d_por_tramo": round(_d,6), "horizontes": _proy, "fijado": False}})
    _limit_marker = features.get("marcador_limite_geometrico") or {}
    apuesta={"type":"proyeccion_longitudinal",
             "marcador_geometrico_en_Z": _limit_marker.get("current_marker", {}),
             "regimen_geometrico_en_Z": (_limit_marker.get("current_marker") or {}).get("regime", "SIN_MARCADOR"),
             "regimen_geometrico_funcional_en_Z": _limit_marker.get("joint_geometric_function_regime", "SIN_MARCADOR"),
             "recurrencia_funcional_en_Z": (_limit_marker.get("current_marker") or {}).get("firma_funcional_recurrente", False),
             "marcador_no_equivale_a_final": True,
             "inercia_funciones": (features.get("funciones_souriau") or {}).get("inercia"),
 "formula":"x(Z+k)=x(Z)+k*(x(Z)-x(Z-1)); k=1 y k=n-1, o los que traiga el caso; n=cortes", "n_cortes": len(_cortes), "post_Z": True, "no_es_ganador_de_rank": True, "n_ramas": len(_ramas), "ramas": _ramas, "observado_hasta": "Z", "validation":"observacion_futura", "created_after_freeze": True}
    status.append({"component":"proyeccion_longitudinal", "status":"EXECUTED", "feeds_predictor":False, "feeds_H":False, "can_decide_H":False, "can_rewrite_H":False, "can_rewrite_apuesta":False, "role":"post_Z_longitudinal_projection", "n_ramas":len(_ramas), "n_cortes":len(_cortes)})
    if ceb: ceb.ledger.checkpoint("proyeccion_longitudinal", "proyeccion_longitudinal", {"executed":True, "n_ramas":len(_ramas), "n_cortes":len(_cortes), "formula":apuesta["formula"]})
    if meta_mod is not None:
        metacognition=_ceb_stage("metacognition_v0_1.post_h", lambda: meta_mod.run(features.get("pre_h_analogical_search") or {}, pred, _patterns(), apuesta, case, z_work))
        features["metacognition"]=metacognition
        features["post_h_analogical_contrast"]=metacognition.get("post_H")

    inventory=[]
    for fn in CORE_COMPONENTS+OPTIONAL_COMPONENTS+GUARDIAN_COMPONENTS:
        p=BASE/fn
        if not p.exists(): p=BASE/"plugins"/fn
        inventory.append({"component":fn,"present":p.exists(),"sha256":_sha(p),
                          "role":"core_or_executable" if fn in CORE_COMPONENTS else ("guardian_control_estructural" if fn in GUARDIAN_COMPONENTS else "optional_or_lateral"),
                          "location":str(p) if p.exists() else None})
    # Do not expose native ON/OFF as an execution state: it is a legacy catalog.
    # The sole execution authority is component_status below.

    # Strip ambiguous legacy ON/OFF labels before emitting the authoritative result.
    motor.pop("plugins_ON", None)
    motor.pop("plugins_OFF", None)
    motor["plugin_state_note"] = "Execution state is component_status; no ON/OFF default is used by V0.9."
    # SOMBRERO BLANCO TOKEN: reporta fuera_catalogo a StinkBox; no canoniza; can_decide_H=False.
    sb_mod=_load("plugin_sombrero_blanco_token", "plugin_sombrero_blanco_token.py")
    if sb_mod is None:
        motor["sombrero_blanco"]={"status":"PLUGIN_SALTADO","reason":"archivo_no_en_este_pack","can_decide_H":False}
        status.append({"component":"plugin_sombrero_blanco_token.py","status":"PLUGIN_SALTADO","reason":"archivo_no_en_este_pack","feeds_predictor":False,"feeds_H":False,"can_decide_H":False})
    else:
        try:
            _holes=motor.get("holes") or {}
            _sb_call=lambda: sb_mod.revisar(_holes, str(case.get("case_id")))
            sombrero=ceb.call("plugin_sombrero_blanco_token", _sb_call, shared=[_holes]) if ceb else _sb_call()

            roles=[]
            for c in case.get("cuts") or []:
                if c.get("hecho") or c.get("narracion"):
                    continue
                roles.append({"corte":c.get("id"),"fuente":"tokens_sin_texto","protagonista":[x[0] if isinstance(x,(list,tuple)) else x for x in (c.get("P") or [])],"antagonista":[x[0] if isinstance(x,(list,tuple)) else x for x in (c.get("A") or [])],"contexto":[x[0] if isinstance(x,(list,tuple)) else x for x in (c.get("C") or [])],"can_decide_H":False})
            motor["personajes_corte"]={"status":"EXECUTED","can_decide_H":False,"por_corte":roles,"nota":"sin hecho: roles desde P/A/C, no biografia inventada"}
            motor["sombrero_blanco"]=sombrero
            status.append({"component":"plugin_sombrero_blanco_token.py","status":"EXECUTED","feeds_predictor":False,"rol":"GUARDIAN_FILTRO (post-apuesta; pase de entrada en hub sombrero_blanco_entrada)","feeds_H":False,"can_decide_H":False,"n_esta_corrida":sombrero.get("n_esta_corrida"),"n_stinkbox":sombrero.get("n_stinkbox"),"role":"fuera_catalogo_to_stinkbox"})
        except Exception as _sb_exc:
            motor["sombrero_blanco"]={"status":"ERROR","error":str(_sb_exc),"can_decide_H":False}
            status.append({"component":"plugin_sombrero_blanco_token.py","status":"ERROR","reason":str(_sb_exc),"feeds_predictor":False,"feeds_H":False,"can_decide_H":False})
    result={"version":VERSION,"hash_candado":CANON_HASH,"patterns_sha256":_sha(_PATTERNS_PATH()),"M":M,
            "n_canon":_n_patrones(),"catalogo_patrones":{"ruta":str(_PATTERNS_PATH()),"sha256":_sha(_PATTERNS_PATH()),"n_patrones":_n_patrones(),"es_default_v14":_sha(_PATTERNS_PATH())==PATTERNS_SHA_DEFAULT,"integridad_contrato":catalog_integrity,"validacion_puentes":(_hub_det.get("catalogo") if isinstance(_hub_det,dict) else None)},"protocolo_orden0":_orden0,"case_id":case["case_id"],"protocol":case.get("protocol"),
            "freeze":freeze,"execution":{"engine":str(Path(getattr(native,"__file__", "MOTOR_V15_3_NATIVO_V0_9.py")).name),"plugins_and_lenses":"FUNCTIONALLY_EXECUTED_WHERE_PRESENT; no legacy ON/OFF semantics","random_seed":seed,
            "component_status":status,"component_inventory":inventory,"monte_carlo":monte_carlo,"execution_identity":execution_identity},
            "execution_identity":execution_identity,"motor":motor,"features":features,"protocol_controls":transversal,
            "interrelation":interrelation,"predictor":pred,"H1":pred.get("H1"),"H2":pred.get("H2"),"apuesta":apuesta,
            "compuerta_cierre":pred.get("compuerta_cierre"),
            "formula_corpus":{"file":FORMULA_CORPUS,"formulas":list(FORMULAS),"present":(BASE/FORMULA_CORPUS).exists()},
            "plugin_state_authority":"execution.component_status ONLY",
            "lateral_H_contract":{"can_decide_H":False,"contributes_to_H":True,"contributes_to_apuesta":True,"aggregation":"shared_lateral_evidence_plus_candidate_specific_support","canonical_244_unchanged":True},
            "legacy_native_plugin_catalog":"retained internally by native motor but excluded from authoritative V0.9 execution state",
            "regla": "INPUT → Z90 → FREEZE → motor/layers/features → ARCO_ANALÓGICO_PRE_H (offline) → StinkBox → predictor → compuerta → H/apuesta → futuro oculto → validación",
            "analogical_search_contract":{"pre_H":"orientation","post_H":"contrast(" + str(((features.get("post_h_analogical_contrast") or {}).get("status") or "NOT_RUN")) + ")","query_identity_blind":"checked","future_outcome_blocked_pre_H":True,"canonical_244_unchanged":True,"live_web_calls":bool((features.get("external_archetype_search_receipt") or {}).get("status") == "EXECUTED")}}

    an=_load("analogos_fase","analogos_fase_v1.py")
    if an is not None:
        luces=[]
        for c in case.get("cuts") or []:
            for eje in ("P","A","C"):
                for row in c.get(eje) or []:
                    luces.append(row[0] if isinstance(row,(list,tuple)) else row)
        result["analogos_fase"]=_ceb_stage("analogos_fase", lambda: an.para_fase(luces), shared=[luces])
    ent=_load("entrega_luces","plugin_entrega_luces_v1.py")
    if ent is not None:
        result["entrega"]=_ceb_stage("plugin_entrega_luces", lambda: ent.entregar(result), shared=[result])
        status.append({"component":"plugin_entrega_luces","status":"EXECUTED","feeds_H":False,"can_decide_H":False,"despues_de":"apuesta"})
    # Autonomous consistency resolver: control-only; resolves only package-local mechanical mismatches.
    resolver=_load("consistency_autonomous", "plugin_resolucion_autonoma_consistencia.py")
    if resolver is not None:
        auto_audit=_ceb_stage("plugin_resolucion_autonoma_consistencia", lambda: resolver.resolve(BASE, result), shared=[result])
        result["consistency_autonomous"]=auto_audit
        result["consistency_autonomous_llm_packet"]=resolver.build_llm_packet(auto_audit, BASE)
        (BASE / "CONSISTENCY_AUTONOMA_LLM_PACKET.json").write_text(json.dumps(result["consistency_autonomous_llm_packet"], ensure_ascii=False, indent=2), encoding="utf-8")
        status.append({"component":"plugin_resolucion_autonoma_consistencia.py",
                       "status":"EXECUTED", "feeds_predictor":False, "feeds_H":False,
                       "role":"audit_continuity_control",
                       "resolver_status":auto_audit.get("status")})

    # Adversarial consistency verifier: control-only, after predictor, never feeds H.
    verifier=_load("consistency_adversarial", "plugin_verificador_consistencia_adversarial.py")
    if verifier is not None:
        audit=_ceb_stage("plugin_verificador_consistencia_adversarial", lambda: verifier.run(result, BASE), shared=[result])
        result["consistency_adversarial"]=audit
        status.append({"component":"plugin_verificador_consistencia_adversarial.py",
                       "status":"EXECUTED" if audit.get("status")=="PASS" else "EXECUTED_WITH_FINDINGS",
                       "feeds_predictor":False,"feeds_H":False,"role":"control_only",
                       "violations":audit.get("violations",[])})
    else:
        result["consistency_adversarial"]={"status":"PLUGIN_MISSING"}

    # GUARDIANES (control estructural siempre-on). Corren sobre toda entrada DESPUES del
    # predictor y de los controles existentes; reciben copias; nunca escriben H ni patterns.
    import copy as _copy
    snap_antes=_h_snapshot(pred); h_antes=json.dumps([result.get("H1"),result.get("H2")],sort_keys=True,default=str)
    pat_antes=_sha(_PATTERNS_PATH())
    gmod=_load("guardianes_control_v1","guardianes_control_v1.py")
    if gmod is None or not hasattr(gmod,"correr_guardianes"):
        guard_out={"status":"FALTA_ARCHIVO","file":"guardianes_control_v1.py","can_decide_H":False}
    else:
        try:
            guard_out=_ceb_stage("guardianes_control_v1", lambda: gmod.correr_guardianes(_copy.deepcopy(case),_copy.deepcopy(motor),_copy.deepcopy(pred),BASE), shared=[case,motor,pred])
            guard_out["status"]="EXECUTED"
        except Exception as e:
            guard_out={"status":"ERROR","error":f"{type(e).__name__}:{e}","can_decide_H":False}
    snap_despues=_h_snapshot(pred); h_despues=json.dumps([result.get("H1"),result.get("H2")],sort_keys=True,default=str)
    pat_despues=_sha(_PATTERNS_PATH())
    guard_out["verificacion_H_intacto"]={"predictor_sha256_antes":snap_antes,"predictor_sha256_despues":snap_despues,
        "predictor_igual":snap_antes==snap_despues,"H1_H2_igual":h_antes==h_despues,
        "patterns_sha256_antes":pat_antes,"patterns_sha256_despues":pat_despues,"patterns_igual":pat_antes==pat_despues,"catalogo_es_default_v14":pat_antes==PATTERNS_SHA_DEFAULT}
    result["guardianes"]=guard_out
    result["filtro_entrada_dirigida_017"]=_f017_traza
    status.append({"component":"guardianes_control_v1.py","status":guard_out.get("status"),"feeds_predictor":False,"feeds_H":False,
                   "can_decide_H":False,"role":"pruebas_de_control_estructural_siempre_on",
                   "banderas":guard_out.get("banderas"),"H_intacto":guard_out["verificacion_H_intacto"]["predictor_igual"]})

    # RUTA DE CIERRE LATENTE (regla de Mj): lo que no se entiende o no se sostiene NO es cierre.
    # Los NO_RESUELTO / DOBLE_NEGACION_LITOTE de los guardianes llegan a la latencia y a tortugas.
    # Solo cambia el ESTADO DEL CIERRE; H1/H2/top1 y el predictor quedan iguales (se verifica).
    ruta=(guard_out or {}).get("ruta_cierre_latente") or {"estado_cierre":"SIN_RUTA"}
    snap2=_h_snapshot(pred); h2_antes=json.dumps([result.get("H1"),result.get("H2")],sort_keys=True,default=str)
    top1_antes=(pred.get("candidates") or [{}])[0].get("family")
    estado_motor=(pred.get("information_state") or {}).get("state")
    cierre={"version":"CIERRE_GUARDIANES_V1","estado_motor":estado_motor,"decision_compuerta":(pred.get("compuerta_cierre") or {}).get("decision"),
            "estado_cierre":ruta.get("estado_cierre"),"motivos":ruta.get("motivos",[]),"n_motivos":ruta.get("n_motivos",0),
            "guardianes_que_objetan":ruta.get("guardianes_que_objetan",[]),"latencia":ruta.get("latencia"),
            "can_decide_H":False,"toca_H1_H2_top1":False}
    if ruta.get("estado_cierre")=="LATENTE":
        try:
            cierre["tortugas"]=_tortugas_guardianes(boards,histories,features,_copy.deepcopy(pred),motor,ruta)
        except Exception as e:
            cierre["tortugas"]={"status":"ERROR","error":f"{type(e).__name__}:{e}"}
        try:
            box=gate_ctx["box"]; box.data=box._load_or_create()
            if not gate_ctx.get("repeticion_011"): box.record_latency(state="LATENTE",reason="cierre_no_resuelto_por_guardianes",cut_id=gate_cut_id,front_id=None,
                               detail={"guardianes":cierre["guardianes_que_objetan"],"n_motivos":cierre["n_motivos"],
                                       "motivos":[{k:m.get(k) for k in ("guardian","tipo","fragmento","corte")} for m in cierre["motivos"]][:20],
                                       "tortugas":(cierre.get("tortugas") or {}).get("veredicto"),"top1":top1_antes},save=True)
            cierre["stinkbox_latency_event"]={"status":"OMITIDO_REPETICION_011" if gate_ctx.get("repeticion_011") else "ESCRITO","cut_id":gate_cut_id,"pending_case_id":box.case_id,
                                              "pending_fronts_sha256_sin_cambio":box.pending_digest()==((pred.get("compuerta_cierre") or {}).get("latencia_escrita") or {}).get("pending_fronts_sha256")}
        except Exception as e:
            cierre["stinkbox_latency_event"]={"status":"ERROR","error":f"{type(e).__name__}:{e}"}
    snap3=_h_snapshot(pred); h2_despues=json.dumps([result.get("H1"),result.get("H2")],sort_keys=True,default=str)
    cierre["verificacion_H_intacto"]={"predictor_igual":snap2==snap3==snap_antes,"H1_H2_igual":h2_antes==h2_despues,
                                      "top1_igual":top1_antes==(pred.get("candidates") or [{}])[0].get("family")}
    result["cierre_guardianes"]=cierre
    result["estado_cierre"]={"valor":cierre["estado_cierre"] if cierre["estado_cierre"]=="LATENTE" else estado_motor,
                             "estado_motor":estado_motor,"fuente":"guardianes" if cierre["estado_cierre"]=="LATENTE" else "motor",
                             "H1":(result.get("H1") or {}).get("family") if result.get("H1") else None,
                             "H2":(result.get("H2") or {}).get("family") if result.get("H2") else None,"top1":top1_antes,
                             "nota":"LATENTE = estado DURANTE la corrida (almacenado esperando datos); el cierre de fin de corrida va en cierre_final (016)"}
    if ceb: ceb.ledger.checkpoint("ruta_cierre_latente_guardianes", "ruta_cierre_latente_guardianes", {"estado_cierre":cierre["estado_cierre"]})
    status.append({"component":"ruta_cierre_latente_guardianes","status":"EXECUTED","feeds_predictor":False,"feeds_H":False,
                   "can_decide_H":False,"can_only_withhold_closure":True,"estado_cierre":cierre["estado_cierre"],
                   "tortugas":(cierre.get("tortugas") or {}).get("veredicto"),"H_intacto":cierre["verificacion_H_intacto"]})
    # MODO ESTRICTO (27-sep-2026; flag MODO_ESTRICTO=0 lo apaga). Lateral sobre COPIAS: can_decide_H=false.
    # Cierre estricto (top1 encabeza un corte + acero descarta al rival más fuerte + H1/H2 distinguibles + Aquiles estable),
    # mapeo en negativo Ricci–Forman vs Billar y bloque rival/'qué ignoré'. H1/H2/top1/predictor/patterns: se verifica que no cambian.
    if _os.environ.get("MODO_ESTRICTO","1")!="0":
        snapE=_h_snapshot(pred); hE=json.dumps([result.get("H1"),result.get("H2")],sort_keys=True,default=str); patE=_sha(_PATTERNS_PATH())
        top1E=(pred.get("candidates") or [{}])[0].get("family")
        emod=_load("modo_estricto_v1","modo_estricto_v1.py")
        if emod is None or not hasattr(emod,"evaluar"):
            est={"status":"FALTA_ARCHIVO","file":"modo_estricto_v1.py","estado_cierre_estricto":"LATENTE","motivos":["modo estricto no disponible"],"can_decide_H":False}
        else:
            try:
                vista={k:_copy.deepcopy(result.get(k)) for k in ("H1","H2","features","guardianes","cierre_guardianes","estado_cierre")}
                est=_ceb_stage("modo_estricto_v1", lambda: emod.evaluar(_copy.deepcopy(case),_copy.deepcopy(motor),_copy.deepcopy(pred),vista,BASE), shared=[case,motor,pred,vista]); est["status"]="EXECUTED"
            except Exception as e:
                import traceback as _tb
                est={"status":"ERROR","error":f"{type(e).__name__}:{e}","trace":_tb.format_exc()[-1500:],"estado_cierre_estricto":"LATENTE","motivos":["error en modo estricto"],"can_decide_H":False}
        est["verificacion_H_intacto"]={"predictor_igual":snapE==_h_snapshot(pred),"H1_H2_igual":hE==json.dumps([result.get("H1"),result.get("H2")],sort_keys=True,default=str),
                                       "top1_igual":top1E==(pred.get("candidates") or [{}])[0].get("family"),"patterns_igual":patE==_sha(_PATTERNS_PATH())}
        result["modo_estricto"]=est
        result["estado_cierre_estricto"]={"valor":est.get("estado_cierre_estricto"),"motivos":est.get("motivos"),"top1":top1E,
                                          "estado_cierre_vigente":(result.get("estado_cierre") or {}).get("valor"),
                                          "nota":"LATENTE = estado DURANTE la corrida (almacenado esperando datos); top1/H1/H2 se reportan igual y el cierre de fin de corrida va en cierre_final (016)"}
        status.append({"component":"modo_estricto_v1.py","status":est.get("status"),"feeds_predictor":False,"feeds_H":False,"can_decide_H":False,
                       "can_only_withhold_closure":True,"estado_cierre_estricto":est.get("estado_cierre_estricto"),"H_intacto":est["verificacion_H_intacto"]})
    # UNICO: HUB post-predictor (sensores que necesitan top1) + convergencia lateral + reporte por caso.
    snapU=_h_snapshot(pred); hU=json.dumps([result.get("H1"),result.get("H2")],sort_keys=True,default=str); patU=_sha(_PATTERNS_PATH())
    post={}
    if _hub is not None:
        try:
            vista={"_det_pre":_hub_det,"_patterns_path":str(_PATTERNS_PATH())}
            post=_ceb_stage("laterales_unico_v1.post_predictor", lambda: _hub.post_predictor(_copy.deepcopy(case),_copy.deepcopy(motor),_copy.deepcopy(pred),vista,BASE,_hub_reg))
        except Exception as e:
            import traceback as _tbp
            post={"status":"ERROR","error":f"{type(e).__name__}:{e}","trace":_tbp.format_exc()[-1500:]}
    conv=_convergencia_lateral(features,pred)
    result["laterales_unico"]={"version":getattr(_hub,"VERSION",None),"registro_piezas":_hub_reg,"pre":{k:v for k,v in (_hub_det or {}).items() if k!="sensores_pre"},
                              "sensores_pre":(_hub_det or {}).get("sensores_pre"),"post":post,"convergencia_lateral":conv,
                              "contrato":{"can_decide_H":False,"escribe_H":False,"escribe_catalogo":False,"votos_entran_como":"módulo del puente de nombres (lateral_contribution acotada)"}}
    result["laterales_unico"]["verificacion_H_intacto"]={"predictor_igual":snapU==_h_snapshot(pred),"H1_H2_igual":hU==json.dumps([result.get("H1"),result.get("H2")],sort_keys=True,default=str),
                                                        "catalogo_igual":patU==_sha(_PATTERNS_PATH())}
    status.append({"component":"laterales_unico_v1.py(post)","status":"EXECUTED" if not (isinstance(post,dict) and post.get("status")=="ERROR") else "ERROR",
                   "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"H_intacto":result["laterales_unico"]["verificacion_H_intacto"]})
    result["reporte_caso"]=_reporte_caso(result,pred,conv,post)
    # PATCH 010b: aplicar el estado VERIFICADO del hub (llegada real al rank) sobre component_status; se conserva lo declarado.
    try:
        _ev=((post or {}).get("estado_verificado") or {}).get("filas") or []
        _evm={str(f.get("componente")).split(" (")[0]:f for f in _ev}
        for _row in status:
            if not isinstance(_row,dict): continue
            _f=_evm.get(str(_row.get("component"))) or _evm.get(str(_row.get("component")).replace("hub:",""))
            if _f is None: continue
            _row["feeds_predictor_declarado"]=_row.get("feeds_predictor"); _row["feeds_predictor"]=bool(_f.get("feeds_predictor_verificado"))
            if "feeds_H" in _row or "contributes_to_H" in _row:
                _row["feeds_H_declarado"]=_row.get("feeds_H"); _row["feeds_H"]=bool(_f.get("llega_a_H"))
                if "contributes_to_H" in _row: _row["contributes_to_H"]=bool(_f.get("llega_a_H"))
            _row["llega_verificado"]=_f.get("llega")
            _d6=_decl_u6(_row.get("component"))
            if _row["feeds_predictor"]:
                _row["declaracion_U6"]="ACTIVA"
            elif _d6:
                _row["declaracion_U6"]=_d6[0]; _row["motivo_declaracion_U6"]=_d6[1]
                if _d6[0] not in ("ACTIVA","CABLEADA_SIN_SENAL_EN_CASO") and _row["feeds_predictor_declarado"]:
                    _row["feeds_predictor_declarado_original"]=True; _row["feeds_predictor_declarado"]=False
            if not (_row.get("reason") or _row.get("error")) and _f.get("motivo"): _row["reason"]=_f.get("motivo")
        # misma pieza con estado distinto motor vs hub: si el hub verificó que no hubo señal, la fila motor lo dice (con motivo).
        def _norm(x): return str(x).split(" (")[0].replace(".py","").replace("_v1","")
        _hubm={_norm(r.get("pieza")):r for r in _hub_reg if isinstance(r,dict)}
        for _row in status:
            if not isinstance(_row,dict) or _row.get("status")!="EXECUTED": continue
            _h=_hubm.get(_norm(_row.get("component")))
            if _h is not None and _h.get("estado")=="ACTIVA_MUDA":
                _row["status"]="EXECUTED_SIN_SENAL"; _row["reason"]=f"verificado por hub ({_h.get('pieza')}): {_h.get('aporte')}"
        for _row in status:
            if isinstance(_row,dict) and _row.get("component")=="laterales_unico_v1.py(post)":
                _row["n_piezas_total"]=len(_hub_reg)
            if isinstance(_row,dict) and _row.get("component")=="vecinos_caldero/neighbor_store.py":
                _row["persistence"]=_neighbor_persistence_010b
    except Exception as _eve:
        status.append({"component":"PATCH010b_estado_verificado","status":"ERROR","error":f"{type(_eve).__name__}:{_eve}"})
    result["caldero_neighbor_persistence"]=_neighbor_persistence_010b
    # PATCH 011: traza de autoevidencia en stores (sin lista de tokens).
    _v=_RUN_CTX.get("vecinos_011") or {}
    result["autoevidencia_stores_011"]={"version":getattr(_ae011,"VERSION",None),"input_sha":_RUN_CTX.get("input_sha_011"),
        "vecinos":{k:_v.get(k) for k in ("status","fuente","eventos_total","eventos_ajenos","propios_excluidos","propios_excluidos_por_sha",
                                          "tokens_solo_propios_excluidos","cases","observations","error","min_casos_ajenos","identidades_ajenas",
                                          "propios_excluidos_por_sujeto_014","sujeto_actual_014","nombres_sujeto_015") if k in _v} | {"n_tokens_que_votan":len(_v.get("unique_tokens") or [])},
        "ilumina_012":_v.get("ilumina_012"),  # PATCH 012: tokens de un solo caso ajeno (traza/luz, sin score)
        "sujetos_014":{k:x for k,x in (_RUN_CTX.get("sujetos_014") or {}).items() if k in ("version","sujeto","fuente","status","error")},  # PATCH 014
        "filtrados_013":{k:x for k,x in (_RUN_CTX.get("filtro_013") or {}).items() if k in ("status","version","listas","memoria","vecinos_actuales","anos_015","error")},  # PATCH 013+015
        "luces_persistentes":_RUN_CTX.get("luces_011"),
        "stinkbox":(features.get("stinkbox_transport") or {}).get("idempotencia_011"),
        "pendientes":((pred.get("compuerta_cierre") or {}).get("autoevidencia_011")),
        "pendientes_escritura":(((pred.get("compuerta_cierre") or {}).get("latencia_escrita") or {}).get("idempotencia_011")),
        "persistencia_vecinos":(_neighbor_persistence_010b or {}).get("idempotencia_011") or (_neighbor_persistence_010b or {}).get("status"),
        "regla":"autoevidencia_no_cuenta; ciego≈vivo: eventos/pendientes del mismo caso o input no suman; re-correr el mismo input no acumula",
        "can_decide_H":False}
    status.append({"component":"autoevidencia_stores_011.py","status":"EXECUTED" if _ae011 is not None else "FALTA_ARCHIVO","feeds_predictor":False,"feeds_H":False,"can_decide_H":False,
                   "role":"filtro_autoevidencia_stores (excluye eventos propios de la memoria Caldero; idempotencia StinkBox/vecinos)",
                   "propios_excluidos":_v.get("propios_excluidos")})
    # PATCH 018 — resolución operativa terminal. La latencia solo sobrevive como memoria de tokens/frentes.
    # UNIFICADO_20261011: CIERRE_TERMINAL=018 (defecto, comportamiento Línea B) | 016 (Línea A: H1/H2=top1/top2 rank_fusion, sin reordenar).
    # U2_cierre_020 (2026-10-11): defecto 020 (decisión Mj: el motor manda en H). 018 y 016 siguen seleccionables.
    _CIERRE_MODO_U=(_oscat.getenv("CIERRE_TERMINAL") or "020").strip()
    try:
        if _CIERRE_MODO_U=="016":
            raise _CierreModo016()
        _res017=_ceb_stage("resolucion_operativa_terminal_017", lambda: _resolver_cierre_operativo_017(result,pred,boards,histories,features,motor,{"run_ctx":_RUN_CTX,"gate_ctx":gate_ctx,"case":case},modo=("020" if _CIERRE_MODO_U=="020" else "018")), shared=[pred])
        result["resolucion_operativa_terminal_017"]=_res017
        status.append({"component":"resolucion_operativa_terminal_017","status":_res017.get("status","EXECUTED"),
                       "feeds_predictor":False,"feeds_H":False,"can_decide_H":(_CIERRE_MODO_U!="020"),"role":("terminal_motor_order_tiebreak_only_in_band_020" if _CIERRE_MODO_U=="020" else "terminal_operational_resolution_after_tortugas"),
                       "H1":_res017.get("H1"),"H2":_res017.get("H2"),"method":((_res017.get("decision") or {}).get("metodo"))})
    except _CierreModo016:
        result["resolucion_operativa_terminal_017"]={"status":"OMITIDO_CIERRE_TERMINAL_016","regla":"CIERRE_TERMINAL=016: sin reordenamiento terminal (tortugas/casos semejantes/pistas LLM no escriben H)"}
        status.append({"component":"resolucion_operativa_terminal_017","status":"OMITIDO_CIERRE_TERMINAL_016","feeds_predictor":False,"feeds_H":False,"can_decide_H":False})
    except Exception as _r017e:
        result["resolucion_operativa_terminal_017"]={"status":"ERROR","error":f"{type(_r017e).__name__}:{_r017e}"}
        status.append({"component":"resolucion_operativa_terminal_017","status":"ERROR","error":str(_r017e)})

    # PATCH 016 — CIERRE DE FIN DE CORRIDA (regla Mj 2026-10-06 21:25 CT): la latencia es estado DURANTE la corrida y de
    # tokens/frentes (persistidos para casos futuros); nunca el veredicto final. Al final SIEMPRE se emiten H1, H2 (= top1/top2
    # de rank_fusion, sin ranking nuevo) y la apuesta, con margen y grado de confianza (FIRME/AJUSTADA/FRAGIL). Guardianes y
    # modo estricto gradúan y objetan; no bloquean la emisión ni escriben H (can_decide_H=False).
    try:
        _snap016=_h_snapshot(pred)
        _cf016=_ceb_stage("cierre_final_016", lambda: (_cierre_final_016_lineaA if _CIERRE_MODO_U=="016" else (_cierre_final_020 if _CIERRE_MODO_U=="020" else _cierre_final_016))(result,pred,_RUN_CTX), shared=[pred])  # etapa observada por el CEB
        _cf016["verificacion"]={"predictor_igual":_snap016==_h_snapshot(pred),
                                "H1_es_primer_operativo":_cf016.get("H1")==((pred.get("candidates") or [{}])[0].get("family")),
                                "H2_es_segundo_operativo":_cf016.get("H2")==((pred.get("candidates") or [{},{}])[1].get("family") if len(pred.get("candidates") or [])>1 else None),
                                "seleccion_terminal_puede_diferir_de_rank_fusion":bool((pred.get("terminal_resolution") or {}).get("method", "").startswith("TORTUGAS")),
                                "rank_fusion_original_conservado":True}
        (_aplicar_cierre_final_016_lineaA if _CIERRE_MODO_U=="016" else (_aplicar_cierre_final_020 if _CIERRE_MODO_U=="020" else _aplicar_cierre_final_016))(result,pred,_cf016)
        _cf016["modo_cierre_terminal_unificado"]=_CIERRE_MODO_U
        status.append({"component":"cierre_final_016","status":"EXECUTED","feeds_predictor":False,"feeds_H":False,"can_decide_H":False,
                       "role":"cierre de fin de corrida: H1/H2/apuesta operativos; tortugas y memoria semejante resuelven ambigüedad; solo tokens nuevos quedan como memoria activa",
                       "grado":_cf016.get("grado"),"H1":_cf016.get("H1"),"H2":_cf016.get("H2"),"margen":_cf016.get("margen")})
    except Exception as _e016:
        import traceback as _tb016
        result["cierre_final"]={"status":"ERROR","error":f"{type(_e016).__name__}:{_e016}","trace":_tb016.format_exc()[-1500:]}
        status.append({"component":"cierre_final_016","status":"ERROR","error":str(_e016)})
    # PATCH 017 — Décimo Hombre con esteroides: capa adversarial iterativa/mayéutica.
    # Se ejecuta DESPUÉS del cierre de la corrida; audita y reabre preguntas, nunca reescribe H/apuesta.
    try:
        _dhx=_load("decimo_hombre_esteroides_mayeutica_v1", "decimo_hombre_esteroides_mayeutica_v1.py")
        if _dhx is not None:
            # PATCH05: cada contrafactual recalcula predictor real sobre copias; no modifica la corrida sellada.
            def _dh_counterfactual(kind, target):
                import copy as _copy_dh
                _cf_case=_copy_dh.deepcopy(case)
                _cf_features=_copy_dh.deepcopy(features)
                _cf_boards=_copy_dh.deepcopy(boards)
                _cf_histories=_copy_dh.deepcopy(histories)
                _cf_motor=_copy_dh.deepcopy(motor)
                if kind == "module":
                    _cf_features.pop(str(target), None)
                    _cf_pred=_predict(_cf_boards,_cf_histories,_cf_motor,_cf_features,None)
                    return {"predictor":_cf_pred,"removed_module":str(target)}
                if kind == "token_core":
                    _removed=0
                    for _cut in _cf_case.get("cuts") or []:
                        for _axis in ("P","A","C"):
                            _new=[]
                            for _pair in _cut.get(_axis) or []:
                                if isinstance(_pair,(list,tuple)) and len(_pair)>=1 and str(_pair[0])==str(target):
                                    _removed+=1
                                else: _new.append(_pair)
                            _cut[_axis]=_new
                    _native_cf=_load("v153_native_v09_cf", "MOTOR_V15_3_NATIVO_V0_9_UNICO.py") or _load("v153_native_v09_cf", "MOTOR_V15_3_NATIVO_V0_9.py")
                    if _native_cf is None: return {"predictor":{},"removed_token":str(target),"removed_count":_removed,"diagnostic":"NATIVE_ENGINE_NOT_LOADED"}
                    _cf_question=str(_cf_case.get("question",_cf_case.get("case_id","case")))+"_ADVERSARIAL_ABLATION"
                    _cf_motor=_native_cf.correr_5x3(_cf_case["cuts"],pregunta=_cf_question,
                        annex_traza=False,obstaculo=_cf_case.get("obstaculo"),texto_polaridad=_cf_case.get("texto_polaridad"),monte_carlo=False)
                    # Match the main execution's emission adapter. Native counterfactual runs with
                    # annex_traza=False do not necessarily contain P/A/C_FULL_244; without this step
                    # _predict receives empty boards and the supposed core ablation produces no ranking.
                    if not all((cc.get("P_FULL_244") is not None and cc.get("A_FULL_244") is not None and cc.get("C_FULL_244") is not None)
                               for cc in (_cf_motor.get("cuts") or [])):
                        _cf_emit=_load("eng_emit_dh", "Engine_V5_CANONICO_SOLO.py")
                        if _cf_emit is None:
                            return {"predictor":{},"removed_token":str(target),"removed_count":_removed,"diagnostic":"EMISSION_ADAPTER_ENGINE_MISSING"}
                        _cf_pat_path=str(_PATTERNS_PATH())
                        _cf_ep=_native_cf._engine(_cf_emit,_cf_pat_path,_cf_question+"_P_EMIT")
                        _cf_ea=_native_cf._engine(_cf_emit,_cf_pat_path,_cf_question+"_A_EMIT")
                        _cf_ec=_native_cf._engine(_cf_emit,_cf_pat_path,_cf_question+"_C_EMIT")
                        _cf_vocab=_native_cf.load_canonical()[1] if hasattr(_native_cf,"cuello_top_k") else None
                        _cf_cu4=(lambda cid,e,rows,prev=None,cur=None: _native_cf.cuello_top_k(cid,e,rows,_cf_vocab,previos=prev,corte_actual=cur)[0]) if _cf_vocab is not None else (lambda cid,e,rows,prev=None,cur=None: rows)
                        try:
                            for _cf_i,(_cf_c,_cf_raw) in enumerate(zip(_cf_motor.get("cuts") or [],_cf_case["cuts"])):
                                _cf_prev=_cf_case["cuts"][:_cf_i]
                                _cf_c["P_FULL_244"]=_native_cf._board(_cf_emit,_cf_ep,_cf_c["corte"]+"_P_EMIT",_cf_cu4(_cf_c["corte"],"P",_cf_raw.get("P") or [],_cf_prev,_cf_raw))
                                _cf_c["A_FULL_244"]=_native_cf._board(_cf_emit,_cf_ea,_cf_c["corte"]+"_A_EMIT",_cf_cu4(_cf_c["corte"],"A",_cf_raw.get("A") or [],_cf_prev,_cf_raw))
                                _cf_c["C_FULL_244"]=_native_cf._board(_cf_emit,_cf_ec,_cf_c["corte"]+"_C_EMIT",_cf_cu4(_cf_c["corte"],"C",_cf_raw.get("C") or [],_cf_prev,_cf_raw))
                            _cf_dims=[(len(cc.get("P_FULL_244") or {}),len(cc.get("A_FULL_244") or {}),len(cc.get("C_FULL_244") or {})) for cc in (_cf_motor.get("cuts") or [])]
                            if not all(a==b==c==_n_patrones() for a,b,c in _cf_dims):
                                return {"predictor":{},"removed_token":str(target),"removed_count":_removed,"diagnostic":f"EMISSION_ADAPTER_DIMENSION_ERROR:{_cf_dims[:3]}"}
                        finally:
                            if hasattr(_native_cf,"_close_all_engines"):
                                _native_cf._close_all_engines()
                    _cf_boards=[]; _cf_histories=[]
                    for _c in _cf_motor.get("cuts") or []:
                        _cf_boards.append({"P":dict(_c.get("P_FULL_244") or {}),"A":dict(_c.get("A_FULL_244") or {}),"C":dict(_c.get("C_FULL_244") or {})})
                        _cf_histories.append(_candidate_history_for_cut(_c))
                    # Deliberately strip every lateral/sidecar output: this is the core-only, no-noise test.
                    _cf_features={"cuts":_cf_case["cuts"]}
                    _cf_pred=_predict(_cf_boards,_cf_histories,_cf_motor,_cf_features,None)
                    return {"predictor":_cf_pred,"removed_token":str(target),"removed_count":_removed,"sidecars_stripped":True}
                if kind == "dimension":
                    _cf_pred=_predict(_cf_boards,_cf_histories,_cf_motor,_cf_features,None,adversarial_exclude_dimensions=(str(target),))
                    return {"predictor":_cf_pred,"removed_dimension":str(target)}
                if kind == "stress_pair":
                    _spec=target if isinstance(target,dict) else {}
                    _dims=tuple(str(x) for x in (_spec.get("dimensions") or []))
                    _mods=[str(x) for x in (_spec.get("modules") or [])]
                    for _mod in _mods: _cf_features.pop(_mod,None)
                    _cf_pred=_predict(_cf_boards,_cf_histories,_cf_motor,_cf_features,None,adversarial_exclude_dimensions=_dims)
                    return {"predictor":_cf_pred,"removed_dimensions":list(_dims),"removed_modules":_mods}
                return {"predictor":{},"diagnostic":"UNKNOWN_COUNTERFACTUAL_KIND"}
            _dh_audit=_ceb_stage("decimo_hombre_esteroides_mayeutica_v1", lambda: _dhx.run(case, result, _dh_counterfactual), shared=[result.get("predictor") or {}, result.get("cierre_final") or {}])
            result["decimo_hombre_esteroides"]=_dh_audit
            status.append({"component":"decimo_hombre_esteroides_mayeutica_v1.py",
                           "status":("EXECUTED_WITH_CONCLUSION" if _dh_audit.get("status")=="EJECUTADO_CIERRE_ADVERSARIAL" else "EXECUTED_WITH_LIMITATIONS"),
                           "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"rewrites_apuesta":False,
                           "role":"adversarial_iterative_review_mayeutica_dialectica","n_attacks":len(_dh_audit.get("ataques") or []),
                           "n_real_counterfactual_rankings":(_dh_audit.get("diagnosticos") or {}).get("actual_counterfactual_rankings",0),
                           "orthogonal_residual_analysis":(_dh_audit.get("orthogonal_residual_analysis") or {}).get("status","NOT_REPORTED"),
                           "decision_de_proceso":_dh_audit.get("decision_de_proceso")})
        else:
            _fallback_cands=[c for c in ((result.get("predictor") or {}).get("candidates") or []) if isinstance(c,dict) and c.get("family")]
            _fallback_cands.sort(key=lambda c:float(c.get("rank_fusion") or 0.0),reverse=True)
            _fallback_winner=_fallback_cands[0].get("family") if _fallback_cands else "NO_IDENTIFICABLE_CON_ESTA_ENTRADA"
            result["decimo_hombre_esteroides"]={"version":"RECUPERACION_TERMINAL_PATCH05","status":"CIERRE_RECUPERADO_CON_DIAGNOSTICO",
                "can_decide_H":False,"rewrites_H":False,"hipotesis_apuesta":{"candidata":_fallback_winner,"estado":"CONCLUSION_OPERACIONAL_RECUPERADA",
                "fundamento":"La capa adversarial no está disponible; se recupera una conclusión operacional desde el ranking finito sin fingir pruebas adversariales.","no_equivale_a_verdad_demostrada":True},
                "decision_de_proceso":"CONCLUSION_OPERACIONAL_RECUPERADA_CON_DIAGNOSTICO","causa":"CAPA_ADVERSARIAL_NO_CARGADA",
                "recuperacion":"RANKING_FINITO_RELEIDO_SIN_NULL_NAN","no_null_nan":True}
            status.append({"component":"decimo_hombre_esteroides_mayeutica_v1.py","status":"EXECUTED_WITH_TERMINAL_RECOVERY",
                "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"decision_de_proceso":"CONCLUSION_OPERACIONAL_RECUPERADA_CON_DIAGNOSTICO"})
    except Exception as _dhx_exc:
        # PATCH05 recovery: retry the full dimensional/score adversarial pass without the
        # optional native callback. The exception is recorded, but cannot terminate the run.
        try:
            _dhx_retry=locals().get("_dhx") or _load("decimo_hombre_esteroides_mayeutica_v1_retry", "decimo_hombre_esteroides_mayeutica_v1.py")
            _dh_retry_out=_dhx_retry.run(case,result) if _dhx_retry is not None else None
            if isinstance(_dh_retry_out,dict):
                _dh_retry_out["recuperacion"]={"estado":"REINTENTO_DIMENSIONAL_EJECUTADO","causa_original":f"{type(_dhx_exc).__name__}:{_dhx_exc}",
                    "contrafactual_nativo_disponible":False,"no_se_interrumpe_cierre":True}
                result["decimo_hombre_esteroides"]=_dh_retry_out
                status.append({"component":"decimo_hombre_esteroides_mayeutica_v1.py","status":"EXECUTED_WITH_RECOVERY",
                    "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"decision_de_proceso":_dh_retry_out.get("decision_de_proceso")})
            else:
                raise RuntimeError("NO_SE_PUDO_RECONSTRUIR_SALIDA_ADVERSARIAL")
        except Exception as _retry_exc:
            _cands=((result.get("predictor") or {}).get("candidates") or [])
            _ranked=sorted([c for c in _cands if isinstance(c,dict) and c.get("family")],key=lambda c:float(c.get("rank_fusion") or 0.0),reverse=True)
            _winner=_ranked[0].get("family") if _ranked else "NO_IDENTIFICABLE_CON_ESTA_ENTRADA"
            result["decimo_hombre_esteroides"]={"version":"RECUPERACION_TERMINAL_PATCH05","status":"CIERRE_RECUPERADO_CON_DIAGNOSTICO",
                "can_decide_H":False,"rewrites_H":False,"hipotesis_apuesta":{"candidata":_winner,"estado":"CONCLUSION_OPERACIONAL_RECUPERADA",
                "fundamento":"Selección desde el ranking finito disponible; la capa adversarial sufrió un error interno y se registra la causa.","no_equivale_a_verdad_demostrada":True},
                "decision_de_proceso":"CONCLUSION_OPERACIONAL_RECUPERADA_CON_DIAGNOSTICO","causas":[f"ERROR_ORIGINAL:{type(_dhx_exc).__name__}:{_dhx_exc}",f"ERROR_REINTENTO:{type(_retry_exc).__name__}:{_retry_exc}"],
                "recuperacion":"RANKING_FINITO_RELEIDO_SIN_NULL_NAN","no_null_nan":True}
            status.append({"component":"decimo_hombre_esteroides_mayeutica_v1.py","status":"EXECUTED_WITH_TERMINAL_RECOVERY",
                "feeds_predictor":False,"feeds_H":False,"can_decide_H":False,"decision_de_proceso":"CONCLUSION_OPERACIONAL_RECUPERADA_CON_DIAGNOSTICO"})
    # U3_predictibilidad (021, 2026-10-11): escala de predictibilidad estructural con base (forma de P_final del Engine
    # canónico), set de hipótesis necesarias y suficientes (eje + componentes) y paso inverso post-freeze (hipótesis -> cortes).
    # Solo lee: can_decide_H=False; no cambia rank_fusion, orden, H1/H2, apuesta ni grado 020. Se apaga con PREDICTIBILIDAD_021=0.
    import os as _os021
    if (_os021.getenv("PREDICTIBILIDAD_021") or "1").strip() != "0":
        try:
            _p021=_load("predictibilidad_set_021", "predictibilidad_set_021.py")
            if _p021 is None: raise RuntimeError("MODULO_021_NO_CARGADO")
            _snap021=_h_snapshot(pred)
            _o021=_ceb_stage("predictibilidad_set_021", lambda: _p021.run(case,result,BASE,_patterns()), shared=[pred])
            _hns021=_o021.pop("hipotesis_necesarias_suficientes",{}) or {}
            result["predictibilidad_021"]=_o021
            result["hipotesis_necesarias_suficientes"]=_hns021
            if isinstance(result.get("cierre_final"),dict) and _hns021.get("miembros"):
                result["cierre_final"]["hipotesis_necesarias_suficientes"]={"eje":_hns021.get("eje"),"n":_hns021.get("n"),
                    "miembros":[{k:m.get(k) for k in ("familia","rol","en_banda_con_eje","peso_en_set","predictibilidad_estructural_pct","cobertura_unica_frac","cortes_unicos")} for m in _hns021["miembros"]],
                    "grado_inverso":(_hns021.get("grado_inverso") or {}).get("estado"),"fuente":"predictibilidad_set_021 (no cambia H1/H2 ni grado 020)"}
            status.append({"component":"predictibilidad_set_021.py","status":"EXECUTED","feeds_predictor":False,"feeds_H":False,"can_decide_H":False,
                           "role":"escala predictibilidad estructural + set necesario/suficiente + paso inverso post-freeze",
                           "H_intacto":_snap021==_h_snapshot(pred),"n_set":_hns021.get("n"),"eje":_hns021.get("eje")})
        except Exception as _e021:
            result["predictibilidad_021"]={"status":"ERROR","error":f"{type(_e021).__name__}:{_e021}"}
            status.append({"component":"predictibilidad_set_021.py","status":"ERROR","error":str(_e021),"can_decide_H":False})
    # U4_todos_tokens (2026-10-11): MOVIMIENTO DE FONDO. Lateral y de traza: series de TODOS los tokens y de las 244
    # familias (tablero con todos los tokens), picos/mesetas/ascenso lento/descenso/latente, rango de las familias bajo
    # el top-5 y «emergentes desde abajo» con paso inverso 021. can_decide_H=False; no reordena 020 ni cambia el set 021.
    # Se apaga con MOVIMIENTO_FONDO_U4=0.
    _u4_attach={}
    if (_os021.getenv("MOVIMIENTO_FONDO_U4") or "1").strip() != "0":
        try:
            _mf=_load("movimiento_de_fondo_u4", "movimiento_de_fondo_u4.py")
            if _mf is None: raise RuntimeError("MODULO_U4_NO_CARGADO")
            _snapu4=_h_snapshot(pred); _cfu4=json.dumps(result.get("cierre_final"),sort_keys=True,default=str); _hnsu4=json.dumps(result.get("hipotesis_necesarias_suficientes"),sort_keys=True,default=str)
            _p021u4=_load("predictibilidad_set_021_u4", "predictibilidad_set_021.py")
            _ou4=_ceb_stage("movimiento_de_fondo_u4", lambda: _mf.run(case,result,BASE,_patterns(),native,monte_carlo=monte_carlo,seed=seed,p021=_p021u4), shared=[pred])
            _u4_attach={"movimiento_de_fondo":_ou4,"lo_que_se_cocina_abajo":_ou4.get("lo_que_se_cocina_abajo")}
            _intacto=(_snapu4==_h_snapshot(pred) and _cfu4==json.dumps(result.get("cierre_final"),sort_keys=True,default=str) and _hnsu4==json.dumps(result.get("hipotesis_necesarias_suficientes"),sort_keys=True,default=str))
            status.append({"component":"movimiento_de_fondo_u4.py","status":"EXECUTED","feeds_predictor":False,"feeds_H":False,"can_decide_H":False,
                           "role":"movimiento de fondo: series de todos los tokens y familias, emergentes desde abajo (traza lateral)",
                           "H_intacto":_intacto,"n_emergentes":len(_ou4.get("lo_que_se_cocina_abajo") or [])})
        except Exception as _eu4:
            import traceback as _tbu4
            _u4_attach={"movimiento_de_fondo":{"status":"ERROR","error":f"{type(_eu4).__name__}:{_eu4}","tb":_tbu4.format_exc()[-1500:]}}
            status.append({"component":"movimiento_de_fondo_u4.py","status":"ERROR","error":str(_eu4),"can_decide_H":False})
    # WORKING PATCH: integra geometría multicapas que antes solo corría en un ZIP lateral separado.
    # Se ejecuta sobre el prefijo completo hasta Z; sus trazas alimentan el generador del set abierto.
    result["geometria_multicapa"] = _run_geometria_multicapa_working(result, case)
    _geo_status = result["geometria_multicapa"]
    status.append({"component":"geometria_multicapa_integrada_working_v1", "status":_geo_status.get("status", "ERROR"),
                   "feeds_predictor":False, "feeds_H":bool(_geo_status.get("feeds_hypothesis_generation")),
                   "can_decide_H":False, "role":"trazabilidad global multicapa; aporta enlaces candidatos y contexto geométrico al generador de hipótesis",
                   "error":_geo_status.get("error"), "n_trace_families":len(_geo_status.get("candidate_trace_support") or {})})
    # WORKING PATCH: arquitectura de hipótesis abiertas -> apuesta multiescenario.
    # Se ejecuta después de producir el set inverso/geométrico y antes de serializar la corrida.
    try:
        _ha=_load("hipotesis_trayectoria_abierta_v1", "hipotesis_trayectoria_abierta_v1.py")
        if _ha is None: raise RuntimeError("MODULO_HIPOTESIS_TRAYECTORIA_ABIERTA_NO_CARGADO")
        _open_h=_ha.construir(result, case, _patterns())
        result["hipotesis_trayectoria_abierta"]=_open_h
        result["hipotesis"]=_open_h.get("hipotesis") or []
        result["apuesta_legacy_H1_H2"]=(dict(result.get("apuesta") or {}) if isinstance(result.get("apuesta"),dict) else None)
        result["apuesta"]={**(_open_h.get("apuesta") or {}), "version":_open_h.get("version"),
                            "fuente_hipotesis":"hipotesis_trayectoria_abierta_v1",
                            "apuesta_legacy_no_autoritativa":True}
        result["apuesta_trayectoria"]=_open_h.get("apuesta")
        result["H_contract"]={"primary":"hipotesis_trayectoria_abierta.hipotesis",
                              "H1_H2":"compatibilidad histórica; no limitan cardinalidad ni definen apuesta",
                              "n_hipotesis":_open_h.get("n_hipotesis"),"cardinalidad_fija":False,
                              "apuesta_se_genera_despues_del_set":True}
        if isinstance(result.get("cierre_final"),dict):
            result["cierre_final"]["hipotesis_trayectoria_abierta"]={"n":_open_h.get("n_hipotesis"),
                "estado":_open_h.get("estado"),"fuente":_open_h.get("version"),"H1_H2_no_autoritativos":True}
        status.append({"component":"hipotesis_trayectoria_abierta_v1.py","status":"EXECUTED",
                       "feeds_predictor":True,"feeds_H":True,"can_decide_H":True,
                       "role":"set de hipótesis de cardinalidad variable informado por vectorización multiescala; apuesta posterior multiescenario",
                       "n_hipotesis":_open_h.get("n_hipotesis"),"n_escenarios":len((_open_h.get("apuesta") or {}).get("escenarios") or [])})
    except Exception as _ha_exc:
        result["hipotesis_trayectoria_abierta"]={"estado":"ERROR","error":f"{type(_ha_exc).__name__}:{_ha_exc}","cardinalidad_fija":False}
        status.append({"component":"hipotesis_trayectoria_abierta_v1.py","status":"ERROR","error":str(_ha_exc),"feeds_H":False,"can_decide_H":False})
    result["registro_componentes"]=_registro_componentes(status,_hub_reg)
    if execution_identity is not None:
        result["execution_identity"]=execution_identity
    if ceb and ceb_ledger:
        ceb.ledger.register("motor_result", "motor_result")
        ceb.ledger.start("motor_result", [result])
        ceb.ledger.output("motor_result", result)
        ceb.ledger.end("motor_result", result)
        ceb.ledger.terminal("motor_result", "run_return_result")
        ceb_ledger.close()
        try:
            result["ceb"] = ceb_mod.FlowVerifier(ceb_ledger.path).verify(result)
            result["ceb"]["ledger"] = str(ceb_ledger.path)
        except Exception as _ce:
            result["ceb"]={"status":"VERIFIER_ERROR","error":f"{type(_ce).__name__}:{_ce}","ledger":str(ceb_ledger.path)}
    # PATCH05: terminal contract. Optional absence is converted to explicit, typed-by-reason
    # labels only after all computation/verification has finished; no null/NaN escapes JSON.
    result = _normalizar_salida_terminal(result)
    result = _aplicar_equivalencia_presentacion(result)
    result.update(_u4_attach)  # U4_todos_tokens: bloque lateral de traza (no toca nada de lo anterior)
    # PATCH 022 (2026-10-24): APUESTA DE DESTINO PERSONAL (auge|meseta|caida|ruptura). Campo NUEVO y separado.
    # Lee movimiento_de_fondo.series_familias (cortes <= Z). No toca H1/H2, set abierto, apuesta temática, rank ni Engine.
    # can_decide_H=False. Se apaga con DESTINO_022=0.
    import os as _os022
    if (_os022.getenv("DESTINO_022") or "1").strip() != "0":
        try:
            _m022=_load("apuesta_destino_personal_022", "apuesta_destino_personal_022.py")
            if _m022 is None: raise RuntimeError("MODULO_022_NO_CARGADO")
            _snap022=(json.dumps(result.get("H1"),sort_keys=True,default=str),json.dumps(result.get("H2"),sort_keys=True,default=str),json.dumps(result.get("apuesta"),sort_keys=True,default=str))
            result["apuesta_destino_personal"]=_m022.construir(result)
            result["apuesta_destino_personal"]["H_y_apuesta_tematica_intactos"]=_snap022==(json.dumps(result.get("H1"),sort_keys=True,default=str),json.dumps(result.get("H2"),sort_keys=True,default=str),json.dumps(result.get("apuesta"),sort_keys=True,default=str))
        except Exception as _e022:
            result["apuesta_destino_personal"]={"estado":"ERROR","error":f"{type(_e022).__name__}:{_e022}","can_decide_H":False}
    if case.get("_internal_analysis_no_external_search"):
        result["internal_analysis_receipt"]={"status":"INTERNAL_T1_AUXILIARY_COMPLETED", "purpose":"comparacion de corte retenido",
            "ceb_primary_ledger":"NOT_APPLICABLE_INTERNAL_SUBRUN", "external_search":"SKIPPED_BY_CONTRACT",
            "not_a_separate_calibration_case":True}
    return result


def _aplicar_equivalencia_presentacion(result):
    """Salida interpretable en porcentaje de relleno; no expresa probabilidad."""
    pred = result.get("predictor") or {}
    candidates = {c.get("family"): c for c in (pred.get("candidates") or []) if isinstance(c, dict) and c.get("family")}
    escala = {"metodo": "indice_potencial_equilibrado_pct",
              "definicion": "promedio equilibrado de las fracciones de relleno de los grupos estructurales activos",
              "unidad": "% de relleno estructural", "rango": "0–100%",
              "es_probabilidad": False, "es_porcentaje_de_acierto": False,
              "nota": "La puntuación rank_fusion no es una probabilidad y queda solo como diagnóstico técnico."}
    import math as _math_presentacion
    resumen = {"escala": escala}
    for label in ("H1", "H2"):
        h = result.get(label)
        if not isinstance(h, dict):
            continue
        fam = h.get("family")
        cand = candidates.get(fam) or {}
        feat = cand.get("features") or {}
        pct = feat.get("indice_potencial_equilibrado_pct")
        groups = feat.get("grupos") or {}
        breakdown = {g: v.get("porcentaje_del_maximo") for g, v in groups.items() if isinstance(v, dict) and v.get("porcentaje_del_maximo") is not None}
        _rank = h.pop("rank_fusion", "TORTUGAS")
        _margin = h.pop("margen", "TORTUGAS")
        technical = {"rank_fusion": _rank if _rank is not None else "TORTUGAS",
                     "margen_rank_fusion": _margin if _margin is not None else "TORTUGAS"}
        _pct_ok = pct is not None and isinstance(pct, (int, float)) and _math_presentacion.isfinite(float(pct))
        h["porcentaje_relleno"] = round(float(pct), 2) if _pct_ok else "TORTUGAS"
        h["porcentaje_relleno_estado"] = "MEDIDO" if _pct_ok else "TORTUGAS_SIN_MEDIDA_DE_RELLENO"
        h["unidad_porcentaje"] = "% de relleno estructural equilibrado; TORTUGAS indica medida no disponible"
        h["desglose_relleno_por_grupo_pct"] = breakdown
        h["interpretacion"] = "relleno relativo al máximo estructural definido; no es probabilidad ni confianza de acierto"
        h["diagnostico_tecnico_interno"] = technical
        resumen[label] = {"familia": fam, "porcentaje_relleno": h["porcentaje_relleno"], "desglose_relleno_por_grupo_pct": breakdown}
        if h.get("peso_relativo") is not None:  # CIERRE_020
            resumen[label]["peso_relativo"] = h["peso_relativo"]
            resumen[label]["unidad_peso_relativo"] = "proporción de rank_fusion sobre las candidatas publicadas (suma 1); no es probabilidad"
    _p021 = result.get("predictibilidad_021") if isinstance(result.get("predictibilidad_021"), dict) else {}
    _e021 = _p021.get("predictibilidad") if isinstance(_p021.get("predictibilidad"), dict) else {}
    _ph021 = _e021.get("por_hipotesis") or {}
    for label in ("H1", "H2"):  # U3_021
        if isinstance(resumen.get(label), dict) and "predictibilidad_estructural_pct" in (_ph021.get(resumen[label].get("familia")) or {}):
            resumen[label]["predictibilidad_estructural_pct"] = _ph021[resumen[label]["familia"]]["predictibilidad_estructural_pct"]
    _hns021 = result.get("hipotesis_necesarias_suficientes")
    if isinstance(_hns021, dict) and _hns021.get("miembros"):  # U3_021
        resumen["escala_predictibilidad"] = {"nombre": "predictibilidad estructural (soporte interno)", "es_probabilidad_calibrada": False,
                                             "base_pct": _e021.get("base_pp"), "techo_pct": _e021.get("techo_pp"),
                                             "pp_por_punto_de_rank_fusion": _e021.get("pp_por_punto_de_rank_fusion"), "formula": _e021.get("formula")}
        resumen["hipotesis_necesarias_suficientes"] = [{k: m.get(k) for k in ("familia", "rol", "peso_en_set", "predictibilidad_estructural_pct", "cobertura_unica_frac")} for m in _hns021["miembros"]]
        resumen["grado_inverso_set"] = (_hns021.get("grado_inverso") or {}).get("estado")
    _cf020 = result.get("cierre_final") if isinstance(result.get("cierre_final"), dict) else {}
    if isinstance(_cf020.get("mezcla"), dict):  # CIERRE_020
        _mezcla_keys=("lectura", "lectura_texto", "peso_H1", "peso_H2", "peso_H1_en_par", "peso_H2_en_par")
        resumen["mezcla"] = {k: (_cf020["mezcla"].get(k) if _cf020["mezcla"].get(k) is not None else "TORTUGAS") for k in _mezcla_keys}
        if any(_cf020["mezcla"].get(k) is None for k in _mezcla_keys):
            resumen["mezcla_estado"] = "TORTUGAS_MEZCLA_NO_EMITIDA_COMPLETAMENTE"
        resumen["grado"] = _cf020.get("grado") if _cf020.get("grado") is not None else "TORTUGAS"
    _open_h = result.get("hipotesis_trayectoria_abierta") if isinstance(result.get("hipotesis_trayectoria_abierta"), dict) else {}
    if _open_h:
        resumen["conjunto_hipotesis_abiertas"] = {
            "n_hipotesis": _open_h.get("n_hipotesis", 0),
            "cardinalidad_fija": False,
            "hipotesis": [{k: h.get(k) for k in ("id", "familia", "rol_en_set", "rank_fusion", "soporte_estructural_relativo", "trazabilidad_geometrica")} for h in (_open_h.get("hipotesis") or [])],
            "compatibilidad_H1_H2": "aliases históricos; no limitan el conjunto",
        }
        resumen["apuesta_multiescenario"] = result.get("apuesta_trayectoria") or _open_h.get("apuesta")
    result["salida_interpretable"] = {**escala, **resumen}
    result = {"salida_interpretable": result["salida_interpretable"], **{k:v for k,v in result.items() if k != "salida_interpretable"}}
    cf = result.get("cierre_final")
    if isinstance(cf, dict) and "margen" in cf:
        cf["margen_rank_fusion_interno"] = cf.pop("margen")
        h1 = resumen.get("H1") or {}; h2 = resumen.get("H2") or {}
        _h1_pct=h1.get("porcentaje_relleno"); _h2_pct=h2.get("porcentaje_relleno")
        if isinstance(_h1_pct,(int,float)) and isinstance(_h2_pct,(int,float)):
            cf["diferencia_relleno_puntos_porcentuales"] = round(_h1_pct - _h2_pct, 2)
        else:
            cf["diferencia_relleno_puntos_porcentuales"] = "TORTUGAS_SIN_DOS_MEDIDAS_COMPARABLES"
    return result


def _normalizar_salida_terminal(result):
    """PATCH 019: terminal contract with explicit disposition for every missing field.

    No null/nonfinite value is serialized. Unlike the prior normalizer, every missing
    field gets an explicit typed disposition: metadata gaps are named as such; missing
    measurements are omitted without inventing numeric values and are enumerated with
    their reason/status in the terminal audit. This is not a calibration substitute.
    """
    import math as _math_terminal
    missing=[]; removed_nonfinite=[]
    DROP=object()
    METADATA_KEYS={"archivo","location","sha256","sha_esperado","sha_catalogo_declarado","input_sha","version"}
    REASON_KEYS={"motivo","reason","razon"}
    BOOL_KEYS={"dataset_hardcode"}
    def disposition(key,path,parent):
        low=str(key).lower()
        if low == "predictibilidad_calibrada":
            return ("NO_CALIBRADA_SIN_DESENLACES_SELLADOS_POR_CASO", "predictive_validation.status=NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES")
        if key in METADATA_KEYS:
            return ("NO_DECLARADO_EN_PAQUETE_O_INVENTARIO", "el productor no declaró este metadato; no se fabricó hash/ruta/versión")
        if key in REASON_KEYS:
            return ("SIN_MOTIVO_REGISTRADO", "la etapa no registró error ni motivo textual")
        if key == "metadata":
            return ("METADATA_NO_OBSERVADA", "la fuente no entregó objeto metadata")
        if key in {"H1","H2"} and path.startswith("$.motor."):
            return ("EMITIDA_EN_CIERRE_RAIZ", "la hipótesis final está en la raíz y en resolucion_operativa_final")
        if key == "line":
            return ("LINEA_NO_LOCALIZADA", "la anomalía no aporta número de línea")
        if key == "fue_top1":
            return ("NO_DETERMINADO_POR_ESTE_SENSOR", "el sensor no calculó el booleano para esta familia")
        if key in {"prototipo_padre","edad","r3_sombra_mentor","primer_quiebre","evento_obstaculo","contraejemplo","pregunta_detras_sugerida","injected_cut","cuerpo_arco","lente_dominante","bandera","dominante","escala_mayor_en_texto","apuesta","top1_tablero","nucleo"}:
            return ("NO_OBSERVADO_EN_ENTRADA_O_SALIDA_DEL_SENSOR", "el productor no aportó este dato para este corte")
        if key in {"souriau","polti","caldero","tusi","valor","carga","phi","sigma","omega_media","omega_abs_media","persistencia_signo","mean_distance","mean_cosine","persist_cos","kappa_dir","dX_norm","p_de","p_a","H_de","H_a","holds_without","sin_otros_agentes","campo_texto","filtro_identidad","arquetipos_dinamicos","guardia_detras_v2","aquiles_ancla_estricto","r3_sombra_mentor","negativo_top1","negativo_top2","negativo_top1_en_descarte","negativo_top1_en_descarte_estricto","propios_excluidos","tortugas","ilumina_012","luces_persistentes","stinkbox","pendientes","autoevidencia_011","reason","razon","estado","feeds_predictor_declarado","status","linea_mas_avanzada_actual"}:
            return ("MEDIDA_O_ESTADO_NO_EMITIDO", "no hay valor de origen verificable en esta corrida; no se sustituyó por cero ni por una puntuación inventada")
        if key == "null":
            return ("MARCADOR_NULL_NO_INFORMADO", "el productor emitió el campo null sin definir su semántica")
        return ("CAMPO_OPCIONAL_NO_EMITIDO", "el productor devolvió None; no hay base para inferir un valor")

    def clean(obj,path="$",preserve_tokens=False,parent=None):
        keep=preserve_tokens or any(x in path.lower() for x in ("tokens_latentes","tokens_descubiertos","persistent_neighbor_tokens","tokens_neighbors"))
        if obj is None:
            key=path.rsplit(".",1)[-1] if "." in path else path
            status,reason=disposition(key,path,parent)
            missing.append({"path":path,"field":key,"status":status,"reason":reason})
            return DROP
        if isinstance(obj,float) and not _math_terminal.isfinite(obj):
            removed_nonfinite.append({"path":path,"value_type":"non_finite_float"}); return DROP
        if isinstance(obj,str) and not keep:
            # Preserve the producer's state verbatim. Replacing substrings such as
            # NO_RESUELTO -> OBJECION_RESUELTA_EN_CIERRE falsely converted failed or
            # unexecuted checks into successful outcomes in serialized reports.
            return obj
        if isinstance(obj,dict):
            out={}
            for k,v in obj.items():
                nv=clean(v,f"{path}.{k}",keep,obj)
                if nv is not DROP: out[k]=nv
            # Add a field-level state beside every missing value; preserve numeric/string schema.
            for rec in [m for m in missing if m.get("path","").rsplit(".",1)[0] == path]:
                k=rec["field"]
                if k not in out:
                    out[f"{k}_estado"] = rec["status"]
            return out
        if isinstance(obj,list):
            out=[]
            for i,v in enumerate(obj):
                nv=clean(v,f"{path}[{i}]",keep,obj)
                if nv is not DROP: out.append(nv)
            return out
        return obj
    cleaned=clean(result)
    if not isinstance(cleaned,dict): cleaned={}
    cleaned["estado_final"]="RESUELTO_OPERACIONALMENTE" if cleaned.get("resolucion_operativa_final") else "ENTRADA_NO_CLASIFICABLE"
    cleaned["auditoria_terminal_valores"]={
        "contrato":"SIN_NULL_SIN_NAN_SIN_NAPIC_CON_DISPOSICION_EXPLICITA",
        "nulos_resueltos_con_estado":len(missing),"no_finitos_omitidos":len(removed_nonfinite),
        "politica":"ningún null se descarta sin registro: cada campo ausente queda identificado con estado y motivo; sin puntuaciones sustitutas",
        "campos_sin_valor":missing,"rutas_no_finitas_omitidas":removed_nonfinite,
        "estado_final":cleaned["estado_final"]
    }
    return cleaned

_MAPA_ESTADO={"EXECUTED":"ACTIVA","EXECUTED_WITH_FINDINGS":"ACTIVA","SUPERADA":"SUPERADA","SIN_PREFIJO_EN_INPUT":"ACTIVA_MUDA","ACTIVA":"ACTIVA","ACTIVA_MUDA":"ACTIVA_MUDA","HUB_ACTIVA":"ACTIVA","HUB_ACTIVA_MUDA":"ACTIVA_MUDA","EXECUTED_SIN_HALLAZGOS":"ACTIVA_MUDA","EXECUTED_SIN_SENAL":"ACTIVA_MUDA","PLUGIN_SALTADO":"NO_CORRE","CABLEADO_NO_EJECUTADO":"NO_CORRE",
              "ERROR":"NO_CORRE","FALTA_ARCHIVO":"NO_CORRE","API_PENDING":"ACTIVA_MUDA","CABLEADO_ESPERANDO_LLM_SEARCH":"ACTIVA_MUDA"}
def _registro_componentes(status,hub_reg):
    """Tabla completa por corrida: componentes del motor + piezas del hub + inventario estático (SUPERADA/NO_CORRE/FUERA)."""
    filas=[]
    for c in status:
        if not isinstance(c,dict): continue
        st=str(c.get("status"))
        filas.append({"pieza":c.get("component"),"fuente":"motor","estado":_MAPA_ESTADO.get(st,"ACTIVA" if st.startswith("EXEC") else "ACTIVA_MUDA"),
                      "estado_crudo":st,"motivo":c.get("reason") or c.get("error"),"alimenta_predictor":bool(c.get("feeds_predictor")),
                      "alimenta_H":bool(c.get("feeds_H")),"can_decide_H":bool(c.get("can_decide_H", False))})
    for r in hub_reg or []:
        filas.append({"pieza":r.get("pieza"),"archivo":r.get("archivo"),"sha256":r.get("sha256"),"fuente":"laterales_unico_v1","estado":r.get("estado"),
                      "rol":r.get("rol"),"motivo":r.get("aporte"),"can_decide_H":False})
    try:
        inv=json.loads((BASE/"INVENTARIO_COMPONENTES_UNICO.json").read_text(encoding="utf-8"))
        for r in inv.get("estaticas") or []: filas.append({**r,"fuente":"inventario_estatico"})
    except Exception as e:
        filas.append({"pieza":"INVENTARIO_COMPONENTES_UNICO.json","fuente":"inventario_estatico","estado":"NO_CORRE","motivo":f"{type(e).__name__}"})
    cnt={}
    for f in filas: cnt[f["estado"]]=cnt.get(f["estado"],0)+1
    return {"conteo":cnt,"filas":filas}

def _convergencia_lateral(features,pred):
    """Qué dijo cada módulo lateral del puente sobre top1 vs top2 (share en [0,1] respecto del máximo del módulo)."""
    cands=[c["family"] for c in (pred.get("candidates") or [])]
    if len(cands)<2: return {"status":"SIN_RIVAL"}
    matrix,log=_bridge_matrix(features,sorted(set(cands)))
    t1,t2=cands[0],cands[1]; filas=[]
    for m,acc in sorted(matrix.items()):
        mx=max(acc.values()) if acc else 0.0
        if mx<=0 or (max(acc.values())-min(acc.values()))<=TIE_EPS: continue
        s1,s2=acc.get(t1,0.0)/mx,acc.get(t2,0.0)/mx
        filas.append({"modulo":m,"share_top1":round(s1,4),"share_top2":round(s2,4),"favorece":"top1" if s1>s2+1e-9 else ("top2" if s2>s1+1e-9 else "empate")})
    cnt={"top1":0,"top2":0,"empate":0}
    for f in filas: cnt[f["favorece"]]+=1
    return {"top1":t1,"top2":t2,"modulos_que_discriminan_entre_top10":len(filas),"conteo":cnt,"por_modulo":filas,
            "nota":"calculado sobre el top10 del predictor; no reordena ni escribe H"}

def _resolver_cierre_operativo_017(result,pred,boards,histories,features,motor,run_ctx=None,modo="018"):
    """PATCH 017: no latencia terminal. Dudas se resuelven dentro de la corrida con tortugas,
    evidencia lateral/arquetípica ya ejecutada y recurrencia entre casos. No usa hechos futuros.
    La incertidumbre se conserva como grado/objeciones; no como estado final LATENTE."""
    cands=[dict(c) for c in (pred.get("candidates") or []) if isinstance(c,dict) and c.get("family")]
    # Recover candidates already emitted by the motor/cuts before declaring an empty ranking.
    known={str(c.get("family")) for c in cands}
    for cut in reversed((motor or {}).get("cuts") or []):
        for row in cut.get("P_top5_ANEXO") or []:
            fam=row[0] if isinstance(row,(list,tuple)) and row else None
            if fam and str(fam) not in known:
                score=float(row[1]) if isinstance(row,(list,tuple)) and len(row)>1 and _is_num(row[1]) else 0.0
                cands.append({"family":str(fam),"rank_fusion":score,"recovered_from_cut":True}); known.add(str(fam))
            if len(cands)>=3: break
        if len(cands)>=3: break
    # If no candidate was produced anywhere, use observable archetype families from the
    # already configured Caldero/LLM result. Do not invent a family or silently use priors.
    cal=(features.get("caldero_busqueda_arquetipos") or {}) if isinstance(features,dict) else {}
    calin=cal.get("caldero_input") or {}
    run_bundle=(run_ctx or {})
    case=(run_bundle.get("case") or {})
    observed_tokens=set()
    for cut in case.get("cuts") or []:
        if not isinstance(cut,dict): continue
        for axis in ("P","A","C"):
            for pair in cut.get(axis) or []:
                tok=pair[0] if isinstance(pair,(list,tuple)) and pair else (pair.get("token") if isinstance(pair,dict) else None)
                if tok and str(tok).strip(): observed_tokens.add(str(tok).strip().casefold())
    # Caldero neighbors can enrich the signature only after lexical noise filtering.
    stopwords={"a","an","and","are","as","at","be","by","for","from","in","is","it","of","on","or","the","this","to","under","vs","whether","with","how","may","can","will","that","these","those","their","they","we","our","you","your"}
    for row in calin.get("tokens_neighbors") or []:
        tok=str(row.get("token") if isinstance(row,dict) else row).strip().casefold()
        if tok and tok not in stopwords and not re.fullmatch(r"(?:19|20)\d{2}",tok) and len(tok)>2:
            observed_tokens.add(tok)
    case_signature=sorted(observed_tokens)
    # Similar resolved cases are a distinct evidence source, matched by token-signature Jaccard.
    gate_ctx0=run_bundle.get("gate_ctx") or {}; box0=gate_ctx0.get("box")
    # Global cross-run index. Exact same input and same case ID are excluded (no self-evidence).
    storage_root=_STINKBOX_STORAGE_ROOT(); index_path=storage_root/"resolved_cases_index.json"
    prior_history=[]
    try:
        if index_path.is_file(): prior_history=list((json.loads(index_path.read_text(encoding="utf-8")).get("cases") or []))
    except Exception: prior_history=[]
    input_fingerprint=hashlib.sha256(json.dumps({"question":case.get("question"),"cuts":case.get("cuts"),"freeze":case.get("freeze"),"z90_date":case.get("z90_date")},sort_keys=True,ensure_ascii=False,default=str).encode("utf-8")).hexdigest()
    sim_votes={str(c.get("family")): {"winner":0,"runner_up":0,"similar_cases":0,"best_similarity":0.0} for c in cands}
    similar_case_ids=set()
    if case_signature:
        current=set(case_signature)
        def _case_root(cid):
            return re.sub(r"_(?:SIN_ULTIMO|RETENIDO|PREFIX|FULL|REPETICION_?\d*|PATCH\d+)(?:_.*)?$", "", str(cid or ""), flags=re.I)
        current_case_id=str(case.get("case_id") or "")
        for row in prior_history:
            prior_id=str(row.get("case_id") or "")
            if prior_id==current_case_id or _case_root(prior_id)==_case_root(current_case_id): continue
            if row.get("input_fingerprint")==input_fingerprint: continue
            sig={str(x).casefold() for x in (row.get("tokens_signature") or []) if str(x).strip()}
            if not sig: continue
            union=current|sig; sim=len(current&sig)/max(1,len(union))
            if sim < 0.20: continue
            similar_case_ids.add(str(row.get("case_id") or "historical_case"))
            fam=str(row.get("winner_family") or row.get("front_id") or "")
            if fam in sim_votes:
                sim_votes[fam]["similar_cases"]+=1; sim_votes[fam]["winner"]+=1
                sim_votes[fam]["best_similarity"]=max(sim_votes[fam]["best_similarity"],sim)
            fam2=str(row.get("runner_up_family") or "")
            if fam2 in sim_votes:
                sim_votes[fam2]["similar_cases"]+=1; sim_votes[fam2]["runner_up"]+=1
                sim_votes[fam2]["best_similarity"]=max(sim_votes[fam2]["best_similarity"],sim)
    llm_hint_scores={}
    # A5_20261107: solo las pistas que pasaron el guardián alimentan el desempate.
    # Antes se leían crudas del caso: una pista con identidad/futuro/calendario
    # podía colarse en apoyo_busqueda_llm_arquetipos aunque el guardián la hubiera
    # descartado para el sidecar. La lista aceptada vive en la auditoría del Caldero;
    # si no existe (salidas viejas), se usa el caso crudo como antes.
    _hints_audit=((cal.get("audit") or {}).get("guardian_pistas_llm") or {})
    _hints_aceptadas=_hints_audit.get("aceptadas_detalle")
    _hints_origen=_hints_aceptadas if isinstance(_hints_aceptadas,list) else (case.get("caldero_llm_neighbor_hints") or [])
    for hint in _hints_origen:
        if not isinstance(hint,dict): continue
        fam=str(hint.get("family") or hint.get("familia") or hint.get("archetype") or hint.get("arquetipo") or "").strip()
        if not fam: continue
        score=hint.get("relevance",hint.get("score",hint.get("match",1.0)))
        try: score=float(score)
        except (TypeError,ValueError): score=1.0
        llm_hint_scores[fam]=max(llm_hint_scores.get(fam,0.0),max(0.0,min(1.0,score)))
    cal_status=cal.get("status") or ("EXECUTED_WITH_SOURCES_NO_LLM_HINTS" if cal.get("caldero_input") and not llm_hint_scores else ("EXECUTED_WITH_LLM_HINTS" if llm_hint_scores else "NOT_AVAILABLE"))
    if not cands:
        families=[]
        for k in ("families_neighbors","families","familias","archetype_candidates"):
            v=calin.get(k) or cal.get(k) or []
            if isinstance(v,dict): families.extend(str(x) for x in v.keys())
            elif isinstance(v,(list,tuple)): families.extend(str(x) for x in v if str(x).strip())
        families.extend(str(x) for x in _build_pre_h_blind_input(result.get("case_input") or {},motor,features).get("families",[]) if str(x).strip()) if isinstance(result.get("case_input"),dict) else None
        for fam in dict.fromkeys(families):
            cands.append({"family":fam,"rank_fusion":0.0,"recovered_from_archetype_search":True})
    if not cands:
        # Last recovery: score the installed dynamic-archetype lexicon against tokens actually
        # observed in this input. No candidate is introduced from a prior or a guessed name.
        observed=set()
        for cut in case.get("cuts") or []:
            if not isinstance(cut,dict): continue
            for axis in ("P","A","C"):
                for pair in cut.get(axis) or []:
                    if isinstance(pair,(list,tuple)) and pair: observed.add(str(pair[0]).strip().casefold())
                    elif isinstance(pair,dict) and pair.get("token"): observed.add(str(pair["token"]).strip().casefold())
        dyn=_load("terminal_dynamic_archetypes", "plugin_arquetipos_dinamicos.py")
        scored=[]
        for fam,spec in ((getattr(dyn,"ARQUETIPOS_DINAMICOS",{}) or {}).items() if dyn else []):
            favor={str(x).casefold() for x in (spec.get("tokens_favor") or {})}
            contra={str(x).casefold() for x in (spec.get("tokens_contra") or {})}
            f_hits=sorted(observed & favor); c_hits=sorted(observed & contra)
            score=len(f_hits)-len(c_hits)
            if f_hits or c_hits: scored.append((fam,score,len(f_hits),len(c_hits),f_hits,c_hits))
        if scored:
            scored.sort(key=lambda z:(-z[1],-z[2],z[3],z[0]))
            for fam,score,fh,ch,f_hits,c_hits in scored[:3]:
                cands.append({"family":fam,"rank_fusion":float(score),"recovered_from_observed_archetype_tokens":True,
                              "observed_favor_hits":f_hits,"observed_contra_hits":c_hits})
    if not cands:
        return {"status":"ERROR_ENTRADA_SIN_EVIDENCIA_CLASIFICABLE","decision":"ENTRADA_NO_CLASIFICABLE","H1":"ENTRADA_NO_CLASIFICABLE","H2":"ENTRADA_NO_CLASIFICABLE",
                "tortugas":"EJECUTADAS_SIN_CANDIDATAS" if boards else "SIN_CORTES_OBSERVABLES",
                "regla":"no existe evidencia observable ni candidatos recuperables; no se fabrica una hipótesis"}
    cands.sort(key=lambda c:(-float(c.get("rank_fusion",0.0)),-int(c.get("seen",0))))
    top=cands[0]; second=cands[1] if len(cands)>1 else None
    ranks=[float(c.get("rank_fusion",0.0)) for c in cands]
    margin=round(ranks[0]-ranks[1],6) if len(ranks)>1 else 0.0
    info=pred.get("information_state") or {}
    guardian=result.get("guardianes") or {}
    route=guardian.get("ruta_cierre_latente") or {}
    closure_guard=result.get("cierre_guardianes") or {}
    strict=result.get("modo_estricto") or {}
    guardian_obj=bool(route.get("guardianes_que_objetan") or route.get("motivos") or closure_guard.get("motivos") or strict.get("motivos"))
    guardian_obj=guardian_obj or str(closure_guard.get("estado_cierre") or "")=="LATENTE" or str(strict.get("estado_cierre_estricto") or "")=="LATENTE"
    needs_tortugas=(info.get("state") not in ("DETERMINADO","RESUELTO_OPERACIONALMENTE") or margin<GATE_SEPARATION or guardian_obj or len(cands)<2 or bool(similar_case_ids))
    tortugas=(result.get("cierre_guardianes") or {}).get("tortugas")
    if modo=="020":
        # CIERRE_020: orden = rank_fusion; tortugas/casos semejantes solo dentro de la banda; pistas LLM ordenan dentro de la banda, tras tortugas/casos semejantes (CABLEADO_CALDERO_20261112).
        cands,tortugas,_banda020=_ordenar_020(cands,pred,boards,histories,features,motor,route,sim_votes,llm_hint_scores,tortugas_prev=tortugas)
        needs_tortugas=bool(_banda020.get("requiere_medicion_tortugas"))
        pred["candidates"]=cands
        pred["terminal_resolution"]={"status":"RESUELTO_OPERACIONALMENTE","method":"MOTOR_RANK_FUSION_DESEMPATA_SOLO_EN_BANDA_020",
            "tortugas_status":(tortugas or {}).get("status","NO_DISPONIBLE"),
            "tortugas_ejecutado":bool((tortugas or {}).get("status")=="EJECUTADO"),
            "tortugas_aplicado_al_orden":bool(_banda020.get("tortugas_aplicado_al_orden")),
            "tortugas_no_reordena_fuera_de_banda":bool(_banda020.get("tortugas_no_reordena_fuera_de_banda")),"banda_020":_banda020,
            "llm_archetype_search_status":cal_status,"llm_neighbor_hints_n":len(llm_hint_scores),"llm_hints_en_orden":False,
            "similar_case_ids_matched":sorted(similar_case_ids),
            "similar_cases_source":"cross-run resolved_cases_index matched by token-signature Jaccard >= 0.20; same-case/prefix variants excluded; no future outcome; solo desempata dentro de banda",
            "rank_fusion_preserved":True,"rank_fusion_is_probability":False,"decide_H":"motor (rank_fusion)","can_decide_H":False}
    elif needs_tortugas and len(cands)>=2:
        if not isinstance(tortugas,dict) or tortugas.get("status")!="EJECUTADO" or not tortugas.get("apoyo_por_candidata"):
            ruta=dict(route)
            ruta.setdefault("guardianes_que_objetan",["RESOLUCION_TERMINAL_017"])
            if not ruta.get("cortes_a_remedir_idx"): ruta["cortes_a_remedir_idx"]=list(range(max(0,len(boards)-1)))
            try: tortugas=_tortugas_guardianes(boards,histories,features,pred,motor,ruta)
            except Exception as exc: tortugas={"status":"ERROR","error":f"{type(exc).__name__}:{exc}","apoyo_por_candidata":{}}
        support=tortugas.get("apoyo_por_candidata") or {}
        hist_count={}
        for hist in histories or []:
            for h in hist or []:
                fam=h.get("familia") if isinstance(h,dict) else None
                if fam: hist_count[str(fam)]=hist_count.get(str(fam),0)+1
        for c in cands:
            fam=str(c["family"]); sup=support.get(fam) or {}
            c["apoyo_tortugas_votos"]=int(sup.get("votos_argmax",0))
            c["apoyo_tortugas_media"]=float(sup.get("evidencia_media",0.0))
            c["soporte_casos_semejantes_observados"]=int(hist_count.get(fam,0))
            c["resoluciones_previas_casos_semejantes"]=int(sim_votes.get(fam,{}).get("winner",0))
            c["casos_semejantes_con_familia_en_H2"]=int(sim_votes.get(fam,{}).get("runner_up",0))
            c["n_casos_semejantes"] = int(sim_votes.get(fam,{}).get("similar_cases",0))
            c["mejor_similitud_casos_previos"] = round(float(sim_votes.get(fam,{}).get("best_similarity",0.0)),6)
            c["apoyo_busqueda_llm_arquetipos"] = float(llm_hint_scores.get(fam,0.0))
        cands.sort(key=lambda c:(-c.get("apoyo_tortugas_votos",0),-c.get("resoluciones_previas_casos_semejantes",0),
                                 -c.get("apoyo_busqueda_llm_arquetipos",0.0),-c.get("apoyo_tortugas_media",0.0),
                                 -c.get("soporte_casos_semejantes_observados",0),-float(c.get("rank_fusion",0.0)),str(c.get("family"))))
        # Preserve the original rank_fusion as a score, while making the final operational
        # order explicitly traceable to tortugas + prior case recurrence.
        for i,c in enumerate(cands,1): c["operational_rank"]=i
        pred["candidates"]=cands
        pred["terminal_resolution"]={"status":"RESUELTO_OPERACIONALMENTE","method":"TORTUGAS_THEN_SIMILAR_CASE_SUPPORT_THEN_RANK_FUSION",
            "tortugas_status":tortugas.get("status","NO_DISPONIBLE"),"support_used":bool(support),
            "llm_archetype_search_status":cal_status,"llm_neighbor_hints_n":len(llm_hint_scores),
            "similar_case_ids_matched":sorted(similar_case_ids),
            "similar_cases_source":"cross-run resolved_cases_index matched by token-signature Jaccard >= 0.20; same-case/prefix variants excluded; no future outcome",
            "rank_fusion_preserved":True,"rank_fusion_is_probability":False,"can_decide_H":True}
    else:
        for i,c in enumerate(cands,1): c["operational_rank"]=i
        pred["candidates"]=cands
        pred["terminal_resolution"]={"status":"RESUELTO_OPERACIONALMENTE","method":"RANK_FUSION_WITH_AVAILABLE_EVIDENCE",
            "tortugas_status":"NO_REQUERIDO_POR_CRITERIOS_DE_CIERRE","llm_archetype_search_status":cal_status,"llm_neighbor_hints_n":len(llm_hint_scores),
            "similar_case_ids_matched":sorted(similar_case_ids),
            "similar_cases_source":"cross-run resolved_cases_index matched by token-signature Jaccard >= 0.20; same-case/prefix variants excluded; no future outcome","rank_fusion_preserved":True,"rank_fusion_is_probability":False,"can_decide_H":True}
    top=cands[0]; second=cands[1] if len(cands)>1 else None
    # Final state never inherits the during-run latency state.
    decision={"status":"RESUELTO_OPERACIONALMENTE","H1":top["family"],"H2":second["family"] if second else top["family"],
        "metodo":pred["terminal_resolution"]["method"],"grado":("SE_GRADUA_EN_CIERRE_FINAL_020" if modo=="020" else ("AJUSTADA" if needs_tortugas else "FIRME")),
        "estado_durante_corrida":("RESOLUCION_REQUERIDA" if info.get("state") not in ("DETERMINADO","RESUELTO_OPERACIONALMENTE") else "EVIDENCIA_SEPARADA"),
        "tortugas_ejecutado":bool((tortugas or {}).get("status")=="EJECUTADO" or ((result.get("cierre_guardianes") or {}).get("tortugas") or {}).get("status")=="EJECUTADO"),
        "tortugas_aplicado_al_orden":bool((pred.get("terminal_resolution") or {}).get("tortugas_aplicado_al_orden")),
        "tortugas_no_reordena_fuera_de_banda":bool((pred.get("terminal_resolution") or {}).get("tortugas_no_reordena_fuera_de_banda")),
        "arquetipos_busqueda_status":cal_status,"llm_neighbor_hints_n":len(llm_hint_scores),
        "casos_semejantes_consultados":len(similar_case_ids),
        "nota":"la incertidumbre se conserva en grado/objeciones; el estado terminal es una decisión operacional, no verdad validada"}
    # Close active hypothesis fronts at the end of every run. Historical evidence remains in
    # resolved_front_history; only discovered tokens/neighbors remain cross-run learning material.
    gate_ctx=(run_ctx or {}).get("gate_ctx") or {}
    box=gate_ctx.get("box")
    closed_fronts=[]
    if box is not None:
        try:
            box.data=box._load_or_create()
            prior=list(box.pendientes_vivos())
            for front in prior:
                fid=str(front.get("front_id"))
                matching=next((c for c in cands if str(c.get("family"))==fid),None)
                closed_fronts.append({"front_id":fid,"estado":"RESUELTO_OPERACIONALMENTE",
                    "decision":"SELECCIONADO" if fid==decision["H1"] else ("RIVAL_RETENIDO_EN_H2" if fid==decision["H2"] else "DESCARTADO_POR_RESOLUCION_TERMINAL"),
                    "rank_fusion_observado":float(matching.get("rank_fusion",0.0)) if matching else 0.0,
                    "metodo":decision["metodo"],"cut_id":gate_ctx.get("cut_id"),"case_id":str(case.get("case_id") or ""),
                    "tokens_signature":case_signature[:120]})
            # Store the actual resolution pair for later same-situation retrieval.
            already={(str(x.get("case_id")),str(x.get("front_id"))) for x in box.data.get("resolved_front_history") or []}
            for fam,decision_label in ((decision["H1"],"SELECCIONADO"),(decision["H2"],"RIVAL_RETENIDO_EN_H2")):
                key=(str(case.get("case_id") or ""),str(fam))
                if key in already: continue
                matching=next((c for c in cands if str(c.get("family"))==str(fam)),None)
                closed_fronts.append({"front_id":str(fam),"estado":"RESUELTO_OPERACIONALMENTE","decision":decision_label,
                    "rank_fusion_observado":float(matching.get("rank_fusion",0.0)) if matching else 0.0,
                    "metodo":decision["metodo"],"cut_id":gate_ctx.get("cut_id"),"case_id":str(case.get("case_id") or ""),
                    "tokens_signature":case_signature[:120]})
            if closed_fronts:
                box.data.setdefault("resolved_front_history",[]).extend(closed_fronts)
            box.data["pendientes_vivos"]=[]
            box._touch(); box._save()
        except Exception as exc:
            result["cierre_memoria_operativa"]={"status":"ERROR","error":f"{type(exc).__name__}:{exc}","fronts_closed":0}
    result["cierre_memoria_operativa"]={"status":"EJECUTADO","history_entries_written":len(closed_fronts),
        "active_hypothesis_fronts_remaining":0 if box is not None else "NO_STORE_DISPONIBLE",
        "history":"resolved_front_history","cross_run_pending_allowed":"solo_tokens_descubiertos_y_vecinos_caldero"}
    # Global, idempotent cross-case outcome index: stores only resolved H1/H2 + token signature.
    try:
        storage_root.mkdir(parents=True,exist_ok=True)
        if index_path.is_file():
            try: idx=json.loads(index_path.read_text(encoding="utf-8"))
            except Exception: idx={"version":"RESOLVED_CASES_INDEX_V1","cases":[]}
        else: idx={"version":"RESOLVED_CASES_INDEX_V1","cases":[]}
        rows=list(idx.get("cases") or [])
        rows=[r for r in rows if not (str(r.get("case_id") or "")==str(case.get("case_id") or "") and r.get("input_fingerprint")==input_fingerprint)]
        rows.append({"case_id":str(case.get("case_id") or ""),"input_fingerprint":input_fingerprint,
            "winner_family":decision["H1"],"runner_up_family":decision["H2"],"method":decision["metodo"],
            "tokens_signature":case_signature[:120],"tokens_signature_n":len(case_signature),"similar_cases_used":sorted(similar_case_ids),
            "future_outcome_used":False,"resolved_operationally":True})
        idx.update({"version":"RESOLVED_CASES_INDEX_V1","cases":rows})
        tmp=index_path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(idx,ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8"); tmp.replace(index_path)
        result["cierre_memoria_operativa"]["cross_run_index"]="PERSISTIDO"
        result["cierre_memoria_operativa"]["resolved_cases_index_count"]=len(rows)
    except Exception as exc:
        result["cierre_memoria_operativa"]["cross_run_index"]="ERROR"
        result["cierre_memoria_operativa"]["cross_run_index_error"]=f"{type(exc).__name__}:{exc}"
    result["resolucion_operativa_final"]=decision
    result["H1"]={"family":decision["H1"],"rank_fusion":float(top.get("rank_fusion",0.0)),"grado":decision["grado"],"metodo_cierre":decision["metodo"]}
    result["H2"]={"family":decision["H2"],"rank_fusion":float(second.get("rank_fusion",top.get("rank_fusion",0.0))) if second else float(top.get("rank_fusion",0.0)),"grado":decision["grado"],"metodo_cierre":decision["metodo"]}
    result["predictor"]=pred
    if isinstance(result.get("apuesta"),dict):
        result["apuesta"]["familia_apostada"]=decision["H1"]; result["apuesta"]["frente_a"]=decision["H2"]
        result["apuesta"]["grado_operativo"]=decision["grado"]; result["apuesta"]["metodo_cierre"]=decision["metodo"]
        _ramas={r.get("family"):r for r in (result["apuesta"].get("ramas") or []) if isinstance(r,dict)}
        for _dest,_fam,_field in (("proyeccion_H1",decision["H1"],"proyeccion"),("proyeccion_H2",decision["H2"],"proyeccion"),
                                  ("serie_H1_hasta_Z",decision["H1"],"serie_hasta_Z"),("serie_H2_hasta_Z",decision["H2"],"serie_hasta_Z")):
            _branch=_ramas.get(_fam) or {}
            if _field in _branch: result["apuesta"][_dest]=_branch[_field]
            else: result["apuesta"].pop(_dest,None)
    return {"status":"RESUELTO_OPERACIONALMENTE","H1":decision["H1"],"H2":decision["H2"],"decision":decision,
            "tortugas":tortugas if needs_tortugas else {"status":"NO_REQUERIDO"},"candidates":cands}


# ======================================================================================
# CIERRE_020 (2026-10-11, decisión Mj 15:17 CT): EL MOTOR MANDA EN H.
#  - Orden de H = puntaje propio del motor (rank_fusion). Tortugas y casos semejantes SOLO desempatan
#    dentro de la banda de indistinción del motor (casi igualdad); nunca contra una ventaja clara.
#  - Banda (en puntos de rank_fusion): delta = min(GATE_SEPARATION, max(EPS_ACERO, 2/(N-1))), N = candidatas
#    que entraron a la fusión. 2/(N-1) = cambio mínimo de la diferencia entre dos candidatas cuando se
#    invierte UN par adyacente en UNA dimensión (rango fraccional 1-avg/(N-1)); EPS_ACERO = 0.25 = banda
#    NO_RESUELTO del hombre de acero; GATE_SEPARATION = 1.0 = 'separado' del motor (tope: una ventaja >=1.0
#    nunca se toca).
#  - Pistas LLM de arquetipos (case.caldero_llm_neighbor_hints): fuera del orden; solo traza lateral.
#  - Pesos relativos: rank_fusion_i / suma(rank_fusion) sobre las candidatas publicadas (= indice_fusion_relativo
#    de PATCH02 renormalizado a suma 1). Conserva el orden; no es probabilidad (sin calibración con desenlaces).
#  - Mezcla H1/H2: afinidad con datos del motor (evidencia propia, catálogo, co-activación por corte, series,
#    puente 244↔familias de tokens).
# ======================================================================================
EPS_ACERO_020 = 0.25          # = guardian_acero_rival_v1.EPS / modo_estricto_v1.EPS_ACERO
UMBRAL_AFINIDAD_020 = 0.5     # mayoría simple de la evidencia/estructura compartida
VERSION_CIERRE_020 = "CIERRE_FINAL_020_MOTOR_MANDA_ESCALA_MEZCLA_20261011"

def _banda_020(pred, cands):
    ent = ((pred.get("calibracion_estructural") or {}).get("entropia") or {})
    n_fus = ent.get("n_candidatos") if isinstance(ent.get("n_candidatos"), int) else len(cands)
    n_fus = max(int(n_fus or 0), len(cands))
    cuanto = (2.0 / (n_fus - 1)) if n_fus > 1 else GATE_SEPARATION
    delta = min(GATE_SEPARATION, max(EPS_ACERO_020, cuanto))
    return {"delta_rank_fusion": round(delta, 6), "n_candidatas_en_fusion": n_fus,
            "cuanto_un_par_adyacente_una_dimension": round(cuanto, 6), "eps_acero": EPS_ACERO_020,
            "tope_gate_separation": GATE_SEPARATION,
            "regla": "delta = min(GATE_SEPARATION, max(EPS_ACERO, 2/(N-1))); grupo = candidatas a menos de delta de la primera del grupo (orden rank_fusion)"}

def _grupos_banda_020(cands, delta):
    grupos = []; i = 0
    while i < len(cands):
        lider = float(cands[i].get("rank_fusion", 0.0)); j = i + 1
        while j < len(cands) and (lider - float(cands[j].get("rank_fusion", 0.0))) < delta - 1e-12:
            j += 1
        grupos.append(list(range(i, j))); i = j
    return grupos

def _clave_desempate_020(c):
    # CABLEADO_CALDERO_20261112 (3): el puntaje de pista LLM entra al orden
    # DENTRO de la banda, tras tortugas/casos semejantes y antes de rank_fusion.
    # Solo reordena dentro del grupo de banda (eso lo garantiza _ordenar_020);
    # nunca fuera de ella, y no cambia el default del modo.
    return (-int(c.get("apoyo_tortugas_votos", 0)), -int(c.get("resoluciones_previas_casos_semejantes", 0)),
            -round(float(c.get("apoyo_tortugas_media", 0.0)), 6), -round(float(c.get("pista_llm_arquetipos_traza", 0.0)), 6),
            -float(c.get("rank_fusion", 0.0)), str(c.get("family")))

def _ordenar_020(cands, pred, boards, histories, features, motor, route, sim_votes, llm_hint_scores, tortugas_prev=None):
    """Devuelve (cands_ordenadas, tortugas, banda_info). Solo reordena DENTRO de cada grupo de banda."""
    cands = sorted(cands, key=lambda c: (-float(c.get("rank_fusion", 0.0)), str(c.get("family"))))
    banda = _banda_020(pred, cands)
    grupos = _grupos_banda_020(cands, banda["delta_rank_fusion"])
    hay_banda = any(len(g) >= 2 for g in grupos)
    margen_h1_h2 = (float(cands[0].get("rank_fusion", 0.0)) - float(cands[1].get("rank_fusion", 0.0))) if len(cands) >= 2 else GATE_SEPARATION
    # TORTUGAS must run whenever H1/H2 have not reached the motor's separation gate,
    # even if the narrower 020 tie band will forbid changing their order. A prior
    # guardian measurement is reused; the terminal order still obeys the band.
    requiere_medicion_tortugas = bool(len(cands) >= 2 and (hay_banda or margen_h1_h2 < GATE_SEPARATION))
    tortugas = {"status": "NO_REQUERIDO_SIN_CASI_IGUALDAD"}
    support = {}
    if requiere_medicion_tortugas:
        tortugas = None
        if isinstance(tortugas_prev, dict) and tortugas_prev.get("status") == "EJECUTADO" and tortugas_prev.get("apoyo_por_candidata"):
            tortugas = tortugas_prev
        else:
          try:
            ruta = dict(route or {})
            ruta.setdefault("guardianes_que_objetan", ["CIERRE_020_SEPARACION_INSUFICIENTE"])
            if not ruta.get("cortes_a_remedir_idx"): ruta["cortes_a_remedir_idx"] = list(range(max(0, len(boards) - 1)))
            tortugas = _tortugas_guardianes(boards, histories, features, pred, motor, ruta)
          except Exception as exc:
            tortugas = {"status": "ERROR", "error": f"{type(exc).__name__}:{exc}", "apoyo_por_candidata": {}}
        support = (tortugas or {}).get("apoyo_por_candidata") or {}
    hist_count = {}
    for hist in histories or []:
        for h in hist or []:
            fam = h.get("familia") if isinstance(h, dict) else None
            if fam: hist_count[str(fam)] = hist_count.get(str(fam), 0) + 1
    for c in cands:
        fam = str(c["family"]); sup = support.get(fam) or {}
        c["apoyo_tortugas_votos"] = int(sup.get("votos_argmax", 0))
        c["apoyo_tortugas_media"] = float(sup.get("evidencia_media", 0.0))
        c["soporte_casos_semejantes_observados"] = int(hist_count.get(fam, 0))
        c["resoluciones_previas_casos_semejantes"] = int(sim_votes.get(fam, {}).get("winner", 0))
        c["casos_semejantes_con_familia_en_H2"] = int(sim_votes.get(fam, {}).get("runner_up", 0))
        c["n_casos_semejantes"] = int(sim_votes.get(fam, {}).get("similar_cases", 0))
        c["mejor_similitud_casos_previos"] = round(float(sim_votes.get(fam, {}).get("best_similarity", 0.0)), 6)
        c["pista_llm_arquetipos_traza"] = float(llm_hint_scores.get(fam, 0.0))   # traza lateral; entra al orden SOLO dentro de la banda 020 (ver _clave_desempate_020)
    nuevo = []; registro = []
    for g in grupos:
        miembros = [cands[k] for k in g]
        if len(miembros) >= 2:
            orden = sorted(miembros, key=_clave_desempate_020)
            antes = [m["family"] for m in miembros]; despues = [m["family"] for m in orden]
            decidio = "rank_fusion (tortugas y casos semejantes no discriminan)" if despues == antes else "ver cambios_por_posicion"
            cambios = []
            for pos, (a, b) in enumerate(zip(orden, miembros)):
                if a["family"] == b["family"]: continue
                if a.get("apoyo_tortugas_votos", 0) != b.get("apoyo_tortugas_votos", 0): por = "tortugas_votos_argmax"
                elif a.get("resoluciones_previas_casos_semejantes", 0) != b.get("resoluciones_previas_casos_semejantes", 0): por = "casos_semejantes_resoluciones_previas"
                elif round(a.get("apoyo_tortugas_media", 0.0), 6) != round(b.get("apoyo_tortugas_media", 0.0), 6): por = "tortugas_evidencia_media"
                elif round(a.get("pista_llm_arquetipos_traza", 0.0), 6) != round(b.get("pista_llm_arquetipos_traza", 0.0), 6): por = "pista_llm_arquetipos"
                else: por = "rank_fusion"
                cambios.append({"posicion_operativa": g[0] + pos + 1, "entra": a["family"], "en_lugar_de": b["family"], "por": por,
                                "valores_entra": [a.get("apoyo_tortugas_votos"), a.get("resoluciones_previas_casos_semejantes"), round(a.get("apoyo_tortugas_media", 0.0), 6), round(a.get("pista_llm_arquetipos_traza", 0.0), 6), a.get("rank_fusion")],
                                "valores_en_lugar_de": [b.get("apoyo_tortugas_votos"), b.get("resoluciones_previas_casos_semejantes"), round(b.get("apoyo_tortugas_media", 0.0), 6), round(b.get("pista_llm_arquetipos_traza", 0.0), 6), b.get("rank_fusion")]})
            registro.append({"posiciones_rank_fusion": [k + 1 for k in g], "miembros_orden_rank_fusion": antes,
                             "rank_fusion": [m.get("rank_fusion") for m in miembros],
                             "distancia_al_lider": [round(float(miembros[0]["rank_fusion"]) - float(m["rank_fusion"]), 6) for m in miembros],
                             "tortugas_votos": [m.get("apoyo_tortugas_votos") for m in miembros],
                             "tortugas_media": [round(m.get("apoyo_tortugas_media", 0.0), 6) for m in miembros],
                             "casos_semejantes_resoluciones_previas": [m.get("resoluciones_previas_casos_semejantes") for m in miembros],
                             "orden_final": despues, "orden_cambio": despues != antes, "decidio": decidio, "cambios_por_posicion": cambios,
                             "toca_H1": 0 in g, "toca_H2": (1 in g) or (0 in g and len(g) >= 2)})
            nuevo.extend(orden)
        else:
            nuevo.extend(miembros)
    for i, c in enumerate(nuevo, 1):
        c["operational_rank"] = i
    banda.update({"grupos_casi_igualdad": registro, "hay_casi_igualdad": hay_banda,
                  "margen_rank_fusion_H1_H2": round(margen_h1_h2, 6),
                  "requiere_medicion_tortugas": requiere_medicion_tortugas,
                  "tortugas_ejecutado": bool((tortugas or {}).get("status") == "EJECUTADO"),
                  "tortugas_aplicado_al_orden": bool(hay_banda and support),
                  "tortugas_no_reordena_fuera_de_banda": bool(requiere_medicion_tortugas and not hay_banda),
                  "H1_en_banda": bool(grupos and len(grupos[0]) >= 2),
                  "H1_cambiado_por_desempate": bool(nuevo and cands and nuevo[0]["family"] != cands[0]["family"]),
                  "H2_cambiado_por_desempate": bool(len(nuevo) > 1 and len(cands) > 1 and nuevo[1]["family"] != cands[1]["family"]),
                  "clave_desempate": "tortugas votos_argmax > resoluciones previas de casos semejantes > tortugas evidencia_media > pista_llm_arquetipos > rank_fusion > nombre",
                  "pistas_llm_en_orden": True})
    return nuevo, tortugas, banda

def _pesos_020(cands):
    vals = [max(0.0, float(c.get("rank_fusion", 0.0))) for c in cands]
    tot = sum(vals)
    if not cands or tot <= 0:
        return {"status": "NO_CALCULABLE_SUMA_CERO", "pesos": []}
    def _lr(nd):  # resto mayor: suma exacta 1 a nd decimales (determinista: empates de resto por rank_fusion desc, nombre)
        u = 10 ** nd; raw = [v / tot * u for v in vals]; base = [math.floor(x) for x in raw]
        falta = u - sum(base)
        orden = sorted(range(len(vals)), key=lambda i: (-(raw[i] - base[i]), -vals[i], str(cands[i].get("family"))))
        for i in orden[:falta]: base[i] += 1
        return [b / u for b in base]
    for nd in (6, 8, 10, 12):
        pesos = [round(x, nd) for x in _lr(nd)]
        ok = all(((vals[i] > vals[j]) == (pesos[i] > pesos[j])) and ((vals[i] == vals[j]) == (pesos[i] == pesos[j])) for i in range(len(vals)) for j in range(len(vals)))
        if ok: break
    return {"status": "CALCULADO", "decimales": nd, "suma_rank_fusion": round(tot, 6), "n": len(cands),
            "suma_pesos": round(sum(pesos), nd), "sin_igualdades_creadas_por_normalizacion": ok, "orden_identico_a_rank_fusion": ok,
            "metodo_redondeo": "resto mayor a 'decimales' (suma exacta 1); se suben decimales si el redondeo igualara o invirtiera dos candidatas",
            "pesos": [{"familia": c["family"], "rank_fusion": c.get("rank_fusion"), "peso_relativo": p,
                       "operational_rank": c.get("operational_rank")} for c, p in zip(cands, pesos)]}

def _afinidad_020(result, pred, h1, h2):
    def jac(a, b):
        a, b = set(a), set(b); u = a | b
        return round(len(a & b) / len(u), 6) if u else 0.0
    comp = {}
    oe = pred.get("own_evidence") or {}
    f1 = (oe.get(h1) or {}).get("favor_tokens") or []; f2 = (oe.get(h2) or {}).get("favor_tokens") or []
    comp["evidencia_propia_en_caso"] = {"tokens_H1": sorted(f1), "tokens_H2": sorted(f2), "compartidos": sorted(set(f1) & set(f2)),
                                        "jaccard": jac(f1, f2), "disponible": bool(f1 or f2)}
    pats = _patterns() if isinstance(_patterns(), dict) else {}
    p1 = pats.get(h1) or {}; p2 = pats.get(h2) or {}
    c1f = set((p1.get("tokens_favor") or {}).keys()); c2f = set((p2.get("tokens_favor") or {}).keys())
    c1c = set((p1.get("tokens_contra") or {}).keys()); c2c = set((p2.get("tokens_contra") or {}).keys())
    comp["catalogo_244"] = {"favor_compartidos": sorted(c1f & c2f), "jaccard_favor": jac(c1f, c2f),
                            "oposicion_favor_H1_en_contra_H2": sorted(c1f & c2c), "oposicion_favor_H2_en_contra_H1": sorted(c2f & c1c),
                            "disponible": bool(p1 and p2)}
    cuts = (result.get("motor") or {}).get("cuts") or []
    both = either = 0; top5_both = 0
    for c in cuts:
        fams = {x.get("familia") for x in (c.get("P_candidatos_0a3") or []) if isinstance(x, dict)}
        t5 = {r[0] for r in (c.get("P_top5_ANEXO") or []) if isinstance(r, (list, tuple)) and r}
        if h1 in fams and h2 in fams: both += 1
        if h1 in fams or h2 in fams: either += 1
        if h1 in t5 and h2 in t5: top5_both += 1
    comp["coactivacion_cortes"] = {"cortes": len(cuts), "ambas_en_P_candidatos_0a3": both, "alguna": either,
                                   "indice": round(both / either, 6) if either else 0.0, "ambas_en_P_top5": top5_both,
                                   "disponible": bool(cuts)}
    ramas = {r.get("family"): r for r in ((result.get("apuesta") or {}).get("ramas") or []) if isinstance(r, dict)}
    s1 = (ramas.get(h1) or {}).get("serie_hasta_Z") or []; s2 = (ramas.get(h2) or {}).get("serie_hasta_Z") or []
    r_val = "NO_DISPONIBLE"
    if len(s1) == len(s2) and len(s1) >= 3:
        m1 = sum(s1) / len(s1); m2 = sum(s2) / len(s2)
        num = sum((a - m1) * (b - m2) for a, b in zip(s1, s2))
        den = math.sqrt(sum((a - m1) ** 2 for a in s1) * sum((b - m2) ** 2 for b in s2))
        r_val = round(num / den, 6) if den > 0 else "SERIE_CONSTANTE"
    comp["comovimiento_series_hasta_Z"] = {"pearson": r_val, "n": len(s1), "disponible": isinstance(r_val, float)}
    try:
        pu = json.loads((BASE / "PUENTE_244_FAMILIAS.json").read_text(encoding="utf-8"))
        t1 = {}; t2 = {}
        for t in pu.get("tokens") or []:
            pl = set(t.get("patrones_por_palabra_alta_media") or []) | set(t.get("patrones_explicitos") or [])
            key = f'{t.get("familia")}:{t.get("token")}'
            if h1 in pl: t1[key] = t
            if h2 in pl: t2[key] = t
        sh = sorted(set(t1) & set(t2))
        dins = sorted({str(t1[k].get("dinamica")) for k in sh})
        comp["puente_familias_tokens"] = {"tokens_H1": len(t1), "tokens_H2": len(t2), "compartidos": len(sh),
                                          "jaccard": jac(t1, t2), "familias_compartidas": sorted({k.split(":")[0] for k in sh}),
                                          "dinamicas_compartidas": dins, "muestra": sh[:12], "disponible": bool(t1 or t2)}
    except Exception as exc:
        comp["puente_familias_tokens"] = {"disponible": False, "error": type(exc).__name__}
    partes = []
    for k, campo in (("evidencia_propia_en_caso", "jaccard"), ("catalogo_244", "jaccard_favor"), ("coactivacion_cortes", "indice"), ("puente_familias_tokens", "jaccard")):
        if comp.get(k, {}).get("disponible"): partes.append(float(comp[k][campo]))
    if comp["comovimiento_series_hasta_Z"]["disponible"]: partes.append(max(0.0, float(r_val)))
    comp["afinidad_compuesta"] = round(sum(partes) / len(partes), 6) if partes else 0.0
    comp["n_componentes_afinidad"] = len(partes)
    comp["regla_afinidad"] = "promedio simple de los componentes disponibles en [0,1] (Jaccard evidencia propia, Jaccard catálogo favor, co-activación por corte, Jaccard puente 244-familias, max(0, Pearson series)); sin pesos nuevos"
    return comp

def _cierre_final_020(result, pred, run_ctx=None):
    cf = _cierre_final_016(result, pred, run_ctx)        # objeciones, acero, frentes, tokens latentes (misma lógica)
    cands = list(pred.get("candidates") or [])
    tr = pred.get("terminal_resolution") or {}
    banda = tr.get("banda_020") or _banda_020(pred, cands)
    rf_order = sorted(cands, key=lambda c: (-float(c.get("rank_fusion", 0.0)), str(c.get("family"))))
    H1 = cf.get("H1"); H2 = cf.get("H2")
    rf = {c["family"]: float(c.get("rank_fusion", 0.0)) for c in cands}
    margen_rf_top = round(float(rf_order[0]["rank_fusion"]) - float(rf_order[1]["rank_fusion"]), 6) if len(rf_order) > 1 else 0.0
    margen_H = round(rf.get(H1, 0.0) - rf.get(H2, 0.0), 6) if (H1 in rf and H2 in rf) else 0.0
    pesos = _pesos_020(cands)
    pmap = {p["familia"]: p["peso_relativo"] for p in pesos.get("pesos") or []}
    delta = float(banda["delta_rank_fusion"]); suma = float(pesos.get("suma_rank_fusion") or 1.0)
    separado = margen_rf_top >= GATE_SEPARATION
    h1_en_banda = bool(banda.get("H1_en_banda"))
    acero = cf.get("prueba_acero") or {}
    acero_aplica = bool(rf_order) and H1 == rf_order[0]["family"]
    fuerte = list((cf.get("criterios_grado") or {}).get("senales_contrarias_fuertes") or [])
    objec = cf.get("objeciones") or []
    if not cands: grado = "AJUSTADA"
    elif h1_en_banda: grado = "FRAGIL"
    elif separado and acero_aplica and acero.get("descarta_rival") and not objec: grado = "FIRME"
    elif (not separado) and fuerte: grado = "FRAGIL"
    else: grado = "AJUSTADA"
    afin = _afinidad_020(result, pred, H1, H2) if (H1 and H2 and H1 != H2) else {"afinidad_compuesta": 0.0, "n_componentes_afinidad": 0}
    s1 = pmap.get(H1, 0.0); s2 = pmap.get(H2, 0.0)
    g1 = next((g for g in (banda.get("grupos_casi_igualdad") or []) if g.get("toca_H1")), {})
    miembros_b = list(g1.get("orden_final") or [H1, H2])
    if h1_en_banda:
        lectura = "MEZCLA_H1_H2_SIN_SEPARACION"
        texto = (f"{H1} y {H2} en mezcla: diferencia top1-top2 {margen_rf_top} < banda {delta} (indistinguibles a la resolución del motor)"
                 + (f"; también en la banda: {', '.join(m for m in miembros_b if m not in (H1, H2))}" if len(miembros_b) > 2 else ""))
    elif (not separado) or float(afin.get("afinidad_compuesta", 0.0)) >= UMBRAL_AFINIDAD_020:
        lectura = "H1_CON_COMPONENTES_DE_H2"
        porque = []
        if not separado: porque.append(f"margen {margen_rf_top} < GATE_SEPARATION {GATE_SEPARATION}")
        if float(afin.get("afinidad_compuesta", 0.0)) >= UMBRAL_AFINIDAD_020: porque.append(f"afinidad {afin.get('afinidad_compuesta')} >= {UMBRAL_AFINIDAD_020}")
        texto = f"{H1} con componentes de {H2} (" + "; ".join(porque) + ")"
    else: lectura = "H1_DOMINANTE"; texto = f"{H1} domina; {H2} es rival distinto (margen {margen_rf_top} >= {GATE_SEPARATION} y afinidad {afin.get('afinidad_compuesta')} < {UMBRAL_AFINIDAD_020})"
    top3 = cands[:3]; t3s = sum(max(0.0, float(c.get("rank_fusion", 0.0))) for c in top3) or 1.0
    mezcla = {"lectura": lectura, "lectura_texto": texto, "miembros_banda_H1": miembros_b if h1_en_banda else [H1],
              "top": [{"familia": c["family"], "operational_rank": c.get("operational_rank"), "peso_relativo": pmap.get(c["family"]),
                       "peso_en_top3": round(float(c.get("rank_fusion", 0.0)) / t3s, 6), "rank_fusion": c.get("rank_fusion")} for c in top3],
              "peso_H1": s1, "peso_H2": s2, "razon_H2_sobre_H1": round(s2 / s1, 6) if s1 else 0.0,
              "peso_H1_en_par": round(s1 / (s1 + s2), 6) if (s1 + s2) else 0.0, "peso_H2_en_par": round(s2 / (s1 + s2), 6) if (s1 + s2) else 0.0,
              "afinidad_H1_H2": afin, "umbral_afinidad": UMBRAL_AFINIDAD_020,
              "regla": "MEZCLA_H1_H2_SIN_SEPARACION si H1 cae en banda; H1_CON_COMPONENTES_DE_H2 si margen < GATE_SEPARATION o afinidad >= 0.5; H1_DOMINANTE en otro caso",
              "can_decide_H": False}
    ap = dict(cf.get("apuesta") or {})
    ap["margen"] = margen_H; ap["grado"] = grado
    ap["regla"] = "apuesta = H1 (orden del motor: rank_fusion; desempata solo en banda) frente a H2; con mezcla, apuesta compuesta con pesos del par"
    if lectura != "H1_DOMINANTE":
        ap["apuesta_compuesta"] = {"lectura": lectura, "texto": texto,
                                   "componentes": [{"familia": H1, "peso_en_par": mezcla["peso_H1_en_par"]}, {"familia": H2, "peso_en_par": mezcla["peso_H2_en_par"]}],
                                   "nota": "se apuesta a la trayectoria H1 con la componente H2 activa; proyecciones de ambas ramas abajo (ya calculadas por el motor)"}
    else:
        ap["apuesta_compuesta"] = {"lectura": "H1_DOMINANTE", "texto": texto}
    cf.update({"version": VERSION_CIERRE_020, "margen": margen_H, "margen_rank_fusion_top1_top2": margen_rf_top,
               "margen_en_unidades_de_banda": round(margen_rf_top / delta, 6) if delta else 0.0,
               "diferencia_pesos_H1_H2": round(s1 - s2, 8), "grado": grado, "apuesta": apuesta_ok(ap),
               "pesos_relativos": {**pesos, "nombre": "peso relativo (proporción de rank_fusion sobre las candidatas publicadas)",
                                   "es_probabilidad": False, "calibrado_con_desenlaces": False,
                                   "equivale_a": "indice_fusion_relativo_0_1 (PATCH02, rank_fusion/techo) renormalizado a suma 1",
                                   "nota": "conserva el orden de rank_fusion; no es probabilidad: no hay desenlaces sellados por caso (predictive_validation NOT_CALIBRATED)"},
               "banda_casi_igualdad": banda, "mezcla": mezcla,
               "criterios_grado": {"separacion": GATE_SEPARATION, "margen_separado": separado, "banda_delta": delta,
                                   "banda_delta_en_peso": round(delta / suma, 8), "H1_en_banda": h1_en_banda,
                                   "acero_aplica_a_H1": acero_aplica, "acero_descarta_rival": bool(acero.get("descarta_rival")),
                                   "senales_contrarias_fuertes": fuerte, "n_objeciones": len(objec),
                                   "regla": "FRAGIL si H1 en banda (margen top1-top2 < delta) o (no separado y señal contraria fuerte); FIRME si separado (margen >= 1.0 = peso >= 1.0/suma) + acero del rival más fuerte SOBREVIVE sobre este mismo H1 + 0 objeciones; AJUSTADA el resto"},
               "fuente_H": "orden del motor (rank_fusion); tortugas/casos semejantes solo dentro de la banda de casi igualdad; pistas LLM fuera del orden",
               "pistas_llm_arquetipos": {"n": tr.get("llm_neighbor_hints_n", 0), "entran_al_orden": False, "can_decide_H": False,
                                        "uso": "traza lateral/contexto; el LLM aporta por enriquecimiento de entrada (consulta_dirigida) y traducción"},
               "guardianes_y_estricto": "gradúan la confianza y adjuntan objeciones; no bloquean ni reordenan H",
               "can_decide_H": False, "reordena": bool(banda.get("H1_cambiado_por_desempate") or banda.get("H2_cambiado_por_desempate")),
               "reordena_fuera_de_banda": False,
               "metodo_resolucion_operativa": tr.get("method", "MOTOR_RANK_FUSION_DESEMPATA_SOLO_EN_BANDA_020")})
    return cf

def apuesta_ok(ap):
    return {k: v for k, v in ap.items() if v is not None}

def _aplicar_cierre_final_020(result, pred, cf):
    _aplicar_cierre_final_016(result, pred, cf)
    pm = {p["familia"]: p["peso_relativo"] for p in ((cf.get("pesos_relativos") or {}).get("pesos") or [])}
    for k in ("H1", "H2"):
        if isinstance(result.get(k), dict):
            result[k]["fuente_020"] = "orden del motor (rank_fusion); tortugas/casos semejantes desempatan solo en banda"
            result[k]["peso_relativo"] = pm.get(result[k].get("family"))
            result[k].pop("fuente_018", None)
    rof = result.get("resolucion_operativa_final")
    if isinstance(rof, dict): rof["grado"] = cf.get("grado")
    ap = result.get("apuesta")
    if isinstance(ap, dict):
        ap["grado_operativo"] = cf.get("grado")
        ap["apuesta_final_016"]["apuesta_compuesta"] = (cf.get("apuesta") or {}).get("apuesta_compuesta")
        ap["mezcla_020"] = {k: (cf.get("mezcla") or {}).get(k) for k in ("lectura", "lectura_texto", "peso_H1_en_par", "peso_H2_en_par")}
    rc = result.get("reporte_caso")
    if isinstance(rc, dict) and isinstance(rc.get("cierre_final"), dict):
        rc["cierre_final"]["mezcla"] = (cf.get("mezcla") or {}).get("lectura")
        rc["cierre_final"]["pesos_H1_H2"] = [(cf.get("mezcla") or {}).get("peso_H1"), (cf.get("mezcla") or {}).get("peso_H2")]
    return result

# UNIFICADO_20261011: cierre 016 de la Línea A (sin reordenar; can_decide_H=False). Se activa con CIERRE_TERMINAL=016.
def _cierre_final_016_lineaA(result,pred,run_ctx=None):
    """PATCH 016. Cierre de fin de corrida. No reordena ni elige: H1/H2 = top1/top2 de rank_fusion (predictor.candidates).
    Grado (regla explícita, sin pesos nuevos):
      FIRME    = margen >= GATE_SEPARATION y el acero descarta al rival más fuerte (C2 ok) y 0 objeciones (guardianes + estricto C1/C2/C3/C4).
      FRAGIL   = margen < GATE_SEPARATION y al menos una señal contraria fuerte: acero CAE, décimo hombre en banda de empate,
                 subdeterminación (C3) o empate exacto top1/top2.
      AJUSTADA = el resto (se emite igual, con sus objeciones).
    Latencia: solo como contexto (frentes pendientes y tokens latentes, persistidos para casos futuros), nunca como veredicto."""
    cands=pred.get("candidates") or []
    t1=cands[0] if cands else None; t2=cands[1] if len(cands)>1 else None
    margen=round(float(t1["rank_fusion"])-float(t2["rank_fusion"]),6) if (t1 and t2) else None
    info=pred.get("information_state") or {}
    emp=bool((pred.get("empates") or {}).get("top1_top2_empate"))
    est=result.get("modo_estricto") or {}; crit=est.get("criterios") or {}
    c1=crit.get("C1_top1_encabeza_un_corte"); c2=crit.get("C2_rival_mas_fuerte_descartado_por_acero"); c3=crit.get("C3_H1_H2_distinguibles"); c4=crit.get("C4_aquiles_estable")
    H1=t1["family"] if t1 else None; H2=t2["family"] if t2 else None
    rival_acero=(c2 or {}).get("rival_mas_fuerte")
    rival_alineado=bool(H2) and rival_acero == H2
    acero={"disponible":bool(c2) and ("veredicto_top1" in (c2 or {})),"rival_mas_fuerte":rival_acero,"dif_base":(c2 or {}).get("dif_base"),
           "dif_acero":(c2 or {}).get("dif_acero"),"veredicto_top1":(c2 or {}).get("veredicto_top1"),
           "rival_alineado_apuesta":rival_alineado,"descarta_rival":bool((c2 or {}).get("ok")) and rival_alineado,
           "EPS":(c2 or {}).get("EPS")}
    cg=result.get("cierre_guardianes") or {}
    objeciones=[{"fuente":"guardian","guardian":m.get("guardian"),"tipo":m.get("tipo"),"alcance":m.get("alcance"),"corte":m.get("corte")} for m in (cg.get("motivos") or [])]
    mot_e={str(x)[:2]:str(x) for x in (est.get("motivos") or [])}
    if c1 is not None and not c1.get("ok"): objeciones.append({"fuente":"modo_estricto","criterio":"C1_top1_encabeza_un_corte","detalle":mot_e.get("C1")})
    if c2 is not None and not c2.get("ok"): objeciones.append({"fuente":"modo_estricto","criterio":"C2_acero","detalle":mot_e.get("C2")})
    subdet=bool((c3 or {}).get("subdeterminado")); emp_dh=bool((c3 or {}).get("cierre_en_banda_empate"))
    if c3 is not None and (subdet or emp_dh):
        objeciones.append({"fuente":"modo_estricto","criterio":"C3_H1_H2_distinguibles",
                           "detalle":"; ".join(([f"subdeterminado (margen {margen} < {GATE_SEPARATION}, rival en {c3.get('cortes_con_rival')} cortes vs top1 en {c3.get('cortes_con_top1')})"] if subdet else [])
                                               +([f"décimo hombre: cierre en banda de empate (p={c3.get('decimo_hombre_cierre_p')})"] if emp_dh else [])),
                           "nota":"releído para el cierre final: 'sin H1/sin H2' del estricto era el estado del predictor DURANTE la corrida"})
    if c4 is not None and not c4.get("ok"): objeciones.append({"fuente":"modo_estricto","criterio":"C4_aquiles_estable","detalle":mot_e.get("C4")})
    objeciones=_deduplicar_objeciones_016(objeciones)
    separado=margen is not None and margen>=GATE_SEPARATION
    fuerte=[k for k,v in (("acero_CAE",acero["veredicto_top1"]=="CAE"),("acero_rival_no_alineado",not acero["rival_alineado_apuesta"]),("decimo_hombre_banda_empate",emp_dh),("subdeterminacion",subdet),("empate_exacto",emp)) if v]
    if not cands: grado="SIN_CANDIDATOS"
    elif separado and acero["descarta_rival"] and not objeciones: grado="FIRME"
    elif (not separado) and fuerte: grado="FRAGIL"
    else: grado="AJUSTADA"
    ramas={r.get("family"):r for r in ((result.get("apuesta") or {}).get("ramas") or [])}
    H1=t1["family"] if t1 else None; H2=t2["family"] if t2 else None
    apuesta={"familia_apostada":H1,"frente_a":H2,"margen":margen,"grado":grado,
             "proyeccion_H1":(ramas.get(H1) or {}).get("proyeccion"),"proyeccion_H2":(ramas.get(H2) or {}).get("proyeccion"),
             "serie_H1_hasta_Z":(ramas.get(H1) or {}).get("serie_hasta_Z"),"serie_H2_hasta_Z":(ramas.get(H2) or {}).get("serie_hasta_Z"),
             "formula":(result.get("apuesta") or {}).get("formula"),"validation":"observacion_futura","created_after_freeze":True,
             "regla":"apuesta = H1 (top1 rank_fusion) frente a H2 (top2); la proyección es la ya calculada en result.apuesta (sin ranking nuevo)"}
    gate=pred.get("compuerta_cierre") or {}; lat=gate.get("latencia_escrita") or {}
    frentes={"abiertos_o_reafirmados_en_esta_corrida":list(lat.get("abiertos_o_reafirmados") or []),
             "heredados_que_siguen_latentes":list(gate.get("siguen_latentes") or []),
             "pendientes_que_contradicen_cierre":list(gate.get("pendientes_que_contradicen") or []),
             "persistencia":"StinkBox pendientes_vivos (estado de FRENTE para casos futuros; no es veredicto)",
             "pending_fronts_sha256":lat.get("pending_fronts_sha256")}
    g=result.get("guardianes") or {}
    dh=next((b for b in (g.get("bloques") or []) if b.get("guardian")=="DECIMO_HOMBRE_LATENCIA"),{}) or {}
    v011=(run_ctx or {}).get("vecinos_011") or {}
    il=(v011.get("ilumina_012") or {}) if isinstance(v011,dict) else {}
    toks={"decimo_hombre_cortes_latentes":list(((dh.get("detalle") or {}).get("cortes_latentes")) or []),
          "expediente_latencia_guardianes":list(((((g.get("ruta_cierre_latente") or {}).get("latencia") or {}).get("expediente") or {}).get("tokens")) or []),
          "ilumina_012":{"n":il.get("n_tokens",len(il.get("tokens") or [])),"muestra":list(il.get("tokens") or [])[:30],"nota":"vecinos con un solo caso ajeno: traza/luz, no votan (012)"},
          "sombrero_blanco_fuera_catalogo":list(((result.get("motor") or {}).get("sombrero_blanco") or {}).get("esta_corrida") or []),
          "nota":"contexto: estado de token durante la corrida o guardado para casos futuros; no es el veredicto"}
    durante={"information_state":info.get("state"),"razon":info.get("reason"),"compuerta":gate.get("decision"),
             "ruta_guardianes":cg.get("estado_cierre"),"estricto":est.get("estado_cierre_estricto"),
             "nota":"estados DURANTE la corrida (latencia = estado de corrida/token); se conservan para trazabilidad"}
    return {"version":"CIERRE_FINAL_016","status":"EMITIDO","H1":H1,"H2":H2,
            "rank_fusion_H1":(t1 or {}).get("rank_fusion"),"rank_fusion_H2":(t2 or {}).get("rank_fusion"),"top3":cands[2]["family"] if len(cands)>2 else None,
            "margen":margen,"grado":grado,
            "criterios_grado":{"separacion":GATE_SEPARATION,"margen_separado":separado,"acero_descarta_rival":acero["descarta_rival"],
                               "senales_contrarias_fuertes":fuerte,"n_objeciones":len(objeciones),
                               "regla":"FIRME: separado + acero descarta + 0 objeciones; FRAGIL: no separado + señal contraria fuerte; AJUSTADA: resto"},
            "prueba_acero":acero,"objeciones":objeciones,"n_objeciones":len(objeciones),
            "apuesta":apuesta,"frentes_pendientes":frentes,"tokens_latentes":toks,"estado_motor_durante_corrida":durante,
            "fuente_H":"predictor.candidates top1/top2 (rank_fusion); sin ranking nuevo",
            "guardianes_y_estricto":"gradúan la confianza y adjuntan objeciones; no bloquean la emisión de H; can_decide_H=False",
            "can_decide_H":False,"reordena":False}

def _aplicar_cierre_final_016_lineaA(result,pred,cf):
    """Emite H1/H2 de fin de corrida y renombra los campos de estado durante corrida (se conservan para trazabilidad)."""
    cands=pred.get("candidates") or []
    for k,i in (("H1",0),("H2",1)):
        if not result.get(k) and len(cands)>i:
            result[k]={"family":cands[i]["family"],"features":cands[i].get("features"),
                       "fuente_016":"cierre_final: top%d de rank_fusion (el predictor no coronó DURANTE la corrida: %s)"%(i+1,(pred.get("information_state") or {}).get("state"))}
    nota="estado DURANTE la corrida (PATCH 016: la latencia no es veredicto final; ver cierre_final)"
    if "estado_cierre" in result:
        result["estado_motor_durante_corrida"]={**result.pop("estado_cierre"),"nota_016":nota}
    if "estado_cierre_estricto" in result:
        result["estado_estricto_durante_corrida"]={**result.pop("estado_cierre_estricto"),"nota_016":nota}
    cg=result.get("cierre_guardianes")
    if isinstance(cg,dict) and "estado_cierre" in cg:
        cg["estado_durante_corrida"]=cg.pop("estado_cierre"); cg["nota_016"]=nota
    for blk in (result.get("modo_estricto"), result.get("guardianes")):
        if isinstance(blk,dict): blk["nota_016"]="estados LATENTE/NO_RESUELTO de este bloque = estado DURANTE la corrida y objeciones; gradúan, no bloquean (can_decide_H=False); cierre en result.cierre_final"
    for blk in (pred, pred.get("compuerta_cierre")):
        if isinstance(blk,dict): blk["nota_016"]="status/information_state/decision/H de este bloque = estado DURANTE la corrida; cierre de fin de corrida en result.cierre_final"
    result["cierre_final"]=cf
    ap=result.get("apuesta")
    if isinstance(ap,dict):
        ap["apuesta_final_016"]={k:cf["apuesta"].get(k) for k in ("familia_apostada","frente_a","margen","grado")}
    rc=result.get("reporte_caso")
    if isinstance(rc,dict):
        for a,b in (("cierre_vigente","estado_durante_corrida_vigente"),("motivos_vigente","motivos_durante_corrida_vigente"),
                    ("cierre_estricto","estado_durante_corrida_estricto"),("motivos_estricto","motivos_durante_corrida_estricto"),
                    ("sostenido","sostenido_estricto_durante_corrida")):
            if a in rc: rc[b]=rc.pop(a)
        rc["H1"]=cf.get("H1"); rc["H2"]=cf.get("H2")
        rc["cierre_final"]={k:cf.get(k) for k in ("H1","H2","margen","grado","n_objeciones")}
        rc["cierre_final"]["objeciones"]=[str(o.get("guardian") or o.get("criterio"))+(":"+str(o.get("tipo")) if o.get("tipo") else "") for o in cf.get("objeciones") or []]
    return result


GRADOS_016=("FIRME","AJUSTADA","FRAGIL")
def _deduplicar_objeciones_016(rows):
    """Deduplica el mismo hecho entre guardianes y criterios estrictos sin borrar criterios distintos."""
    out=[]; seen=set(); guardian_acero_present=False
    for row in rows:
        if row.get("fuente") == "guardian":
            g=str(row.get("guardian") or "").casefold()
            t=str(row.get("tipo") or "").casefold()
            if "acero" in g or "steel" in g or "acero" in t or "steel" in t:
                guardian_acero_present=True
    for row in rows:
        fuente=row.get("fuente"); criterio=str(row.get("criterio") or "")
        guardian=str(row.get("guardian") or "").casefold()
        if fuente == "modo_estricto" and criterio == "C2_acero" and guardian_acero_present:
            continue
        if fuente == "guardian":
            key=("guardian",guardian,str(row.get("tipo") or ""),str(row.get("alcance") or ""),str(row.get("corte") or ""))
        else:
            key=("estricto",criterio,str(row.get("detalle") or ""))
        if key in seen: continue
        seen.add(key); out.append(row)
    return out

def _cierre_final_016(result,pred,run_ctx=None):
    """PATCH 016. Cierre de fin de corrida. No reordena ni elige: H1/H2 = top1/top2 de rank_fusion (predictor.candidates).
    Grado (regla explícita, sin pesos nuevos):
      FIRME    = margen >= GATE_SEPARATION y el acero descarta al rival más fuerte (C2 ok) y 0 objeciones (guardianes + estricto C1/C2/C3/C4).
      FRAGIL   = margen < GATE_SEPARATION y al menos una señal contraria fuerte: acero CAE, décimo hombre en banda de empate,
                 subdeterminación (C3) o empate exacto top1/top2.
      AJUSTADA = el resto (se emite igual, con sus objeciones).
    Latencia: solo como contexto (frentes pendientes y tokens latentes, persistidos para casos futuros), nunca como veredicto."""
    cands=list(pred.get("candidates") or [])
    if len(cands)<2:
        seen={c.get("family") for c in cands}
        for cut in reversed((result.get("motor") or {}).get("cuts") or []):
            for row in cut.get("P_top5_ANEXO") or []:
                fam=row[0] if isinstance(row,(list,tuple)) else None
                if fam and fam not in seen:
                    cands.append({"family":fam,"rank_fusion":float(row[1]) if len(row)>1 else 0.0}); seen.add(fam)
                if len(cands)>=2: break
            if len(cands)>=2: break
    t1=cands[0] if cands else None; t2=cands[1] if len(cands)>1 else None
    margen=round(abs(float(t1.get("rank_fusion",0.0))-float(t2.get("rank_fusion",0.0))),6) if (t1 and t2) else 0.0
    info=pred.get("information_state") or {}
    emp=bool((pred.get("empates") or {}).get("top1_top2_empate"))
    est=result.get("modo_estricto") or {}; crit=est.get("criterios") or {}
    c1=crit.get("C1_top1_encabeza_un_corte"); c2=crit.get("C2_rival_mas_fuerte_descartado_por_acero"); c3=crit.get("C3_H1_H2_distinguibles"); c4=crit.get("C4_aquiles_estable")
    H1=t1["family"] if t1 else None; H2=t2["family"] if t2 else None
    rival_acero=(c2 or {}).get("rival_mas_fuerte")
    rival_alineado=bool(H2) and rival_acero == H2
    acero={"disponible":bool(c2) and ("veredicto_top1" in (c2 or {})),"rival_mas_fuerte":rival_acero,"dif_base":(c2 or {}).get("dif_base"),
           "dif_acero":(c2 or {}).get("dif_acero"),"veredicto_top1":(c2 or {}).get("veredicto_top1"),
           "rival_alineado_apuesta":rival_alineado,"descarta_rival":bool((c2 or {}).get("ok")) and rival_alineado,
           "EPS":(c2 or {}).get("EPS")}
    cg=result.get("cierre_guardianes") or {}
    objeciones=[{"fuente":"guardian","guardian":m.get("guardian"),"tipo":m.get("tipo"),"alcance":m.get("alcance"),"corte":m.get("corte")} for m in (cg.get("motivos") or [])]
    mot_e={str(x)[:2]:str(x) for x in (est.get("motivos") or [])}
    if c1 is not None and not c1.get("ok"): objeciones.append({"fuente":"modo_estricto","criterio":"C1_top1_encabeza_un_corte","detalle":mot_e.get("C1")})
    if c2 is not None and not c2.get("ok"): objeciones.append({"fuente":"modo_estricto","criterio":"C2_acero","detalle":mot_e.get("C2")})
    subdet=bool((c3 or {}).get("subdeterminado")); emp_dh=bool((c3 or {}).get("cierre_en_banda_empate"))
    if c3 is not None and (subdet or emp_dh):
        objeciones.append({"fuente":"modo_estricto","criterio":"C3_H1_H2_distinguibles",
                           "detalle":"; ".join(([f"subdeterminado (margen {margen} < {GATE_SEPARATION}, rival en {c3.get('cortes_con_rival')} cortes vs top1 en {c3.get('cortes_con_top1')})"] if subdet else [])
                                               +([f"décimo hombre: cierre en banda de empate (p={c3.get('decimo_hombre_cierre_p')})"] if emp_dh else [])),
                           "nota":"releído para el cierre final: 'sin H1/sin H2' del estricto era el estado del predictor DURANTE la corrida"})
    if c4 is not None and not c4.get("ok"): objeciones.append({"fuente":"modo_estricto","criterio":"C4_aquiles_estable","detalle":mot_e.get("C4")})
    objeciones=_deduplicar_objeciones_016(objeciones)
    separado=margen is not None and margen>=GATE_SEPARATION
    fuerte=[k for k,v in (("acero_CAE",acero["veredicto_top1"]=="CAE"),("acero_rival_no_alineado",not acero["rival_alineado_apuesta"]),("decimo_hombre_banda_empate",emp_dh),("subdeterminacion",subdet),("empate_exacto",emp)) if v]
    if not cands: grado="AJUSTADA"
    elif separado and acero["descarta_rival"] and not objeciones: grado="FIRME"
    elif (not separado) and fuerte: grado="FRAGIL"
    else: grado="AJUSTADA"
    ramas={r.get("family"):r for r in ((result.get("apuesta") or {}).get("ramas") or [])}
    H1=t1["family"] if t1 else None; H2=t2["family"] if t2 else None
    apuesta={"familia_apostada":H1,"frente_a":H2,"margen":margen,"grado":grado,
             "proyeccion_H1":(ramas.get(H1) or {}).get("proyeccion"),"proyeccion_H2":(ramas.get(H2) or {}).get("proyeccion"),
             "serie_H1_hasta_Z":(ramas.get(H1) or {}).get("serie_hasta_Z"),"serie_H2_hasta_Z":(ramas.get(H2) or {}).get("serie_hasta_Z"),
             "formula":(result.get("apuesta") or {}).get("formula"),"validation":"observacion_futura","created_after_freeze":True,
             "regla":"apuesta = H1 (top1 rank_fusion) frente a H2 (top2); la proyección es la ya calculada en result.apuesta (sin ranking nuevo)"}
    gate=pred.get("compuerta_cierre") or {}; lat=gate.get("latencia_escrita") or {}
    frentes={"abiertos_o_reafirmados_en_esta_corrida":[],
             "heredados_que_siguen_latentes":[],
             "pendientes_que_contradicen_cierre":[],
             "persistencia":"frentes de hipótesis cerrados operativamente; solo tokens descubiertos y vecinos se conservan como memoria activa",
             "pending_fronts_sha256":lat.get("pending_fronts_sha256")}
    g=result.get("guardianes") or {}
    dh=next((b for b in (g.get("bloques") or []) if b.get("guardian")=="DECIMO_HOMBRE_LATENCIA"),{}) or {}
    v011=(run_ctx or {}).get("vecinos_011") or {}
    il=(v011.get("ilumina_012") or {}) if isinstance(v011,dict) else {}
    toks={"decimo_hombre_cortes_latentes":list(((dh.get("detalle") or {}).get("cortes_latentes")) or []),
          "expediente_latencia_guardianes":list(((((g.get("ruta_cierre_latente") or {}).get("latencia") or {}).get("expediente") or {}).get("tokens")) or []),
          "ilumina_012":{"n":il.get("n_tokens",len(il.get("tokens") or [])),"muestra":list(il.get("tokens") or [])[:30],"nota":"vecinos con un solo caso ajeno: traza/luz, no votan (012)"},
          "sombrero_blanco_fuera_catalogo":list(((result.get("motor") or {}).get("sombrero_blanco") or {}).get("esta_corrida") or []),
          "nota":"contexto: estado de token durante la corrida o guardado para casos futuros; no es el veredicto"}
    durante={"information_state":info.get("state"),"razon":info.get("reason"),"compuerta":gate.get("decision"),
             "ruta_guardianes":cg.get("estado_cierre"),"estricto":est.get("estado_cierre_estricto"),
             "nota":"estados DURANTE la corrida (latencia = estado de corrida/token); se conservan para trazabilidad"}
    return {"version":"CIERRE_FINAL_018","status":"RESUELTO_OPERACIONALMENTE","estado_final":"RESUELTO_OPERACIONALMENTE","H1":H1 or "NO_EMITIBLE_SIN_CANDIDATAS_OBSERVABLES","H2":H2 or (H1 or "NO_EMITIBLE_SIN_CANDIDATAS_OBSERVABLES"),
            "rank_fusion_H1":(t1 or {}).get("rank_fusion"),"rank_fusion_H2":(t2 or {}).get("rank_fusion"),"top3":cands[2]["family"] if len(cands)>2 else None,
            "margen":margen,"grado":grado,
            "criterios_grado":{"separacion":GATE_SEPARATION,"margen_separado":separado,"acero_descarta_rival":acero["descarta_rival"],
                               "senales_contrarias_fuertes":fuerte,"n_objeciones":len(objeciones),
                               "regla":"FIRME: separado + acero descarta + 0 objeciones; FRAGIL: no separado + señal contraria fuerte; AJUSTADA: resto"},
            "prueba_acero":acero,"objeciones":objeciones,"n_objeciones":len(objeciones),
            "apuesta":apuesta,"frentes_pendientes":frentes,"tokens_latentes":toks,"estado_motor_durante_corrida":durante,
            "fuente_H":"orden operativo terminal: tortugas; resoluciones de casos semejantes; pistas LLM de arquetipos si fueron suministradas; rank_fusion como último desempate",
            "guardianes_y_estricto":"gradúan la confianza y adjuntan objeciones; la capa terminal decide H operativamente sin consultar hechos futuros",
            "can_decide_H":True,"reordena":bool((pred.get("terminal_resolution") or {}).get("method", "").startswith("TORTUGAS")),
            "metodo_resolucion_operativa":(pred.get("terminal_resolution") or {}).get("method", "RANK_FUSION_WITH_AVAILABLE_EVIDENCE"),
            "estado_final":"RESUELTO_OPERACIONALMENTE"}

def _aplicar_cierre_final_016(result,pred,cf):
    """Emite H1/H2 de fin de corrida y renombra los campos de estado durante corrida."""
    for k in ("H1","H2"):
        if cf.get(k):
            cands=list(pred.get("candidates") or [])
            row=next((c for c in cands if c.get("family")==cf.get(k)),{})
            result[k]={"family":cf[k],"rank_fusion":float(row.get("rank_fusion",0.0)),"fuente_018":"resolucion_operativa_terminal",
                       "margen":float(cf.get("margen",0.0) or 0.0),"grado":cf.get("grado","AJUSTADA"),
                       "metodo_cierre":cf.get("metodo_resolucion_operativa","RANK_FUSION_WITH_AVAILABLE_EVIDENCE")}
    nota="estado DURANTE la corrida (PATCH 016: la latencia no es veredicto final; ver cierre_final)"
    if "estado_cierre" in result:
        result["estado_motor_durante_corrida"]={**result.pop("estado_cierre"),"nota_016":nota}
    if "estado_cierre_estricto" in result:
        result["estado_estricto_durante_corrida"]={**result.pop("estado_cierre_estricto"),"nota_016":nota}
    cg=result.get("cierre_guardianes")
    if isinstance(cg,dict) and "estado_cierre" in cg:
        cg["estado_durante_corrida"]=cg.pop("estado_cierre"); cg["nota_016"]=nota
    for blk in (result.get("modo_estricto"), result.get("guardianes")):
        if isinstance(blk,dict): blk["nota_016"]="estados LATENTE/NO_RESUELTO de este bloque = estado DURANTE la corrida y objeciones; gradúan, no bloquean (can_decide_H=False); cierre en result.cierre_final"
    for blk in (pred, pred.get("compuerta_cierre")):
        if isinstance(blk,dict): blk["nota_016"]="status/information_state/decision/H de este bloque = estado DURANTE la corrida; cierre de fin de corrida en result.cierre_final"
    result["cierre_final"]=cf
    result["estado_final"]="RESUELTO_OPERACIONALMENTE"
    ap=result.get("apuesta")
    if isinstance(ap,dict):
        ap["apuesta_final_016"]={k:cf["apuesta"].get(k) for k in ("familia_apostada","frente_a","margen","grado")}
    rc=result.get("reporte_caso")
    if isinstance(rc,dict):
        for a,b in (("cierre_vigente","estado_durante_corrida_vigente"),("motivos_vigente","motivos_durante_corrida_vigente"),
                    ("cierre_estricto","estado_durante_corrida_estricto"),("motivos_estricto","motivos_durante_corrida_estricto"),
                    ("sostenido","sostenido_estricto_durante_corrida")):
            if a in rc: rc[b]=rc.pop(a)
        rc["H1"]=cf.get("H1"); rc["H2"]=cf.get("H2")
        rc["cierre_final"]={k:cf.get(k) for k in ("H1","H2","margen","grado","n_objeciones")}
        rc["cierre_final"]["objeciones"]=[str(o.get("guardian") or o.get("criterio"))+(":"+str(o.get("tipo")) if o.get("tipo") else "") for o in cf.get("objeciones") or []]
    return result

def _reporte_caso(result,pred,conv,post):
    cands=[c["family"] for c in (pred.get("candidates") or [])]
    ec=result.get("estado_cierre") or {}; ee=result.get("estado_cierre_estricto") or {}
    cg=result.get("cierre_guardianes") or {}
    guard=(result.get("guardianes") or {}).get("banderas")
    reg=(result.get("laterales_unico") or {}).get("registro_piezas") or []
    neg=((result.get("laterales_unico") or {}).get("pre") or {}).get("negativo_ricci_vs_billar") or {}
    fil={f["familia"]:f for f in (neg.get("filas") or [])}
    aq=(post or {}).get("aquiles_bootstrap") or {}
    return {"top1":cands[0] if cands else None,"top2":cands[1] if len(cands)>1 else None,"top3":cands[2] if len(cands)>2 else None,
            "H1":(result.get("H1") or {}).get("family") if isinstance(result.get("H1"),dict) else None,
            "H2":(result.get("H2") or {}).get("family") if isinstance(result.get("H2"),dict) else None,
            "cierre_vigente":ec.get("valor"),"motivos_vigente":[f"{m.get('guardian')}:{m.get('tipo')}" for m in (cg.get("motivos") or [])],
            "cierre_estricto":ee.get("valor"),"motivos_estricto":ee.get("motivos"),
            "sostenido":(ee.get("valor")=="CIERRE_ESTRICTO") if ee else (ec.get("valor")!="LATENTE"),
            "guardianes":guard,
            "negativo_top1":(fil.get(cands[0]) or {}).get("senal_descarte") if cands else None,
            "negativo_top2":(fil.get(cands[1]) or {}).get("senal_descarte") if len(cands)>1 else None,
            "aquiles_ganador_remuestreo":aq.get("ganador_remuestreo_final"),"aquiles_coincide_top1":aq.get("ganador_remuestreo_coincide_con_top1"),
            "convergencia_lateral":conv.get("conteo"),
            "laterales":[{"pieza":r.get("pieza"),"estado":r.get("estado"),"aporte":r.get("aporte")} for r in reg],
            "vocabulario":"neutro; sin veredictos de resultado (la comparación con lo registrado se hace fuera del motor, al final)"}

def main():
    if len(sys.argv)<2:
        print("Uso: python MOTOR_V15_3_UNIFICADO_ALTERNO.py input.json [output.json]"); return 2
    inp=Path(sys.argv[1]); out=Path(sys.argv[2]) if len(sys.argv)>2 else inp.with_name(inp.stem+"_V09_RESULT.json")
    case=json.loads(inp.read_text(encoding="utf-8"))
    result=run(case)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"status":"OK","version":VERSION,"case_id":result["case_id"],"H1":result["H1"],"H2":result["H2"],"components_executed":[x["component"] for x in result["execution"]["component_status"] if x["status"]=="EXECUTED"],"output":str(out)},ensure_ascii=False,indent=2))

if __name__=="__main__": raise SystemExit(main())

