from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from ..models.templates import Template
from ..amqp.publisher import publisher

from .templates_stuff import temp_text, msg_to_json

router = APIRouter()


class TemplateModel(BaseModel):
    name: str
    text: str


class MessageModel(BaseModel):
    temp_uuid: str
    msg_to: str
    params: dict
    subject: str


class BasicMessage(BaseModel):
    msg_to: str
    msg_text: str
    msg_subject: str


@router.get("/api/v1/templates/{uid}")
async def get_template(uid: str):
    temp = await Template.get_or_404(uid)
    return temp.to_dict()


@router.post("/api/v1/templates")
async def add_template(template: TemplateModel):
    rv = await Template.create(name=template.name, text=template.text)
    return rv.to_dict()


@router.post("/api/v1/templates/all")
async def get_all_templates():
    templates = await Template.query.gino.all()
    temp_list = [temp.to_dict() for temp in templates]
    return temp_list


@router.delete("/api/v1/templates/{uid}")
async def delete_template(uid: str):
    temp = await Template.get_or_404(uid)
    await temp.delete()
    return dict(uuid=uid)


@router.post("/api/v1/templates/send")
async def send_msg(message: MessageModel):
    template = await Template.get_or_404(message.temp_uuid)
    msg_text = temp_text(template, message.params)
    msg = msg_to_json(msg_text, message.msg_to, message.subject)
    await publisher(msg)
    return JSONResponse(content="Message has been sent!")


@router.post("/api/v1/send")
async def send_basic_msg(message: dict):
    msg = msg_to_json(message["msg_text"], message["msg_to"], message["msg_subject"])
    await publisher(msg)
    return JSONResponse(content="ok")


def init_app(app):
    app.include_router(router)
