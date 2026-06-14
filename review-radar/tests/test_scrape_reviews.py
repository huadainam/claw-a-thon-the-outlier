import scraper_live
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

def test_app_store_fetch_uses_additional_storefronts_when_limit_exceeds_one_country(monkeypatch):
    class FakeResp:
        def __init__(self, entries):
            self._entries = entries

        def json(self):
            return {"feed": {"entry": self._entries}}

    def entry(country, page, idx):
        rid = f"{country}-{page}-{idx}"
        return {
            "id": {"label": rid},
            "author": {"name": {"label": "User"}},
            "content": {"label": f"Review {rid}"},
            "im:rating": {"label": "5"},
            "updated": {"label": f"2026-06-{idx + 1:02d}T00:00:00Z"},
        }

    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        country = url.split("itunes.apple.com/")[1].split("/")[0]
        page = int(url.split("page=")[1].split("/")[0])
        per_page = 50 if country == "vn" and page <= 10 else 25 if country == "us" and page == 1 else 0
        return FakeResp([entry(country, page, i) for i in range(per_page)])

    monkeypatch.setattr(scraper_live.requests, "get", fake_get)

    out = scraper_live._as_fetch_pages("app", 510, countries=("vn", "us"))

    assert len(out) == 510
    assert any(r["country"] == "US" for r in out)
    assert any("/us/rss/customerreviews/" in url for url in calls)
