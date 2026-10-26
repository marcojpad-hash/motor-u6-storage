"""Filtro de tokens StinkBox / Caldero arquetipos v1 (no toca Engine ni catálogo 244).

Descarta ruido genérico (stopwords ES/EN, conectores, adverbios -mente, números, URLs,
puntuación, tokens diminutos, boilerplate de snippets web, cortes de guion) y conserva
sustantivos/verbos/frases con contenido. `brechas()` compara contra el vocabulario del
catálogo (patterns_final_v14.json, SOLO LECTURA) + familias_tokens para listar tokens
que aún no tenemos (posibles familias faltantes)."""
from __future__ import annotations
import json, re, unicodedata
from pathlib import Path

_STOP_ES = """a al algo algun alguna algunas alguno algunos ante antes aqui asi aun aunque bajo bien cada casi como con contra cual cuales cuando anos ano llevo tuvo tuvieron incluye incluyen realizo realizar sostiene finales multiples hacia segun traves dentro fuera cerca lejos aqui alli menos alla dice decir dicen seria sola solo genera generan sigue tanto muchos muchas cuando cuanto de del desde donde dos el ella ellas ello ellos en entre era eran es esa esas ese eso esos esta estaba estado estan estar este esto estos fue fueron ha han hasta hay la las le les lo los mas me mi mientras mismo mucho muy nada ni no nos nosotros o otra otras otro otros para pero poco por porque pues que quien quienes se sea segun ser si sido sin sino sobre solo son su sus tal tambien tan tanto te tiene tienen todo todos tras tu un una uno unos unas usted ya yo ademas asimismo incluso entonces luego despues ahora siempre nunca tampoco hacia mediante durante cuyo cuya cuyos cuyas dicho dicha dichos dichas cual otro ello aquel aquella aquello esto estas aborda abordar aborda presenta presente propone refleja resulta representa permite puede pueden podria podrian debe deben hace hacen hacer dar dando tener tiene haber sera seran estas somos eres soy fui sea sean through tres cuatro cinco seis siete ocho nueve diez primero primera segundo segunda tercero varios varias diversas diversos distintos distintas diferentes propia propio propias propios mayoria parte partes forma formas manera tipo tipos caso casos vez veces cosa cosas modo general generales gran grandes nuevo nueva nuevos nuevas mejor peor mayor menor alto alta bajo baja demas cierto cierta ciertos ciertas misma mismos mismas toda todas mediante respecto acerca traves etc""".split()
_STOP_EN = """a an the and or but if then of to in on at by for with from as is are was were be been being this that these those it its into about over under than so such not no yes can could would should will may might must do does did done have has had having he she they we you i me my our your their them his her also more most other some any each all both few many much very just only own same too here there when where why how what which who whom while during before after above below again further once out up down off between through via et al early life john december describes describing faced face shaped seeking traces""".split()
STOPWORDS = {unicodedata.normalize('NFKD', w).encode('ascii', 'ignore').decode() for w in _STOP_ES + _STOP_EN}
BOILERPLATE = set("""wikipedia enciclopedia libre articulo articulos pdf html http https www com org net doi isbn issn cookies cookie suscribete suscribirse login registrate leer lee mas click clic aqui pagina paginas sitio web blog post publicado publicacion autor autores fecha resumen abstract introduccion conclusion conclusiones capitulo seccion figura tabla vol pp ed edicion editorial copyright derechos reservados descargar download menu inicio buscar search home ver video videos foto fotos imagen imagenes enlace enlaces link links fuente fuentes referencias citar cita editar preliminary evaluation""".split())
_MIN_LEN = 4

def _sin_acentos(s: str) -> str:
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()

def normalizar(t) -> str:
    return re.sub(r'\s+', ' ', str(t or '').strip()).casefold()

def motivo_descarte(token) -> str | None:
    """None si se conserva; si no, la razón del descarte."""
    t = normalizar(token)
    if not t: return 'vacio'
    if re.search(r'(https?://|www\.|\.(com|org|net|pdf|html?)\b|@)', t): return 'url'
    if not re.search(r'[^\W\d_]', t): return 'numero_o_puntuacion'
    if re.match(r'^[\W_]|[\W_]$', t.replace(' ', 'x')) and not t.replace('_', '').isalnum(): return 'corte_guion_o_puntuacion'
    if re.search(r'-(miento|mientos|dad|dades|cion|ción|ciones|mente|idad|ia|ía)$', t) and t.count('-') == 1 and '_' not in t:
        return 'corte_guion_o_puntuacion'  # corte silábico de PDF/snippet (conoci-miento)
    if re.search(r'\d', t) and not re.search(r'[a-z]{4,}', _sin_acentos(t)): return 'numero_o_puntuacion'
    a = _sin_acentos(t)
    partes = [p for p in re.split(r'[\s_]+', a) if p]
    if len(partes) == 1:
        if len(a) < _MIN_LEN: return 'muy_corto'
        if a in STOPWORDS: return 'stopword'
        if a in BOILERPLATE: return 'boilerplate_snippet'
        if a.endswith('mente') and len(a) > 7: return 'adverbio_generico'
    else:
        if all(p in STOPWORDS or p in BOILERPLATE or len(p) < 3 for p in partes): return 'frase_sin_contenido'
    return None

def conservar(token) -> bool:
    return motivo_descarte(token) is None

def filtrar(tokens):
    return [t for t in tokens if conservar(t)]

def _raiz(p: str) -> str:
    return p[:6]

def vocabulario_catalogo(motor_dir: Path) -> dict:
    """Lee (sin modificar) catálogo 244 y familias_tokens. Devuelve {token_norm: [familias]}."""
    voc: dict = {}
    def add(tok, fam):
        voc.setdefault(_sin_acentos(normalizar(tok)), set()).add(fam)
    pat = motor_dir / 'patterns_final_v14.json'
    if pat.is_file():
        for fam, d in json.loads(pat.read_text(encoding='utf-8')).items():
            add(fam, fam)
            if isinstance(d, dict):
                for k in ('tokens_favor', 'tokens_contra'):
                    for tok in (d.get(k) or {}): add(tok, fam)
    for p in sorted((motor_dir / 'familias_tokens').glob('*.json')):
        try: d = json.loads(p.read_text(encoding='utf-8'))
        except Exception: continue
        fam = d.get('id', p.stem) if isinstance(d, dict) else p.stem
        add(fam, fam)
        if isinstance(d, dict):
            for k in ('tokens_favor', 'tokens_contra'):
                v = d.get(k) or {}
                for tok in (v if isinstance(v, (dict, list)) else []): add(tok, fam)
    return voc

def brechas(tokens, voc: dict) -> list[str]:
    """Tokens conservados que no aparecen en el catálogo ni comparten raíz con ninguna pieza de él."""
    raices = {_raiz(p) for k in voc for p in k.split('_') if len(p) >= 4}
    out = []
    for t in tokens:
        a = _sin_acentos(normalizar(t)).replace(' ', '_')
        if a in voc: continue
        if any(_raiz(p) in raices for p in a.split('_') if len(p) >= 4): continue
        out.append(t)
    return out
