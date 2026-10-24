#!/usr/bin/env python3
"""Resolve a persistent StinkBox home without placing its state inside U6 ZIPs."""
from __future__ import annotations
import os, shutil
from pathlib import Path

def resolve(root: Path) -> Path:
    explicit=os.environ.get("STINKBOX_HOME")
    if explicit:
        home=Path(explicit).expanduser().resolve()
    else:
        candidates=[root.parent/"STINKBOX_PERSISTENTE_20261020", root.parent/"STINKBOX_PERSISTENTE", Path.home()/"STINKBOX_PERSISTENTE"]
        home=next((p.resolve() for p in candidates if (p/"data"/"registro_tokens.json").is_file()), candidates[-1].resolve())
    home.mkdir(parents=True,exist_ok=True)
    os.environ["STINKBOX_HOME"]=str(home)
    os.environ.setdefault("STINKBOX_STORAGE_ROOT",str(home/"STINKBOX_STORAGE"))
    return home

if __name__=="__main__":
    import json
    print(json.dumps({"STINKBOX_HOME":str(resolve(Path(__file__).resolve().parent))},ensure_ascii=False))
