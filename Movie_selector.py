import os
import random
import token
from typing import Any, Callable

import pandas as pd
import requests

DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"
GENRE_LIST_URL = "https://api.themoviedb.org/3/genre/movie/list"

# Dark comedy / satire keyword IDs (TMDB). Pipe = OR in discover.
DARK_COMEDY_KEYWORDS = "612|10183|9717"
THRILLER_GENRE_ID = 53
COMEDY_GENRE_ID = 35

MAINSTREAM_SHARE = 0.4
MAX_DISCOVER_PAGE = 500
POOL_PAGE_ATTEMPTS = 6


def get_tmdb_token() -> str:
    token = os.environ.get("TMDB_READ_ACCESS_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "Set TMDB_READ_ACCESS_TOKEN to your TMDB API read access token (Bearer).\n"
            "Example (PowerShell): $env:TMDB_READ_ACCESS_TOKEN = 'read access token'"
        )
    return token


def discover_movies(
    token: str, params: dict[str, Any]
) -> tuple[list[dict[str, Any]], int]:
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
    }
    clean = {k: v for k, v in params.items() if not str(k).startswith("_")}
    response = requests.get(DISCOVER_URL, params=clean, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    total_pages = int(data.get("total_pages") or 1)
    total_pages = max(1, min(total_pages, MAX_DISCOVER_PAGE))

    movies: list[dict[str, Any]] = []
    for m in data.get("results", []):
        mid = m.get("id")
        if mid is None:
            continue
        movies.append(
            {
                "id": int(mid),
                "Title": m.get("title") or "",
                "Year": m["release_date"][:4] if m.get("release_date") else "N/A",
                "Rating": m.get("vote_average"),
                "Popularity": m.get("popularity"),
                # EXPLICITLY MAP THESE LOWERCASE KEYS FROM TMDB:
                "poster_path": m.get("poster_path"),
                "overview": m.get("overview") or "No description available.",
            }
        )
    return movies, total_pages


def _gather_pool(
    token: str,
    rng: random.Random,
    build_params: Callable[[int], dict[str, Any]],
    source_label: str,
) -> list[dict[str, Any]]:
    """Fetch several random discover pages and return deduped normalized rows with Source."""
    first_params = build_params(1)
    first_batch, total_pages = discover_movies(token, first_params)
    by_id: dict[int, dict[str, Any]] = {}
    for row in first_batch:
        by_id[row["id"]] = {**row, "Source": source_label}

    for _ in range(POOL_PAGE_ATTEMPTS - 1):
        page = rng.randint(1, total_pages)
        params = build_params(page)
        batch, _ = discover_movies(token, params)
        for row in batch:
            mid = row["id"]
            if mid not in by_id:
                by_id[mid] = {**row, "Source": source_label}

    return list(by_id.values())


def _sample_unique(
    candidates: list[dict[str, Any]],
    k: int,
    used_ids: set[int],
    rng: random.Random,
) -> list[dict[str, Any]]:
    pool = [c for c in candidates if c["id"] not in used_ids]
    rng.shuffle(pool)
    return pool[:k]


def _backfill(
    token: str,
    genre_id: int,
    rng: random.Random,
    need: int,
    used_ids: set[int],
) -> list[dict[str, Any]]:
    if need <= 0:
        return []

    def build(page: int) -> dict[str, Any]:
        return {
            "with_genres": str(genre_id),
            "vote_count.gte": 40,
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        }

    extra = _gather_pool(token, rng, build, "backfill")
    return _sample_unique(extra, need, used_ids, rng)


def build_mixed_recommendations(
    genre_id: int, num_movies: int, token: str, rng: random.Random
) -> pd.DataFrame:
    if num_movies < 1:
        return pd.DataFrame()

    mainstream_target = max(1, round(num_movies * MAINSTREAM_SHARE))
    if num_movies == 1:
        mainstream_target = 1
        dark_target = 0
        thriller_target = 0
    else:
        mainstream_target = min(mainstream_target, num_movies - 1)
        mainstream_target = max(1, mainstream_target)
        alt = num_movies - mainstream_target
        dark_target = (alt + 1) // 2
        thriller_target = alt // 2

    used_ids: set[int] = set()
    picked: list[dict[str, Any]] = []

    def mainstream_params(page: int) -> dict[str, Any]:
        return {
            "with_genres": str(genre_id),
            "vote_count.gte": 200,
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        }

    mainstream_candidates = _gather_pool(
        token, rng, mainstream_params, "mainstream"
    )
    mainstream_pick = _sample_unique(
        mainstream_candidates, mainstream_target, used_ids, rng
    )
    for row in mainstream_pick:
        used_ids.add(row["id"])
        picked.append(row)

    def dark_params(page: int) -> dict[str, Any]:
        return {
            "with_genres": str(genre_id),
            "with_keywords": DARK_COMEDY_KEYWORDS,
            "vote_count.gte": 50,
            "vote_count.lte": 500,
            "sort_by": "vote_average.desc",
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        }

    dark_candidates = _gather_pool(token, rng, dark_params, "dark_comedy_keywords")
    if dark_target > 0 and len([c for c in dark_candidates if c["id"] not in used_ids]) < dark_target:

        def dark_broad_params(page: int) -> dict[str, Any]:
            return {
                "with_keywords": DARK_COMEDY_KEYWORDS,
                "vote_count.gte": 50,
                "vote_count.lte": 500,
                "sort_by": "vote_average.desc",
                "include_adult": "false",
                "language": "en-US",
                "page": page,
            }

        more = _gather_pool(
            token, rng, dark_broad_params, "dark_comedy_keywords"
        )
        seen = {c["id"] for c in dark_candidates}
        for row in more:
            if row["id"] not in seen:
                dark_candidates.append(row)
                seen.add(row["id"])

    dark_pick = _sample_unique(dark_candidates, dark_target, used_ids, rng)
    for row in dark_pick:
        used_ids.add(row["id"])
        picked.append(row)

    def thriller_params(page: int) -> dict[str, Any]:
        return {
            "with_genres": str(THRILLER_GENRE_ID),
            "vote_count.gte": 50,
            "vote_count.lte": 450,
            "sort_by": "popularity.asc",
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        }

    def comedy_thriller_params(page: int) -> dict[str, Any]:
        return {
            "with_genres": f"{COMEDY_GENRE_ID},{THRILLER_GENRE_ID}",
            "vote_count.gte": 50,
            "vote_count.lte": 450,
            "sort_by": "popularity.asc",
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        }

    thriller_candidates = _gather_pool(token, rng, thriller_params, "thriller")
    ct = _gather_pool(token, rng, comedy_thriller_params, "thriller")
    t_seen = {c["id"] for c in thriller_candidates}
    for row in ct:
        if row["id"] not in t_seen:
            thriller_candidates.append(row)
            t_seen.add(row["id"])

    thriller_pick = _sample_unique(
        thriller_candidates, thriller_target, used_ids, rng
    )
    for row in thriller_pick:
        used_ids.add(row["id"])
        picked.append(row)

    shortage = num_movies - len(picked)
    if shortage > 0:
        picked.extend(_backfill(token, genre_id, rng, shortage, used_ids))

    rng.shuffle(picked)
    display_rows = [
        {
            "Title": r["Title"],
            "Year": r["Year"],
            "Rating": r["Rating"],
            "Popularity": r["Popularity"],
            "Source": r["Source"],
            # PASS THEM DOWN TO THE DATAFRAME REC:
            "poster_path": r.get("poster_path"),
            "overview": r.get("overview"),
        }
        for r in picked[:num_movies]
    ]
    return pd.DataFrame(display_rows)


def get_genre_list(token: str) -> dict[str, int]:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{GENRE_LIST_URL}?language=en", headers=headers, timeout=30
    )
    response.raise_for_status()
    data = response.json()
    return {g["name"]: g["id"] for g in data.get("genres", [])}


def main() -> None:
    token = get_tmdb_token()
    genre_name = input(
        "Enter a movie genre (e.g., Action, Comedy, Drama): "
    ).strip()
    genre_key = genre_name[:1].upper() + genre_name[1:] if genre_name else ""
    num_movies = int(input("How many movies to display? "))
    
    genres = get_genre_list(token)
    genre_id = genres.get(genre_key) or genres.get(genre_name)

    if not genre_id:
        print(f"Sorry, I couldn't find the genre: {genre_name}")
        return

    rng = random.Random()
    df = build_mixed_recommendations(genre_id, num_movies, token, rng)
    if not df.empty:
        label = next((n for n, gid in genres.items() if gid == genre_id), genre_name)
        print(
            f"\n{num_movies} mixed picks for {label} (mainstream + dark comedy / thriller):"
        )
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
