import math
import secrets
from datetime import timedelta, datetime

import jwt
import tokens
from aiohttp import web
from db import create_user, hash_password, login_user, user_info
from settings import JWT

SECRET_KEY = JWT["SECRET"]
ALGORITHM = JWT["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


# registration of new user with 4 params(username, password, name, age)
async def signin(request):
    """
    ---
    description: This route allow to register users
    tags:
    - Registration
    produces:
    - text/plain
    parameters_strategy: merge
    omit_parameters:
        - path
    parameters:
        - name: Username
          description: Enter your username
          required: true
          type: string
          paramType: form
        - name: Password
          description: Enter your password
          required: true
          type: string
          paramType: form
        - name: Name
          description: Enter your name
          required: true
          type: string
          paramType: form
        - name: Age
          description: Enter your age
          required: true
          type: string
          paramType: form
    """

    req = await request.post()

    data = {
        "username": req.get("username"),
        "password": await hash_password(req.get("password")),
        "name": req.get("name"),
        "age": req.get("age"),
    }

    result = await create_user(
        request.app["db"], data["username"], data["password"], data["name"], data["age"]
    )
    if result:
        return web.Response(
            content_type="application/json", text=tokens.convert_json_status("Success")
        )

    return web.Response(
        content_type="application/json", text=tokens.convert_json_status("User exists"),
    )


async def login(request):
    """
    ---
    description: This route allow to sign up
    tags:
    - Login
    produces:
    - application/json
    parameters_strategy: merge
    omit_parameters:
        - path
    parameters:
        - name: Username
          description: Enter your username
          required: true
          type: string
          paramType: form
        - name: Password
          description: Enter your password
          required: true
          type: string
          paramType: form
    """

    req = await request.post()

    data = {
        "username": req.get("username"),
        "password": req.get("password"),
    }

    result = await login_user(request.app["db"], data["username"], data["password"])
    if not result:
        raise web.HTTPUnauthorized(text="Incorrect username or password")

    # add an expire time to access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    user_credits = await user_info(request.app["db"], data["username"])

    # creating a new access token for user with his uuid and username
    access_token = await tokens.create_access_token(
        data={"uuid": str(user_credits["id"]), "username": user_credits["username"]},
        expires_delta=access_token_expires,
    )

    refresh_token = secrets.token_hex(32)

    refresh_exp = math.ceil((datetime.utcnow() + timedelta(days=30)).timestamp())

    redis = request.app["redis"]
    await redis.set(access_token.decode("utf-8"), refresh_token)
    await redis.expireat(access_token.decode("utf-8"), refresh_exp)

    # convert timestamp to float
    num_ac_tok_exp = tokens.time_to_float(access_token_expires)

    return web.Response(
        text=tokens.convert_json_tokens(
            access_token.decode("utf-8"), num_ac_tok_exp, refresh_token, refresh_exp,
        ),
        status=200,
    )


async def logout(request):
    """
    ---
    description: This route allow to logout
    tags:
    - Logout
    produces:
    - application/json
    consumes:
      - application/json
    parameters:
      - in: header
        name: "Authorization"
        required: false
        schema:
          type: "string"
    """
    try:
        data = await request.post()
    except Exception:
        raise web.HTTPBadRequest(reason="json is invalid")
    await tokens.del_session(request, data["jwt_token"])
    return web.Response(
        content_type="application/json",
        text=tokens.convert_json_status("You are logged out"),
    )


async def get_user_info(request):
    """
    ---
    description: This route get information about user by access token
    tags:
        - Get user information
    produces:
        - application/json
    consumes:
      - application/json
    parameters:
      - in: header
        name: "Authorization"
        required: false
        schema:
          type: "string"
    """
    try:
        data = await request.post()
    except Exception:
        raise web.HTTPBadRequest(reason="json is invalid")

    try:
        decoded_jwt = await tokens.decode_jwt(data["jwt_token"])
    except jwt.exceptions.DecodeError as dec:
        return web.json_response(text=f"Something went wrong: {dec}")

    try:
        username = decoded_jwt["username"]
    except KeyError:
        return web.json_response(text="Refresh your tokens")

    user_credits = await user_info(request.app["db"], username)
    username = user_credits["username"]
    name = user_credits["name"]
    age = user_credits["age"]

    return web.Response(
        content_type="application/json",
        text=tokens.convert_json_info(username, name, age),
    )


async def get_new_tokens(request):
    """
    ---
    description: This route uses for get new tokens by refresh token
    tags:
        - Get new tokens
    produces:
        - application/json
    consumes:
      - application/json
    parameters:
      - in: header
        name: "Authorization"
        required: false
        schema:
          type: "string"
    """

    try:
        data = await request.post()
    except Exception:
        raise web.HTTPBadRequest(reason="json is invalid")

    redis = request.app["redis"]

    refresh_stored = await redis.get(data["jwt"], encoding="utf-8")
    if refresh_stored != data["refresh"]:
        return web.Response(
            content_type="application/json",
            text=tokens.convert_json_status("Incorrect jwt token"),
        )

    rfr_exp = math.ceil((datetime.utcnow() + timedelta(days=30)).timestamp())

    # check if refresh token expires
    if rfr_exp - math.ceil(datetime.utcnow().timestamp()) > 0:
        decoded_access = jwt.decode(
            data["jwt"], SECRET_KEY, verify=False, algorithms=ALGORITHM
        )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        ac_tok = await tokens.create_access_token(
            data={
                "uuid": decoded_access["uuid"],
                "username": decoded_access["username"],
            },
            expires_delta=access_token_expires,
        )

        rfr_token = secrets.token_hex(32)

        await redis.set(ac_tok.decode("utf-8"), rfr_token)
        await redis.expireat(ac_tok.decode("utf-8"), rfr_exp)

        num_ac_tok_exp = tokens.time_to_float(access_token_expires)
        await tokens.del_session(request, data["jwt"])

        return web.Response(
            content_type="application/json",
            text=tokens.convert_json_tokens(
                ac_tok.decode("utf-8"), num_ac_tok_exp, rfr_token, rfr_exp,
            ),
            status=200,
        )

    await logout(request)
    return web.Response(
        content_type="application/json",
        text=tokens.convert_json_status("Refresh token has expired"),
    )


async def validate(request):
    """
    ---
    description: This end-point avalidates token
    tags:
        - Auth
    produces:
        - application/json
    consumes:
      - application/json
    parameters:
      - in: header
        name: "Authorization"
        required: false
        schema:
          type: "string"
        description: "User's JWT"
    """

    try:
        data = await request.post()
    except Exception:
        raise web.HTTPBadRequest(reason="json is invalid")

    try:
        decoded_jwt = await tokens.decode_jwt(data["jwt_token"])
    except jwt.exceptions.DecodeError as dec:
        return web.json_response(text=f"Something went wrong: {dec}")

    try:
        username = decoded_jwt["username"]
    except KeyError:
        return web.json_response(text="Refresh your tokens")

    user_credits = await user_info(request.app["db"], username)
    user_id = user_credits["id"]
    send_data = dict(user_id=str(user_id))

    return web.json_response(data=send_data, status=200)
