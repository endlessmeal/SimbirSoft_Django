from fastapi import FastAPI
from .models import db
from .views.stats import init_app


def get_app():
    app = FastAPI(title="Monitor service")
    db.init_app(app)
    init_app(app)
    return app
