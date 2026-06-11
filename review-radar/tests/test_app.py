import json
from storage import LocalStore
from app import create_app

def make_client(tmp_path, **overrides):
    store = LocalStore(data_dir=str(tmp_path))
    app = create_app(store=store, **overrides)
    app.config["TESTING"] = True
    return app.test_client(), store

def test_health_always_200(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/health").status_code == 200

def test_resolve_endpoint(tmp_path):
    def fake_resolve(name):
        return {"status": "matched", "app": {"title": "Zalo", "gp_id": "g", "as_id": "a"}}
    client, _ = make_client(tmp_path, resolve_fn=fake_resolve)
    resp = client.post("/api/resolve", json={"name": "zalo"})
    body = resp.get_json()
    assert body["status"] == "matched"
    assert body["app"]["title"] == "Zalo"

def test_track_sets_config_and_runs(tmp_path):
    calls = {"ran": 0}
    def fake_run(store):
        calls["ran"] += 1
        return {"new_reviews": 0}
    client, store = make_client(tmp_path, run_fn=fake_run)
    resp = client.post("/api/track", json={"title": "Zalo", "gp_id": "g", "as_id": "a"})
    assert resp.status_code == 200
    assert store.load_config()["title"] == "Zalo"
    assert calls["ran"] == 1

def test_patch_todo_status(tmp_path):
    client, store = make_client(tmp_path)
    store.save_todos([{"id": "t1", "topic": "login", "status": "open"}])
    resp = client.patch("/api/todos/t1", json={"status": "done"})
    assert resp.status_code == 200
    assert store.load_todos()[0]["status"] == "done"

def test_stats_shape(tmp_path):
    client, store = make_client(tmp_path)
    store.save_config({"title": "Zalo"})
    store.append_reviews([
        {"id": "1", "label": "BUG_REPORT", "at": "2026-06-10T00:00:00"},
        {"id": "2", "label": "POSITIVE", "at": "2026-06-10T00:00:00"},
    ])
    body = client.get("/api/stats").get_json()
    assert body["app"]["title"] == "Zalo"
    assert body["total"] == 2
    assert body["by_label"]["BUG_REPORT"] == 1
