import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'motor'))
import filtro_tokens_arquetipos_v2 as f
import filtro_tokens_arquetipos_v1 as f1


def test_superconjunto_de_v1():
    # Todo lo que v1 descarta, v2 lo descarta; todo lo que v1 conserva, v2 lo conserva.
    for t in ['aborda', 'además', 'the', 'de', '1762', '...', 'https://x.com/a', 'wikipedia', 'conoci-miento',
              '-presentación', 'significativamente', 'abc', '', 'de la', 'www.algo.org']:
        assert not f.conservar(t), t
    for t in ['rivalidad_poder', 'sacrificio', 'desconfianza', 'chivo expiatorio', 'ciudades-estado', 'traición', 'dios', 'miedo_caos']:
        assert f.conservar(t), t


def test_descarta_digitos():
    for t in ['ciencia2024', 'abcd123', '2024ciencia']:
        assert f.motivo_descarte(t) == 'con_digitos', t
    # Sin racha de >=4 letras lo descarta antes v1 (numero_o_puntuacion);
    # lo que importa es que no pasa.
    assert not f.conservar('abc123def')
    assert f.motivo_descarte('abc123def') == 'numero_o_puntuacion'


def test_allowlist_digitos():
    assert f.conservar('formula10')
    assert f.conservar('r732')


def test_descarta_genericos_observados():
    for t in ['knowledge', 'science', 'development', 'influence']:
        assert f.motivo_descarte(t) == 'ingles_generico', t
    for t in ['obra', 'ejemplo', 'documento']:
        assert f.motivo_descarte(t) == 'generico_es', t


def test_descarta_meses_y_prefijos():
    assert f.motivo_descarte('enero') == 'mes_calendario'
    assert f.motivo_descarte('february') == 'mes_calendario'
    assert f.motivo_descarte('src_brit') == 'prefijo_procedencia'
    assert f.motivo_descarte('src_notion') == 'prefijo_procedencia'


def test_nombres_propios_fase_2_no_se_adivinan():
    # Fase 2 pendiente (necesita lista curada): v2 NO descarta mozart/viena.
    # Se deja constancia explícita en vez de fingir que el filtro los cubre.
    assert f.conservar('mozart')
    assert f.conservar('viena')


def test_exencion_catalogo():
    # Contenido real del catálogo se conserva aunque caiga en una lista genérica.
    assert f.conservar('sacrificio')
    assert f.conservar('rivalidad_poder')
    voc = f.vocabulario_catalogo(Path(__file__).resolve().parents[1] / 'motor')
    assert len(voc) > 244
    assert f.brechas(['rivalidad_poder', 'traiciones', 'mecenazgo'], {'rivalidad_poder': {'x'}, 'traicion': {'y'}}) == ['mecenazgo']


def test_filtrar():
    assert f.filtrar(['sacrificio', 'knowledge', 'obra', 'dios', 'ciencia2024']) == ['sacrificio', 'dios']
