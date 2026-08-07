from typing import TypedDict, List

class AgentState(TypedDict):
    target_url: str
    tech_stack: dict
    pages: List[str]
    findings: List[dict]
    modules_run: List[str]
    pending_chains: List[dict]
    _next_action: str
    decision_log: List[str]
    done: bool

def initial_state(target_url: str) -> AgentState:
    """Returns a fresh, empty state — call this once at the start of a run."""
    return {
        "target_url": target_url,
        "tech_stack": {},
        "pages": [],
        "findings": [],
        "modules_run": [],
        "pending_chains": [],
        "_next_action": "",
        "decision_log": [],
        "done": False
    }

def summarize_state(state: AgentState) -> str:
    """Condenses the full state into a short text block for LLM prompts."""
    lines = []
    lines.append(f"Target: {state['target_url']}")

    if state["tech_stack"]:
        lines.append(f"Tech stack identified: {state['tech_stack']}")

    lines.append(f"Modules already run: {state['modules_run'] or 'none yet'}")
    lines.append(f"Pending chains: {len(state['pending_chains'])}")
    lines.append(f"Total findings so far: {len(state['findings'])}")

    return "\n".join(lines)