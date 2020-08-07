from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from gino.api import Gino
from ..models.templates import Template
from ..amqp.publisher import publisher

from sqlalchemy.sql import select

router = APIRouter()


class TemplateModel(BaseModel):
    name: str
    text: str


class MessageModel(BaseModel):
    msg_text: str


@router.get("/templates/{uid}")
async def get_template(uid: str):
    temp = await Template.get_or_404(uid)
    return temp.to_dict()


@router.post("/templates")
async def add_template(template: TemplateModel):
    rv = await Template.create(name=template.name, text=template.text)
    return rv.to_dict()


@router.delete("/templates/{uid}")
async def delete_template(uid: str):
    temp = await Template.get_or_404(uid)
    await temp.delete()
    return dict(uuid=uid)


@router.post("/templates/send")
async def send_msg(message: MessageModel):
    msg_text = message.msg_text
    await publisher(msg_text)
    return JSONResponse(content="Message has been sent!")


def init_app(app):
    app.include_router(router)