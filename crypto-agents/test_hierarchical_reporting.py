"""No-network regression of actual worker -> supervisors -> directors -> Chief D."""
import json, tempfile
from pathlib import Path
from hierarchical_reporting import chain,generate

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj),encoding="utf-8")

with tempfile.TemporaryDirectory() as temp:
    root=Path(temp)
    raw=root/"raw"
    ids=["D01-M01-W01","D01-M01-W01-S001","D01-M01-W01-S001-G001","D01-M01-W01-S001-G001-H001"]
    save(raw/"manifest-D01.json",{"director_id":"D01","workforce_namespace":"transferexperiment","worker_processes_selected":ids})
    for wid in ids:
        save(raw/(wid+".json"),{
            "worker_id":wid,"globally_unique_agent_id":"transferexperiment/"+wid,
            "workforce_namespace":"transferexperiment","director_id":"D01","parent_id":chain(wid)[-2],
            "os_process_pid":1234,"inference_status":"model_completed",
            "model_response":"A source-backed independent research idea and action",
            "source_items":[{"url":"https://example.org"}],
            "cognitive_checkpoint":{"next_action":"Verify payer eligibility before submitting"}
        })
    first=raw/(ids[0]+".json")
    example=json.loads(first.read_text())
    example["practical_training_while_working"]={"result":{
        "status":"APPLIED_ORIGINAL_DRAFT_NEEDS_INDEPENDENT_REVIEW",
        "real_model_call_completed":True},"actual_work_sample_file":"ai-process-reports/sample.md"}
    save(first,example)
    save(root/"strict.json",{"fleet":"transferexperiment","individual_results":[
        {"id":"transferexperiment/"+x,"grade":"QUALIFIED_SOURCE_BACKED_AI_RESEARCH","defects":[]} for x in ids]})
    r=generate(raw,root/"strict.json",root/"out","transferexperiment")
    assert r["attempted_worker_reports"]==4, r
    assert r["completed_worker_model_reports"]==4, r
    assert r["strict_qualified_research_reports"]==4, r
    assert r["real_training_model_calls"]==1, r
    assert r["applied_training_drafts_needing_review"]==1, r
    assert r["supervisor_inboxes"]==5, r
    assert r["recorded_handoffs"]==sum(len(chain(w)) for w in ids), r
    assert (root/"out"/"transferexperiment"/"workers"/(ids[-1]+".md")).exists()
    supervisor=json.loads((root/"out"/"transferexperiment"/"manager"/"D01-M01.json").read_text())
    assert supervisor["attempted_descendant_reports"]==4
    assert supervisor["real_supervisor_model_review_verified"] is False
    worker=json.loads((root/"out"/"transferexperiment"/"workers"/(ids[-1]+".json")).read_text())
    assert worker["direct_parent"]=="transferexperiment/D01-M01-W01-S001-G001"
    assert worker["route_to_D"][-1]=="CHIEF_D"
    bad=raw/(ids[0]+".json")
    d=json.loads(bad.read_text())
    d["inference_status"]="model_failed"
    save(bad,d)
    r2=generate(raw,root/"strict.json",root/"out2","transferexperiment")
    assert r2["completed_worker_model_reports"]==3
    assert r2["directors"][0]["corrections"]>=1
    for wid in ("D01-M16-W01","D01-M01-W51","D01-M01-W01-S151","D01-M01-W01-G001"):
        try:
            chain(wid)
            raise AssertionError("Incorrectly accepted "+wid)
        except ValueError:
            pass
    try:
        generate(raw,root/"strict.json",root/"out3","BountyScoutAI")
        raise AssertionError("Wrong-company strict grades were accepted")
    except ValueError:
        pass
print("PASS real W/S/G/H report ladder, 5 inboxes, all handoffs, failure corrections, company isolation")
