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
