from scraper import scrape_google_play, scrape_app_store

def fake_gp_fetch(app_id, count):
    return [
        {"reviewId": "g1", "userName": "An", "content": "App lỗi", "score": 1,
         "at": "2026-06-01T10:00:00"},
    ]

def fake_as_fetch(app_id, count):
    return [
        {"review_id": "a1", "user_name": "Binh", "review": "Tốt", "rating": 5,
         "date": "2026-06-02T11:00:00"},
    ]

def test_gp_normalizes_and_tags_source():
    out = scrape_google_play("com.zing.zalo", fetch=fake_gp_fetch)
    assert out[0]["id"] == "g1"
    assert out[0]["content"] == "App lỗi"
    assert out[0]["source"] == "google_play"

def test_as_normalizes_and_tags_source():
    out = scrape_app_store("579523206", fetch=fake_as_fetch)
    assert out[0]["id"] == "a1"
    assert out[0]["source"] == "app_store"

def test_scrape_returns_empty_on_error():
    def boom(app_id, count):
        raise RuntimeError("blocked")
    assert scrape_google_play("x", fetch=boom) == []
    assert scrape_app_store("x", fetch=boom) == []

def test_scrape_returns_empty_for_missing_app_id():
    assert scrape_google_play(None, fetch=fake_gp_fetch) == []
    assert scrape_app_store(None, fetch=fake_as_fetch) == []
