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
        self.session = requests.Session()  # 使用 Session 提高效率

    def _get_new_token(self):
        """获取新的 OAuth2 token"""
        data = {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "grant_type": "client_credentials",
            "scope": "public"
        }
        resp = self.session.post(self.config["token_url"], data=data, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        self.token = result["access_token"]
        self.token_expires_at = time.time() + result["expires_in"] - 30

    def _ensure_token(self):
        """确保 token 有效，过期则刷新"""
        with self.lock:
            if not self.token or time.time() >= self.token_expires_at:
                self._get_new_token()

    def get_user(self, user_id, mode="osu"):
        """获取单个用户信息"""
        self._ensure_token()
        url = f"{self.config['api_base']}/users/{user_id}/{mode}"
        resp = self.session.get(url, headers={"Authorization": f"Bearer {self.token}"}, params={"mode": mode}, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_user_scores(self, user_id, mode="osu", limit=50):
        """获取用户 best 成绩"""
        self._ensure_token()
        url = f"{self.config['api_base']}/users/{user_id}/scores/best"
        resp = self.session.get(url, headers={"Authorization": f"Bearer {self.token}"}, params={"mode": mode, "limit": limit}, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_leaderboard(self, mode="osu", type_="performance", country=None, limit=50, offset=0):
        """获取排行榜"""
        
        self._ensure_token()
        url = f"{self.config['api_base']}/rankings/{mode}/{type_}"
        page = offset // limit + 1
        params = {"page": page, "variant": "4k"}
        if country:
            params["country"] = country
        resp = self.session.get(url, headers={"Authorization": f"Bearer {self.token}"}, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("ranking", [])
    
    def get_beatmap(self, beatmap_id):
        self._ensure_token()
        url = f"{self.config['api_base']}/beatmaps/{beatmap_id}"
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
