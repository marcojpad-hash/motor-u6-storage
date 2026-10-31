import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("mortality_source_normalizer", ROOT/"scripts"/"normalizar_mortalidad_preparacion.py")
mod=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

def test_normalize_qx_and_mx_source_rows():
    base={
        "population_id":"250","country_or_area":"France","subnational_area":"",
        "sex":"Both sexes","period_type":"period","year_start":"1816","year_end":"1820",
        "age_start":"0","age_end":"4","unit":"probability","data_status":"MODELLED",
        "source_organization":"INED","source_dataset":"Bonneuil life tables",
        "source_url":"https://example.org/data","source_version_or_revision":"v1",
        "retrieval_date":"2026-10-31","source_file_sha256":"a"*64,"notes":"test fixture"
    }
    rows=[
        {**base,"indicator":"q_x","value":"0.4626"},
        {**base,"indicator":"m_x","value":"0.1234"}
    ]
    result=mod.normalize_rows(rows)
    assert result["rejected"]==[]
    assert len(result["records"])==2
    assert {r["rate_type"] for r in result["records"]}=={"q_x","m_x"}
    assert {r["rate_value"] for r in result["records"]}=={0.4626,0.1234}
    assert all(r["historical_epoch"]=="1816-1820" for r in result["records"])

def test_normalize_deaths_and_exposure_as_one_rate():
    base={
        "population_id":"MEX","country_or_area":"Mexico","subnational_area":"",
        "sex":"Female","period_type":"annual","year_start":"2000","year_end":"2000",
        "age_start":"65","age_end":"69","unit":"persons","data_status":"OBSERVED",
        "source_organization":"Example","source_dataset":"mortality",
        "source_url":"https://example.org/data","source_version_or_revision":"v1",
        "retrieval_date":"2026-10-31","source_file_sha256":"b"*64,"notes":"test fixture"
    }
    rows=[
        {**base,"indicator":"deaths","value":"100"},
        {**base,"indicator":"population_exposure","value":"50000"}
    ]
    result=mod.normalize_rows(rows)
    assert result["rejected"]==[]
    assert len(result["records"])==1
    row=result["records"][0]
    assert row["rate_type"]=="deaths_per_100000_exposure"
    assert row["deaths"]==100.0 and row["exposure"]==50000.0

def test_normalizer_rejects_unknown_indicators_and_bad_hashes():
    row={
        "country_or_area":"France","year_start":"1816","year_end":"1820",
        "age_start":"0","age_end":"4","indicator":"life_expectancy","value":"32",
        "source_url":"https://example.org/data","retrieval_date":"2026-10-31",
        "source_file_sha256":"not-a-hash"
    }
    result=mod.normalize_rows([row])
    assert result["records"]==[]
    assert result["rejected"]
