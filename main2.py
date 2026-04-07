import os
import re
from datetime import datetime
import requests
from typing import Dict, Any

# =========================
# Configuration & Constants
# =========================

PIXELA_BASE = "https://pixe.la/v1/users"

# Load from environment (preferred over hardcoding)
USERNAME = os.getenv("PIXELA_USERNAME", "xavierpython")
TOKEN = os.getenv("PIXELA_TOKEN", "fdjlaklfkjsdhfdslkjhh")

GRAPH_ID = "graph1"         # 1–16 chars, must start with a letter
GRAPH_NAME = "Running Graph"
GRAPH_UNIT = "Km"           # free text
GRAPH_TYPE = "float"        # "int" or "float"
GRAPH_COLOR = "sora"        # shibafu | momiji | sora | ichou | ajisai | kuro

# Username validation per earlier rule (first char a-z, then 1–32 of a-z0-9-)
USERNAME_RULE = re.compile(r"^[a-z][a-z0-9-]{1,32}$")
GRAPH_ID_RULE = re.compile(r"^[a-zA-Z][a-zA-Z0-9]{0,15}$")  # Pixela graph ID rule


# =========================
# Utility / HTTP
# =========================

def _session(headers: Dict[str, str]) -> requests.Session:
    """Create a requests.Session with default headers."""
    s = requests.Session()
    s.headers.update(headers)
    return s


def _print_result(action: str, resp: requests.Response) -> None:
    """Print a concise, useful line for each API call."""
    try:
        resp.raise_for_status()
        print(f"{action}: {resp.text}")
    except requests.HTTPError:
        # Show status code + body to help debugging
        print(f"{action} FAILED [{resp.status_code}]: {resp.text}")


# =========================
# Pixela API Calls
# =========================

def create_user(s: requests.Session, username: str, token: str) -> None:
    """
    Create a Pixela user (run once).
    Safe to re-run; Pixela returns 'User already exist.' if it already exists.
    """
    payload = {
        "token": token,
        "username": username,
        "agreeTermsOfService": "yes",
        "notMinor": "yes",
    }
    resp = s.post(url=PIXELA_BASE, json=payload)
    _print_result("Create user", resp)


def create_graph(s: requests.Session, username: str, graph_id: str) -> None:
    """
    Create a Pixela graph for a given user (run once).
    """
    endpoint = f"{PIXELA_BASE}/{username}/graphs"
    payload = {
        "id": graph_id,
        "name": GRAPH_NAME,
        "unit": GRAPH_UNIT,
        "type": GRAPH_TYPE,
        "color": GRAPH_COLOR,
    }
    resp = s.post(url=endpoint, json=payload)
    _print_result("Create graph", resp)


def post_pixel(s: requests.Session, username: str, graph_id: str, date_str: str, quantity: str) -> None:
    """
    Post a pixel (daily entry). date_str must be YYYYMMDD; quantity must be a string.
    """
    endpoint = f"{PIXELA_BASE}/{username}/graphs/{graph_id}"
    payload = {
        "date": date_str,
        "quantity": quantity,
    }
    resp = s.post(url=endpoint, json=payload)
    _print_result("Post pixel", resp)


# =========================
# Main Flow
# =========================

def main() -> None:
    # --- Basic validation before hitting the API ---
    if not USERNAME_RULE.match(USERNAME):
        raise ValueError(
            "USERNAME invalid. Must match [a-z][a-z0-9-]{1,32}. "
            f"Got: {USERNAME}"
        )
    if not GRAPH_ID_RULE.match(GRAPH_ID):
        raise ValueError(
            "GRAPH_ID invalid. Must start with a letter and be 1–16 alphanumerics. "
            f"Got: {GRAPH_ID}"
        )
    if not TOKEN or len(TOKEN) < 8:
        raise ValueError("TOKEN missing or too short (min 8 chars).")

    # --- Shared session & headers (token in header is best practice) ---
    s = _session(headers={"X-USER-TOKEN": TOKEN})

    # 1) Create user (comment out after first success)
    create_user(s, USERNAME, TOKEN)

    # 2) Create graph (comment out after first success)
    create_graph(s, USERNAME, GRAPH_ID)

    # 3) Post today's pixel
    today_str = datetime.now().strftime("%Y%m%d")
    post_pixel(s, USERNAME, GRAPH_ID, today_str, quantity="12")

    # 4) Show where to view the graph
    graph_url = f"{PIXELA_BASE}/{USERNAME}/graphs/{GRAPH_ID}.html"
    print(f"Open your graph: {graph_url}")


if __name__ == "__main__":
    main()
