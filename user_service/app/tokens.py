import json
from typing import Optional
from datetime import timedelta, datetime
import jwt
from settings import JWT
import math
from aiohttp import web


def convert_json_status(message):
    return json.dumps({"status": message})


def convert_json_info(username, name, age):
    return json.dumps({"username": username, "name": name, "age": age})


def convert_json_tokens(ac_tok, ac_exp, rf_tok, rf_exp):
    return json.dumps(
        {
            "access token": {"token": ac_tok, "expires": ac_exp},
            "refresh token": {"token": rf_tok, "expires": rf_exp},
        }
    )


async def del_session(request, jwt):
    redis = request.app["redis"]
    await redis.delete(jwt)


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT["SECRET"], algorithm=JWT["ALGORITHM"])
    return encoded_jwt


def time_to_float(access_token_expires):
    return math.ceil((datetime.utcnow() + access_token_expires).timestamp())


async def decode_jwt(access_token):
    try:
        decoded_jwt = jwt.decode(
            access_token, JWT["SECRET"], algorithms=JWT["ALGORITHM"]
        )
    except jwt.ExpiredSignatureError as j:
        return web.Response(
            content_type="application/json",
            text=convert_json_status(f"Time of access token has expired: {j}"),
        )

    return decoded_jwt
