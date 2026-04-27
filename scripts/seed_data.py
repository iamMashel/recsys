"""
Seed script — downloads MovieLens 100k and loads it into PostgreSQL.
Run: python scripts/seed_data.py
Requires DATABASE_URL in .env (or env vars).
"""
import asyncio
import csv
import io
import uuid
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

import asyncpg
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/recsys")
# asyncpg uses plain postgres:// not postgresql+asyncpg://
PG_DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql://", "postgresql://")

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
DATA_DIR = Path("data")


def download_movielens():
    DATA_DIR.mkdir(exist_ok=True)
    zip_path = DATA_DIR / "ml-latest-small.zip"
    if not zip_path.exists():
        print("Downloading MovieLens dataset...")
        urlretrieve(MOVIELENS_URL, zip_path)
    return zip_path


def parse_movielens(zip_path: Path):
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open("ml-latest-small/movies.csv") as f:
            movies = list(csv.DictReader(io.TextIOWrapper(f)))
        with zf.open("ml-latest-small/ratings.csv") as f:
            ratings = list(csv.DictReader(io.TextIOWrapper(f)))
    return movies, ratings


async def seed(movies, ratings):
    conn = await asyncpg.connect(PG_DSN)
    try:
        # Map movielens_id → our UUID
        movie_id_map: dict[int, uuid.UUID] = {}

        print(f"Inserting {len(movies)} movies...")
        for m in movies:
            mid = int(m["movieId"])
            title = m["title"]
            genres = m["genres"].replace("|", ", ")
            item_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO items (id, title, genres, movielens_id)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (movielens_id) DO NOTHING
                """,
                item_id, title, genres, mid,
            )
            movie_id_map[mid] = item_id

        # Create synthetic users from movielens user IDs
        user_id_map: dict[int, uuid.UUID] = {}
        ml_user_ids = {int(r["userId"]) for r in ratings}
        print(f"Inserting {len(ml_user_ids)} synthetic users...")
        for uid in ml_user_ids:
            user_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO users (id, email, password_hash)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING
                """,
                user_id, f"user{uid}@movielens.local", "seeded",
            )
            user_id_map[uid] = user_id

        print(f"Inserting {len(ratings)} interactions...")
        for r in ratings:
            uid = int(r["userId"])
            mid = int(r["movieId"])
            if uid not in user_id_map or mid not in movie_id_map:
                continue
            rating = float(r["rating"])
            await conn.execute(
                """
                INSERT INTO interactions (id, user_id, item_id, event_type, rating, timestamp)
                VALUES ($1, $2, $3, 'rating', $4, to_timestamp($5))
                """,
                uuid.uuid4(), user_id_map[uid], movie_id_map[mid], rating, float(r["timestamp"]),
            )

        # Update avg_rating on items
        print("Updating item statistics...")
        await conn.execute(
            """
            UPDATE items i
            SET avg_rating = sub.avg_r, rating_count = sub.cnt
            FROM (
                SELECT item_id, AVG(rating) AS avg_r, COUNT(*) AS cnt
                FROM interactions
                WHERE rating IS NOT NULL
                GROUP BY item_id
            ) sub
            WHERE i.id = sub.item_id
            """
        )
        print("Seed complete.")
    finally:
        await conn.close()


async def main():
    zip_path = download_movielens()
    movies, ratings = parse_movielens(zip_path)
    await seed(movies, ratings)


if __name__ == "__main__":
    asyncio.run(main())
