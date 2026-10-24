#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sidecar_caldero_busqueda_arquetipos.py

SIDE-CAR AISLADO — implementación inicial del SPEC_USO_CALDERO_BUSQUEDA_ARQUETIPOS.md

Candados:
    TOCA_F = NO
    TOCA_244 = NO
    TOCA_Engine_V5 = NO
    TOCA_FREEZE = NO

Este módulo NO integra ni modifica el motor canónico, patrones, P/A/C,
freeze, H1/H2 ni probabilidades.

Flujo:
    arquetipo ciego
        -> construcción de query
        -> búsqueda externa (adapter)
        -> filtro externo de self-match
        -> extracción tokenizada
        -> salida lateral

Los identificadores reales del caso viven exclusivamente en SelfMatchIdentity
y solo son consumidos por el filtro externo. No se entregan al resultado
tokenizado que recibe Caldero.

La búsqueda real queda desacoplada mediante SearchAdapter. Así el sidecar puede
probarse sin red y luego conectarse al buscador elegido.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from collections import Counter
from typing import Any, Iterable, Mapping, Protocol, Sequence
import hashlib
import json
import re
import os
import urllib.request
import urllib.error
from html.parser import HTMLParser
from urllib.parse import urlencode, unquote


CANON_LOCK = {
    "TOCA_F": False,
    "TOCA_244": False,
    "TOCA_Engine_V5": False,
    "TOCA_FREEZE": False,
}

VERSION = "0.1"
SCHEMA = "caldero_archetype_search_sidecar_v1"

# Del spec: estos son los tipos de identificadores que el filtro puede recibir.
# El criterio fino de coincidencia queda deliberadamente configurable.
@dataclass(frozen=True)
class SelfMatchIdentity:
    name: str | None = None
    birth_date: str | None = None
    death_date: str | None = None
    unique_facts: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "SelfMatchIdentity":
        facts = raw.get("unique_facts", raw.get("hechos_unicos", ())) or ()
        return cls(
            name=raw.get("name", raw.get("nombre")),
            birth_date=raw.get("birth_date", raw.get("fecha_nacimiento")),
            death_date=raw.get("death_date", raw.get("fecha_muerte")),
            unique_facts=tuple(str(x) for x in facts),
        )


@dataclass(frozen=True)
class ArchetypeInput:
    """Entrada ciega: no debe contener identidad real del caso."""
    tokens: tuple[str, ...] = ()
    patterns: tuple[str, ...] = ()
    families: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ArchetypeInput":
        def vals(*keys: str) -> tuple[str, ...]:
            for k in keys:
                v = raw.get(k)
                if v is not None:
                    if isinstance(v, str):
                        return (v,)
                    return tuple(str(x) for x in v)
            return ()
        return cls(
            tokens=vals("tokens", "tokens_activos"),
            patterns=vals("patterns", "patrones_activos"),
            families=vals("families", "familias_activas"),
        )


@dataclass(frozen=True)
class SearchSource:
    url: str
    title: str = ""
    snippet: str = ""
    metadata: Mapping[str, Any] | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "SearchSource":
        url = str(raw.get("url") or raw.get("origen") or raw.get("id") or "llm://source")
        title = str(raw.get("title") or raw.get("titulo") or raw.get("id") or "")
        snippet = str(raw.get("snippet") or raw.get("texto") or raw.get("text") or "")
        meta = raw.get("metadata") if isinstance(raw.get("metadata"), Mapping) else {k: raw[k] for k in raw if k not in ("url", "title", "snippet", "texto", "text", "titulo", "origen", "id")}
        return cls(url=url, title=title, snippet=snippet, metadata=meta or None)

    def as_dict(self) -> dict[str, Any]:
        # Metadata es opcional. No serializar metadata=None como si fuera un campo
        # de datos emitido y ausente; distinguirlo explícitamente sin inventar contenido.
        out = {"url": self.url, "title": self.title, "snippet": self.snippet}
        if self.metadata:
            out["metadata"] = dict(self.metadata)
        else:
            out["metadata_estado"] = "NO_ENTREGADA_POR_FUENTE"
        return out


class SearchAdapter(Protocol):
    def search(self, query: str) -> Sequence[SearchSource]:
        """Ejecuta una búsqueda y devuelve fuentes completas antes del filtro."""
        ...


class StaticSearchAdapter:
    """Adapter de prueba: permite probar el sidecar sin red."""

    def __init__(self, sources: Sequence[SearchSource]):
        self.sources = list(sources)

    def search(self, query: str) -> Sequence[SearchSource]:
        return list(self.sources)


class ExternalSearchConfigurationError(RuntimeError):
    """La búsqueda externa requerida no está configurada."""


class ExaSearchAdapter:
    """Búsqueda externa real mediante Exa API. Requiere EXA_API_KEY en el entorno.

    No hace fallback silencioso a una lista vacía: los errores se propagan para que
    el recibo pueda marcar la etapa obligatoria como fallida.
    """
    def __init__(self, api_key: str, num_results: int = 8, timeout: float = 20.0):
        if not api_key or not api_key.strip():
            raise ExternalSearchConfigurationError("EXA_API_KEY ausente; búsqueda externa obligatoria no configurada")
        self.api_key = api_key.strip()
        self.num_results = max(1, min(int(num_results), 10))
        self.timeout = float(timeout)
        self.last_receipt: dict[str, Any] = {"provider": "exa", "status": "NOT_RUN", "query_count": 0, "result_count": 0}

    @classmethod
    def from_env(cls):
        return cls(os.environ.get("EXA_API_KEY", ""))

    def search(self, query: str) -> Sequence[SearchSource]:
        if not query or not query.strip():
            raise ValueError("query_externa_vacia")
        payload = {
            "query": query,
            "type": "auto",
            "numResults": self.num_results,
            "contents": {"text": {"maxCharacters": 1600}},
        }
        req = urllib.request.Request(
            "https://api.exa.ai/search",
            data=json.dumps(payload).encode("utf-8"),
            headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            self.last_receipt = {"provider": "exa", "status": "FAILED", "query_count": 1, "result_count": 0, "error": f"{type(exc).__name__}:{exc}"}
            raise RuntimeError(f"búsqueda Exa fallida: {type(exc).__name__}: {exc}") from exc
        rows = raw.get("results") or []
        sources = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            sources.append(SearchSource(
                url=str(row.get("url") or ""),
                title=str(row.get("title") or ""),
                snippet=str(row.get("text") or row.get("snippet") or ""),
                metadata={"provider": "exa", "publishedDate": row.get("publishedDate"), "author": row.get("author")},
            ))
        self.last_receipt = {"provider": "exa", "status": "EXECUTED", "query_count": 1, "result_count": len(sources), "query_sha256": _stable_hash(query), "http_status": 200}
        return sources



class OpenAIResponsesWebSearchAdapter:
    """Búsqueda web nativa de OpenAI Responses API. Requiere OPENAI_API_KEY.

    No usa la sesión privada de ChatGPT: usa el endpoint API y su herramienta
    web_search. La evidencia solo cuenta como ejecutada si hay citas URL HTTP(S).
    """
    def __init__(self, api_key: str, model: str | None = None, num_results: int = 8, timeout: float = 60.0):
        if not api_key or not api_key.strip():
            raise ExternalSearchConfigurationError("OPENAI_API_KEY ausente")
        self.api_key=api_key.strip()
        self.model=(model or os.environ.get("OPENAI_SEARCH_MODEL") or "gpt-5.4").strip()
        self.num_results=max(1,min(int(num_results),10)); self.timeout=float(timeout)
        self.last_receipt={"provider":"openai_responses_web_search","status":"NOT_RUN","query_count":0,"result_count":0,"model":self.model}

    @classmethod
    def from_env(cls):
        return cls(os.environ.get("OPENAI_API_KEY", ""), model=os.environ.get("OPENAI_SEARCH_MODEL"))

    def search(self, query: str) -> Sequence[SearchSource]:
        if not query or not query.strip(): raise ValueError("query_externa_vacia")
        payload={"model":self.model,"tools":[{"type":"web_search"}],"input":query}
        req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(payload).encode("utf-8"),headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as response:
                raw=json.loads(response.read().decode("utf-8")); http_status=getattr(response,"status",200)
        except Exception as exc:
            self.last_receipt={"provider":"openai_responses_web_search","status":"FAILED","query_count":1,"result_count":0,"model":self.model,"error":f"{type(exc).__name__}:{exc}"}
            raise RuntimeError(f"búsqueda OpenAI Responses web_search fallida: {type(exc).__name__}: {exc}") from exc
        texts=[]; citations=[]
        for item in raw.get("output") or []:
            if not isinstance(item,dict): continue
            for part in item.get("content") or []:
                if not isinstance(part,dict): continue
                if part.get("text"): texts.append(str(part.get("text")))
                for ann in part.get("annotations") or []:
                    if not isinstance(ann,dict) or ann.get("type")!="url_citation": continue
                    data=ann.get("url_citation") if isinstance(ann.get("url_citation"),dict) else ann
                    url=str(data.get("url") or "")
                    if url.startswith(("https://","http://")):
                        citations.append(SearchSource(url=url,title=str(data.get("title") or ""),snippet=" ".join(texts)[:1600],metadata={"provider":"openai_responses_web_search","model":self.model}))
        unique=[]; seen=set()
        for source in citations:
            if source.url not in seen: seen.add(source.url); unique.append(source)
            if len(unique)>=self.num_results: break
        if not unique:
            self.last_receipt={"provider":"openai_responses_web_search","status":"FAILED_NO_URL_CITATIONS","query_count":1,"result_count":0,"model":self.model,"http_status":http_status}
            raise RuntimeError("OpenAI Responses web_search no devolvió citas URL verificables")
        self.last_receipt={"provider":"openai_responses_web_search","status":"EXECUTED","query_count":1,"result_count":len(unique),"query_sha256":hashlib.sha256(query.encode("utf-8")).hexdigest(),"model":self.model,"http_status":http_status}
        return unique


class OpenRouterWebSearchAdapter:
    """Búsqueda web agnóstica al modelo mediante OpenRouter server tool.

    Puede enrutar a búsqueda nativa del proveedor/modelo y no requiere Exa API key.
    Requiere OPENROUTER_API_KEY. Solo considera ejecutada la búsqueda si la respuesta
    devuelve citas URL verificables.
    """
    def __init__(self, api_key: str, model: str | None = None, num_results: int = 8, timeout: float = 45.0, engine: str = "auto"):
        if not api_key or not api_key.strip():
            raise ExternalSearchConfigurationError("OPENROUTER_API_KEY ausente")
        self.api_key = api_key.strip()
        self.model = (model or os.environ.get("OPENROUTER_SEARCH_MODEL") or "openai/gpt-5.2").strip()
        self.num_results = max(1, min(int(num_results), 10))
        self.timeout = float(timeout)
        self.engine = engine or os.environ.get("OPENROUTER_WEB_SEARCH_ENGINE", "auto")
        self.last_receipt = {"provider": "openrouter", "status": "NOT_RUN", "query_count": 0, "result_count": 0, "model": self.model}

    @classmethod
    def from_env(cls):
        return cls(os.environ.get("OPENROUTER_API_KEY", ""), engine=os.environ.get("OPENROUTER_WEB_SEARCH_ENGINE", "auto"))

    def search(self, query: str) -> Sequence[SearchSource]:
        if not query or not query.strip():
            raise ValueError("query_externa_vacia")
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": (
                "Debes ejecutar la herramienta de búsqueda web para esta consulta. "
                "No respondas solo de memoria. Busca fuentes que permitan identificar "
                "arquetipos, patrones o trayectorias análogas a estos términos ciegos: " + query + ". "
                "Devuelve una síntesis breve con citas URL de las fuentes encontradas."
            )}],
            "tools": [{"type": "openrouter:web_search", "parameters": {"engine": self.engine, "max_results": self.num_results}}],
            "max_tokens": 1200,
        }
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json", "HTTP-Referer": "https://openrouter.ai", "X-Title": "V15.3 StinkBox archetype search"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
                http_status = getattr(response, "status", 200)
        except Exception as exc:
            self.last_receipt = {"provider": "openrouter", "status": "FAILED", "query_count": 1, "result_count": 0, "model": self.model, "error": f"{type(exc).__name__}:{exc}", "query_sha256": hashlib.sha256(query.encode()).hexdigest()}
            raise RuntimeError(f"búsqueda OpenRouter fallida: {type(exc).__name__}: {exc}") from exc
        message = (((raw.get("choices") or [{}])[0]).get("message") or {})
        annotations = message.get("annotations") or []
        content = message.get("content") or ""
        found: dict[str, SearchSource] = {}
        for ann in annotations:
            if not isinstance(ann, dict):
                continue
            cite = ann.get("url_citation") or ann.get("citation") or ann
            if not isinstance(cite, dict):
                continue
            url = str(cite.get("url") or cite.get("uri") or "").strip()
            if url.startswith(("http://", "https://")):
                found[url] = SearchSource(url=url, title=str(cite.get("title") or ""), snippet=str(cite.get("content") or cite.get("snippet") or content)[:1800], metadata={"provider": "openrouter", "model": self.model, "annotation_type": ann.get("type")})
        # Compatibilidad con endpoints que incluyan URLs citadas en el texto sin annotations.
        for url in re.findall(r'https?://[^\s)\]}>"\']+', str(content)):
            url = url.rstrip(".,;:")
            if url not in found:
                found[url] = SearchSource(url=url, title="", snippet=str(content)[:1800], metadata={"provider": "openrouter", "model": self.model, "extracted_from": "cited_response_text"})
        sources = list(found.values())[:self.num_results]
        if not sources:
            self.last_receipt = {"provider": "openrouter", "status": "FAILED_NO_CITATIONS", "query_count": 1, "result_count": 0, "model": self.model, "http_status": http_status, "query_sha256": hashlib.sha256(query.encode()).hexdigest(), "response_excerpt": str(content)[:300]}
            raise RuntimeError("OpenRouter respondió sin citas URL verificables; búsqueda no acreditada")
        self.last_receipt = {"provider": "openrouter", "status": "EXECUTED", "query_count": 1, "result_count": len(sources), "model": self.model, "engine": self.engine, "http_status": http_status, "query_sha256": hashlib.sha256(query.encode()).hexdigest()}
        return sources


class TavilySearchAdapter:
    """Búsqueda web directa por Tavily, alternativa independiente de Exa."""
    def __init__(self, api_key: str, num_results: int = 8, timeout: float = 20.0):
        if not api_key or not api_key.strip(): raise ExternalSearchConfigurationError("TAVILY_API_KEY ausente")
        self.api_key, self.num_results, self.timeout = api_key.strip(), max(1,min(int(num_results),10)), float(timeout)
        self.last_receipt = {"provider":"tavily","status":"NOT_RUN","query_count":0,"result_count":0}
    @classmethod
    def from_env(cls): return cls(os.environ.get("TAVILY_API_KEY", ""))
    def search(self, query: str) -> Sequence[SearchSource]:
        payload={"api_key":self.api_key,"query":query,"max_results":self.num_results,"search_depth":"basic","include_answer":False}
        req=urllib.request.Request("https://api.tavily.com/search",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as r: raw=json.loads(r.read().decode()); code=getattr(r,"status",200)
        except Exception as exc:
            self.last_receipt={"provider":"tavily","status":"FAILED","query_count":1,"result_count":0,"error":f"{type(exc).__name__}:{exc}"}; raise RuntimeError(f"búsqueda Tavily fallida: {exc}") from exc
        rows=raw.get("results") or []
        out=[SearchSource(url=str(x.get("url") or ""),title=str(x.get("title") or ""),snippet=str(x.get("content") or ""),metadata={"provider":"tavily","score":x.get("score")}) for x in rows if isinstance(x,dict) and str(x.get("url","")).startswith("http")]
        if not out: self.last_receipt={"provider":"tavily","status":"FAILED_NO_RESULTS","query_count":1,"result_count":0,"http_status":code}; raise RuntimeError("Tavily no devolvió resultados URL verificables")
        self.last_receipt={"provider":"tavily","status":"EXECUTED","query_count":1,"result_count":len(out),"http_status":code,"query_sha256":hashlib.sha256(query.encode()).hexdigest()}
        return out



class _DDGParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.current=None; self.capture=None; self.buf=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); cls=a.get("class","")
        if tag=="a" and "result__a" in cls:
            self.current={"url":a.get("href", ""),"title":""}; self.capture="title"; self.buf=[]
        elif tag in ("a","div") and ("result__snippet" in cls or "result__body" in cls):
            self.capture="snippet"; self.buf=[]
    def handle_data(self, data):
        if self.capture: self.buf.append(data)
    def handle_endtag(self, tag):
        if tag=="a" and self.current is not None and self.capture=="title":
            self.current["title"]=" ".join("".join(self.buf).split()); self.rows.append(self.current); self.current=None; self.capture=None; self.buf=[]
        elif tag=="div" and self.capture=="snippet":
            snippet=" ".join("".join(self.buf).split())
            if snippet and self.rows and not self.rows[-1].get("snippet"): self.rows[-1]["snippet"]=snippet
            self.capture=None; self.buf=[]


class DuckDuckGoHtmlSearchAdapter:
    """Búsqueda web HTML sin API key; se usa como fallback de red, no de memoria."""
    def __init__(self, num_results: int=8, timeout: float=20.0):
        self.num_results=max(1,min(int(num_results),10)); self.timeout=float(timeout)
        self.last_receipt={"provider":"duckduckgo_html","status":"NOT_RUN","query_count":0,"result_count":0}
    def search(self, query: str) -> Sequence[SearchSource]:
        url="https://html.duckduckgo.com/html/?"+urlencode({"q":query})
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; V15.3-Research/1.0)","Accept":"text/html"})
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as r: html=r.read().decode("utf-8","replace"); code=getattr(r,"status",200)
        except Exception as exc:
            self.last_receipt={"provider":"duckduckgo_html","status":"FAILED","query_count":1,"result_count":0,"error":f"{type(exc).__name__}:{exc}"}
            raise RuntimeError(f"búsqueda DuckDuckGo HTML fallida: {exc}") from exc
        parser=_DDGParser(); parser.feed(html)
        rows=[]
        for row in parser.rows:
            target=str(row.get("url") or "").strip()
            if target.startswith("//duckduckgo.com/l/?"):
                from urllib.parse import parse_qs, urlparse
                target=parse_qs(urlparse("https:"+target).query).get("uddg",[target])[0]
            if target.startswith("http") and "duckduckgo.com" not in target:
                rows.append(SearchSource(url=target,title=row.get("title", ""),snippet=row.get("snippet", ""),metadata={"provider":"duckduckgo_html"}))
            if len(rows)>=self.num_results: break
        if not rows:
            self.last_receipt={"provider":"duckduckgo_html","status":"FAILED_NO_RESULTS","query_count":1,"result_count":0,"http_status":code,"query_sha256":hashlib.sha256(query.encode()).hexdigest()}
            raise RuntimeError("DuckDuckGo HTML no devolvió URLs de resultados verificables")
        self.last_receipt={"provider":"duckduckgo_html","status":"EXECUTED","query_count":1,"result_count":len(rows),"http_status":code,"query_sha256":hashlib.sha256(query.encode()).hexdigest()}
        return rows


class _GoogleParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.anchor=None; self.in_h3=False; self.title_buf=[]; self.snippets=[]; self.in_snippet=False; self.snip_buf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); cls=a.get("class","")
        if tag=="a" and a.get("href","").startswith("http") and "google.com" not in a.get("href",""):
            self.anchor=a.get("href"); self.title_buf=[]; self.in_h3=False
        if tag=="h3" and self.anchor: self.in_h3=True
        if tag=="div" and "VwiC3b" in cls: self.in_snippet=True; self.snip_buf=[]
    def handle_data(self,data):
        if self.anchor and self.in_h3: self.title_buf.append(data)
        if self.in_snippet: self.snip_buf.append(data)
    def handle_endtag(self,tag):
        if tag=="h3" and self.anchor:
            title=" ".join("".join(self.title_buf).split())
            if title: self.rows.append({"url":self.anchor,"title":title,"snippet":""})
            self.in_h3=False
        if tag=="a": self.anchor=None; self.in_h3=False
        if tag=="div" and self.in_snippet:
            snip=" ".join("".join(self.snip_buf).split())
            if snip and self.rows and not self.rows[-1]["snippet"]: self.rows[-1]["snippet"]=snip
            self.in_snippet=False; self.snip_buf=[]


class GoogleHtmlSearchAdapter:
    """Google HTML search without API key; browser-like query as requested."""
    def __init__(self, num_results: int=8, timeout: float=20.0):
        self.num_results=max(1,min(int(num_results),10)); self.timeout=float(timeout)
        self.last_receipt={"provider":"google_html","status":"NOT_RUN","query_count":0,"result_count":0}
    def search(self,query: str) -> Sequence[SearchSource]:
        url="https://www.google.com/search?"+urlencode({"q":query,"num":self.num_results,"hl":"en"})
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"})
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as r: html=r.read().decode("utf-8","replace"); code=getattr(r,"status",200)
        except Exception as exc:
            self.last_receipt={"provider":"google_html","status":"FAILED","query_count":1,"result_count":0,"error":f"{type(exc).__name__}:{exc}"}
            raise RuntimeError(f"búsqueda Google HTML fallida: {exc}") from exc
        parser=_GoogleParser(); parser.feed(html)
        rows=[]; seen=set()
        for row in parser.rows:
            if row['url'] not in seen: seen.add(row['url']); rows.append(SearchSource(url=row['url'],title=row['title'],snippet=row['snippet'],metadata={"provider":"google_html"}))
            if len(rows)>=self.num_results: break
        if not rows:
            self.last_receipt={"provider":"google_html","status":"FAILED_NO_RESULTS","query_count":1,"result_count":0,"http_status":code,"query_sha256":hashlib.sha256(query.encode()).hexdigest()}
            raise RuntimeError("Google HTML no devolvió URLs de resultados verificables")
        self.last_receipt={"provider":"google_html","status":"EXECUTED","query_count":1,"result_count":len(rows),"http_status":code,"query_sha256":hashlib.sha256(query.encode()).hexdigest()}
        return rows

def create_search_adapter(provider: str | None = None) -> SearchAdapter:
    """Selecciona proveedor configurable; no fija la arquitectura a Exa.

    SEARCH_PROVIDER=auto|openai|openrouter|tavily|brave|exa. Auto prioriza OpenAI Responses web_search
    (LLM + búsqueda nativa/auto), luego proveedores directos disponibles.
    """
    # TIRADA_20261024: Caldero es AGNÓSTICO al buscador. CALDERO_BUSCADOR (o SEARCH_PROVIDER)
    # =auto|ddgs|ddg|ddg_lite|bing|searx|wiki|google|exa|brave|serper|tavily (o lista "a,b").
    # auto = primer buscador libre que responda; claves solo si existen. No usa LLM.
    selected=(provider or os.environ.get("CALDERO_BUSCADOR") or os.environ.get("SEARCH_PROVIDER") or "auto").strip().casefold()
    if selected not in ("offline","openai","openrouter"):
        import importlib.util as _ilu, sys as _sys
        _p=os.path.join(os.path.dirname(os.path.abspath(__file__)),"caldero_buscadores.py")
        if "caldero_buscadores" not in _sys.modules:
            _sp=_ilu.spec_from_file_location("caldero_buscadores",_p); _m=_ilu.module_from_spec(_sp); _sys.modules["caldero_buscadores"]=_m; _sp.loader.exec_module(_m)
        try:
            return _sys.modules["caldero_buscadores"].crear_cadena(SearchSource,selected)
        except ValueError as exc:
            raise ExternalSearchConfigurationError(str(exc)) from exc
    constructors={
        "openai": lambda: OpenAIResponsesWebSearchAdapter.from_env(),
        "openrouter": lambda: OpenRouterWebSearchAdapter.from_env(),
        "tavily": lambda: TavilySearchAdapter.from_env(),
        "exa": lambda: ExaSearchAdapter.from_env(),
        "brave": lambda: BraveSearchAdapter.from_env(),
        "google": lambda: GoogleHtmlSearchAdapter(),
        "duckduckgo": lambda: DuckDuckGoHtmlSearchAdapter(),
    }
    if selected == "offline":  # UNIFICADO_20261011: pruebas sin red (determinista; misma ruta que proveedores fallidos)
        return OfflineSearchAdapter()
    if selected not in ("auto", *constructors.keys()):
        raise ExternalSearchConfigurationError(f"SEARCH_PROVIDER no soportado: {selected}")
    if selected != "auto":
        return constructors[selected]()
    available=[]
    if os.environ.get("OPENAI_API_KEY"): available.append(constructors["openai"]())
    if os.environ.get("OPENROUTER_API_KEY"): available.append(constructors["openrouter"]())
    if os.environ.get("TAVILY_API_KEY"): available.append(constructors["tavily"]())
    if os.environ.get("BRAVE_SEARCH_API_KEY"): available.append(constructors["brave"]())
    if os.environ.get("EXA_API_KEY"): available.append(constructors["exa"]())
    # El navegador web directo no necesita API key; se intenta al final si hay red.
    available.extend([constructors["google"](), constructors["duckduckgo"]()])
    return FallbackSearchAdapter(available)


class OfflineSearchAdapter:
    """UNIFICADO_20261011: SEARCH_PROVIDER=offline. No hace HTTP. Falla igual que 'todos los proveedores fallaron'."""
    def __init__(self):
        self.last_receipt={"provider":"offline","status":"OFFLINE_SIN_RED","query_count":0,"result_count":0,"attempts":[]}
    def search(self, query: str) -> Sequence[SearchSource]:
        raise RuntimeError("SEARCH_PROVIDER=offline: búsqueda externa deshabilitada (pruebas sin red)")


class FallbackSearchAdapter:
    """Prueba los proveedores configurados en orden y solo falla tras agotarlos."""
    def __init__(self, adapters):
        self.adapters=list(adapters)
        self.last_receipt={"provider":"auto","status":"NOT_RUN","query_count":0,"result_count":0,"attempts":[]}
    def search(self, query: str) -> Sequence[SearchSource]:
        errors=[]
        for adapter in self.adapters:
            try:
                rows=list(adapter.search(query))
                receipt=dict(getattr(adapter,"last_receipt",{}) or {})
                if receipt.get("status")=="EXECUTED" and rows:
                    self.last_receipt={**receipt,"provider":receipt.get("provider") or type(adapter).__name__,"attempts":errors+[{'provider':receipt.get('provider'),'status':'EXECUTED'}]}
                    return rows
                errors.append({"provider":receipt.get("provider") or type(adapter).__name__,"status":receipt.get("status","NO_RESULTS"),"error":"sin resultados verificables"})
            except Exception as exc:
                receipt=dict(getattr(adapter,"last_receipt",{}) or {})
                errors.append({"provider":receipt.get("provider") or type(adapter).__name__,"status":receipt.get("status","FAILED"),"error":str(exc)[:500]})
        self.last_receipt={"provider":"auto","status":"FAILED_ALL_PROVIDERS","query_count":len(self.adapters),"result_count":0,"attempts":errors}
        raise RuntimeError("Todos los proveedores configurados fallaron: "+json.dumps(errors,ensure_ascii=False))


class BraveSearchAdapter:
    """Búsqueda web directa mediante Brave Search API."""
    def __init__(self, api_key: str, num_results: int = 8, timeout: float = 20.0):
        if not api_key or not api_key.strip(): raise ExternalSearchConfigurationError("BRAVE_SEARCH_API_KEY ausente")
        self.api_key, self.num_results, self.timeout = api_key.strip(), max(1,min(int(num_results),10)), float(timeout)
        self.last_receipt={"provider":"brave","status":"NOT_RUN","query_count":0,"result_count":0}
    @classmethod
    def from_env(cls): return cls(os.environ.get("BRAVE_SEARCH_API_KEY", ""))
    def search(self, query: str) -> Sequence[SearchSource]:
        from urllib.parse import urlencode
        url="https://api.search.brave.com/res/v1/web/search?"+urlencode({"q":query,"count":self.num_results})
        req=urllib.request.Request(url,headers={"X-Subscription-Token":self.api_key,"Accept":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as r: raw=json.loads(r.read().decode()); code=getattr(r,"status",200)
        except Exception as exc:
            self.last_receipt={"provider":"brave","status":"FAILED","query_count":1,"result_count":0,"error":f"{type(exc).__name__}:{exc}"}; raise RuntimeError(f"búsqueda Brave fallida: {exc}") from exc
        rows=((raw.get("web") or {}).get("results") or [])
        out=[SearchSource(url=str(x.get("url") or ""),title=str(x.get("title") or ""),snippet=str(x.get("description") or ""),metadata={"provider":"brave"}) for x in rows if isinstance(x,dict) and str(x.get("url","")).startswith("http")]
        if not out: self.last_receipt={"provider":"brave","status":"FAILED_NO_RESULTS","query_count":1,"result_count":0,"http_status":code}; raise RuntimeError("Brave no devolvió resultados URL verificables")
        self.last_receipt={"provider":"brave","status":"EXECUTED","query_count":1,"result_count":len(out),"http_status":code,"query_sha256":hashlib.sha256(query.encode()).hexdigest()}
        return out

def _norm(value: Any) -> str:
    return str(value).strip().casefold()


def _stable_hash(payload: Any) -> str:
    raw = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _clean_terms(values: Iterable[str]) -> list[str]:
    out = []
    seen = set()
    for value in values:
        term = _norm(value)
        if term and term not in seen:
            seen.add(term)
            out.append(term)
    return out


def build_blind_query(archetype: ArchetypeInput) -> str:
    """
    Construye la query SOLO desde tokens/patrones/familias.

    No acepta ni consulta SelfMatchIdentity.
    """
    terms = _clean_terms(
        list(archetype.tokens)
        + list(archetype.patterns)
        + list(archetype.families)
    )
    if not terms:
        raise ValueError("arquetipo_vacio")
    return " ".join(terms)


class SelfMatchFilter:
    """
    Filtro EXTERNO al Caldero.

    El criterio inicial es conservador y explícito:
      - coincidencia por nombre normalizado en URL/título/snippet;
      - coincidencia por fecha de nacimiento/muerte en URL/título/snippet;
      - coincidencia por hecho único en URL/título/snippet.

    No pretende resolver todavía la política fina de tolerancia/partial match:
    eso queda configurable y auditable, tal como deja pendiente el SPEC.
    """

    def __init__(self, identity: SelfMatchIdentity):
        self.identity = identity

    @staticmethod
    def _hay(text: str, term: str | None) -> bool:
        return bool(term) and _norm(term) in _norm(text)

    def match_reason(self, source: SearchSource) -> str | None:
        haystack = " ".join(
            [source.url or "", source.title or "", source.snippet or ""]
        )

        if self._hay(haystack, self.identity.name):
            return "name_match"

        if self._hay(haystack, self.identity.birth_date):
            return "birth_date_match"

        if self._hay(haystack, self.identity.death_date):
            return "death_date_match"

        for fact in self.identity.unique_facts:
            if self._hay(haystack, fact):
                return "unique_fact_match"

        return None

    def filter(
        self, sources: Sequence[SearchSource]
    ) -> tuple[list[SearchSource], list[dict[str, Any]]]:
        kept = []
        discarded = []

        for source in sources:
            reason = self.match_reason(source)
            if reason is None:
                kept.append(source)
            else:
                discarded.append(
                    {
                        "url": source.url,
                        "title": source.title,
                        "reason": reason,
                    }
                )
        return kept, discarded


_TOKEN_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_'-]+")
_STOPWORDS = set("""
a al algo algunas algunos ante antes como con contra cual cuando de del desde donde durante e el ella ellas ellos en entre era es esa esas ese esos esta estaba estaban estas este estos fue fueron ha hasta hay la las le les lo los más mas me mi mis mucha muchas mucho muchos muy nada ni no nos o os otra otras otro otros para pero por porque que quien se sea según sin sobre son su sus te tener tiene tienen todo todos tras tu tus un una unas uno unos y ya
about after all also an and any are as at be because been before being between both but by can did do does down during each few for from further had has have he her here hers herself him himself his how i if in into is it its itself just more most my myself no nor not of off on once only or other our ours ourselves out over own same she should so some such than that the their theirs them themselves then there these they this those through to too under until up very was we were what when where which while who whom why will with you your yours
""".split())


def extract_tokens(text: str) -> list[str]:
    """Extracción determinista de términos informativos; excluye ruido lingüístico y cifras sueltas."""
    out=[]; seen=set()
    for raw in _TOKEN_RE.findall(text or ""):
        token=_norm(raw)
        if len(token) < 3 or token in _STOPWORDS or token.isdigit():
            continue
        if not any(ch.isalpha() for ch in token):
            continue
        if token not in seen:
            seen.add(token); out.append(token)
    return out


def tokenize_sources(
    sources: Sequence[SearchSource],
    *,
    token_whitelist: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Produce tokens/vecinos con frecuencia de co-activación por fuente.

    Una fuente cuenta como una observación: un token repetido varias veces
    dentro de la misma fuente no aumenta su frecuencia de co-activación.
    """
    allowed = None
    if token_whitelist is not None:
        allowed = set(_clean_terms(token_whitelist))

    token_sources: dict[str, set[str]] = {}
    source_refs: dict[str, set[str]] = {}

    for source in sources:
        source_id = source.url or _stable_hash(source.as_dict())
        tokens = set(extract_tokens(" ".join([source.title, source.snippet])))

        if allowed is not None:
            tokens &= allowed

        for token in tokens:
            token_sources.setdefault(token, set()).add(source_id)
            source_refs.setdefault(token, set()).add(source.url)

    rows = []
    for token in sorted(token_sources):
        rows.append(
            {
                "token": token,
                "coactivation_frequency": len(token_sources[token]),
                "source_refs": sorted(x for x in source_refs[token] if x),
            }
        )
    return rows


class CalderoArchetypeSearchSidecar:
    """
    Orquestador aislado.

    Importante:
      - recibe arquetipo ciego;
      - recibe identidad solo en el filtro externo;
      - Caldero solo debería consumir `caldero_input`;
      - `audit` conserva información que NO debe exponerse al Caldero.
    """

    def __init__(
        self,
        search_adapter: SearchAdapter,
        self_match_filter: SelfMatchFilter,
    ):
        self.search_adapter = search_adapter
        self.self_match_filter = self_match_filter

    def run(self, archetype: ArchetypeInput, llm_neighbor_hints: Any = None, **_extra) -> dict[str, Any]:
        try:
            query = build_blind_query(archetype)
        except ValueError:
            query = "caldero_lateral"

        raw_sources = list(self.search_adapter.search(query))

        kept, discarded = self.self_match_filter.filter(raw_sources)
        provider_receipt = dict(getattr(self.search_adapter, "last_receipt", {}) or {})
        if not provider_receipt:
            provider_receipt = {"provider": "static_fixture", "status": "EXECUTED", "query_count": 1, "result_count": len(raw_sources)}

        token_rows = tokenize_sources(kept)
        hints = []
        for h in llm_neighbor_hints or []:
            if isinstance(h, Mapping) and h.get("token"):
                hints.append({"token": str(h.get("token")), "source": "llm_hint"})
            elif isinstance(h, str) and h.strip():
                hints.append({"token": h.strip(), "source": "llm_hint"})
        if hints:
            token_rows = list(token_rows) + hints

        return {
            "schema": SCHEMA,
            "version": VERSION,
            "CANON_LOCK": dict(CANON_LOCK),
            "caldero_input": {
                "tokens_neighbors": token_rows,
                "freeze_read_only": True,
                "query_blind": True,
                "self_match_filtered": True,
                "raw_sources_exposed": False,
                "identity_exposed": False,
            },
            "audit": {
                "query_exact": query,
                "provider_receipt": provider_receipt,
                "raw_sources_before_self_match": [
                    s.as_dict() for s in raw_sources
                ],
                "discarded_by_self_match": discarded,
                "final_tokens_neighbors": token_rows,
                "llm_neighbor_hints_n": len(hints),
            },
        }


def manifest() -> dict[str, Any]:
    return {
        "plugin": "sidecar_caldero_busqueda_arquetipos",
        "version": VERSION,
        "status": "SIDE_CAR_ISOLATED",
        "schema": SCHEMA,
        "CANON_LOCK": dict(CANON_LOCK),
        "query_blind": True,
        "self_match_filter_external": True,
        "modifies_freeze": False,
        "modifies_244": False,
        "modifies_engine_v5": False,
        "free_text_to_caldero": False,
        "prediction": False,
        "pending_policy": [
            "ubicacion_fuente_identidad_real",
            "criterio_fino_de_coincidencia",
        ],
    }


# ------------------------- pruebas mínimas -------------------------

def _assert_raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"se esperaba {exc_type.__name__}")


def test_query_is_blind():
    q = build_blind_query(
        ArchetypeInput(
            tokens=("ambicion",),
            patterns=("audaz_empresa",),
            families=("obtencion",),
        )
    )
    assert q == "ambicion audaz_empresa obtencion"
    assert "musk" not in q
    assert "1971" not in q


def test_empty_archetype_rejected():
    _assert_raises(ValueError, build_blind_query, ArchetypeInput())


def test_self_match_external_filter():
    identity = SelfMatchIdentity(
        name="Caso Ejemplo",
        birth_date="1971-06-28",
        death_date="2026-01-01",
        unique_facts=("hecho irrepetible",),
    )
    sources = [
        SearchSource(
            url="https://example.org/caso",
            title="Caso Ejemplo",
            snippet="ambicion audaz_empresa",
        ),
        SearchSource(
            url="https://example.org/otro",
            title="Otro personaje",
            snippet="ambicion audaz_empresa",
        ),
    ]
    kept, discarded = SelfMatchFilter(identity).filter(sources)
    assert len(kept) == 1
    assert len(discarded) == 1
    assert discarded[0]["reason"] == "name_match"


def test_identity_never_enters_query_or_caldero_output():
    identity = SelfMatchIdentity(name="Caso Secreto", birth_date="1900-01-01")
    adapter = StaticSearchAdapter(
        [
            SearchSource(
                url="https://example.org/other",
                title="Ambición",
                snippet="audaz empresa obtencion",
            )
        ]
    )
    result = CalderoArchetypeSearchSidecar(
        adapter, SelfMatchFilter(identity)
    ).run(ArchetypeInput(tokens=("ambicion",)))

    assert "Caso Secreto" not in result["audit"]["query_exact"]
    assert "1900-01-01" not in result["audit"]["query_exact"]
    assert result["caldero_input"]["identity_exposed"] is False
    assert result["caldero_input"]["raw_sources_exposed"] is False


def test_audit_keeps_raw_sources_and_discard_reason():
    identity = SelfMatchIdentity(name="Propio")
    adapter = StaticSearchAdapter(
        [
            SearchSource(
                url="https://example.org/propio",
                title="Propio",
                snippet="x",
            ),
            SearchSource(
                url="https://example.org/otro",
                title="Otro",
                snippet="x y",
            ),
        ]
    )
    result = CalderoArchetypeSearchSidecar(
        adapter, SelfMatchFilter(identity)
    ).run(ArchetypeInput(tokens=("x",)))

    assert len(result["audit"]["raw_sources_before_self_match"]) == 2
    assert len(result["audit"]["discarded_by_self_match"]) == 1
    assert len(result["audit"]["final_tokens_neighbors"]) >= 1


def test_no_canonical_modification_flags():
    m = manifest()
    assert m["CANON_LOCK"] == {
        "TOCA_F": False,
        "TOCA_244": False,
        "TOCA_Engine_V5": False,
        "TOCA_FREEZE": False,
    }
    assert m["modifies_freeze"] is False
    assert m["modifies_244"] is False
    assert m["modifies_engine_v5"] is False
    assert m["prediction"] is False


def run_self_tests() -> dict[str, Any]:
    tests = [
        test_query_is_blind,
        test_empty_archetype_rejected,
        test_self_match_external_filter,
        test_identity_never_enters_query_or_caldero_output,
        test_audit_keeps_raw_sources_and_discard_reason,
        test_no_canonical_modification_flags,
    ]
    for test in tests:
        test()
    return {"passed": len(tests), "failed": 0, "status": "PASS"}


if __name__ == "__main__":
    print(json.dumps(
        {
            "manifest": manifest(),
            "self_tests": run_self_tests(),
        },
        ensure_ascii=False,
        indent=2,
    ))
