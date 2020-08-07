from fastapi import FastAPI
from .models import db
from .views.templates import init_app


def get_app():
    app = FastAPI(title='Messages service')
    db.init_app(app)
    init_app(app)
    return app




