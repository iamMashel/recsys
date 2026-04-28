"""
Protected admin endpoints — for operations that need the Shell on paid plans.
Protected by X-Admin-Key header (must match SECRET_KEY env var).
"""
import asyncio
from fastapi import APIRouter, Header, HTTPException, status, BackgroundTasks
from app.core.config import get_settings
from app.core.logging import get_logger

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger(__name__)


def _require_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != get_settings().SECRET_KEY:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid admin key")


@router.post("/seed", status_code=202)
async def trigger_seed(background_tasks: BackgroundTasks, x_admin_key: str = Header(...)):
    """
    Download MovieLens dataset and load it into the database.
    Runs in the background — check /health or logs for progress.
    Call once after first deploy.

    curl -X POST https://your-app.onrender.com/api/v1/admin/seed \\
         -H "X-Admin-Key: <your SECRET_KEY>"
    """
    _require_admin_key(x_admin_key)
    background_tasks.add_task(_run_seed)
    return {"message": "Seed started in background. Check logs for progress."}


@router.post("/train", status_code=202)
async def trigger_train(background_tasks: BackgroundTasks, x_admin_key: str = Header(...)):
    """
    Build the item-item CF model and cache it in Redis.
    Run after seeding is complete.
    """
    _require_admin_key(x_admin_key)
    background_tasks.add_task(_run_train)
    return {"message": "Training started in background. Check logs for progress."}


async def _run_seed():
    logger.info("admin_seed_started")
    try:
        proc = await asyncio.create_subprocess_exec(
            "python", "scripts/seed_data.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0:
            logger.info("admin_seed_complete")
        else:
            logger.error("admin_seed_failed", output=stdout.decode())
    except Exception as e:
        logger.error("admin_seed_error", error=str(e))


async def _run_train():
    logger.info("admin_train_started")
    try:
        proc = await asyncio.create_subprocess_exec(
            "python", "-m", "recommender.train",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0:
            logger.info("admin_train_complete")
        else:
            logger.error("admin_train_failed", output=stdout.decode())
    except Exception as e:
        logger.error("admin_train_error", error=str(e))
