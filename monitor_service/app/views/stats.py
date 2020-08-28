from fastapi import APIRouter
from fastapi.responses import JSONResponse
from monitor_service.app.models.base_models import StatsModel
from monitor_service.app.celery.tasks import send_task

router = APIRouter()


@router.post("/api/v1/send/")
async def send_stats(stat: StatsModel):
    await send_task.delay(**stat.dict())
    return JSONResponse(content="Success")


def init_app(app):
    app.include_router(router)
