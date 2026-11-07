import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # raíz del repo


def _load_sidecar():
    spec = importlib.util.spec_from_file_location(
        "sidecar_caldero_busqueda_arquetipos",
        ROOT / "motor" / "motor" / "sidecar_caldero_busqueda_arquetipos.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _fuentes(mod):
    # (a) pre-Z, (b) post-Z, (c) Z exacto, (d) sin fecha. Tokens exclusivos por fuente.
    S = mod.SearchSource
    return [
        S(url="https://ejemplo.test/pre", title="naufragio tormenta", snippet="fragata motin",
          metadata={"publishedDate": "1870-06-01"}),
        S(url="https://ejemplo.test/post", title="cohete satelite", snippet="orbita cohete",
          metadata={"publishedDate": "2026-10-28"}),
        S(url="https://ejemplo.test/exacta", title="naufragio fragata", snippet="tormenta motin",
          metadata={"publishedDate": "1871-05-01"}),
        S(url="https://ejemplo.test/sin-fecha", title="vela aparejo", snippet="marinero vela",
          metadata={"provider": "ddg"}),
    ]


def _run(mod, fuentes, z="1871-05-01", modo="estricto"):
    identity = mod.SelfMatchIdentity(name="Caso Ejemplo", birth_date="1971-06-28",
                                     death_date="2026-01-01", unique_facts=("hecho irrepetible",))
    arch = mod.ArchetypeInput(tokens=("ambicion",), patterns=("audaz_empresa",), families=("obtencion",))
    return mod.CalderoArchetypeSearchSidecar(
        mod.StaticSearchAdapter(list(fuentes)), mod.SelfMatchFilter(identity)
    ).run(arch, cutoff_date=z, corte_modo=modo)


def _toks(out):
    return {r["token"] for r in out["caldero_input"]["tokens_neighbors"]}


def test_pre_z_se_conserva_y_post_z_se_descarta():
    mod = _load_sidecar()
    out = _run(mod, _fuentes(mod))
    toks = _toks(out)
    assert "naufragio" in toks and "fragata" in toks  # (a) pre-Z
    assert "cohete" not in toks and "satelite" not in toks and "orbita" not in toks  # (b) post-Z
    aud = out["audit"]["corte_temporal"]
    assert aud["aplicado"] is True and aud["z_corte"] == "1871-05-01" and aud["modo"] == "estricto"
    assert [d["url"] for d in aud["descartadas_post_z"]] == ["https://ejemplo.test/post"]
    assert aud["descartadas_post_z"][0]["publishedDate"] == "2026-10-28"
    assert aud["tokens_antes_corte"] > aud["tokens_despues_corte"]


def test_fecha_exacta_z_se_conserva_inclusivo():
    mod = _load_sidecar()
    out = _run(mod, _fuentes(mod))
    assert "naufragio" in _toks(out)  # (c) 1871-05-01 == Z se conserva


def test_sin_fecha_estricto_descarta_leniente_conserva_con_marca():
    mod = _load_sidecar()
    out_e = _run(mod, _fuentes(mod), modo="estricto")
    assert "vela" not in _toks(out_e)
    assert [d["url"] for d in out_e["audit"]["corte_temporal"]["descartadas_sin_fecha"]] == ["https://ejemplo.test/sin-fecha"]
    out_l = _run(mod, _fuentes(mod), modo="leniente")
    assert "vela" in _toks(out_l) and "aparejo" in _toks(out_l)
    assert out_l["audit"]["corte_temporal"]["conservadas_sin_fecha_n"] == 1
    assert out_l["audit"]["corte_temporal"]["descartadas_sin_fecha"] == []
    assert "cohete" not in _toks(out_l)  # post-Z cae también en leniente


def test_misma_terna_via_from_mapping_puente_o_fixture():
    mod = _load_sidecar()
    crudos = [
        {"url": "https://ejemplo.test/pre", "title": "naufragio tormenta", "snippet": "fragata motin",
         "metadata": {"publishedDate": "1870-06-01"}},
        {"url": "https://ejemplo.test/post", "title": "cohete satelite", "snippet": "orbita cohete",
         "metadata": {"publishedDate": "2026-10-28"}},
    ]
    fuentes = [mod.SearchSource.from_mapping(r) for r in crudos]
    out = _run(mod, fuentes)
    assert "naufragio" in _toks(out) and "cohete" not in _toks(out)


def test_auditoria_no_pierde_lo_descartado_y_sin_z_no_cambia_nada():
    mod = _load_sidecar()
    out = _run(mod, _fuentes(mod))
    assert len(out["audit"]["raw_sources_before_self_match"]) == 4
    out_sin = _run(mod, _fuentes(mod), z=None)
    assert out_sin["audit"]["corte_temporal"]["aplicado"] is False
    assert "cohete" in _toks(out_sin)  # sin Z: comportamiento actual
