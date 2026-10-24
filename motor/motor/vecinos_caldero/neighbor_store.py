#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
from typing import Any

class NeighborStore:
    """Persistent, case-independent store of Caldero search neighbors.

    It never changes the 244, Engine V5, P/A/C, freeze, H1/H2 or canonical files.
    """
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.events = self.root / "neighbor_events.jsonl"
        self.index = self.root / "neighbor_index.json"
        if not self.index.exists():
            self.index.write_text(json.dumps({"schema":"caldero_neighbor_store_v1","neighbors":{}}, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _hash(obj: Any) -> str:
        raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",",":"), default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def append(self, *, case_id: str, query: str, tokens_neighbors: list[dict[str, Any]], audit_meta: dict[str, Any] | None = None) -> dict[str, Any]:
        idx = json.loads(self.index.read_text(encoding="utf-8"))
        neighbors = idx.setdefault("neighbors", {})
        added = []
        now = datetime.now(timezone.utc).isoformat()
        event = {
            "timestamp_utc": now,
            "case_id": case_id,
            "query": query,
            "tokens_neighbors": tokens_neighbors,
            "audit_meta": audit_meta or {},
        }
        event_id = self._hash(event)
        event["event_id"] = event_id
        with self.events.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        for row in tokens_neighbors:
            token = str(row.get("token", "")).strip().casefold()
            if not token:
                continue
            rec = neighbors.setdefault(token, {"first_seen_utc": now, "observations": 0, "cases": [], "sources": []})
            rec["observations"] += int(row.get("coactivation_frequency", 1) or 1)
            if case_id not in rec["cases"]:
                rec["cases"].append(case_id)
            for src in row.get("source_refs", []) or []:
                if src and src not in rec["sources"]:
                    rec["sources"].append(src)
            added.append(token)

        idx["updated_utc"] = now
        self.index.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"event_id": event_id, "tokens_added_or_updated": sorted(set(added)), "store": str(self.root)}
