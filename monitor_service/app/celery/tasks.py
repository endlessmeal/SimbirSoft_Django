from .worker import celery
from monitor_service.app.models.stats import Stats
from gino import create_engine
from monitor_service.app.config import DB_DSN


@celery.task(name="tasks.send_task")
async def send_task(**params):
    engine = await create_engine(str(DB_DSN))
    await Stats.create(**params, bind=engine)
    await engine.close()
    return True
