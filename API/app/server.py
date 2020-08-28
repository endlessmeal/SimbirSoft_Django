from fastapi import FastAPI
from .user_auth.user_service import user_routes
from .goods.views import goods_routes


def get_app():
    app = FastAPI(title="API")
    app.include_router(user_routes)
    app.include_router(goods_routes)
    return app
