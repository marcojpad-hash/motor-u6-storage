import csv, gzip, importlib.util, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("wpp_importer", ROOT/"scripts"/"import_wpp_life_table.py")
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

def test_wpp_importer_filters_and_normalizes_real_schema(tmp_path):
    raw=tmp_path/"sample.csv.gz"
    fields=["Location","LocID","Variant","Time","AgeGrp","AgeGrpStart","AgeGrpSpan","Sex","mx","qx","LocTypeName"]
    rows=[
        {"Location":"France","LocID":"250","Variant":"Medium","Time":"1950","AgeGrp":"0-4","AgeGrpStart":"0","AgeGrpSpan":"5","Sex":"Both sexes","mx":"0.15","qx":"0.52","LocTypeName":"Country/Area"},
        {"Location":"Europe","LocID":"908","Variant":"Medium","Time":"1950","AgeGrp":"0-4","AgeGrpStart":"0","AgeGrpSpan":"5","Sex":"Both sexes","mx":"0.15","qx":"0.52","LocTypeName":"Region"}
    ]
    with gzip.open(raw,"wt",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    out=tmp_path/"mortality_statistics.jsonl.gz"
    manifest=tmp_path/"manifest.json"
    result=mod.build(raw,out,manifest)
    with gzip.open(out,"rt",encoding="utf-8") as f:
        records=[json.loads(line) for line in f]
    assert len(records)==1
    row=records[0]
    assert row["population"]=="France"
    assert row["age_interval"]=="0-4" and row["age_end"]==4
    assert row["rate_type"]=="life_table_mx_qx"
    assert row["mx"]==0.15 and row["qx"]==0.52
    assert row["source_sha256"]==mod.sha256_file(raw)
    assert result["records_written"]==1 and result["rows_skipped"]==0
