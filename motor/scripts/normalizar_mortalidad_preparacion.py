#!/usr/bin/env python3
"""Normalize the preparation CSV schema into the validated mortality sidecar schema."""
from __future__ import annotations
import argparse, csv, json, re
from collections import defaultdict
from pathlib import Path

def _num(value):
    if value is None or str(value).strip() == "":
        return None
    return float(str(value).replace(",", "."))

def _indicator(value):
    key = re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")
    aliases = {
        "deaths": "deaths", "death": "deaths", "death_count": "deaths",
        "dx": "deaths", "exposure": "exposure", "population_exposure": "exposure",
        "lx": "exposure", "person_years": "exposure",
        "qx": "q_x", "q_x": "q_x", "probability_of_dying": "q_x",
        "mx": "m_x", "m_x": "m_x", "central_death_rate": "m_x"
    }
    return aliases.get(key)

def normalize_rows(rows):
    groups = defaultdict(dict)
    rejected = []
    for i, row in enumerate(rows):
        try:
            y0 = int(row["year_start"])
            y1 = int(row.get("year_end") or y0)
            age0 = int(row["age_start"])
            age1_raw = row.get("age_end")
            age1 = int(age1_raw) if age1_raw not in (None, "") else None
            value = _num(row.get("value"))
        except (KeyError, TypeError, ValueError):
            rejected.append({"row": i, "reason": "INVALID_PERIOD_AGE_OR_VALUE"})
            continue
        if y0 < 1 or y1 < y0 or y1 > 2100 or age0 < 0 or (age1 is not None and age1 < age0):
            rejected.append({"row": i, "reason": "OUT_OF_RANGE_PERIOD_OR_AGE"})
            continue
        source_sha = str(row.get("source_file_sha256") or "").lower()
        if not re.fullmatch(r"[0-9a-f]{64}", source_sha):
            rejected.append({"row": i, "reason": "INVALID_SOURCE_SHA256"})
            continue
        source_url = str(row.get("source_url") or "")
        if not source_url.startswith(("https://", "http://")):
            rejected.append({"row": i, "reason": "INVALID_SOURCE_URL"})
            continue
        indicator = _indicator(row.get("indicator"))
        if indicator is None or value is None:
            rejected.append({"row": i, "reason": "UNSUPPORTED_INDICATOR_OR_EMPTY_VALUE"})
            continue
        population = str(row.get("country_or_area") or row.get("population_id") or "").strip()
        if not population:
            rejected.append({"row": i, "reason": "MISSING_POPULATION"})
            continue
        age_interval = f"{age0}-{age1}" if age1 is not None else f"{age0}+"
        key = (
            population, str(row.get("subnational_area") or ""), str(row.get("sex") or ""),
            y0, y1, age_interval, source_url, source_sha,
            str(row.get("source_organization") or ""), str(row.get("source_dataset") or ""),
            str(row.get("source_version_or_revision") or ""), str(row.get("retrieval_date") or ""),
            str(row.get("data_status") or ""), str(row.get("unit") or ""), str(row.get("notes") or "")
        )
        g = groups[key]
        if indicator in g:
            rejected.append({"row": i, "reason": "DUPLICATE_INDICATOR_IN_GROUP", "indicator": indicator})
            continue
        g[indicator] = value
        g["_meta"] = row
    records = []
    for key, values in groups.items():
        population, subnational, sex, y0, y1, age_interval, source_url, source_sha, org, dataset, version, retrieved, status, unit, notes = key
        meta = values["_meta"]
        common = {
            "population": population, "country": population, "year": y0,
            "age_interval": age_interval, "source_url": source_url,
            "retrieved_at": retrieved, "source_sha256": source_sha,
            "historical_epoch": f"{y0}-{y1}" if y1 != y0 else None,
            "sex": sex or None, "subnational_area": subnational or None,
            "period_type": meta.get("period_type") or None,
            "year_start": y0, "year_end": y1, "age_start": int(meta["age_start"]),
            "age_end": int(meta["age_end"]) if meta.get("age_end") not in (None, "") else None,
            "data_status": status or None, "source_organization": org or None,
            "source_dataset": dataset or None, "source_version_or_revision": version or None,
            "unit": unit or None, "population_id": meta.get("population_id") or None,
            "indicator": meta.get("indicator") or None, "value": _num(meta.get("value")),
            "notes": notes or None
        }
        if "q_x" in values:
            records.append({**common, "rate_type": "q_x", "rate_value": values["q_x"]})
        if "m_x" in values:
            records.append({**common, "rate_type": "m_x", "rate_value": values["m_x"]})
        if "deaths" in values and "exposure" in values:
            records.append({**common, "rate_type": "deaths_per_100000_exposure",
                            "deaths": values["deaths"], "exposure": values["exposure"]})
        if not any(k in values for k in ("q_x", "m_x")) and not ("deaths" in values and "exposure" in values):
            rejected.append({"group": str(key[:6]), "reason": "INCOMPLETE_DEATHS_EXPOSURE_OR_RATE"})
    return {"schema_version": "1.1", "records": records, "rejected": rejected}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("output_json", type=Path)
    args = ap.parse_args()
    with args.input_csv.open("r", encoding="utf-8-sig", newline="") as f:
        result = normalize_rows(csv.DictReader(f))
    args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(result["records"]), "rejected": len(result["rejected"]), "output": str(args.output_json)}))

if __name__ == "__main__":
    main()
