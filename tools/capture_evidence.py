"""Capture the real shipped 3D viewer, without changing its source.

Run with Windows Python (playwright installed) from the lab root after export.
The simulation and screenshots run locally; no browser account is used.
"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence"
SHOTS = EVID / "shots"


def read(name):
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def write(name, data):
    (EVID / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def simulate(page, run, policy):
    return page.evaluate("""({run,policy}) => {
        const S = window.SimCore;
        const log = run.others === 'replay' ? S.rollout({ego:'human', params:run.params, hazards:run.hazards}) : null;
        const r = S.rollout({ego:'planner', others:run.others || 'reactive', params:run.params,
                            policy, hazards:run.hazards, log});
        return r.events.filter(e => e.a === 'ego' || e.b === 'ego');
    }""", {"run": run, "policy": policy})


def capture(page, name, at):
    if page.locator("#play").get_attribute("aria-label") == "Dừng":
        page.locator("#play").click()
    page.locator("#time").evaluate("(el,t)=>{el.value=t;el.dispatchEvent(new Event('input',{bubbles:true}));}", at)
    page.wait_for_timeout(1200)
    page.screenshot(path=str(SHOTS / name))


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    viewer = read("viewer.json")
    fix = read("fix.json")
    chosen = fix["chosen"]["policy"]
    checks = {"source": "Shipped viewer/index.html and SimCore; actual browser screenshots", "runs": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--allow-file-access-from-files", "--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
        page.emulate_media(color_scheme="light")
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        url = (ROOT / "viewer" / "index.html").as_uri()
        page.goto(url + "#lab")
        page.locator("#labFile").set_input_files(str(EVID / "viewer.json"))
        page.wait_for_timeout(500)
        for rid, name in [("B-01", "bus_bypass.png"), ("C-01", "crosswalk_block.png")]:
            run = next(r for r in viewer["runs"] if r["id"] == rid)
            events = simulate(page, run, run.get("policy") or {})
            assert events, rid
            button = page.locator("#labRuns button").nth(viewer["runs"].index(run))
            button.click()
            at = events[0]["t"]
            capture(page, name, at)
            checks["runs"].append(dict(id=rid, source="viewer.json", events=events, screenshot="shots/" + name, time=at))

        # In the normal export, pinned hunt runs show baseline as solid and fix as ghost.
        # A separate supported viewer artifact makes the chosen policy solid and baseline the ghost.
        improved = None
        for run in viewer["runs"]:
            if run.get("label") not in ("bus_bypass", "crosswalk_block"):
                continue
            before = simulate(page, run, run.get("policy") or {})
            after = simulate(page, run, chosen)
            if before and not after:
                improved = (run, before, after)
                break
        assert improved, "No avoided exported scenario found; inspect fix before claiming a visual improvement"
        run, before, after = improved
        comparison = dict(format="avsim-viewer/1", title="Chosen policy solid; original policy ghost", policy=chosen,
                          baseline_policy={}, runs=[dict(id="F-01", label=run["label"], outcome="safe", others="reactive", params=run["params"], policy=None)])
        write("fix_comparison_viewer.json", comparison)
        page.locator("#labFile").set_input_files(str(EVID / "fix_comparison_viewer.json"))
        page.locator("#labRuns button").filter(has_text="F-01").click()
        page.locator("#tLabG").check()
        capture(page, "fix_with_baseline_ghost.png", before[0]["t"])
        checks["fix_comparison"] = dict(source_run=run["id"], source="fix_comparison_viewer.json", baseline_events=before,
                                         chosen_events=after, time=before[0]["t"], screenshot="shots/fix_with_baseline_ghost.png")

        # Reopen the exact original studio artifact, including its assumptions.
        hazard = json.loads((ROOT / "hazard.json").read_text(encoding="utf-8"))
        page.get_by_role("button", name="10 xưởng", exact=True).click()
        page.locator("#stuOpen").set_input_files(str(ROOT / "hazard.json"))
        page.wait_for_timeout(500)
        hazard_run = dict(params=hazard["params"], hazards=hazard["hazards"])
        events = simulate(page, hazard_run, hazard.get("policy") or {})
        assert events, "Exact hazard scene must have the collision described in the report"
        capture(page, "hazard_exact.png", events[0]["t"])
        checks["hazard"] = dict(source="hazard.json", events=events, time=events[0]["t"], screenshot="shots/hazard_exact.png")
        checks["page_errors"] = errors
        assert not errors, errors
        write("visual_checks.json", checks)
        browser.close()
    print("Captured four actual viewer screenshots; no JavaScript page errors.")


if __name__ == "__main__":
    main()
