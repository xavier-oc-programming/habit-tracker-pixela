import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import requests
from client import PixelaClient
from config import (
    GRAPH_ID, GRAPH_NAME, GRAPH_UNIT, GRAPH_TYPE, GRAPH_COLOR,
    USERNAME_RULE, GRAPH_ID_RULE, MIN_TOKEN_LEN, DATE_FORMAT, DATE_DISPLAY,
)

# ------------------------------------------------------------------ #
# Credentials
# ------------------------------------------------------------------ #

USERNAME = os.getenv("PIXELA_USERNAME", "")
TOKEN = os.getenv("PIXELA_TOKEN", "")


def _validate_credentials() -> None:
    if not USERNAME_RULE.match(USERNAME):
        raise ValueError(
            f"PIXELA_USERNAME invalid. Must match [a-z][a-z0-9-]{{1,32}}. Got: '{USERNAME}'"
        )
    if not GRAPH_ID_RULE.match(GRAPH_ID):
        raise ValueError(
            f"GRAPH_ID invalid. Must start with a letter, 1–16 alphanumerics. Got: '{GRAPH_ID}'"
        )
    if len(TOKEN) < MIN_TOKEN_LEN:
        raise ValueError(
            f"PIXELA_TOKEN missing or too short (min {MIN_TOKEN_LEN} chars). Set it in .env."
        )


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _prompt_date(prompt: str) -> str:
    """Prompt until the user enters a valid YYYYMMDD date string."""
    while True:
        raw = input(prompt).strip()
        try:
            dt = datetime.strptime(raw, DATE_FORMAT)
            return dt.strftime(DATE_FORMAT)
        except ValueError:
            print(f"  Invalid date. Enter in YYYYMMDD format (e.g. {datetime.now().strftime(DATE_FORMAT)}).")


def _prompt_quantity(prompt: str) -> str:
    """Prompt until the user enters a positive number."""
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw)
            if val <= 0:
                raise ValueError
            return raw
        except ValueError:
            print("  Enter a positive number (e.g. 5.2).")


def _call(action: str, fn, *args, **kwargs) -> None:
    """Run an API call, print the result, and handle errors gracefully."""
    try:
        result = fn(*args, **kwargs)
        msg = result.get("message", str(result))
        print(f"  {action}: {msg}")
    except requests.HTTPError as exc:
        print(f"  {action} FAILED [{exc.response.status_code}]: {exc.response.text}")
    except requests.RequestException as exc:
        print(f"  {action} ERROR: {exc}")


# ------------------------------------------------------------------ #
# Menu actions
# ------------------------------------------------------------------ #

def log_today(client: PixelaClient) -> None:
    quantity = _prompt_quantity("  Quantity to log (e.g. 5.2 Km): ")
    date_str = datetime.now().strftime(DATE_FORMAT)
    _call("Log today", client.post_pixel, GRAPH_ID, date_str, quantity)


def update_pixel(client: PixelaClient) -> None:
    date_str = _prompt_date("  Date to update (YYYYMMDD): ")
    quantity = _prompt_quantity("  New quantity: ")
    _call("Update pixel", client.update_pixel, GRAPH_ID, date_str, quantity)


def delete_pixel(client: PixelaClient) -> None:
    date_str = _prompt_date("  Date to delete (YYYYMMDD): ")
    confirm = input(f"  Delete pixel for {datetime.strptime(date_str, DATE_FORMAT).strftime(DATE_DISPLAY)}? [y/N]: ").strip().lower()
    if confirm == "y":
        _call("Delete pixel", client.delete_pixel, GRAPH_ID, date_str)
    else:
        print("  Cancelled.")


def show_graph_url(client: PixelaClient) -> None:
    url = client.graph_url(GRAPH_ID)
    print(f"  Graph URL: {url}")


MENU = {
    "1": ("Log today's activity", log_today),
    "2": ("Update a past pixel", update_pixel),
    "3": ("Delete a past pixel", delete_pixel),
    "4": ("Show graph URL", show_graph_url),
}


# ------------------------------------------------------------------ #
# Entry point
# ------------------------------------------------------------------ #

def main() -> None:
    _validate_credentials()
    client = PixelaClient(USERNAME, TOKEN)

    print(f"\nPixela Habit Tracker — graph: {GRAPH_NAME} ({GRAPH_UNIT})")
    print(f"User: {USERNAME}  |  Graph: {GRAPH_ID}\n")

    while True:
        print("What would you like to do?")
        for key, (label, _) in MENU.items():
            print(f"  {key} — {label}")
        print("  q — Quit")

        choice = input("\n> ").strip().lower()
        print()

        if choice in MENU:
            _, action_fn = MENU[choice]
            action_fn(client)
        elif choice == "q":
            break
        else:
            print("  Invalid choice.")
        print()


if __name__ == "__main__":
    main()
