#!/usr/bin/env python3
"""Fail-closed U6 sandbox preflight; never invokes Engine, shell, LLM or network."""
import argparse, json, os, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sandbox_runtime"
REPORT=Path(os.getenv("SANDBOX_REPORT","sandbox-report.json"))
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
    result={"status":"BLOCKED","commit_sha":a.expected_sha,"engine_invoked":False,"llm_called":False,"dispatch_performed":False}
    def finish(code,reason=None):
        if reason: result["reason"]=reason
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(result,ensure_ascii=False))
        return code
    if not re.fullmatch(r"[0-9a-f]{40}",a.expected_sha): return finish(2,"expected SHA must be full 40-char SHA")
    if os.getenv("GITHUB_SHA") and os.environ["GITHUB_SHA"]!=a.expected_sha: return finish(2,"workflow selected SHA mismatch")
    try:
        from jsonschema import Draft202012Validator
        js=load(BASE/"contracts/sandbox-job-v1.schema.json")
        bs=load(BASE/"contracts/llm-bridge-response-v1.schema.json")
        Draft202012Validator.check_schema(js); Draft202012Validator.check_schema(bs)
        job=load(Path(a.plan)); Draft202012Validator(js).validate(job)
        policy=load(BASE/"policy/protected-paths.json")
    except Exception as e: return finish(2,"contract validation failed: "+type(e).__name__+": "+str(e))
    if job["source"]["repository"]!="marcojpad-hash/motor-u6-storage" or job["source"]["ref"]!="sandbox-testing": return finish(2,"repo/ref mismatch")
    if job["source"]["commit_sha"]=="0"*40: job["source"]["commit_sha"]=a.expected_sha
    if job["source"]["commit_sha"]!=a.expected_sha: return finish(2,"plan SHA differs from selected SHA")
    if policy.get("complete") is not True: return finish(2,"protected-path inventory incomplete; fail closed")
    result["status"]="PREFLIGHT_PASS"
    result["steps_validated"]=len(job["steps"])
    result["execution_kind"]="INFRASTRUCTURE_FIXTURE"
    return finish(0)
if __name__=="__main__": sys.exit(main())
