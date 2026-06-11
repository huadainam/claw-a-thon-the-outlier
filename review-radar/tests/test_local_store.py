from storage import LocalStore

def test_local_store_roundtrip(tmp_path):
    s = LocalStore(data_dir=str(tmp_path))

    # config
    s.save_config({"title": "Zalo", "gp_id": "com.zing.zalo", "as_id": "579523206"})
    assert s.load_config()["title"] == "Zalo"

    # processed ids
    assert s.load_processed_ids() == set()
    s.save_processed_ids({"a", "b"})
    assert s.load_processed_ids() == {"a", "b"}

    # reviews append
    assert s.load_reviews() == []
    s.append_reviews([{"id": "a", "content": "x"}])
    s.append_reviews([{"id": "b", "content": "y"}])
    assert len(s.load_reviews()) == 2

    # todos
    s.save_todos([{"id": "t1", "topic": "login", "status": "open"}])
    assert s.load_todos()[0]["topic"] == "login"

def test_local_store_reset(tmp_path):
    s = LocalStore(data_dir=str(tmp_path))
    s.save_processed_ids({"a"})
    s.append_reviews([{"id": "a"}])
    s.save_todos([{"id": "t1"}])
    s.reset()
    assert s.load_processed_ids() == set()
    assert s.load_reviews() == []
    assert s.load_todos() == []
