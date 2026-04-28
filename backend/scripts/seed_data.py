"""
Seed the database with MovieLens 100K data.
Downloads ml-100k.zip, parses movies + ratings, upserts into the items table.
Safe to run multiple times (ON CONFLICT DO NOTHING on movielens_id).
"""
import io
import os
import re
import sys
import urllib.request
import zipfile
import uuid
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras

ML_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"

GENRE_NAMES = [
    "unknown", "Action", "Adventure", "Animation", "Children's", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror",
    "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western",
]


def _get_dsn() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL env var is not set")
    # psycopg2 needs postgresql://, strip asyncpg variant
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("postgres://", "postgresql://")
    return url


def _download_zip() -> bytes:
    print(f"Downloading {ML_URL} ...", flush=True)
    with urllib.request.urlopen(ML_URL, timeout=120) as resp:
        data = resp.read()
    print(f"Downloaded {len(data) // 1024} KB", flush=True)
    return data


def _parse_movies(zf: zipfile.ZipFile) -> list[dict]:
    """Parse ml-100k/u.item — pipe-separated, latin-1 encoded."""
    with zf.open("ml-100k/u.item") as f:
        content = f.read().decode("latin-1")

    movies = []
    for line in content.splitlines():
        parts = line.split("|")
        if len(parts) < 24:
            continue
        ml_id = int(parts[0])
        raw_title = parts[1].strip()
        release_date = parts[2].strip()  # e.g. "01-Jan-1995"

        # Extract year from title "(1995)" or from release_date
        year = None
        m = re.search(r"\((\d{4})\)\s*$", raw_title)
        if m:
            year = int(m.group(1))
            title = raw_title[: m.start()].strip()
        else:
            title = raw_title
            if release_date:
                try:
                    year = int(release_date.split("-")[-1])
                except ValueError:
                    pass

        genre_flags = parts[5:24]
        genres = "|".join(
            GENRE_NAMES[i] for i, flag in enumerate(genre_flags) if flag == "1"
        )

        movies.append({
            "id": str(uuid.uuid4()),
            "title": title[:500],
            "genres": genres[:500] if genres else None,
            "release_year": year,
            "movielens_id": ml_id,
        })

    return movies


def _parse_ratings(zf: zipfile.ZipFile) -> dict[int, tuple[float, int]]:
    """Return {movielens_id: (avg_rating, count)} from u.data."""
    with zf.open("ml-100k/u.data") as f:
        content = f.read().decode("latin-1")

    totals: dict[int, list] = {}
    for line in content.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        ml_id = int(parts[1])
        rating = float(parts[2])
        if ml_id not in totals:
            totals[ml_id] = [0.0, 0]
        totals[ml_id][0] += rating
        totals[ml_id][1] += 1

    return {
        ml_id: (total / count, count)
        for ml_id, (total, count) in totals.items()
    }


def main() -> None:
    dsn = _get_dsn()
    raw = _download_zip()

    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        movies = _parse_movies(zf)
        ratings = _parse_ratings(zf)

    print(f"Parsed {len(movies)} movies", flush=True)

    now = datetime.now(timezone.utc)
    rows = []
    for m in movies:
        avg, cnt = ratings.get(m["movielens_id"], (0.0, 0))
        rows.append((
            m["id"],
            m["title"],
            m["genres"],
            None,          # description — not in MovieLens 100K
            m["release_year"],
            round(avg, 4),
            cnt,
            m["movielens_id"],
            now,
        ))

    conn = psycopg2.connect(dsn)
    try:
        with conn:
            with conn.cursor() as cur:
                psycopg2.extras.execute_values(
                    cur,
                    """
                    INSERT INTO items
                        (id, title, genres, description, release_year,
                         avg_rating, rating_count, movielens_id, created_at)
                    VALUES %s
                    ON CONFLICT (movielens_id) DO NOTHING
                    """,
                    rows,
                    page_size=500,
                )
                cur.execute("SELECT COUNT(*) FROM items")
                count = cur.fetchone()[0]
        print(f"Seed complete. Items in DB: {count}", flush=True)
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"SEED FAILED: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
