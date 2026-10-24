#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""caldero_buscadores.py — capa de buscadores AGNÓSTICA para Caldero (TIRADA 20261024).

Caldero usa un *buscador*, no un LLM: entra una consulta ciega, salen filas
{url, title, snippet}. Se usa el primer motor libre que responda (como una
persona que abre Google). Claves de API (EXA/Brave/Serper/Tavily) son
opcionales y solo se usan si están en el entorno.

CALDERO_BUSCADOR=auto|ddgs|ddg|ddg_lite|bing|searx|wiki|google|exa|brave|serper|tavily|offline
   (lista separada por comas = orden propio; SEARCH_PROVIDER se acepta como alias)
CALDERO_SEARX_INSTANCIAS=https://a,https://b  (opcional)

Cada intento queda registrado (proveedor, consulta, URLs, fecha de consulta UTC).
Si ninguno responde se levanta RuntimeError con la lista de intentos: nunca se
inventan resultados. No toca F/244/Engine/FREEZE/H1/H2.
"""
from __future__ import annotations
import datetime as _dt, hashlib, json, os, re, sys, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, parse_qs, urlparse, unquote

_HERE = Path(__file__).resolve().parent
# runs/ESTANDAR__X copia solo archivos de motor/: buscar el vendor también en ../../motor/
_VENDOR = next((c for c in (_HERE / "_vendor_buscador", _HERE.parent.parent / "motor" / "_vendor_buscador") if c.is_dir()), _HERE / "_vendor_buscador")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
SEARX_DEFAULT = ["https://searx.be", "https://search.inetol.net", "https://priv.au", "https://searx.tiekoetter.com", "https://search.sapti.me"]


def _now(): return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
def _sha(q): return hashlib.sha256(q.encode("utf-8")).hexdigest()
def _clean(s): return " ".join(re.sub(r"<[^>]+>", " ", str(s or "")).split())


def _get(url, timeout, headers=None, data=None):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}; h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return getattr(r, "status", 200), r.read().decode("utf-8", "replace")


class _Base:
    name = "base"; needs_key = None
    def __init__(self, source_cls, num_results=8, timeout=15.0):
        self.S = source_cls; self.n = max(1, min(int(num_results), 10)); self.timeout = float(timeout)
        self.last_receipt = {"provider": self.name, "status": "NOT_RUN", "query_count": 0, "result_count": 0}
    def _rows(self, query): raise NotImplementedError
    def search(self, query):
        if not query or not query.strip(): raise ValueError("query_externa_vacia")
        when = _now()
        try:
            code, rows = self._rows(query)
        except Exception as exc:
            self.last_receipt = {"provider": self.name, "status": "FAILED", "query_count": 1, "result_count": 0,
                                 "query": query, "query_sha256": _sha(query), "consultado_utc": when, "error": f"{type(exc).__name__}:{str(exc)[:300]}"}
            raise RuntimeError(f"buscador {self.name} fallido: {exc}") from exc
        out, seen = [], set()
        for r in rows:
            u = str(r.get("url") or "").strip()
            if not u.startswith(("http://", "https://")) or u in seen: continue
            seen.add(u)
            out.append(self.S(url=u, title=_clean(r.get("title")), snippet=_clean(r.get("snippet")),
                              metadata={"provider": self.name, "consultado_utc": when, **({"publishedDate": r["date"]} if r.get("date") else {})}))
            if len(out) >= self.n: break
        base = {"provider": self.name, "query_count": 1, "query": query, "query_sha256": _sha(query), "consultado_utc": when, "http_status": code, "llm": False}
        if not out:
            self.last_receipt = {**base, "status": "FAILED_NO_RESULTS", "result_count": 0}
            raise RuntimeError(f"buscador {self.name} sin resultados URL verificables")
        self.last_receipt = {**base, "status": "EXECUTED", "result_count": len(out), "urls": [s.url for s in out]}
        return out


class DDGS(_Base):
    """Paquete ddgs (vendorizado en _vendor_buscador): metabuscador libre sin clave."""
    name = "ddgs"
    def _rows(self, q):
        if str(_VENDOR) not in sys.path and _VENDOR.is_dir(): sys.path.insert(0, str(_VENDOR))
        try: from ddgs import DDGS as _D
        except ImportError: from duckduckgo_search import DDGS as _D  # type: ignore
        res = _D(timeout=int(self.timeout)).text(q, region=os.environ.get("CALDERO_REGION", "wt-wt"), max_results=self.n)
        return 200, [{"url": x.get("href"), "title": x.get("title"), "snippet": x.get("body")} for x in res or []]


class _DDGParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows = []; self.cap = None; self.buf = []
    def handle_starttag(self, t, a):
        a = dict(a); c = a.get("class") or ""
        if t == "a" and "result__a" in c: self.rows.append({"url": a.get("href", ""), "title": ""}); self.cap = "title"; self.buf = []
        elif "result__snippet" in c: self.cap = "snippet"; self.buf = []
    def handle_data(self, d):
        if self.cap: self.buf.append(d)
    def handle_endtag(self, t):
        if self.cap and t in ("a", "div", "td"):
            if self.rows: self.rows[-1][self.cap] = " ".join("".join(self.buf).split())
            self.cap = None


def _ddg_target(u):
    if "duckduckgo.com/l/?" in u: u = parse_qs(urlparse(("https:" + u) if u.startswith("//") else u).query).get("uddg", [u])[0]
    return u


class DDGHtml(_Base):
    name = "duckduckgo_html"
    def _rows(self, q):
        code, html = _get("https://html.duckduckgo.com/html/", self.timeout, {"Content-Type": "application/x-www-form-urlencoded"}, urlencode({"q": q}).encode())
        p = _DDGParser(); p.feed(html)
        return code, [{**r, "url": _ddg_target(r["url"])} for r in p.rows if "duckduckgo.com/y.js" not in r.get("url", "")]


class DDGLite(_Base):
    name = "duckduckgo_lite"
    def _rows(self, q):
        code, html = _get("https://lite.duckduckgo.com/lite/?" + urlencode({"q": q}), self.timeout)
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*class=.result-link.[^>]*>(.*?)</a>', html, re.S)
        snips = re.findall(r"class=.result-snippet.[^>]*>(.*?)</td>", html, re.S)
        return code, [{"url": _ddg_target(u.replace("&amp;", "&")), "title": t, "snippet": snips[i] if i < len(snips) else ""} for i, (u, t) in enumerate(links)]


class BingHtml(_Base):
    name = "bing_html"
    def _rows(self, q):
        code, html = _get("https://www.bing.com/search?" + urlencode({"q": q, "count": self.n, "setlang": "en"}), self.timeout)
        rows = []
        for blk in re.findall(r'<li class="b_algo".*?</li>', html, re.S):
            m = re.search(r'<h2[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
            if not m: continue
            u = m.group(1).replace("&amp;", "&")
            if "bing.com/ck/a" in u:  # redirección: u=a1<base64url>
                import base64
                tok = parse_qs(urlparse(u).query).get("u", [""])[0]
                if tok.startswith("a1"):
                    try: u = base64.urlsafe_b64decode(tok[2:] + "=" * (-len(tok[2:]) % 4)).decode()
                    except Exception: pass
            s = re.search(r"<p[^>]*>(.*?)</p>", blk, re.S)
            rows.append({"url": u, "title": m.group(2), "snippet": s.group(1) if s else ""})
        return code, rows


class Searx(_Base):
    name = "searxng"
    def _rows(self, q):
        insts = [x.strip() for x in os.environ.get("CALDERO_SEARX_INSTANCIAS", "").split(",") if x.strip()] or SEARX_DEFAULT
        errs = []
        for base in insts:
            try:
                code, body = _get(base.rstrip("/") + "/search?" + urlencode({"q": q, "format": "json", "language": "en"}), self.timeout, {"Accept": "application/json"})
                res = json.loads(body).get("results") or []
                if res:
                    self.name = f"searxng:{urlparse(base).netloc}"
                    return code, [{"url": r.get("url"), "title": r.get("title"), "snippet": r.get("content"), "date": r.get("publishedDate")} for r in res]
                errs.append(f"{base}:sin_resultados")
            except Exception as e:
                errs.append(f"{base}:{type(e).__name__}")
        raise RuntimeError("instancias SearXNG sin respuesta: " + "; ".join(errs))


class Wiki(_Base):
    name = "wikipedia_api"
    def _rows(self, q):
        code, body = _get("https://en.wikipedia.org/w/api.php?" + urlencode({"action": "query", "list": "search", "srsearch": q, "srlimit": self.n, "format": "json"}), self.timeout)
        hits = (json.loads(body).get("query") or {}).get("search") or []
        if not hits and len(q.split()) > 4:  # Wikipedia exige todos los términos: reintento con OR
            code, body = _get("https://en.wikipedia.org/w/api.php?" + urlencode({"action": "query", "list": "search", "srsearch": " OR ".join(q.split()[:12]), "srlimit": self.n, "format": "json"}), self.timeout)
            hits = (json.loads(body).get("query") or {}).get("search") or []
        return code, [{"url": "https://en.wikipedia.org/wiki/" + h["title"].replace(" ", "_"), "title": h["title"], "snippet": h.get("snippet")} for h in hits]


class GoogleHtml(_Base):
    name = "google_html"
    def _rows(self, q):
        code, html = _get("https://www.google.com/search?" + urlencode({"q": q, "num": self.n, "hl": "en"}), self.timeout)
        rows = []
        for u, t in re.findall(r'<a href="/url\?q=([^&"]+)[^"]*"[^>]*>.*?<h3[^>]*>(.*?)</h3>', html, re.S):
            rows.append({"url": unquote(u), "title": t, "snippet": ""})
        for u, t in re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>\s*<h3[^>]*>(.*?)</h3>', html, re.S):
            if "google." not in u: rows.append({"url": u, "title": t, "snippet": ""})
        return code, rows


class _Keyed(_Base):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.key = os.environ.get(self.needs_key, "").strip()
        if not self.key: raise RuntimeError(f"{self.needs_key} ausente")


class Exa(_Keyed):
    name = "exa"; needs_key = "EXA_API_KEY"
    def _rows(self, q):
        code, b = _get("https://api.exa.ai/search", self.timeout, {"x-api-key": self.key, "Content-Type": "application/json"}, json.dumps({"query": q, "numResults": self.n, "contents": {"text": {"maxCharacters": 1600}}}).encode())
        return code, [{"url": r.get("url"), "title": r.get("title"), "snippet": r.get("text"), "date": r.get("publishedDate")} for r in json.loads(b).get("results") or []]


class Brave(_Keyed):
    name = "brave"; needs_key = "BRAVE_SEARCH_API_KEY"
    def _rows(self, q):
        code, b = _get("https://api.search.brave.com/res/v1/web/search?" + urlencode({"q": q, "count": self.n}), self.timeout, {"X-Subscription-Token": self.key, "Accept": "application/json"})
        return code, [{"url": r.get("url"), "title": r.get("title"), "snippet": r.get("description")} for r in (json.loads(b).get("web") or {}).get("results") or []]


class Serper(_Keyed):
    name = "serper"; needs_key = "SERPER_API_KEY"
    def _rows(self, q):
        code, b = _get("https://google.serper.dev/search", self.timeout, {"X-API-KEY": self.key, "Content-Type": "application/json"}, json.dumps({"q": q, "num": self.n}).encode())
        return code, [{"url": r.get("link"), "title": r.get("title"), "snippet": r.get("snippet"), "date": r.get("date")} for r in json.loads(b).get("organic") or []]


class Tavily(_Keyed):
    name = "tavily"; needs_key = "TAVILY_API_KEY"
    def _rows(self, q):
        code, b = _get("https://api.tavily.com/search", self.timeout, {"Content-Type": "application/json"}, json.dumps({"api_key": self.key, "query": q, "max_results": self.n}).encode())
        return code, [{"url": r.get("url"), "title": r.get("title"), "snippet": r.get("content")} for r in json.loads(b).get("results") or []]


LIBRES = {"ddgs": DDGS, "ddg": DDGHtml, "ddg_lite": DDGLite, "bing": BingHtml, "searx": Searx, "wiki": Wiki, "google": GoogleHtml}
CON_CLAVE = {"exa": Exa, "brave": Brave, "serper": Serper, "tavily": Tavily}
ORDEN_AUTO = ["ddgs", "ddg", "ddg_lite", "bing", "searx", "wiki", "google", "exa", "brave", "serper", "tavily"]


class CadenaBuscadores:
    """Prueba buscadores en orden; usa el primero con resultados reales."""
    def __init__(self, nombres, source_cls):
        self.nombres = list(nombres); self.S = source_cls
        self.last_receipt = {"provider": "caldero_buscador_auto", "status": "NOT_RUN", "query_count": 0, "result_count": 0, "attempts": []}
    def search(self, query):
        intentos = []
        for nm in self.nombres:
            cls = LIBRES.get(nm) or CON_CLAVE.get(nm)
            if cls is None: intentos.append({"provider": nm, "status": "DESCONOCIDO"}); continue
            if cls.needs_key and not os.environ.get(cls.needs_key):
                intentos.append({"provider": cls.name, "status": "SALTADO_SIN_CLAVE"}); continue
            try:
                ad = cls(self.S)
                rows = list(ad.search(query))
                r = dict(ad.last_receipt)
                intentos.append({"provider": r["provider"], "status": "EXECUTED", "consultado_utc": r.get("consultado_utc")})
                self.last_receipt = {**r, "selector": os.environ.get("CALDERO_BUSCADOR") or os.environ.get("SEARCH_PROVIDER") or "auto", "attempts": intentos}
                return rows
            except Exception as exc:
                r = dict(getattr(locals().get("ad"), "last_receipt", {}) or {})
                intentos.append({"provider": r.get("provider") or getattr(cls, "name", nm), "status": r.get("status", "FAILED"), "consultado_utc": r.get("consultado_utc") or _now(), "error": str(exc)[:300]})
            finally:
                locals().pop("ad", None)
        self.last_receipt = {"provider": "caldero_buscador_auto", "status": "FAILED_ALL_PROVIDERS", "query_count": len(intentos), "result_count": 0,
                             "query": query, "query_sha256": _sha(query), "consultado_utc": _now(), "attempts": intentos,
                             "nota": "ningún buscador respondió; no se inventan resultados"}
        raise RuntimeError("Ningún buscador respondió: " + json.dumps(intentos, ensure_ascii=False))


def crear_cadena(source_cls, selector=None):
    sel = (selector or os.environ.get("CALDERO_BUSCADOR") or os.environ.get("SEARCH_PROVIDER") or "auto").strip().casefold()
    nombres = ORDEN_AUTO if sel == "auto" else [x.strip() for x in sel.split(",") if x.strip()]
    if sel == "duckduckgo": nombres = ["ddgs", "ddg", "ddg_lite"]
    bad = [x for x in nombres if x not in LIBRES and x not in CON_CLAVE]
    if bad: raise ValueError(f"CALDERO_BUSCADOR no soportado: {bad}")
    return CadenaBuscadores(nombres, source_cls)
