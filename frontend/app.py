import html
import math
import os
import random

import requests
import streamlit as st

# =============================
# CONFIG
# =============================
# Deployed backend by default. For local testing run:
#   set API_BASE=http://127.0.0.1:8000   (Windows)
#   export API_BASE=http://127.0.0.1:8000 (Mac/Linux)


# =============================
# CONFIG
# =============================
try:
    API_BASE = (
        os.getenv("API_BASE")
        or st.secrets["API_BASE"]
    )
except (KeyError, FileNotFoundError):
    API_BASE = "http://127.0.0.1:8000"

API_BASE = API_BASE.rstrip("/")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

CATEGORIES = {
    "trending": "Trending today",
    "popular": "Popular",
    "top_rated": "Top rated",
    "now_playing": "In theaters",
    "upcoming": "Coming soon",
}

st.set_page_config(page_title="Plotkin", page_icon="🎞️", layout="wide")

# =============================
# STYLES
# =============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --bg: #0d171d;
  --surface: #15232c;
  --surface-2: #1d303c;
  --line: #2a4150;
  --text: #e8eff3;
  --muted: #8fa5b2;
  --amber: #ffb547;
  --teal: #3fb6a8;
}

html, body, .stApp, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
header[data-testid="stHeader"], #MainMenu, footer,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

/* remove the focus outline that appears around the scrolling page area */
[data-testid="stMain"], [data-testid="stAppViewContainer"], section.main,
[data-testid="stMain"]:focus, [data-testid="stMain"]:focus-visible,
[data-testid="stAppViewContainer"]:focus, [data-testid="stAppViewContainer"]:focus-visible {
  outline: none !important;
  box-shadow: none !important;
}
.block-container { max-width: 1320px; padding-top: 1.5rem; padding-bottom: 4rem; }

/* ---------- top bar ---------- */
.brand { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: 2rem; letter-spacing: -0.02em; color: var(--text); margin: 0; }
.brand a { color: inherit; text-decoration: none; }
.brand b { color: var(--amber); font-weight: 800; }
.tagline { color: var(--muted); margin: 2px 0 0 0; font-size: 0.95rem; }

/* ---------- search input ---------- */
.stTextInput label { display: none; }
.stTextInput input {
  background: var(--surface) !important; color: var(--text) !important;
  border: 1px solid var(--line) !important; border-radius: 14px !important;
  padding: 0.85rem 1rem !important; font-size: 1rem !important;
}
.stTextInput input:focus { border-color: var(--amber) !important; box-shadow: 0 0 0 3px rgba(255,181,71,0.18) !important; }
.stTextInput input::placeholder { color: var(--muted) !important; }

/* ---------- category pills ---------- */
.pills { display: flex; gap: 8px; flex-wrap: wrap; margin: 18px 0 8px 0; }
.pill { padding: 7px 16px; border-radius: 999px; border: 1px solid var(--line);
  color: var(--muted) !important; text-decoration: none !important; font-size: 0.9rem; font-weight: 500; }
.pill:hover { color: var(--text) !important; border-color: var(--muted); }
.pill.on { background: var(--amber); border-color: var(--amber); color: #1b1305 !important; font-weight: 600; }

/* ---------- filter widgets ---------- */
[data-testid="stWidgetLabel"] p, .stCheckbox label p { color: var(--muted) !important; font-size: 0.85rem; }
[data-testid="stCaptionContainer"] { color: var(--muted) !important; }
div[data-baseweb="select"] > div { background: var(--surface) !important; border-color: var(--line) !important; }
div[data-baseweb="select"] * { color: var(--text) !important; }
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li { background: var(--surface) !important; color: var(--text) !important; }
div[data-baseweb="popover"] li:hover { background: var(--surface-2) !important; }
.stSlider [role="slider"] { background: var(--amber) !important; }
[data-testid="stSliderThumbValue"] { color: var(--amber) !important; }
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] { color: var(--muted) !important; }

/* ---------- section headings ---------- */
.sec { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700;
  font-size: 1.45rem; letter-spacing: -0.01em; margin: 30px 0 4px 0; color: var(--text); }
.sec-sub { color: var(--muted); font-size: 0.9rem; margin: 0 0 14px 0; }

/* ---------- poster cards ---------- */
.grid { display: grid; gap: 18px; grid-template-columns: repeat(var(--cols, 5), minmax(0, 1fr)); }
.rail { display: flex; gap: 16px; overflow-x: auto; padding-bottom: 12px; scrollbar-width: thin; }
.rail .card { flex: 0 0 160px; }

.card { display: block; text-decoration: none !important; color: var(--text) !important; }
.poster { position: relative; aspect-ratio: 2 / 3; border-radius: 10px; overflow: hidden;
  background: var(--surface); border: 1px solid var(--line); transition: transform .18s ease, border-color .18s ease; }
.card:hover .poster { transform: translateY(-4px); border-color: var(--amber); }
.poster img { width: 100%; height: 100%; object-fit: cover; display: block; }
.noposter { height: 100%; display: flex; align-items: center; justify-content: center;
  color: var(--muted); font-size: 0.85rem; padding: 12px; text-align: center; }
.chip { position: absolute; left: 8px; bottom: 8px; background: rgba(13,23,29,0.88);
  color: var(--amber); font-weight: 600; font-size: 0.78rem; padding: 3px 8px; border-radius: 6px; }
.ctitle { margin: 9px 2px 0 2px; font-weight: 600; font-size: 0.92rem; line-height: 1.25;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.cyear { margin: 2px 2px 0 2px; color: var(--muted); font-size: 0.82rem; }

/* ---------- details hero ---------- */
.back { display: inline-block; color: var(--muted) !important; text-decoration: none !important;
  font-size: 0.92rem; margin-bottom: 14px; }
.back:hover { color: var(--amber) !important; }
.hero { position: relative; border-radius: 18px; overflow: hidden; border: 1px solid var(--line);
  background: var(--surface); }
.hero-bg { position: absolute; inset: 0; background-size: cover; background-position: center 20%;
  opacity: 0.35; filter: blur(2px); }
.hero-fade { position: absolute; inset: 0;
  background: linear-gradient(90deg, rgba(13,23,29,0.96) 25%, rgba(13,23,29,0.55) 100%); }
.hero-in { position: relative; display: flex; gap: 32px; padding: 30px; align-items: flex-start; }
.hero-poster { flex: 0 0 240px; border-radius: 12px; overflow: hidden; border: 1px solid var(--line); }
.hero-poster img { width: 100%; display: block; }
.hero-text { flex: 1; min-width: 0; }
.hero-title { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: clamp(1.9rem, 4vw, 3.1rem); line-height: 1.05; letter-spacing: -0.02em; margin: 4px 0 14px 0; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
.tag { border: 1px solid var(--line); background: rgba(21,35,44,0.8); color: var(--text);
  padding: 4px 12px; border-radius: 999px; font-size: 0.85rem; }
.tag.year { border-color: var(--amber); color: var(--amber); font-weight: 600; }
.ov-h { color: var(--teal); font-weight: 600; font-size: 0.95rem; margin-bottom: 6px; }
.overview { color: #cbd8df; line-height: 1.65; max-width: 68ch; font-size: 1rem; }

@media (max-width: 720px) {
  .hero-in { flex-direction: column; padding: 18px; }
  .hero-poster { flex-basis: auto; width: 180px; }
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
  .rail .card { flex-basis: 130px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (via query params)
# =============================
qp = st.query_params
view = qp.get("view", "home")
category = qp.get("cat", "trending")
if category not in CATEGORIES:
    category = "trending"

tmdb_id = None
if qp.get("id"):
    try:
        tmdb_id = int(qp.get("id"))
        view = "details"
    except ValueError:
        tmdb_id = None
if view == "details" and tmdb_id is None:
    view = "home"


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=120, show_spinner=False)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=60)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


# =============================
# RENDER HELPERS
# =============================
def card_html(m: dict, badge: str | None = None) -> str:
    tid = m.get("tmdb_id")
    if not tid:
        return ""
    title = html.escape(m.get("title") or "Untitled")
    poster = m.get("poster_url")
    year = (m.get("release_date") or "")[:4]
    rating = m.get("vote_average")

    img = (
        f'<img src="{poster}" alt="{title}" loading="lazy">'
        if poster
        else '<div class="noposter">No poster</div>'
    )
    if badge:
        chip = f'<span class="chip">{html.escape(badge)}</span>'
    elif rating:
        chip = f'<span class="chip">★ {float(rating):.1f}</span>'
    else:
        chip = ""

    year_html = f'<div class="cyear">{year}</div>' if year else ""
    return (
        f'<a class="card" href="?view=details&id={int(tid)}" target="_self">'
        f'<div class="poster">{img}{chip}</div>'
        f'<div class="ctitle">{title}</div>{year_html}</a>'
    )


def render_cards(cards, layout: str = "grid", badges: list | None = None, cols: int = 5):
    if not cards:
        st.info("No movies match the current filters.")
        return

    style = ""
    if layout == "grid":
        # Drop the leftover cards so every row is full on desktop (cols)
        # and on phones (2 columns).
        step = math.lcm(cols, 2)
        keep = len(cards) - len(cards) % step
        if keep:
            cards = cards[:keep]
        style = f' style="--cols:{cols}"'

    parts = []
    for i, m in enumerate(cards):
        badge = badges[i] if badges and i < len(badges) else None
        parts.append(card_html(m, badge))
    st.markdown(f'<div class="{layout}"{style}>{"".join(parts)}</div>', unsafe_allow_html=True)


def section(title: str, sub: str = ""):
    st.markdown(f'<div class="sec">{html.escape(title)}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="sec-sub">{html.escape(sub)}</div>', unsafe_allow_html=True)


def tmdb_search_to_cards(data, limit: int = 30):
    """Convert the raw TMDB search response from /tmdb/search into card dicts."""
    if not isinstance(data, dict):
        return []
    cards = []
    for m in data.get("results") or []:
        title = (m.get("title") or "").strip()
        mid = m.get("id")
        if not title or not mid:
            continue
        path = m.get("poster_path")
        cards.append(
            {
                "tmdb_id": int(mid),
                "title": title,
                "poster_url": f"{TMDB_IMG}{path}" if path else None,
                "release_date": m.get("release_date"),
                "vote_average": m.get("vote_average"),
            }
        )
    return cards[:limit]


def tfidf_items_to_cards(items):
    cards, badges = [], []
    for x in items or []:
        t = x.get("tmdb") or {}
        if not t.get("tmdb_id"):
            continue
        cards.append(
            {
                "tmdb_id": t["tmdb_id"],
                "title": t.get("title") or x.get("title") or "Untitled",
                "poster_url": t.get("poster_url"),
                "release_date": t.get("release_date"),
            }
        )
        badges.append(f"{int(round(float(x.get('score', 0)) * 100))}% match")
    return cards, badges


def pills_html(active: str) -> str:
    out = []
    for key, label in CATEGORIES.items():
        cls = "pill on" if key == active else "pill"
        out.append(f'<a class="{cls}" href="?view=home&cat={key}" target="_self">{label}</a>')
    return f'<div class="pills">{"".join(out)}</div>'


def apply_filters(cards, key: str):
    """Draw the filter bar and return (filtered_cards, columns_per_row)."""
    years = sorted(
        int(c["release_date"][:4])
        for c in cards
        if (c.get("release_date") or "")[:4].isdigit()
    )

    # The year slider only makes sense when the movies span more than one year
    # (Trending, In theaters and Coming soon are usually all the same year).
    has_years = bool(years) and years[0] != years[-1]
    slots = st.columns([1.2, 1.2, 1.6, 1] if has_years else [1.2, 1.2, 1])

    with slots[0]:
        sort_by = st.selectbox(
            "Sort by",
            ["Default", "Highest rated", "Newest first", "Oldest first", "Title A–Z"],
            key=f"{key}_sort",
        )
    with slots[1]:
        min_rating = st.slider("Minimum rating", 0.0, 9.0, 0.0, 0.5, key=f"{key}_rating")

    year_range = None
    if has_years:
        with slots[2]:
            year_range = st.slider(
                "Release year",
                years[0],
                years[-1],
                (years[0], years[-1]),
                key=f"{key}_year_{years[0]}_{years[-1]}",
            )

    with slots[-1]:
        cols = st.slider("Posters per row", 4, 8, 5, key=f"{key}_cols")

    only_posters = st.checkbox("Hide movies without a poster", key=f"{key}_poster")

    out = []
    for c in cards:
        year = (c.get("release_date") or "")[:4]
        if (c.get("vote_average") or 0) < min_rating:
            continue
        if only_posters and not c.get("poster_url"):
            continue
        if year_range and year.isdigit() and not (year_range[0] <= int(year) <= year_range[1]):
            continue
        out.append(c)

    if sort_by == "Highest rated":
        out.sort(key=lambda c: c.get("vote_average") or 0, reverse=True)
    elif sort_by == "Newest first":
        out.sort(key=lambda c: c.get("release_date") or "", reverse=True)
    elif sort_by == "Oldest first":
        out.sort(key=lambda c: c.get("release_date") or "9999")
    elif sort_by == "Title A–Z":
        out.sort(key=lambda c: (c.get("title") or "").lower())

    st.caption(f"Showing {len(out)} of {len(cards)} movies")
    return out, cols


def surprise_html(cards) -> str:
    if not cards:
        return ""
    pick = random.choice(cards)
    return (
        '<div class="pills">'
        f'<a class="pill" href="?view=details&id={int(pick["tmdb_id"])}" target="_self">🎲 Surprise me</a>'
        "</div>"
    )


# =============================
# HEADER
# =============================
st.markdown(
    '<p class="brand"><a href="?view=home" target="_self">plot<b>kin</b></a></p>'
    '<p class="tagline">Pick a movie you like. Get ten more that feel the same.</p>',
    unsafe_allow_html=True,
)

# ==========================================================
# VIEW: HOME
# ==========================================================
if view == "home":
    typed = st.text_input(
        "Search",
        placeholder="Search a title, e.g. Inception, Batman, Coco",
        label_visibility="collapsed",
    ).strip()

    # ----- search mode -----
    if typed:
        if len(typed) < 2:
            st.caption("Type at least 2 characters to search.")
        else:
            with st.spinner("Searching..."):
                data, err = api_get_json("/tmdb/search", {"query": typed})
            if err or data is None:
                st.error(f"Search failed. {err}")
            else:
                cards = tmdb_search_to_cards(data)
                if cards:
                    section(f"Results for “{typed}”", "Open a movie to see similar titles.")
                    cards, cols = apply_filters(cards, "search")
                    st.markdown(surprise_html(cards), unsafe_allow_html=True)
                    render_cards(cards, "grid", cols=cols)
                else:
                    st.info(f"No movies found for “{typed}”. Try a different spelling.")
        st.stop()

    # ----- home feed -----
    st.markdown(pills_html(category), unsafe_allow_html=True)
    with st.spinner("Loading movies..."):
        feed, err = api_get_json("/home", {"category": category, "limit": 24})
    if err or not feed:
        st.error(
            "Could not load the movie feed. If the backend is hosted on Render's free tier, "
            f"it may be waking up — refresh in a few seconds. ({err or 'Unknown error'})"
        )
        st.stop()

    section(CATEGORIES[category])
    feed, cols = apply_filters(feed, f"feed_{category}")
    st.markdown(surprise_html(feed), unsafe_allow_html=True)
    render_cards(feed, "grid", cols=cols)

# ==========================================================
# VIEW: DETAILS
# ==========================================================
else:
    st.markdown('<a class="back" href="?view=home" target="_self">← Back to browse</a>', unsafe_allow_html=True)

    with st.spinner("Loading movie..."):
        data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load this movie. {err or ''}")
        st.stop()

    title = data.get("title") or ""
    year = (data.get("release_date") or "")[:4]
    genres = [g.get("name", "") for g in data.get("genres", []) if g.get("name")]
    overview = html.escape(data.get("overview") or "No overview available.")
    poster = data.get("poster_url")
    backdrop = data.get("backdrop_url")

    tags = ""
    if year:
        tags += f'<span class="tag year">{year}</span>'
    tags += "".join(f'<span class="tag">{html.escape(g)}</span>' for g in genres)

    bg = f'<div class="hero-bg" style="background-image:url(\'{backdrop}\')"></div>' if backdrop else ""
    poster_html = (
        f'<div class="hero-poster"><img src="{poster}" alt="{html.escape(title)}"></div>' if poster else ""
    )

    st.markdown(
        '<div class="hero">'
        f"{bg}<div class=\"hero-fade\"></div>"
        '<div class="hero-in">'
        f"{poster_html}"
        '<div class="hero-text">'
        f'<div class="hero-title">{html.escape(title)}</div>'
        f'<div class="meta">{tags}</div>'
        '<div class="ov-h">Overview</div>'
        f'<div class="overview">{overview}</div>'
        "</div></div></div>",
        unsafe_allow_html=True,
    )

    # ----- recommendations -----
    if not title.strip():
        st.warning("No title available to compute recommendations.")
        st.stop()

    with st.spinner("Finding similar movies..."):
        bundle, err2 = api_get_json(
            "/movie/search",
            {"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

    if not err2 and bundle:
        tf_cards, tf_badges = tfidf_items_to_cards(bundle.get("tfidf_recommendations"))
        if tf_cards:
            section("Similar story and themes", "Matched on plot, cast and keywords.")
            render_cards(tf_cards, "rail", tf_badges)

        genre_cards = bundle.get("genre_recommendations") or []
        if genre_cards:
            first_genre = genres[0] if genres else "this genre"
            section(f"Popular in {first_genre}")
            render_cards(genre_cards, "rail")

        if not tf_cards and not genre_cards:
            st.info("No recommendations available for this movie yet.")
    else:
        genre_only, err3 = api_get_json("/recommend/genre", {"tmdb_id": tmdb_id, "limit": 18})
        if not err3 and genre_only:
            section("More like this", "Showing genre picks while similarity data is unavailable.")
            render_cards(genre_only, "rail")
        else:
            st.warning("No recommendations available right now.")