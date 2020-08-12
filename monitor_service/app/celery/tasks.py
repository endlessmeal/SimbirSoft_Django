from .worker import celery
from ..models.stats import Stats
from gino import create_engine
from ..config import DB_DSN
from ..models import db
import celery_pool_asyncio


@celery.task(name="tasks.send_task")
async def send_task(service, url, status):
    engine = await create_engine(str(DB_DSN))
    await Stats.create(service=service, url=url, status_code=status, bind=engine)
    await engine.close()
    return True
