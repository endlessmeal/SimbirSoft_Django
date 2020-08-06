from fastapi import APIRouter
from pydantic import BaseModel

from ..models.templates import Template

router = APIRouter()


@router.get("/templates/{uid}")
async def get_template(uid: str):
    temp = await Template.get_or_404(uid)
    return temp.to_dict()


class TemplateModel(BaseModel):
    name: str
    text: str


@router.post("/templates")
async def add_template(template: TemplateModel):
    rv = await Template.create(name=template.name, text=template.text)
    return rv.to_dict()


@router.delete("/templates/{uid}")
async def delete_template(uid: str):
    temp = await Template.get_or_404(uid)
    await temp.delete()
    return dict(uuid=uid)


def init_app(app):
    app.include_router(router)