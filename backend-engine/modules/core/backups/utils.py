import asyncio
from fastapi import BackgroundTasks, HTTPException
from modules.core.backups.progress_store import progress_queues

async def run_backup(account_id: str):
    if account_id not in progress_queues:
        progress_queues[account_id] = asyncio.Queue()

    steps = [
        ("Initializing", 10),
        ("Scanning files", 30),
        ("Compressing", 60),
        ("Uploading", 90),
        ("Finalizing", 100),
    ]

    for step, percent in steps:
        progress = {
            "account_id": account_id,
            "step": step,
            "percent": percent,
            "status": "running" if percent < 100 else "completed"
        }
        print(progress)
        await progress_queues[account_id].put(progress)
        await asyncio.sleep(1)  # simulate work

    # completion message
    await progress_queues[account_id].put({
        "account_id": account_id,
        "step": "Completed",
        "percent": 100,
        "status": "completed"
    })