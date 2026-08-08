"""TEMPORARY stub version of recon.py — no real HTTP requests."""
def run_fingerprint(state) -> dict:
    print(f"[STUB] Simulating fingerprint on {state['target_url']} ...")
    return {
        "finding_type": "fingerprint",
        "data": {"tech_stack": {"status_code": 200, "server_header": "Express"}},
        "chain_trigger": False,
        "chain_data": None,
    }

def run_crawl(state) -> dict:
    print(f"[STUB] Simulating crawl on {state['target_url']} ...")
    return {
        "finding_type": "crawl",
        "data": {"discovered_pages": ["/rest/products/search", "/rest/user/login"]},
        "chain_trigger": False,
        "chain_data": None,
    }