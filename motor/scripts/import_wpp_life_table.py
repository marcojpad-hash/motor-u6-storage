#!/usr/bin/env python3
"""Fetch and normalize the official UN WPP 2024 abridged life table.

The output is JSON Lines gzip so the mortality sidecar can stream it without
loading millions of observations into memory.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import os
import tempfile
import urllib.request
from pathlib import Path

SOURCE_URL = (
    "https://population.un.org/wpp/assets/Excel%20Files/"
    "1_Indicator%20%28Standard%29/CSV_FILES/"
    "WPP2024_Life_Table_Abridged_Medium_1950-2023.csv.gz"
)
CATALOGUE_URL = "https://population.un.org/wpp/assets/downloads.json"
LICENSE = "CC BY 3.0 IGO"
REQUIRED_COLUMNS = {"Location", "LocID", "Time", "AgeGrp", "AgeGrpStart", "Sex", "mx", "qx", "LocTypeName"}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def number(value):
    if value is None or str(value).strip() in ("", "NA", "NaN", "nan"):
        return None
    return float(value)

def age_interval(row):
    label = str(row.get("AgeGrp") or "").strip()
    if label and ( "-" in label or "+" in label):
        return label
    start = number(row.get("AgeGrpStart"))
    span = number(row.get("AgeGrpSpan"))
    if start is None:
        raise ValueError("AgeGrpStart is missing")
    if span is None or span <= 0:
        return f"{int(start)}+"
    return f"{int(start)}-{int(start + span - 1)}"

def download(url: str, destination: Path):
    request = urllib.request.Request(url, headers={"User-Agent": "CAPCOT-Mortality-Audit/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

def build(raw_path: Path, output_path: Path, manifest_path: Path, source_url: str = SOURCE_URL):
    source_hash = sha256_file(raw_path)
    retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    skipped = 0
    with gzip.open(raw_path, "rt", encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            raise ValueError("UN WPP CSV schema mismatch; missing columns: " + ", ".join(missing))
        with gzip.open(output_path, "wt", encoding="utf-8", newline="") as out:
            for row in reader:
                if row.get("LocTypeName") != "Country/Area":
                    continue
                variant = str(row.get("Variant") or "Medium").strip().lower()
                if variant not in ("medium", "medium variant"):
                    continue
                mx = number(row.get("mx"))
                qx = number(row.get("qx"))
                if mx is None or qx is None or mx < 0 or not 0 <= qx <= 1:
                    skipped += 1
                    continue
                try:
                    year = int(float(row["Time"]))
                    age_start = int(float(row["AgeGrpStart"]))
                    age = age_interval(row)
                    loc_id = str(row["LocID"]).strip()
                    location = str(row["Location"]).strip()
                    sex = str(row["Sex"]).strip()
                except (TypeError, ValueError, KeyError):
                    skipped += 1
                    continue
                record = {
                    "population": location,
                    "population_id": loc_id,
                    "country": location,
                    "year": year,
                    "year_start": year,
                    "year_end": year,
                    "age_interval": age,
                    "age_start": age_start,
                    "age_end": (int(age_start + float(row["AgeGrpSpan"]) - 1)
                                if row.get("AgeGrpSpan") not in (None, "") and float(row["AgeGrpSpan"]) > 0 else None),
                    "sex": sex,
                    "rate_type": "life_table_mx_qx",
                    "mx": mx,
                    "qx": qx,
                    "source_url": source_url,
                    "retrieved_at": retrieved_at,
                    "source_sha256": source_hash,
                    "historical_epoch": "WPP2024_PERIOD_1950_2023",
                    "period_type": "period_life_table",
                    "data_status": "MODELLED_PERIOD_LIFE_TABLE",
                    "source_organization": "United Nations DESA Population Division",
                    "source_dataset": "World Population Prospects 2024",
                    "source_version_or_revision": "2024 Medium",
                    "indicator": "mx_qx",
                    "unit": "mx_per_person_year_and_qx_probability",
                    "notes": "Period life table for a hypothetical cohort; not observed deaths or actual population exposure. WPP variant Medium."
                }
                out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                count += 1
    size = output_path.stat().st_size
    if size > 90 * 1024 * 1024:
        output_path.unlink(missing_ok=True)
        raise ValueError(f"Normalized output exceeds 90 MiB GitHub file guard: {size} bytes")
    manifest = {
        "schema_version": "1.1",
        "status": "DATASET_BUILT",
        "source": "United Nations World Population Prospects 2024",
        "source_url": source_url,
        "catalogue_url": CATALOGUE_URL,
        "license": LICENSE,
        "retrieved_at": retrieved_at,
        "source_sha256": source_hash,
        "records_written": count,
        "rows_skipped": skipped,
        "filters": {"LocTypeName": "Country/Area", "Variant": "Medium", "years": "1950-2023", "sex": "all source values"},
        "data_status": "MODELLED_PERIOD_LIFE_TABLE",
        "interpretation": "mx/qx from period life tables; hypothetical cohort; not observed deaths or actual population exposure.",
        "output_file": str(output_path.name),
        "output_bytes": size,
        "output_sha256": sha256_file(output_path)
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=None, help="Use an already downloaded .csv.gz source")
    ap.add_argument("--output", type=Path, default=Path("motor/MORTALITY_AUDIT/mortality_statistics.jsonl.gz"))
    ap.add_argument("--manifest", type=Path, default=Path("motor/MORTALITY_AUDIT/mortality_statistics_manifest.json"))
    ap.add_argument("--url", default=SOURCE_URL)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="wpp2024_") as tmp:
        raw = args.raw
        if raw is None:
            raw = Path(tmp) / "wpp2024_life_table.csv.gz"
            download(args.url, raw)
        result = build(raw, args.output, args.manifest, args.url)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
