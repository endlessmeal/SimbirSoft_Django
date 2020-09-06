from celery import Celery
from monitor_service.app.config import BROKER_CONN_URI

celery = Celery("statistics", broker=BROKER_CONN_URI, include=["app.celery.tasks"])
celery.autodiscover_tasks(["app", "celery"])
