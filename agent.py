"""
Module 1: Agent Core & Orchestrator
"""

from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

from state import AgentState, initial_state, summarize_state
from modules.recon import run_fingerprint, run_crawl
from modules.vuln_assess import run_auth_check, run_idor_check, run_sqli_check, run_xss_check
from modules.report import generate_report


AVAILABLE_MODULES = {
    "fingerprint": run_fingerprint,
    "crawl": run_crawl,
    "auth_check": run_auth_check,
    "idor_check": run_idor_check,
    "sqli_check": run_sqli_check,
    "xss_check": run_xss_check,
}

llm = ChatOllama(model="llama3.1:8b", temperature=0)


def decide_node(state: AgentState) -> AgentState:
    state["step_count"] += 1

    if state["step_count"] > state["max_steps"]:
        state["done"] = True
        return state

    if state.get("pending_chain") and state.get("chaining_enabled", True):
        next_module = state["pending_chain"]["next_module"]
        reason = state["pending_chain"]["reason"]
        state["decision_log"].append(
            f"Step {state['step_count']}: CHAINED into '{next_module}' because: {reason}"
        )
        state["_next_action"] = next_module
        return state

    available = [m for m in AVAILABLE_MODULES if m not in state["modules_run"]]

    if not available:
        state["done"] = True
        return state

    prompt = f"""You are an autonomous web security assessment agent.

Current assessment state:
{summarize_state(state)}

Available modules you have NOT yet run: {available}

Pick exactly ONE module name from the list above to run next, and briefly
say why. Respond in this exact format:
MODULE: <module_name>
REASON: <one sentence>
"""
    response = llm.invoke(prompt).content

    chosen = available[0]
    reason = "default fallback choice"
    for line in response.splitlines():
        if line.upper().startswith("MODULE:"):
            candidate = line.split(":", 1)[1].strip()
            if candidate in available:
                chosen = candidate
        if line.upper().startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()

    state["decision_log"].append(f"Step {state['step_count']}: chose '{chosen}' — {reason}")
    state["_next_action"] = chosen
    return state


def execute_node(state: AgentState) -> AgentState:
    action = state.get("_next_action")
    print(f"[execute_node] received action = {action!r}, done = {state['done']}")
    if not action or state["done"]:
        print("[execute_node] skipping — no action or already done")
        return state

    tool_fn = AVAILABLE_MODULES[action]
    result = tool_fn(state)

    state["modules_run"].append(action)
    state["findings"].append({"finding_type": result["finding_type"], "data": result["data"]})

    if result["finding_type"] == "fingerprint":
        state["tech_stack"] = result["data"]["tech_stack"]
    if result["finding_type"] == "crawl":
        state["discovered_pages"] = result["data"]["discovered_pages"]
    if result["finding_type"] == "auth":
        state["auth_status"] = result["data"]

    if result.get("chain_trigger"):
        state["pending_chain"] = result["chain_data"]
    else:
        state["pending_chain"] = None

    return state


def should_continue(state: AgentState) -> str:
    return "stop" if state["done"] else "decide"


graph = StateGraph(AgentState)
graph.add_node("decide", decide_node)
graph.add_node("execute", execute_node)

graph.set_entry_point("decide")
graph.add_edge("decide", "execute")
graph.add_conditional_edges("execute", should_continue, {
    "decide": "decide",
    "stop": END,
})

app = graph.compile()


# ============================================================
# TRUE FIXED-SEQUENCE BASELINE — no LLM, no reasoning at all.
# This simulates a traditional scanner: runs every module,
# always in the same order, regardless of findings.
# ============================================================
def run_fixed_baseline(target_url: str):
    """
    Simulates a traditional scanner / AWE-style independent pipelines:
    runs every module in a fixed order, but NEVER shares findings between
    modules (no pending_chain propagation at all).
    """
    state = initial_state(target_url=target_url, max_steps=20, chaining_enabled=False)

    fixed_order = ["fingerprint", "crawl", "auth_check", "sqli_check", "xss_check", "idor_check"]

    for action in fixed_order:
        state["step_count"] += 1
        state["decision_log"].append(
            f"Step {state['step_count']}: fixed sequence — running '{action}' (no reasoning, no cross-module data sharing)"
        )

        tool_fn = AVAILABLE_MODULES[action]
        result = tool_fn(state)

        state["modules_run"].append(action)
        state["findings"].append({"finding_type": result["finding_type"], "data": result["data"]})

        if result["finding_type"] == "auth":
            state["auth_status"] = result["data"]

        # NOTE: deliberately NOT setting state["pending_chain"] here.
        # This is the key difference — a true independent-pipeline system
        # (like AWE) never carries a finding from one module into another.
        # state["pending_chain"] stays None throughout the whole baseline run.

    state["done"] = True
    return state


if __name__ == "__main__":
    TARGET_URL = "http://localhost:3000"

    print("=" * 70)
    print("RUN 1: TRUE BASELINE (fixed sequence, no LLM reasoning, no chaining)")
    print("=" * 70)
    baseline_result = run_fixed_baseline(TARGET_URL)
    print("\n" + generate_report(baseline_result))

    print("\n\n")
    print("=" * 70)
    print("RUN 2: FULL AGENT (adaptive LLM reasoning + chaining ENABLED)")
    print("=" * 70)
    full_state = initial_state(target_url=TARGET_URL, max_steps=10, chaining_enabled=True)
    full_result = app.invoke(full_state)
    print("\n" + generate_report(full_result))

    print("\n\n")
    print("=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    def confirmed_vulns(findings):
        return {f["finding_type"] for f in findings if f["data"].get("vulnerable") is True}

    baseline_vulns = confirmed_vulns(baseline_result["findings"])
    full_vulns = confirmed_vulns(full_result["findings"])
    only_in_full = full_vulns - baseline_vulns

    print(f"Baseline (fixed, no chaining) — CONFIRMED vulnerabilities: {baseline_vulns}")
    print(f"Full agent (adaptive + chaining) — CONFIRMED vulnerabilities: {full_vulns}")
    print(f"Vulnerabilities ONLY confirmed via chaining: {only_in_full}")
    print(f"\nModules run — baseline: {len(baseline_result['modules_run'])}, full agent: {len(full_result['modules_run'])}")