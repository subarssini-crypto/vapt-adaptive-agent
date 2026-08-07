from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from state import AgentState, initial_state, summarize_state

llm = ChatOllama(model="llama3.1:8b")

CORE_MODULES = ["fingerprint", "auth_check", "sqli_check", "xss_check"]
MAX_STEPS = 15

# --- Stub modules (Person B will replace these with real logic) ---
def run_fingerprint():
    return {
        "finding_type": "tech_stack_identified",
        "data": {"stack": "Node.js", "version": "18.2"},
        "chain_trigger": False,
        "chain_data": None
    }

def run_auth_check():
    return {
        "finding_type": "auth_token_found",
        "data": {"token": "abc123", "user": "lowpriv_user"},
        "chain_trigger": True,
        "chain_data": {"suggested_module": "idor_check", "token": "abc123"}
    }

def run_idor_check(token):
    print(f"  -> running IDOR check using token: {token}")
    return {
        "finding_type": "idor_confirmed",
        "data": {"leaked_user": "other_user"},
        "chain_trigger": False,
        "chain_data": None
    }

def run_sqli_check():
    return {
        "finding_type": "no_vulnerability",
        "data": {},
        "chain_trigger": False,
        "chain_data": None
    }

def run_xss_check():
    return {
        "finding_type": "xss_found",
        "data": {"field": "search_box"},
        "chain_trigger": False,
        "chain_data": None
    }

MODULE_RUNNERS = {
    "fingerprint": lambda state: run_fingerprint(),
    "auth_check": lambda state: run_auth_check(),
    "sqli_check": lambda state: run_sqli_check(),
    "xss_check": lambda state: run_xss_check(),
    "idor_check": lambda state: run_idor_check(state["pending_chains"][0]["token"]),
}

# --- decide_node ---
def decide_node(state: AgentState):
    step_num = len(state["decision_log"]) + 1

    if step_num > MAX_STEPS:
        reason = "hit max step limit — stopping to avoid infinite loop"
        state["decision_log"].append(f"Step {step_num}: {reason}")
        state["_next_action"] = "stop"
        state["done"] = True
        print(f"  [Step {step_num}] {reason}")
        return state

    if state["pending_chains"]:
        chain = state["pending_chains"][0]
        action = chain["suggested_module"]
        reason = f"CHAINED into '{action}' because: previous finding provided data ({chain})"
        state["decision_log"].append(f"Step {step_num}: {reason}")
        state["_next_action"] = action
        print(f"  [Step {step_num}] {reason}")
        return state

    remaining = [m for m in CORE_MODULES if m not in state["modules_run"]]

    if not remaining:
        reason = "all core modules run, no pending chains — assessment complete"
        state["decision_log"].append(f"Step {step_num}: {reason}")
        state["_next_action"] = "stop"
        state["done"] = True
        print(f"  [Step {step_num}] {reason}")
        return state

    prompt = f"""Current assessment status:
{summarize_state(state)}

Modules not yet run: {remaining}
Answer with exactly one word — pick the most sensible one to run next."""

    response = llm.invoke(prompt)
    raw = response.content.strip().lower()

    action = next((m for m in remaining if m in raw), remaining[0])
    reason = f"chose '{action}' — next unrun module in the assessment"

    state["decision_log"].append(f"Step {step_num}: {reason}")
    state["_next_action"] = action
    print(f"  [Step {step_num}] {reason}")
    return state

# --- execute_node ---
def execute_node(state: AgentState):
    action = state["_next_action"]
    try:
        result = MODULE_RUNNERS[action](state)
    except Exception as e:
        print(f"  [ERROR] {action} failed: {e}")
        result = {"finding_type": "error", "data": {"error": str(e)}, "chain_trigger": False, "chain_data": None}

    state["findings"].append(result)
    state["modules_run"].append(action)

    if action == "fingerprint" and "stack" in result.get("data", {}):
        state["tech_stack"] = result["data"]

    if action == "idor_check" and state["pending_chains"]:
        state["pending_chains"].pop(0)

    if result["chain_trigger"]:
        state["pending_chains"].append(result["chain_data"])

    return state

def route_after_decide(state: AgentState):
    return "end" if state["done"] else "execute"

graph = StateGraph(AgentState)
graph.add_node("decide", decide_node)
graph.add_node("execute", execute_node)
graph.set_entry_point("decide")
graph.add_conditional_edges("decide", route_after_decide, {"execute": "execute", "end": END})
graph.add_edge("execute", "decide")
app = graph.compile()

if __name__ == "__main__":
    state = initial_state("http://localhost:3000")
    final_state = app.invoke(state)

    print("\n--- DECISION LOG (Module 1's full output) ---")
    for line in final_state["decision_log"]:
        print(line)

    print("\nFINAL modules run:", final_state["modules_run"])
    print("FINAL findings count:", len(final_state["findings"]))
    print("FINAL tech stack:", final_state["tech_stack"])