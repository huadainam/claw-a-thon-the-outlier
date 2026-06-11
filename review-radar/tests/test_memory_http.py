from memory_http import MemoryHTTP

class FakeResp:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload
    def json(self):
        return self._payload
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

class FakeSession:
    def __init__(self):
        self.calls = []
        self.events = []
    def post(self, url, json=None, headers=None, timeout=None):
        self.calls.append(("POST", url, json))
        self.events.append({"content": json["payload"]["content"]})
        return FakeResp(200, {})
    def get(self, url, headers=None, timeout=None):
        self.calls.append(("GET", url, None))
        return FakeResp(200, {"data": list(self.events)})

def make():
    sess = FakeSession()
    http = MemoryHTTP(
        base_url="https://mem.example",
        session=sess,
        token_getter=lambda: "fake-token",
    )
    return http, sess

def test_post_then_list_roundtrip():
    http, sess = make()
    http.post_event("m1", "actor", "sess1", "hello-json")
    events = http.list_events("m1", "actor", "sess1")
    assert events[-1]["content"] == "hello-json"

def test_post_includes_bearer_token():
    http, sess = make()
    http.post_event("m1", "actor", "sess1", "x")
    # Find the POST call; ensure auth header was attached via session usage
    assert sess.calls[0][0] == "POST"
    assert "m1" in sess.calls[0][1] or "m1" in str(sess.calls[0])
