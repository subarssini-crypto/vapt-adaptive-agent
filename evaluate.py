"""
Module 6b: Evaluation — baseline (no chaining) vs. full agent (chaining enabled)
"""

from agent import app
from state import initial_state
from modules.report import generate_report

TARGET = "http://localhost:3000"

def run_mode(chaining_enabled: bool):
    label = "WITH CHAINING" if chaining_enabled else "BASELINE (NO CHAINING)"
    print(f"\n{'='*60}")
    print(f"RUNNING: {label}")
    print(f"{'='*60}")

    state = initial_state(TARGET, chaining_enabled=chaining_enabled)
    final_state = app.invoke(state)
    return final_state

def summarize_run(label, final_state):
    vulnerable_findings = [
        f for f in final_state["findings"]
        if isinstance(f["data"], dict) and f["data"].get("vulnerable") is True
    ]

    return {
        "label": label,
        "modules_run": final_state["modules_run"],
        "total_steps": final_state["step_count"],
        "total_findings": len(final_state["findings"]),
        "vulnerabilities_confirmed": [f["finding_type"] for f in vulnerable_findings],
        "idor_ran": "idor_check" in final_state["modules_run"],
    }

if __name__ == "__main__":
    baseline_result = run_mode(chaining_enabled=False)
    baseline_summary = summarize_run("BASELINE (chaining disabled)", baseline_result)

    chained_result = run_mode(chaining_enabled=True)
    chained_summary = summarize_run("FULL AGENT (chaining enabled)", chained_result)

    print("\n" + generate_report(chained_result))

    print(f"\n\n{'='*60}")
    print("COMPARISON: BASELINE vs. CHAINING-ENABLED AGENT")
    print(f"{'='*60}\n")

    for summary in [baseline_summary, chained_summary]:
        print(f"--- {summary['label']} ---")
        print(f"  Modules run: {summary['modules_run']}")
        print(f"  Total steps: {summary['total_steps']}")
        print(f"  Total findings: {summary['total_findings']}")
        print(f"  Confirmed vulnerabilities: {summary['vulnerabilities_confirmed']}")
        print(f"  Did IDOR get tested?: {summary['idor_ran']}")
        print()

    print(f"{'='*60}")
    print("KEY RESULT")
    print(f"{'='*60}")
    if not baseline_summary["idor_ran"] and chained_summary["idor_ran"]:
        print("Baseline NEVER tested for IDOR, even though a valid session token")
        print("was discovered during auth_check. The chaining-enabled agent")
        print("automatically used that token to test IDOR and confirmed it as")
        print("vulnerable — a finding the isolated-pipeline baseline missed entirely.")
    else:
        print("Both modes tested IDOR — check chaining_enabled logic if unexpected.")