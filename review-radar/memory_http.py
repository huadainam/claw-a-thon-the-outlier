import subprocess
import requests

def _default_token_getter() -> str:
    """Obtain an IAM token via the AgentBase helper script (repo root)."""
    out = subprocess.run(
        ["bash", ".claude/skills/agentbase/scripts/get_token.sh"],
        capture_output=True, text=True, cwd="..",
    )
    return out.stdout.strip()

class MemoryHTTP:
    def __init__(self, base_url, session=None, token_getter=None):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.token_getter = token_getter or _default_token_getter

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token_getter()}",
            "Content-Type": "application/json",
        }

    def _events_url(self, memory_id, actor_id, session_id):
        return (
            f"{self.base_url}/memories/{memory_id}"
            f"/actors/{actor_id}/sessions/{session_id}/events"
        )

    def post_event(self, memory_id, actor_id, session_id, content):
        url = self._events_url(memory_id, actor_id, session_id)
        body = {"payload": {"role": "assistant", "content": content}}
        resp = self.session.post(url, json=body, headers=self._headers(), timeout=30)
        resp.raise_for_status()

    def list_events(self, memory_id, actor_id, session_id):
        url = self._events_url(memory_id, actor_id, session_id)
        resp = self.session.get(url, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json().get("data", [])
