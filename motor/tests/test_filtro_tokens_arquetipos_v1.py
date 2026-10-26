import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'motor'))
import filtro_tokens_arquetipos_v1 as f

def test_descarta_ruido():
    for t in ['aborda', 'además', 'the', 'de', '1762', '...', 'https://x.com/a', 'wikipedia', 'conoci-miento',
              '-presentación', 'significativamente', 'abc', '', 'de la', 'www.algo.org']:
        assert not f.conservar(t), t

def test_conserva_contenido():
    for t in ['rivalidad_poder', 'sacrificio', 'desconfianza', 'chivo expiatorio', 'ciudades-estado', 'traición', 'dios', 'miedo_caos']:
        assert f.conservar(t), t

def test_brechas_contra_catalogo():
    voc = {'rivalidad_poder': {'x'}, 'traicion': {'y'}}
    assert f.brechas(['rivalidad_poder', 'traiciones', 'mecenazgo'], voc) == ['mecenazgo']

def test_vocabulario_real_lee_sin_modificar():
    d = Path(__file__).resolve().parents[1] / 'motor'
    p = d / 'patterns_final_v14.json'; antes = p.read_bytes()
    voc = f.vocabulario_catalogo(d)
    assert len(voc) > 244 and p.read_bytes() == antes
