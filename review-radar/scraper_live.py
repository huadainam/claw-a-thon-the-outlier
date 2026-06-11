import requests
from google_play_scraper import search as gp_search_fn, reviews, Sort

def gp_search_live(name):
    results = gp_search_fn(name, lang="vi", country="vn", n_hits=5)
    return [{"title": r["title"], "developer": r.get("developer", ""),
             "icon": r.get("icon", ""), "app_id": r["appId"],
             "store": "google_play"} for r in results]

def gp_reviews_live(app_id, count):
    result, _ = reviews(app_id, lang="vi", country="vn",
                        sort=Sort.NEWEST, count=count)
    return result

def as_search_live(name):
    resp = requests.get("https://itunes.apple.com/search",
                        params={"term": name, "country": "vn",
                                "entity": "software", "limit": 5}, timeout=20)
    items = resp.json().get("results", [])
    return [{"title": it["trackName"], "developer": it.get("artistName", ""),
             "icon": it.get("artworkUrl100", ""), "app_id": str(it["trackId"]),
             "store": "app_store"} for it in items]

def as_reviews_live(app_id, count):
    out = []
    for page in range(1, 11):  # up to 10 pages × 50 reviews
        url = (f"https://itunes.apple.com/vn/rss/customerreviews/"
               f"page={page}/id={app_id}/sortby=mostrecent/json")
        resp = requests.get(url, timeout=20)
        entries = resp.json().get("feed", {}).get("entry", [])
        review_entries = [e for e in entries if "im:rating" in e]
        for e in review_entries:
            out.append({
                "review_id": e["id"]["label"],
                "user_name": e.get("author", {}).get("name", {}).get("label", ""),
                "review": e.get("content", {}).get("label", ""),
                "rating": int(e["im:rating"]["label"]),
                "date": e.get("updated", {}).get("label", ""),
            })
        if not review_entries or len(out) >= count:
            break
    return out[:count]
