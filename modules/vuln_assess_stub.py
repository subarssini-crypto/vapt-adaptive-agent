"""
TEMPORARY stub version of vuln_assess.py — mimics his real function
signatures and return shapes, but doesn't need Docker/Juice Shop running.
Delete this file once Docker is ready and swap back to the real one.
"""

def run_auth_check(state) -> dict:
    print(f"[STUB] Simulating auth check on {state['target_url']} ...")
    return {
        "finding_type": "auth",
        "data": {
            "session_token": "fake_token_xyz",
            "role": "user",
            "logged_in_as": "test3@test.com",
        },
        "chain_trigger": True,
        "chain_data": {
            "next_module": "idor_check",
            "reason": "Valid session obtained — worth testing if it can access other users' data",
            "token": "fake_token_xyz",
        },
    }

def run_idor_check(state) -> dict:
    token = state["pending_chain"]["token"] if state.get("pending_chain") else None
    print(f"[STUB] Simulating IDOR check using token: {token}")
    return {
        "finding_type": "idor",
        "data": {
            "vulnerable": True,
            "accessible_basket_ids": [3, 5],
            "detail": "Simulated: found accessible basket IDs 3 and 5",
        },
        "chain_trigger": False,
        "chain_data": None,
    }

def run_sqli_check(state) -> dict:
    print(f"[STUB] Simulating SQLi check on {state['target_url']} ...")
    return {
        "finding_type": "sqli",
        "data": {"vulnerable": False, "detail": "Simulated: login endpoint rejected SQLi payload"},
        "chain_trigger": False,
        "chain_data": None,
    }

def run_xss_check(state) -> dict:
    print(f"[STUB] Simulating XSS check on {state['target_url']} ...")
    return {
        "finding_type": "xss",
        "data": {"vulnerable": True, "detail": "Simulated: payload reflected without escaping"},
        "chain_trigger": False,
        "chain_data": None,
    }