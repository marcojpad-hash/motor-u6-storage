import importlib.util, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("mortality_matrix_test", ROOT/"motor"/"matriz_mortalidad_z90_v0_2.py")
mod=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

def test_matrix_is_wired_but_does_not_feed_h():
    result=mod.build_mortality_matrix({"cuts":[]},{"H1":{"family":"A"},"H2":{"family":"B"}},ROOT)
    assert result["wired_to_active_runner"] is True
    assert result["status"]=="WIRED_WAITING_VERIFIED_MORTALITY_DATA"
    assert result["feeds_H"] is False and result["can_decide_H"] is False
    assert result["accepted_statistical_rows"]==0

def test_textual_death_classification_and_z90_guard():
    case={"case_subject":"Casanova","z90_date":"1791-12-31",
          "cuts":[{"cut_id":"C1","descripcion":"Casanova muere en Praga en 1798"}]}
    result=mod.build_mortality_matrix(case,{},ROOT)
    events=result["classified_mortality_events"]
    assert events and events[0]["classification"][0]["token"]=="mort_evento_propio"
    assert events[0]["classification"][0]["status"]=="REJECTED_POST_Z90"
    assert result["feeds_H"] is False

def test_verified_statistics_are_grouped_by_year_and_epoch():
    row={"population":"Testland","year":1900,"historical_epoch":"1900-1910","age_interval":"all",
         "deaths":20,"exposure":10000,"rate_type":"deaths_per_100000_exposure",
         "source_url":"https://example.org/data","retrieved_at":"2026-10-15",
         "source_sha256":"a"*64}
    accepted,rejected=mod._validate_stats([row])
    assert len(accepted)==1 and rejected==[]
    assert accepted[0]["calculated_rate"]==200.0
    assert mod._validate_stats([{"year":1900}])[1][0]["reason"]=="MISSING_REQUIRED_FIELDS"

def test_canonical_locks_unchanged():
    engine=ROOT/"motor"/"Engine_V5_CANONICO_SOLO.py"
    patterns=ROOT/"motor"/"patterns_final_v14.json"
    assert hashlib.sha256(engine.read_bytes()).hexdigest()=="665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082"
    assert hashlib.sha256(patterns.read_bytes()).hexdigest()=="d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"


def test_qx_and_mx_rate_values_are_preserved_without_fabricated_counts():
    base={"population":"France","year":1816,"age_interval":"0-4",
          "source_url":"https://example.org/life-table","retrieved_at":"2026-10-31",
          "source_sha256":"b"*64,"historical_epoch":"1816-1820"}
    qx={**base,"rate_type":"q_x","rate_value":0.4626}
    mx={**base,"rate_type":"m_x","rate_value":0.1234}
    accepted,rejected=mod._validate_stats([qx,mx])
    assert rejected==[]
    assert [x["rate_value"] for x in accepted]==[0.4626,0.1234]

def test_qx_outside_probability_range_is_rejected():
    row={"population":"France","year":1816,"age_interval":"0-4","rate_type":"q_x",
         "rate_value":1.01,"source_url":"https://example.org/life-table",
         "retrieved_at":"2026-10-31","source_sha256":"c"*64}
    accepted,rejected=mod._validate_stats([row])
    assert accepted==[]
    assert rejected[0]["reason"]=="RATE_VALUE_OUT_OF_RANGE"

def test_wpp_life_table_mx_qx_pair_is_preserved():
    row={"population":"France","year":1950,"age_interval":"0-4",
         "rate_type":"life_table_mx_qx","mx":0.15,"qx":0.52,
         "deaths":52000,"exposure":350000,"source_url":"https://population.un.org/wpp/",
         "retrieved_at":"2026-10-31","source_sha256":"d"*64,
         "data_status":"MODELLED_PERIOD_LIFE_TABLE"}
    accepted,rejected=mod._validate_stats([row])
    assert rejected==[] and len(accepted)==1
    assert accepted[0]["mx"]==0.15 and accepted[0]["qx"]==0.52

def test_statistics_summary_keeps_life_table_rates():
    base={"population":"France","year":1816,"age_interval":"0-4",
          "source_url":"https://example.org/life-table","retrieved_at":"2026-10-31",
          "source_sha256":"e"*64}
    case={"mortality_statistics":[
        {**base,"rate_type":"q_x","rate_value":0.4626},
        {**base,"rate_type":"m_x","rate_value":0.1234}
    ]}
    result=mod.build_mortality_matrix(case,{},ROOT)
    summary=result["statistics_by_year"]["1816"]
    assert summary["qx_rate_value_mean"]==0.4626
    assert summary["mx_rate_value_mean"]==0.1234


def test_jsonl_gz_table_is_streamed_and_summarized(tmp_path):
    import gzip, json
    audit=tmp_path/"MORTALITY_AUDIT"
    audit.mkdir()
    rows=[
        {"population":"France","year":1950,"age_interval":"0-4","rate_type":"life_table_mx_qx",
         "mx":0.15,"qx":0.52,"source_url":"https://population.un.org/wpp/",
         "retrieved_at":"2026-10-31","source_sha256":"f"*64,
         "data_status":"MODELLED_PERIOD_LIFE_TABLE"}
    ]
    path=audit/"mortality_statistics.jsonl.gz"
    with gzip.open(path,"wt",encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row)+"\n")
    result=mod.build_mortality_matrix({}, {}, tmp_path)
    assert result["status"]=="STATISTICAL_TABLE_LOADED"
    assert result["accepted_statistical_rows"]==1
    assert result["rejected_statistical_rows"]==0
    assert result["data_table"]=="MORTALITY_AUDIT/mortality_statistics.jsonl.gz"
    assert result["statistics_by_year"]["1950"]["life_table_qx_mean"]==0.52
    assert result["statistics_by_year"]["1950"]["life_table_mx_mean"]==0.15
