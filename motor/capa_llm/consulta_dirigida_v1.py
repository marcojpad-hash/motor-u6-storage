#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""consulta_dirigida_v1.py — capa LLM de CONSULTAS DIRIGIDAS de contexto (UNIFICADO 2026-10-11).

Pedido de Mj (11 oct 2026): el motor puede hacer consultas DIRIGIDAS al LLM para engrosar el input, dentro del
contexto del propio caso, desde el inicio hasta Z (corte de congelamiento): contexto, otras personas presentes,
antagonista, otros factores. Filtros: las consultas NUNCA piden hipótesis ni apuestas, NUNCA son consultas de futuro
(nada posterior a Z), y se protege contra la fuga historiográfica (el LLM conoce los desenlaces por entrenamiento).

Ubicación: FUERA del motor (capa LLM, la llama el runner antes de motor.run). El motor nunca importa este módulo.
Contrato: CONTRATO_LLM_UNIFICADO_20261011 (ver INFORME). can_decide_H=False · no escribe H · no toca question,
external_lights, caldero_* ni pesos existentes · determinista · sin red (el adaptador por defecto es OFFLINE).

Flujo
  1. detectar_huecos(case): por REGLAS sobre lo que ya hay en el input (personajes_corte_016 sobre el texto propio del
     corte; ejes P/A/C), nunca pidiendo conclusiones. Huecos -> tipos de pregunta:
       G_SIN_TEXTO        corte sin hecho/narracion                         -> CONTEXTO
       G_SIN_OTROS        corte sin otros agentes (016) o sin texto         -> AGENTES_PRESENTES
       G_SIN_ANTAGONISTA  ningún agente con función marte/ANTAGONISTA hasta este corte (acumulado) -> ANTAGONISTA
       G_SIN_INSTITUCION  sin AUTORIDAD/INSTITUCION en este corte ni en el anterior               -> INSTITUCIONES
       G_POCOS_FACTORES   eje C con < 2 tokens                              -> FACTORES
       G_SIN_ENTORNO      sin COLECTIVO y sin bienes nombrados en el corte  -> ENTORNO
     Máx. MAX_PREGUNTAS_POR_CORTE por corte (orden de prioridad de la lista). Solo cortes <= Z.
  2. Cada pregunta: plantilla fija neutral ligada a UN corte (id, índice, fecha máx = fecha del corte o Z), con roles
     neutros (PROTAGONISTA), sin nombres ni años. validar_pregunta() la rechaza si trae hipótesis/apuesta/etiqueta
     244/arquetipo/futuro.
  3. Adaptador (enchufable): responder(pregunta_sellada) -> {"texto","tokens","fuente"}. OFFLINE (defecto: no
     responde), MOCK (respuestas fijas de prueba desde JSON), EXTERNO (se inyecta un callable; no se usa en pruebas).
  4. Filtros sobre cada respuesta (en orden; rechazo = la respuesta no entra; 'neutralizar' = entra sin el span):
     F0 PROCEDENCIA  sin 'fuente' o pregunta desconocida/corte fuera de rango -> rechazo
     F1 TEMPORAL     años > año del corte o > Z; marcadores de futuro/retrospectiva (más tarde, finalmente, -ría de
                     desenlace, terminaría...); desenlace/valoración de resultado; muerte del protagonista en corte que
                     no es el último; anuncio de fama/posteridad; mención de un corte posterior -> rechazo
     F2 HIPOTESIS    palabras de hipótesis/apuesta/ranking/predicción; id literal o lema de familia del 244 (salvo
                     sustantivos de rol del léxico 016); arquetipo/tipo de personaje; rasgo evaluativo; teleología -> rechazo
     F3 NOMBRES/AÑOS (015) nombres propios, títulos de obra y fechas -> neutralizar a ids de rol/'(fecha)' (017);
                     verificación posterior: si queda un nombre del veto 015 o un año -> rechazo
     F4 FUGA HISTORIOGRAFICA  fraseo de desenlace conocido ('como se sabe', 'los historiadores', 'pasaría a la
                     historia', 'conocido como'...), etiquetas de narrativa canónica ('precursor', 'mártir', 'genio',
                     'visionario', 'legado', 'adelantado a su tiempo'...), periodizaciones retrospectivas -> rechazo
     F5 OBSERVABLE   la respuesta neutralizada debe conservar al menos 3 palabras de contenido -> si no, rechazo
     Tokens propuestos: solo vocabulario canónico (tokens_favor/contra del catálogo cargado); nunca id/lema de familia;
     nunca nombre/número; sin duplicar el corte; entran al eje C con peso fijo PESO_TOKEN (el LLM no fija pesos) y
     solo si hay hueco (máx 5 por eje, regla del motor nativo).
  5. Entrada al motor: texto neutral anexado al texto propio del corte (campo hecho, o narracion si el caso usa
     narracion) + tokens aceptados en C. Procedencia (id de pregunta, corte, fuente, sha del texto original, texto
     original) SOLO en el sidecar SELLADO (no lo lee el motor). verificar_no_escribe_H() comprueba que solo cambiaron
     cuts[i].hecho/narracion/C de cortes <= Z.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

VERSION = "CONSULTA_DIRIGIDA_V1_20261011"
CONTRATO = "CONTRATO_LLM_UNIFICADO_20261011"
TIPOS = ("CONTEXTO", "AGENTES_PRESENTES", "ANTAGONISTA", "FACTORES", "INSTITUCIONES", "ENTORNO")
PRIORIDAD = ("CONTEXTO", "AGENTES_PRESENTES", "ANTAGONISTA", "INSTITUCIONES", "FACTORES", "ENTORNO")
MAX_PREGUNTAS_POR_CORTE = 4
PESO_TOKEN = 0.60
MAX_TOKENS_POR_RESPUESTA = 2
CAMPOS_PERMITIDOS_CORTE = ("hecho", "narracion", "C")

PLANTILLAS = {
    "CONTEXTO": "Hasta el corte {corte} (nada posterior a {limite}): describe la situación observable del PROTAGONISTA en ese "
                "momento (qué hace, dónde actúa en términos genéricos, con quién se relaciona).",
    "AGENTES_PRESENTES": "Hasta el corte {corte} (nada posterior a {limite}): ¿qué otros agentes (personas, grupos o "
                         "instituciones, como roles genéricos) estaban presentes o actuando junto al PROTAGONISTA?",
    "ANTAGONISTA": "Hasta el corte {corte} (nada posterior a {limite}): ¿hay algún agente que se opone, compite o presiona "
                   "al PROTAGONISTA en ese momento? Descríbelo como rol genérico y por sus actos observables.",
    "FACTORES": "Hasta el corte {corte} (nada posterior a {limite}): ¿qué otros factores observables del mismo periodo "
                "(recursos, dependencias, restricciones, apoyos) condicionan al PROTAGONISTA?",
    "INSTITUCIONES": "Hasta el corte {corte} (nada posterior a {limite}): ¿qué instituciones o autoridades (como roles "
                     "genéricos) regulan o enmarcan la actividad del PROTAGONISTA en ese momento?",
    "ENTORNO": "Hasta el corte {corte} (nada posterior a {limite}): ¿cómo es el entorno social o material inmediato "
               "(grupos, comunidades, condiciones) en que actúa el PROTAGONISTA?",
}
REGLAS_RESPUESTA = ("solo hechos observables EN ese corte; roles genéricos, sin nombres propios ni años; "
                    "sin valoraciones, sin desenlaces, sin lo que pasó después; no proponer hipótesis, familias, arquetipos ni apuestas; "
                    "declarar la fuente")

BASE = Path(__file__).resolve().parent


def _n(s: str) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().casefold()


def sha8(s: Any) -> str:
    return hashlib.sha256(json.dumps(s, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:8]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)  # type: ignore
    return m


# ------------------------------------------------------------------ léxicos de filtro (normalizados, sin acentos)
RX_FUTURO = [r"\bmas tarde\b", r"\bfinalmente\b", r"\bposteriormente\b", r"\bdespues de (?:su|la|el|esto|ello|aquello)\b",
             r"\btiempo despues\b", r"\banos despues\b", r"\ba la postre\b", r"\bcon el tiempo\b", r"\beventualmente\b",
             r"\bluego (?:seria|fue|llegaria)\b", r"\b(?:terminar|acabar|llegar|convertir|lograr|alcanzar|marcar|llevar|conducir|"
             r"pasar|ser|quedar|resultar|morir|fallecer|recordar|condenar|ejecutar|triunfar|fracasar|influir|inspirar)(?:ia|ian)\b",
             r"\bsentaria las bases\b", r"\bpresagi\w*", r"\bpreludio de\b", r"\bantes de (?:su muerte|morir|convertirse|ser condenad)\w*",
             r"\bal final de su vida\b", r"\bdesenlace\b", r"\bdestino final\b", r"\bsu final\b"]
RX_DESENLACE = [r"\bexito\w*", r"\bfracas\w*", r"\bculmina\w*", r"\bconsagra\w*", r"\btriunf\w*", r"\bderrota final\b",
                r"\bse derrumba\w*", r"\bcondenad[oa] a muerte\b", r"\bejecutad[oa]\b", r"\bhoguera\b", r"\bmurio\b", r"\bfallecio\b"]
RX_MUERTE = re.compile(r"\b(?:muere|fallece|murio|fallecio|muerte|ejecucion|ejecutado|hoguera)\b")
RX_FAMA = [r"\bpasar\w* a la historia\b", r"\bseria recordad\w*", r"\bposteridad\b", r"\blegado\b", r"\bfam(?:a|os[oa]s?)\b",
           r"\bcelebre\w*", r"\blegendari\w*", r"\binmortal\w*", r"\bicon\w*"]
RX_HIPOTESIS = [r"\bhipotesis\b", r"\bapuesta\w*", r"\bapostar\b", r"\bH[12]\b", r"\bganador\w*", r"\branking\b", r"\bpredic\w*",
                r"\bprobabl\w*", r"\bencaja con\b", r"\bcorresponde a la familia\b", r"\bpatron(?:es)?\b", r"\barquetip\w*",
                r"\bfamilia del catalogo\b", r"\brank_fusion\b", r"\bveredicto\b", r"\bconclusion\w*", r"\bdeberia ganar\b"]
RX_EVALUATIVO = [r"\bambicios[oa]s?\b", r"\bcarismatic\w*", r"\bmegaloman\w*", r"\bnarcisist\w*", r"\bheroic\w*", r"\bheroe\w*",
                 r"\btiranic\w*", r"\bdespotic\w*", r"\blider nat\w*", r"\bgeni(?:o|os|al|ales|alidad)\b", r"\bprodigi\w*",
                 r"\bextraordinari\w*", r"\bexcepcional\w*", r"\bvisionari\w*"]
RX_TELEO = [r"\bdestinad[oa] a\b", r"\bsu destino\b", r"\bpredestinad\w*", r"\bvocacion de\b", r"\bllamad[oa] a ser\b", r"\bnacio para\b"]
RX_FUGA = [r"\bcomo (?:se sabe|es sabido|es bien sabido|sabemos)\b", r"\bes (?:bien )?conocid[oa]\b", r"\bconocid[oa] como\b",
           r"\blo que se conoce como\b", r"\bhistoriador\w*", r"\bhistoriograf\w*", r"\bla historia (?:lo|la|le|recuerda|juzga)\b",
           r"\bsegun la historia\b", r"\bhoy (?:se|lo|la|le)\b", r"\bactualmente\b", r"\ben retrospectiva\b", r"\bvisto desde hoy\b",
           r"\bprecursor\w*", r"\bpioner[oa]s?\b", r"\bmartir\w*", r"\badelantad[oa] a su (?:tiempo|epoca)\b", r"\bpadre de la\b",
           r"\brevolucion cientifica\b", r"\bilustracion\b", r"\bmodernidad\b", r"\bedad moderna\b", r"\bsimbolo de\b",
           r"\bse convirti\w* en (?:un )?simbolo\b", r"\binfluy\w* en (?:la|el|los|las) (?:ciencia|filosofia|pensamiento|historia)\b"]
RX_ANIO = re.compile(r"(?<!\d)(1\d{3}|20\d{2})(?!\d)")

def _sin_anios(texto: str) -> str:
    """Quita el DATO del año sin tocar el contenido: el año no entra, la pregunta sí.
    Regla de Mj (2026-11-12): se rechaza la entrada del dato del año, no todo lo
    que viene después de que se dijo un año. Matar, comer, morir, dormir, soñar
    surgen en cualquier momento, sin año. Neutraliza a '(fecha)', como F3."""
    return RX_ANIO.sub("(fecha)", str(texto or ""))
RX_CORTE_REF = re.compile(r"\bcorte\s+([A-Z]?\d+|[A-F])\b", re.I)
# sustantivos de ROL del léxico 016 permitidos aunque coincidan con un lema de familia (rol observable, no etiqueta)
ROLES_016_PERMITIDOS = {"mentor", "familia", "pareja", "autoridad", "institucion", "colectivo", "antagonista", "rival", "maestro",
                        "protector", "aliado", "comunidad", "grupo"}
PALABRAS_VACIAS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "y", "o", "en", "a", "al", "con", "por", "para",
                   "que", "se", "su", "sus", "es", "son", "hay", "lo", "le", "les", "como", "ese", "esa", "este", "esta", "momento",
                   "corte", "protagonista", "fecha", "np"}


def _hits(pats: List[str], t: str) -> List[str]:
    out = []
    for p in pats:
        for m in re.finditer(p, t):
            out.append(m.group(0))
    return out


# ------------------------------------------------------------------ catálogo / veto 015 / filtro 017
class Recursos:
    def __init__(self, motor_dir: Path, filtro017_path: Optional[Path] = None):
        self.motor_dir = Path(motor_dir)
        pat = self.motor_dir / "patterns_final_v14.json"
        self.cat = json.loads(pat.read_text(encoding="utf-8"))
        self.patterns_sha256 = hashlib.sha256(pat.read_bytes()).hexdigest()
        self.vocab = set()
        for p in self.cat.values():
            if isinstance(p, dict):
                self.vocab |= set(p.get("tokens_favor") or {}); self.vocab |= set(p.get("tokens_contra") or {})
        self.f017 = _load("_f017_cd", filtro017_path or (BASE / "filtro_entrada_dirigida_017.py"))
        self.f017.BASE = self.motor_dir  # veto 015: sujetos_014.py y catálogo del motor cargado (solo lectura)
        et = self.f017.etiquetas_catalogo(self.cat)
        self.ids = {k.casefold() for k in self.cat}
        self.lemas = {l.replace("_", " ") for l in et["lema_a_fams"].keys() if len(l) >= 4}
        self.personaje = set(et["personaje"])
        self.p016 = _load("_p016_cd", self.motor_dir / "personajes_corte_016.py")
        try:
            s014 = _load("_s014_cd", self.motor_dir / "sujetos_014.py")
            self.veto015 = {_n(t) for t in s014.nombres_que_no_votan(None) if len(str(t)) >= 3}
        except Exception:
            self.veto015 = set()


# ------------------------------------------------------------------ Z y cortes
def _anio(s: Any) -> Optional[int]:
    m = re.match(r"^\s*(\d{4})", str(s or ""))
    return int(m.group(1)) if m else None


def indice_z(case: Mapping[str, Any]) -> Tuple[int, Optional[str]]:
    """Índice del último corte <= Z. Z = z90_date/freeze; si no hay, el último corte del input (Z = corte final)."""
    cuts = list(case.get("cuts") or [])
    z = case.get("z90_date") or case.get("freeze")
    if not z:
        return len(cuts) - 1, None
    zi = -1
    for i, c in enumerate(cuts):
        d = c.get("date")
        if d is None or str(d) <= str(z):
            zi = i
    return zi, str(z)


def _campo_texto(case: Mapping[str, Any]) -> str:
    cuts = case.get("cuts") or []
    if any(c.get("hecho") for c in cuts):
        return "hecho"
    if any(c.get("narracion") for c in cuts):
        return "narracion"
    return "hecho"


# ------------------------------------------------------------------ 1. huecos -> preguntas
def detectar_huecos(case: Mapping[str, Any], R: Recursos) -> Dict[str, Any]:
    cuts = list(case.get("cuts") or [])
    zi, z = indice_z(case)
    ext = R.p016.extraer(cuts)
    pcs = {pc.get("corte"): pc for pc in ext.get("por_corte") or []}
    huecos = []
    antagonista_visto = False
    inst_prev = False
    for i, c in enumerate(cuts):
        if i > zi:
            break
        cid = c.get("id")
        pc = pcs.get(cid) or {}
        sin_texto = pc.get("estado") != "DERIVADO"
        ags = pc.get("agentes") or []
        tipos_ag = {a.get("tipo") for a in ags}
        if any(a.get("funcion") == "marte" or a.get("tipo") == "ANTAGONISTA" for a in ags):
            antagonista_visto = True
        inst_aqui = bool(tipos_ag & {"AUTORIDAD", "INSTITUCION"})
        reglas = []
        if sin_texto:
            reglas.append(("CONTEXTO", "G_SIN_TEXTO"))
        if sin_texto or pc.get("sin_otros_agentes"):
            reglas.append(("AGENTES_PRESENTES", "G_SIN_OTROS"))
        if not antagonista_visto:
            reglas.append(("ANTAGONISTA", "G_SIN_ANTAGONISTA"))
        if not inst_aqui and not inst_prev:
            reglas.append(("INSTITUCIONES", "G_SIN_INSTITUCION"))
        if len(c.get("C") or []) < 2:
            reglas.append(("FACTORES", "G_POCOS_FACTORES"))
        if "COLECTIVO" not in tipos_ag and not (pc.get("bienes") or []):
            reglas.append(("ENTORNO", "G_SIN_ENTORNO"))
        inst_prev = inst_aqui
        reglas.sort(key=lambda r: PRIORIDAD.index(r[0]))
        for tipo, regla in reglas[:MAX_PREGUNTAS_POR_CORTE]:
            huecos.append({"corte": cid, "corte_idx": i, "tipo": tipo, "regla": regla, "fecha_corte": c.get("date")})
    return {"z": z, "z_idx": zi, "n_cortes": len(cuts), "modo_caso_016": ext.get("modo_caso"), "huecos": huecos}


def validar_pregunta(texto: str, R: Recursos) -> List[str]:
    """Una pregunta NUNCA pide hipótesis/apuesta ni futuro, ni trae nombres/años/etiquetas 244."""
    t = _n(texto); mot = []
    if _hits(RX_HIPOTESIS, t): mot.append("Q_HIPOTESIS:" + ",".join(_hits(RX_HIPOTESIS, t)))
    fut = [h for h in _hits(RX_FUTURO + RX_DESENLACE, t) if h not in ("nada posterior a",)]
    if fut or re.search(r"\b(?:que paso despues|que ocurrio despues|como termino|resultado final|que pasara)\b", t):
        mot.append("Q_FUTURO:" + ",".join(fut))
    if not re.search(r"\bhasta el corte\b", t) or "nada posterior a" not in t:
        mot.append("Q_SIN_LIMITE_TEMPORAL")
    if RX_ANIO.search(t): mot.append("Q_ANIO")  # guarda: si un año quedó en el texto, el dato no entra
    lem = [l for l in R.lemas if l not in ROLES_016_PERMITIDOS and re.search(r"\b" + re.escape(l) + r"\b", t)]
    ids = [i for i in R.ids if i in t]
    if lem or ids: mot.append("Q_ETIQUETA_244:" + ",".join(sorted(set(lem) | set(ids))))
    nom = [w for w in re.findall(r"[a-z]+", t) if w in R.veto015]
    if nom: mot.append("Q_NOMBRE_015")
    return mot


def construir_preguntas(case: Mapping[str, Any], R: Recursos) -> Dict[str, Any]:
    H = detectar_huecos(case, R)
    base = sha8({"cuts": case.get("cuts"), "z": H["z"]})
    preguntas = []
    for h in H["huecos"]:
        limite = h["fecha_corte"] or (H["z"] or "el corte " + str(h["corte"]))
        if H["z"] and h["fecha_corte"] and str(h["fecha_corte"]) > str(H["z"]):
            limite = H["z"]
        corte_ref = "C" + str(int(h["corte_idx"]) + 1)  # referencia sin año: el id crudo ("C1_1831") trae el año como dato
        txt = PLANTILLAS[h["tipo"]].format(corte=corte_ref, limite="la fecha del corte" if h["fecha_corte"] else "ese corte")
        q = {"id": f"Q-{base}-{h['corte']}-{h['tipo']}", "tipo": h["tipo"], "corte": h["corte"], "corte_idx": h["corte_idx"],
             "regla_hueco": h["regla"], "texto": txt, "reglas_respuesta": REGLAS_RESPUESTA,
             "limite_sellado": {"fecha_max": limite, "z": H["z"], "z_idx": H["z_idx"]}}
        q["validacion"] = validar_pregunta(txt, R)
        preguntas.append(q)
    return {"huecos": H, "preguntas": preguntas}


# ------------------------------------------------------------------ 3. adaptadores
class AdaptadorOffline:
    nombre = "offline"
    def responder(self, pregunta: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        return None


class AdaptadorMock:
    """Respuestas fijas de prueba (JSON: {case_key: {pregunta_id_o_'corte|tipo': respuesta}})."""
    nombre = "mock"
    def __init__(self, fixture: Mapping[str, Any], case_key: str):
        self.tabla = dict((fixture or {}).get(case_key) or {})
    def responder(self, pregunta: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        return self.tabla.get(pregunta["id"]) or self.tabla.get(f"{pregunta['corte']}|{pregunta['tipo']}")


class AdaptadorExterno:
    """Enchufe para un LLM real: se inyecta `llamar(pregunta_sellada) -> dict`. No se usa en pruebas (sin red)."""
    nombre = "externo"
    def __init__(self, llamar: Callable[[Mapping[str, Any]], Optional[Dict[str, Any]]]):
        self.llamar = llamar
    def responder(self, pregunta: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        return self.llamar(pregunta)


# CABLEADO_CALDERO_20261112 (4): adaptador REAL al LM del par gratis
# (Gemini, client.py del conector custom.gemini). Antes, el modo "on" del
# runner usaba AdaptadorOffline, que nunca responde: fingir que corre.
# Este adaptador pregunta de verdad: construye el prompt desde la pregunta
# sellada + los hechos del corte, llama al CLI de Gemini y devuelve
# {"texto","tokens","fuente"}. Nunca levanta: cualquier fallo (red, CLI,
# JSON, timeout) devuelve None (SIN_RESPUESTA) y la corrida sigue.
# No decide H: solo engrosa el input; los filtros F0-F5 y
# verificar_no_escribe_H siguen mandando.
class AdaptadorGemini:
    nombre = "gemini-3-flash-preview"
    def __init__(self, case=None, modelo: str = "gemini-3-flash-preview", timeout: float = 60.0, cli=None):
        self.case = dict(case or {})
        self.modelo = modelo
        self.timeout = float(timeout)
        self.cli = Path(cli or os.environ.get("GEMINI_CLI") or (Path.home() / "workspace/custom-connectors/custom.gemini/bin/client.py"))
        if not self.cli.is_file():
            raise FileNotFoundError(f"GEMINI_CLI_AUSENTE:{self.cli}")
        self._hechos = {}
        for c in (self.case.get("cuts") or []):
            self._hechos[str(c.get("id"))] = str(c.get("hecho") or c.get("narracion") or "")[:1500]

    def responder(self, pregunta: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return self._responder(pregunta)
        except Exception:
            return None

    def _responder(self, pregunta: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        corte = str(pregunta.get("corte") or "")
        # Referencia sin año y límite sin fecha: el año no entra como dato (regla de Mj).
        corte_ref = "C" + str(int(pregunta.get("corte_idx", 0)) + 1) if str(pregunta.get("corte_idx", "")).strip() != "" else _sin_anios(corte)
        limite = "ese corte"
        hecho = _sin_anios(self._hechos.get(corte, ""))
        prompt = (
            "Describe hechos observables de un caso, solo hasta el corte indicado. "
            f"Corte {corte_ref} (nada posterior a {limite}). "
            f"Hechos del corte: {hecho or '(sin texto)'} "
            f"Pregunta: {pregunta.get('texto') or ''} "
            "Reglas estrictas: solo hechos observables en ese corte; roles genéricos, sin nombres propios de personas, "
            "sin años ni fechas, sin valoraciones, sin desenlaces, sin hipótesis, sin arquetipos, sin predicciones, "
            "sin mencionar lo que pasó después. "
            "Responde SOLO con este JSON, sin más texto: {\"texto\": \"...\", \"tokens\": [\"palabra1\", \"palabra2\"]} "
            "donde tokens son 0 a 2 palabras simples que aparecen en los hechos del corte (o lista vacía)."
        )
        r = subprocess.run([sys.executable, str(self.cli), "generate", "--model", self.modelo, "--prompt", prompt],
                           capture_output=True, text=True, timeout=self.timeout)
        out = (r.stdout or "").strip()
        if not out:
            return None
        ini, fin = out.find("{"), out.rfind("}")
        if ini < 0 or fin <= ini:
            return None
        data = json.loads(out[ini:fin + 1])
        texto = str(data.get("texto") or "").strip()
        toks = [str(t).strip() for t in (data.get("tokens") or []) if str(t).strip()][:2]
        if not texto:
            return None
        return {"texto": texto, "tokens": toks, "fuente": "gemini:" + self.modelo}


# ------------------------------------------------------------------ 4. filtros
def filtrar_respuesta(resp: Mapping[str, Any], q: Mapping[str, Any], case: Mapping[str, Any], R: Recursos) -> Dict[str, Any]:
    cuts = list(case.get("cuts") or [])
    zi = q["limite_sellado"]["z_idx"]; idx = q["corte_idx"]
    texto = str(resp.get("texto") or "")
    t = _n(texto)
    rech: List[str] = []; neutral: List[str] = []; avisos: List[str] = []
    # F0 procedencia / rango
    if not str(resp.get("fuente") or "").strip():
        rech.append("F0_SIN_FUENTE")
    if idx > zi or str(resp.get("corte") or q["corte"]) != str(q["corte"]):
        rech.append("F0_CORTE_FUERA_DE_LIMITE")
    if not texto.strip():
        rech.append("F0_VACIA")
    # F1 temporal
    anio_corte = _anio(q["limite_sellado"]["fecha_max"]) if q["limite_sellado"]["fecha_max"] else None
    anio_z = _anio(q["limite_sellado"]["z"])
    anios = [int(a) for a in RX_ANIO.findall(texto)]
    tope = min([a for a in (anio_corte, anio_z) if a] or [None]) if (anio_corte or anio_z) else None
    if tope and any(a > tope for a in anios):
        rech.append(f"F1_ANIO_POSTERIOR_AL_CORTE:{max(anios)}>{tope}")
    if not tope and anios:
        rech.append("F1_ANIO_NO_VERIFICABLE_SIN_FECHA_DE_CORTE_NI_Z")
    f = _hits(RX_FUTURO, t)
    if f: rech.append("F1_MARCADOR_FUTURO:" + ",".join(f))
    d = _hits(RX_DESENLACE, t)
    if d: rech.append("F1_DESENLACE:" + ",".join(d))
    if idx < len(cuts) - 1 and RX_MUERTE.search(t):
        rech.append("F1_MUERTE_ANTES_DEL_ULTIMO_CORTE")
    fa = _hits(RX_FAMA, t)
    if fa: rech.append("F1_FAMA_POSTERIDAD:" + ",".join(fa))
    for m in RX_CORTE_REF.finditer(texto):
        ref = m.group(1)
        ids = [str(c.get("id")) for c in cuts]
        if ref in ids and ids.index(ref) > idx:
            rech.append("F1_REFIERE_CORTE_POSTERIOR:" + ref)
    # F2 hipótesis / 244 / arquetipo / evaluativo / teleología
    h = _hits(RX_HIPOTESIS, t)
    if h: rech.append("F2_HIPOTESIS_APUESTA:" + ",".join(h))
    lem = sorted({l for l in R.lemas if l not in ROLES_016_PERMITIDOS and re.search(r"\b" + re.escape(l) + r"\b", t)})
    ids = sorted({i for i in R.ids if re.search(r"\b" + re.escape(i) + r"\b", texto.casefold())})
    if lem or ids: rech.append("F2_ETIQUETA_244:" + ",".join(lem + ids))
    per = sorted({l for l in R.personaje if l not in ROLES_016_PERMITIDOS and re.search(r"\b" + re.escape(l) + r"(?:es|s|a|as)?\b", t)})
    if per: rech.append("F2_ARQUETIPO:" + ",".join(per))
    ev = _hits(RX_EVALUATIVO, t)
    if ev: rech.append("F2_EVALUATIVO:" + ",".join(ev))
    te = _hits(RX_TELEO, t)
    if te: rech.append("F2_TELEOLOGIA:" + ",".join(te))
    # F4 fuga historiográfica
    fu = _hits(RX_FUGA, t)
    if fu: rech.append("F4_FUGA_HISTORIOGRAFICA:" + ",".join(fu))
    # F3 nombres/años -> neutralizar (filtro 017, tipos activos en vivo)
    mini = {"case_id": "consulta", "person": case.get("person"), "caldero_identity": case.get("caldero_identity"),
            "cuts": [{"id": q["corte"], "hecho": texto}]}
    try:
        payload, inf = R.f017.aplicar(mini, set(R.f017.TIPOS_ACTIVOS_EN_VIVO), R.cat)
        txt_n = payload["cuts"][0]["hecho"]
        for b in inf["reporte"]["banderas"]:
            if b["tipo"] in R.f017.TIPOS_ACTIVOS_EN_VIVO and b.get("inicio") is not None:
                neutral.append(f"F3_{b['tipo']}:{R.f017.huella(b['span'])}")
    except Exception as e:  # sin filtro 017 no entra nada
        txt_n = ""; rech.append(f"F3_FILTRO_017_ERROR:{type(e).__name__}")
    txt_n = re.sub(r"\bNP\d+\b", "OTRO_AGENTE", txt_n)
    txt_n = txt_n.replace("(fecha)", "").replace("  ", " ").strip(" ;,")
    resid = [w for w in re.findall(r"[a-z]+", _n(txt_n)) if w in R.veto015]
    if resid or RX_ANIO.search(txt_n):
        rech.append("F3_RESIDUO_NOMBRE_O_ANIO")
    # F5 observable mínimo
    cont = [w for w in re.findall(r"[a-z]+", _n(txt_n)) if w not in PALABRAS_VACIAS and len(w) > 2]
    if len(cont) < 3:
        rech.append("F5_SIN_CONTENIDO_OBSERVABLE")
    # tokens
    tok_ok, tok_rech = [], []
    ya = {str(p[0]) for e in ("P", "A", "C") for p in (cuts[idx].get(e) or []) if isinstance(p, (list, tuple)) and p} if idx < len(cuts) else set()
    for tk in list(resp.get("tokens") or [])[:8]:
        k = str(tk).strip()
        kn = _n(k).replace("_", " ")
        if k.casefold() in R.ids or kn in R.lemas:
            tok_rech.append((k, "TOKEN_ETIQUETA_244"))
        elif re.fullmatch(r"\d+", k) or _n(k) in R.veto015:
            tok_rech.append((k, "TOKEN_NOMBRE_O_NUMERO"))
        elif k not in R.vocab:
            tok_rech.append((k, "TOKEN_FUERA_DE_VOCABULARIO"))
        elif k in ya:
            tok_rech.append((k, "TOKEN_YA_EN_CORTE"))
        elif len(tok_ok) >= MAX_TOKENS_POR_RESPUESTA:
            tok_rech.append((k, "TOKEN_EXCEDE_MAXIMO"))
        else:
            tok_ok.append(k)
    estado = "RECHAZADA" if rech else ("ACEPTADA_NEUTRALIZADA" if neutral else "ACEPTADA")
    return {"estado": estado, "motivos_rechazo": rech, "neutralizaciones": neutral, "avisos": avisos,
            "texto_neutral": (txt_n if not rech else None), "tokens_aceptados": (tok_ok if not rech else []),
            "tokens_rechazados": tok_rech}


# ------------------------------------------------------------------ 5. aplicar
def verificar_no_escribe_H(orig: Mapping[str, Any], aug: Mapping[str, Any], zi: int) -> List[str]:
    v = []
    ko = {k for k in orig if k != "cuts"}; ka = {k for k in aug if k != "cuts"}
    if ko != ka: v.append("CLAVES_DE_CASO_CAMBIADAS:" + ",".join(sorted(ko ^ ka)))
    for k in ko & ka:
        if json.dumps(orig[k], sort_keys=True, default=str) != json.dumps(aug[k], sort_keys=True, default=str):
            v.append("CAMPO_DE_CASO_CAMBIADO:" + k)
    co, ca = list(orig.get("cuts") or []), list(aug.get("cuts") or [])
    if len(co) != len(ca): v.append("N_CORTES_CAMBIADO")
    for i, (a, b) in enumerate(zip(co, ca)):
        for k in set(a) | set(b):
            if json.dumps(a.get(k), sort_keys=True, default=str) != json.dumps(b.get(k), sort_keys=True, default=str):
                if k not in CAMPOS_PERMITIDOS_CORTE: v.append(f"CORTE_{i}_CAMPO_NO_PERMITIDO:{k}")
                elif i > zi: v.append(f"CORTE_{i}_POSTERIOR_A_Z")
                elif k == "C":
                    old = [list(p) for p in a.get("C") or []]
                    if [list(p) for p in (b.get("C") or [])][:len(old)] != old: v.append(f"CORTE_{i}_C_EXISTENTE_MODIFICADO")
    return v


def aplicar(case: Mapping[str, Any], adaptador, R: Recursos) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Devuelve (case_aumentado, traza_para_resultado_sin_contenido, sidecar_sellado)."""
    orig = copy.deepcopy(dict(case)); aug = copy.deepcopy(dict(case))
    P = construir_preguntas(orig, R)
    zi = P["huecos"]["z_idx"]
    campo = _campo_texto(orig)
    filas, sellado = [], []
    cubierto = {"ANTAGONISTA": None, "INSTITUCIONES_idx": None}
    # Puente PRE-H sellado (Línea B, PATCH13): la búsqueda externa del host quedó ligada al sha de la
    # semilla ciega (tokens P/A/C de los cortes). Si la consulta agrega tokens, el puente se rechaza
    # (SEARCH_BRIDGE_QUERY_MISMATCH) y se pierden los tokens análogos. Con puente: entra solo el texto
    # neutral; los tokens quedan RETENIDOS (sidecar + traza) hasta re-ejecutar la búsqueda del host.
    puente = isinstance(orig.get("caldero_search_bridge"), dict) and not orig.get("caldero_archetype_input")
    for q in P["preguntas"]:
        fila = {"pregunta_id": q["id"], "corte": q["corte"], "tipo": q["tipo"], "regla_hueco": q["regla_hueco"]}
        # hueco ya cubierto por una respuesta aceptada anterior (regla acumulada / corte anterior): no se pregunta otra vez
        if q["tipo"] == "ANTAGONISTA" and cubierto["ANTAGONISTA"] is not None:
            fila.update(estado="OMITIDA_HUECO_CUBIERTO", motivos=["antagonista aceptado en " + str(cubierto["ANTAGONISTA"])]); filas.append(fila); continue
        if q["tipo"] == "INSTITUCIONES" and cubierto["INSTITUCIONES_idx"] is not None and q["corte_idx"] == cubierto["INSTITUCIONES_idx"] + 1:
            fila.update(estado="OMITIDA_HUECO_CUBIERTO", motivos=["institución aceptada en el corte anterior"]); filas.append(fila); continue
        if q["validacion"]:
            fila.update(estado="PREGUNTA_RECHAZADA", motivos=q["validacion"]); filas.append(fila); continue
        sobre = {k: q[k] for k in ("id", "tipo", "corte", "corte_idx", "texto", "reglas_respuesta", "limite_sellado")}
        resp = adaptador.responder(sobre)
        if not resp:
            fila.update(estado="SIN_RESPUESTA"); filas.append(fila); continue
        r = filtrar_respuesta(resp, q, orig, R)
        fila.update(estado=r["estado"], motivos=r["motivos_rechazo"], neutralizaciones=r["neutralizaciones"],
                    tokens_aceptados=r["tokens_aceptados"], tokens_rechazados=[f"{a}:{b}" for a, b in r["tokens_rechazados"]],
                    etiqueta_prueba=resp.get("etiqueta_prueba"))
        sellado.append({"pregunta_id": q["id"], "corte": q["corte"], "tipo": q["tipo"], "texto_pregunta": q["texto"],
                        "limite": q["limite_sellado"], "fuente": resp.get("fuente"), "adaptador": getattr(adaptador, "nombre", "?"),
                        "texto_original": resp.get("texto"), "sha256_texto_original": hashlib.sha256(str(resp.get("texto") or "").encode("utf-8")).hexdigest(),
                        "tokens_propuestos": resp.get("tokens"), "estado": r["estado"], "motivos_rechazo": r["motivos_rechazo"],
                        "texto_neutral_entregado": r["texto_neutral"], "tokens_entregados": r["tokens_aceptados"],
                        "etiqueta_prueba": resp.get("etiqueta_prueba")})
        if r["estado"].startswith("ACEPTADA"):
            if q["tipo"] == "ANTAGONISTA": cubierto["ANTAGONISTA"] = q["corte"]
            if q["tipo"] == "INSTITUCIONES": cubierto["INSTITUCIONES_idx"] = q["corte_idx"]
            c = aug["cuts"][q["corte_idx"]]
            prev = str(c.get(campo) or "").strip()
            c[campo] = (prev + ("; " if prev else "") + r["texto_neutral"]) if r["texto_neutral"] else prev
            ejeC = [list(p) for p in (c.get("C") or [])]
            dentro = {str(p[0]) for e in ("P", "A", "C") for p in (c.get(e) or []) if isinstance(p, (list, tuple)) and p}
            entr = []
            if puente:
                fila["tokens_retenidos_por_puente_sellado"] = list(r["tokens_aceptados"])
            for tk in ([] if puente else r["tokens_aceptados"]):
                if len(ejeC) >= 5 or tk in dentro:
                    continue
                ejeC.append([tk, PESO_TOKEN]); dentro.add(tk); entr.append(tk)
            if entr or "C" in c:
                c["C"] = ejeC
            fila["tokens_entregados_al_motor"] = entr
        filas.append(fila)
    viol = verificar_no_escribe_H(orig, aug, zi)
    if viol:  # nunca se entrega un caso que toque H o algo fuera de lo permitido
        aug = orig
    cont = {}
    for f in filas:
        cont[f["estado"]] = cont.get(f["estado"], 0) + 1
    traza = {"version": VERSION, "contrato": CONTRATO, "adaptador": getattr(adaptador, "nombre", "?"),
             "z": P["huecos"]["z"], "z_idx": zi, "campo_texto": campo, "n_preguntas": len(P["preguntas"]),
             "conteo_por_estado": dict(sorted(cont.items())), "verificacion_no_escribe_H": viol or "OK",
             "filas": [{k: v for k, v in f.items() if k not in ("etiqueta_prueba",)} for f in filas],
             "can_decide_H": False, "escribe_H": False, "llamadas_red": 0,
             "modo_tokens": "RETENIDOS_PUENTE_PRE_H_SELLADO" if puente else "ENTREGADOS_EJE_C",
             "nota": "el motor recibe solo texto neutral y tokens de vocabulario canónico (peso fijo); la procedencia está en el sidecar sellado"}
    side = {"version": VERSION, "contrato": CONTRATO, "case_id": orig.get("case_id"), "sellado": True,
            "preguntas": P["preguntas"], "huecos": P["huecos"], "respuestas": sellado,
            "sha256_case_original": hashlib.sha256(json.dumps(orig, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest(),
            "sha256_case_aumentado": hashlib.sha256(json.dumps(aug, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()}
    return aug, traza, side
