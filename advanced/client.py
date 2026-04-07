import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from config import PIXELA_BASE


class PixelaClient:
    """Handles all HTTP communication with the Pixela API.

    Pure logic — no print(), no sys.exit(), no UI.
    Raises requests.HTTPError on non-2xx responses.
    """

    def __init__(self, username: str, token: str) -> None:
        self.username = username
        self._session = requests.Session()
        self._session.headers.update({"X-USER-TOKEN": token})
        self._token = token

    # ------------------------------------------------------------------ #
    # Account
    # ------------------------------------------------------------------ #

    def create_user(self) -> dict:
        """Create a Pixela account. Safe to call again; returns 'already exists' message."""
        payload = {
            "token": self._token,
            "username": self.username,
            "agreeTermsOfService": "yes",
            "notMinor": "yes",
        }
        resp = requests.post(url=PIXELA_BASE, json=payload)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------ #
    # Graph
    # ------------------------------------------------------------------ #

    def create_graph(self, graph_id: str, name: str, unit: str, type_: str, color: str) -> dict:
        """Create a new graph on the user's account."""
        endpoint = f"{PIXELA_BASE}/{self.username}/graphs"
        payload = {"id": graph_id, "name": name, "unit": unit, "type": type_, "color": color}
        resp = self._session.post(url=endpoint, json=payload)
        resp.raise_for_status()
        return resp.json()

    def graph_url(self, graph_id: str) -> str:
        """Return the public HTML URL for a graph."""
        return f"{PIXELA_BASE}/{self.username}/graphs/{graph_id}.html"

    # ------------------------------------------------------------------ #
    # Pixels
    # ------------------------------------------------------------------ #

    def post_pixel(self, graph_id: str, date_str: str, quantity: str) -> dict:
        """Add a new pixel. date_str must be YYYYMMDD; quantity must be a numeric string."""
        endpoint = f"{PIXELA_BASE}/{self.username}/graphs/{graph_id}"
        payload = {"date": date_str, "quantity": quantity}
        resp = self._session.post(url=endpoint, json=payload)
        resp.raise_for_status()
        return resp.json()

    def update_pixel(self, graph_id: str, date_str: str, quantity: str) -> dict:
        """Overwrite the quantity of an existing pixel."""
        endpoint = f"{PIXELA_BASE}/{self.username}/graphs/{graph_id}/{date_str}"
        payload = {"quantity": quantity}
        resp = self._session.put(url=endpoint, json=payload)
        resp.raise_for_status()
        return resp.json()

    def delete_pixel(self, graph_id: str, date_str: str) -> dict:
        """Delete a pixel on the given date."""
        endpoint = f"{PIXELA_BASE}/{self.username}/graphs/{graph_id}/{date_str}"
        resp = self._session.delete(url=endpoint)
        resp.raise_for_status()
        return resp.json()
