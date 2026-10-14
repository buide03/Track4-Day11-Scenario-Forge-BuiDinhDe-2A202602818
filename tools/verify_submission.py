"""Validate saved artifacts and one exact hazard replay without rerunning the searches."""
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from avsim import core, studio
from lab11 import metrics


def read(name):
    return json.loads((ROOT / "evidence" / (name + ".json")).read_text(encoding="utf-8"))


def main():
    meta = read("meta")
    expected_steps = {"world", "replay", "mc", "hunt", "estimate", "fix", "mine", "export"}
    assert set(meta["steps"]) == expected_steps
    assert all(not row["quick"] for row in meta["steps"].values())
    for name in ["world", "replay", "mc", "hunt", "estimate", "fix", "mine", "meta"]:
        provenance = read(name)["_run"]
        assert provenance["mssv"] == "202602818" and provenance["town"] == "A"
        assert not provenance["quick"] and not provenance["salted"]
    cloud, hunt = read("cloud"), read("hunt")
    assert len(cloud) == 9600
    for index, mode in enumerate(["bus_bypass", "cut_in", "crosswalk_block", "rear_ended"]):
        rows = cloud[index * 2400:(index + 1) * 2400]
        assert dict(Counter(r["mode"] for r in rows if r["out"] == "crash")) == hunt[mode]["found"]
        assert sum(r["out"] == "infeasible" for r in rows) == hunt[mode]["infeasible"]
    mc, est = read("mc"), read("estimate")
    assert mc["n"] == 3000
    assert sum(row["k"] for row in mc["per_mode"].values()) == mc["crashes"]
    assert est["other"]["k"] == mc["modes"].get("other", 0)
    assert est["other"]["n"] == mc["n"]
    assert len(est["seeds"]) == 3
    assert all(r["n"] == 600 for seed in est["seeds"] for r in seed["per"].values())
    fix = read("fix")
    eligible = [r for r in fix["table"] if r["progress"] >= 0.95 * fix["baseline_train"]["progress"]]
    assert fix["chosen"] == sorted(eligible, key=lambda r: (r["fail_hi"], -r["progress"]))[0]
    doc = studio.load(str(ROOT / "hazard.json"))
    assert studio.check_space(doc) == [] and studio.hazard_ok(doc["hazards"], doc["params"])
    mine = read("mine")
    exact = core.rollout(doc["params"], policy=doc["policy"], hazards=doc["hazards"])
    assert [[e["a"], e["b"], e["t"]] for e in exact.events[0]] == mine["exact"]["planner"]
    assert mine["accepted"] >= 0.5 and mine["world"] == "scene"
    for name in ["baseline", "chosen"]:
        row = mine[name]
        assert row["crashes"] == sum(row[k] for k in ["avoidable", "unavoidable", "unattributed"])
        assert row["n"] == 1500 and row["overlap_at_start"] == 0
    vis = read("visual_checks")
    assert vis["page_errors"] == []
    assert not vis["fix_comparison"]["chosen_events"] and vis["fix_comparison"]["baseline_events"]
    assert [(e["a"], e["b"], e["f"], e["kind"]) for e in vis["hazard"]["events"]] == [
        (e["a"], e["b"], e["f"], e["kind"]) for e in metrics.ego_events(exact, 0)]
    report = (ROOT / "REPORT.md").read_text(encoding="utf-8")
    assert report.splitlines()[0] == "MSSV: 202602818"
    assert len(re.findall(r"^## [1-9]\.", report, re.M)) == 9
    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", report)
    assert len(images) == 4 and all((ROOT / image).is_file() for image in images)
    subprocess.run(["git", "diff", "--exit-code", "--", "avsim", "run_all.py", "tests", "policy_candidates.json", "requirements.txt"], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    summary = dict(mssv="202602818", town="A", full_budget_steps=sorted(expected_steps),
                   todos_public_tests_passed=31, python_js_parity_tests_passed=10,
                   test_note="Counts observed during completion: public TODO tests in WSL; parity tests with Windows Python and Node. This artifact verifier does not rerun those tests. Hidden grader tests unavailable.",
                   protected_files_unchanged=True, screenshot_count=len(images),
                   cloud_rows=len(cloud), artifact_consistency="passed", exact_hazard_replay="matched")
    (ROOT / "evidence" / "validation.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
