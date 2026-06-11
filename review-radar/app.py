import os
import threading
from collections import Counter
from flask import Flask, jsonify, request, send_from_directory

DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), "dashboard")

def create_app(store=None, resolve_fn=None, run_fn=None):
    if store is None:
        from storage import get_store
        store = get_store()
    if resolve_fn is None:
        from scraper import resolve_app
        resolve_fn = resolve_app
    if run_fn is None:
        from pipeline import run_pipeline
        run_fn = lambda s: run_pipeline(store=s)

    app = Flask(__name__, static_folder=DASHBOARD_DIR, static_url_path="")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.get("/")
    def index():
        return send_from_directory(DASHBOARD_DIR, "index.html")

    @app.post("/api/resolve")
    def resolve():
        name = (request.get_json(silent=True) or {}).get("name", "").strip()
        if not name:
            return jsonify({"status": "not_found", "message": "Nhập tên app."}), 200
        return jsonify(resolve_fn(name)), 200

    @app.post("/api/track")
    def track():
        data = request.get_json(silent=True) or {}
        app_obj = {"title": data.get("title", ""), "gp_id": data.get("gp_id"),
                   "as_id": data.get("as_id")}
        store.reset()
        store.save_config(app_obj)
        run_fn(store)
        return jsonify({"ok": True, "app": app_obj}), 200

    @app.post("/run")
    def run_now():
        threading.Thread(target=run_fn, args=(store,), daemon=True).start()
        return jsonify({"ok": True, "started": True}), 200

    @app.get("/api/stats")
    def stats():
        reviews = store.load_reviews()
        by_label = dict(Counter(r.get("label") for r in reviews))
        by_day = dict(Counter(
            (r.get("at") or "")[:10] for r in reviews if r.get("label") == "BUG_REPORT"
        ))
        return jsonify({"app": store.load_config(), "total": len(reviews),
                        "by_label": by_label, "bug_by_day": by_day})

    @app.get("/api/todos")
    def get_todos():
        return jsonify(store.load_todos())

    @app.patch("/api/todos/<todo_id>")
    def patch_todo(todo_id):
        data = request.get_json(silent=True) or {}
        todos = store.load_todos()
        for t in todos:
            if t["id"] == todo_id and "status" in data:
                t["status"] = data["status"]
        store.save_todos(todos)
        return jsonify({"ok": True})

    @app.get("/api/reviews")
    def get_reviews():
        return jsonify(store.load_reviews())

    return app

def _start_scheduler(store):
    import schedule
    import time
    from pipeline import run_pipeline
    schedule.every(1).hours.do(run_pipeline, store=store)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import sys
    from storage import get_store
    store = get_store()
    application = create_app(store=store)
    if "--serve" in sys.argv:
        threading.Thread(target=_start_scheduler, args=(store,), daemon=True).start()
    application.run(host="0.0.0.0", port=8080)
