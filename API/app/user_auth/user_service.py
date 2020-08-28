import httpx
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Form
from API.app.config import user_url, messages_url
from fastapi.responses import JSONResponse
from API.app.user_auth.responses import main_response, cut_response
import json

from .mail import (
    create_token,
    make_redis_pool,
    store_token,
    token_is_valid,
    remove_token,
)

user_routes = APIRouter()


class UserSigninModel(BaseModel):
    username: str
    password: str
    name: str
    age: int


class RefreshTokens(BaseModel):
    jwt_token: str
    refresh_token: str


class AccessToken(BaseModel):
    jwt_token: str


class RequestToken(BaseModel):
    address: EmailStr


@user_routes.post("/api/v1/users/login")
async def users_login(username: str = Form(None), password: str = Form(None)):
    req = dict(username=username, password=password)
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{user_url}/api/v1/login", data=req)
        resp_json = await main_response(resp)
        return JSONResponse(content=resp_json)


@user_routes.post("/api/v1/users/signin")
async def users_signin(
    username: str = Form(None),
    password: str = Form(None),
    name: str = Form(None),
    age: int = Form(None),
    token: str = Form(None),
    email: str = Form(None),
):
    redis = await make_redis_pool()
    if token_is_valid(email, token, redis):
        await remove_token(email, redis)
        req = dict(username=username, password=password, name=name, age=age)
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{user_url}/api/v1/signin", data=req)
            resp_json = await main_response(resp)
            return JSONResponse(content=resp_json)
    return JSONResponse("Something went wrong")


@user_routes.post("/api/v1/users/request_token")
async def users_token(mail: RequestToken):
    redis = await make_redis_pool()
    token = create_token()
    await store_token(mail.address, token, redis)
    text_msg = json.dumps(
        {
            "msg_to": mail.address,
            "msg_text": f"Your token is {token}",
            "msg_subject": "Confirmation",
        }
    )
    async with httpx.AsyncClient() as client:
        await client.post(f"{messages_url}/api/v1/send", data=text_msg)
    resp_json = await cut_response(200, "Ok")
    return JSONResponse(content=resp_json)


@user_routes.post("/api/v1/users/logout")
async def users_logout(token: AccessToken):
    req = dict(jwt_token=token.jwt_token)
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{user_url}/api/v1/logout", data=req)
        resp_json = await main_response(resp)
        return JSONResponse(content=resp_json)


@user_routes.post("/api/v1/users/user_info")
async def users_info(token: AccessToken):
    req = dict(jwt_token=token.jwt_token)
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{user_url}/api/v1/info", data=req)
        resp_json = await main_response(resp)
        return JSONResponse(content=resp_json)


@user_routes.post("/api/v1/users/new_tokens")
async def users_new_tokens(tokens: RefreshTokens):
    req = dict(jwt=tokens.jwt_token, refresh=tokens.refresh_token)
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{user_url}/api/v1/newtokens", data=req)
        resp_json = await main_response(resp)
        return JSONResponse(content=resp_json)
