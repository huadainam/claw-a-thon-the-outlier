import time
import requests
from google_play_scraper import search as gp_search_fn, reviews, Sort

APP_STORE_COUNTRIES = ("vn", "us", "gb", "au", "ca", "sg", "my", "th", "id", "ph")

def gp_search_live(name):
    # google-play-scraper's search() can raise (e.g. TypeError) on no-result or
    # gibberish queries, and sometimes returns the top/featured hit with appId=None.
    # Return [] on any failure and skip candidates without a usable appId so we
    # never crash resolution or tag the google_play store with a null id.
    try:
        results = gp_search_fn(name, lang="vi", country="vn", n_hits=5)
    except Exception:
        return []
    return [{"title": r["title"], "developer": r.get("developer", ""),
             "icon": r.get("icon", ""), "app_id": r["appId"],
             "store": "google_play"} for r in results if r.get("appId")]

def gp_reviews_live(app_id, count, attempts=3):
    # Google Play throttles rapid back-to-back requests (returns errors or an empty
    # batch). Retry with backoff so a transient throttle doesn't yield 0 reviews.
    last_exc = None
    for i in range(attempts):
        try:
            result, _ = reviews(app_id, lang="vi", country="vn",
                                sort=Sort.NEWEST, count=count)
            if result:
                return result
        except Exception as e:
            last_exc = e
        time.sleep(2 * (i + 1))
    if last_exc:
        raise last_exc
    return []

def as_search_live(name):
    try:
        resp = requests.get("https://itunes.apple.com/search",
                            params={"term": name, "country": "vn",
                                    "entity": "software", "limit": 5}, timeout=20)
        items = resp.json().get("results", [])
    except Exception:
        return []
    return [{"title": it["trackName"], "developer": it.get("artistName", ""),
             "icon": it.get("artworkUrl100", ""), "app_id": str(it["trackId"]),
             "store": "app_store"} for it in items]

def _as_entry_time(review):
    return review.get("date") or ""

def _as_fetch_pages(app_id, count, countries=None):
    # Apple's customer-reviews RSS caps each storefront at 10 pages × 50 reviews.
    # For large backfills, walk additional storefronts and dedup globally so a
    # user-selected 1,000 review crawl is not artificially limited to Vietnam's
    # RSS window. The first country stays VN to preserve the local signal.
    countries = countries or APP_STORE_COUNTRIES
    out = []
    seen = set()
    for country in countries:
        for page in range(1, 11):
            url = (f"https://itunes.apple.com/{country}/rss/customerreviews/"
                   f"page={page}/id={app_id}/sortby=mostrecent/json")
            try:
                resp = requests.get(url, timeout=20)
                entries = resp.json().get("feed", {}).get("entry", [])
            except (ValueError, requests.RequestException):
                # Empty body / non-JSON (Apple returns these for some pages even
                # when other pages have data) — skip this page, keep going.
                continue
            if isinstance(entries, dict):  # iTunes returns a dict when there's one entry
                entries = [entries]
            for e in entries:
                if "im:rating" not in e:
                    continue
                rid = e["id"]["label"]
                if rid in seen:
                    continue
                seen.add(rid)
                out.append({
                    "review_id": rid,
                    "user_name": e.get("author", {}).get("name", {}).get("label", ""),
                    "review": e.get("content", {}).get("label", ""),
                    "rating": int(e["im:rating"]["label"]),
                    "date": e.get("updated", {}).get("label", ""),
                    "country": country.upper(),
                })
            if len(out) >= count:
                break
        if len(out) >= count:
            break
    out.sort(key=_as_entry_time, reverse=True)
    return out[:count]

def as_reviews_live(app_id, count, attempts=3):
    # Apple's RSS throttles under rapid requests (returns empty/errors). Retry with
    # backoff so a transient throttle doesn't look like "no reviews".
    last_exc = None
    for i in range(attempts):
        try:
            out = _as_fetch_pages(app_id, count)
            if out:
                return out
        except Exception as e:
            last_exc = e
        time.sleep(2 * (i + 1))
    if last_exc:
        raise last_exc
    return []
