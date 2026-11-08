#!/usr/bin/env python3
"""Fail-closed U6 sandbox preflight. No engine, shell, LLM or network execution."""
import argparse, hashlib, json, os, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sandbox_runtime"
def load(path):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d: raise ValueError("duplicate JSON key: "+k)
            d[k]=v
        return d
    return json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=pairs,parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--expected-sha",required=True)
    p.add_argument("--plan",default=str(BASE/"execution-plan.json"))
    a=p.parse_args()
    def block(msg):
        print(json.dumps({"status":"BLOCKED","reason":msg},ensure_ascii=False)); return 2
    if not re.fullmatch(r"[0-9a-f]{40}",a.expected_sha): return block("expected SHA must be full 40-char SHA")
    if os.getenv("GITHUB_SHA") and os.environ["GITHUB_SHA"]!=a.expected_sha: return block("workflow control SHA mismatch")
    try:
        from jsonschema import Draft202012Validator
        js=load(BASE/"contracts/sandbox-job-v1.schema.json")
        bs=load(BASE/"contracts/llm-bridge-response-v1.schema.json")
        Draft202012Validator.check_schema(js); Draft202012Validator.check_schema(bs)
        job=load(Path(a.plan)); Draft202012Validator(js).validate(job)
        policy=load(BASE/"policy/protected-paths.json")
    except Exception as e: return block("contract validation failed: "+type(e).__name__+": "+str(e))
    if job["source"]["repository"]!="marcojpad-hash/motor-u6-storage" or job["source"]["ref"]!="sandbox-testing": return block("repo/ref mismatch")
    if job["source"]["commit_sha"]!=a.expected_sha: return block("plan SHA differs from selected SHA")
    if policy.get("complete") is not True: return block("protected-path inventory incomplete; fail closed")
    print(json.dumps({"status":"PREFLIGHT_PASS","commit_sha":a.expected_sha,"engine_invoked":False,"llm_called":False,"dispatch_performed":False}))
    return 0
if __name__=="__main__": sys.exit(main())
