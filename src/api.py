from typing import Optional, Dict, Iterable, Callable
import requests
from constants import API_BASE

class YWMClient:
    def __init__(self, oauth_token: str):
        self.headers = {"Authorization": f"OAuth {oauth_token}", "Accept": "application/json"}

    def get_user_id(self) -> int:
        try:
            r = requests.get(f"{API_BASE}/user", headers=self.headers, timeout=60)
            r.raise_for_status()
            uid = r.json().get("user_id")
            return int(uid) if uid else -1
        except requests.RequestException as e:
            return -1

    def find_host_id(self, user_id: int, host_domain: str) -> Optional[str]:
        try:
            r = requests.get(f"{API_BASE}/user/{user_id}/hosts", headers=self.headers, timeout=60)
            r.raise_for_status()
            hosts = r.json().get("hosts")
            target = host_domain.strip().lower()

            for h in hosts:
                hid = h.get("host_id")

                if not hid:
                    continue

                if target in hid:
                    return hid

            return None
        except requests.RequestException as e:
            return None

    def iter_external_links(self, user_id: int, host_id: str, limit: int, offset: int, on_tick: Optional[Callable[[int, int], None]] = None) -> Iterable[Dict]:
        tick = on_tick or (lambda *_: None)

        while True:
            url = f"{API_BASE}/user/{user_id}/hosts/{host_id}/links/external/samples"
            params = {"limit": limit, "offset": offset}
            resp = requests.get(url, headers=self.headers, params=params, timeout=90)

            if resp.status_code == 401:
                raise RuntimeError("401 Unauthorized: проверьте YWM_OAUTH_TOKEN")
            if resp.status_code == 403:
                raise RuntimeError("403 Forbidden: нет прав на этот host_id")

            resp.raise_for_status()

            data = resp.json()
            links = data.get("links", [])

            for link in links:
                yield link

            got = len(links)
            tick(got, offset)

            if got < limit:
                break

            offset += limit