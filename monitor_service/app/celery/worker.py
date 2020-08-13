from celery import Celery
from ..config import BROKER_CONN_URI

celery = Celery("statistics", broker=BROKER_CONN_URI, include=["app.celery.tasks"])
celery.autodiscover_tasks(["app", "celery"])
