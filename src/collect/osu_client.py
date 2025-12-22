# src/collect/osu_client.py
import time
import requests
from threading import Lock
from src.utils.config_loader import load_config

class OsuApiClient:
    def __init__(self):
        self.config = load_config()["osu"]
        self.token = None
        self.token_expires_at = 0
        self.lock = Lock()

    def _get_new_token(self):
        data = {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "grant_type": "client_credentials",
            "scope": "public"
        }
        resp = requests.post(self.config["token_url"], data=data, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        self.token = result["access_token"]
        self.token_expires_at = time.time() + result["expires_in"] - 30

    def _ensure_token(self):
        with self.lock:
            if not self.token or time.time() >= self.token_expires_at:
                self._get_new_token()

    def get_user_scores(self, user_id, mode="osu", limit=50):
        self._ensure_token()
        url = f"{self.config['api_base']}/users/{user_id}/scores/best"
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            params={"mode": mode, "limit": limit},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
