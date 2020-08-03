from aiohttp import web
from aiohttp_session import get_session, new_session
import jwt
from datetime import timedelta, datetime
import sqlalchemy as sa
import secrets
import math
from settings import JWT
import tokens
from db import create_user, hash_password, login_user, user_info
from models import TableUser

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

    data = [
        req.get('username'),
        await hash_password(req.get('password')),
        req.get('name'),
        req.get('age'),
    ]

    result = await create_user(request.app["db"], data[0],
                               data[1], data[2], data[3])
    if result:
        return web.Response(
            content_type="application/json",
            text=tokens.convert_json_status("Success")
        )

    return web.Response(
        content_type="application/json",
        text=tokens.convert_json_status("User exists"),
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

    data = [
        req.get('username'),
        req.get('password'),
    ]

    result = await login_user(request.app['db'], data[0], data[1])
    if not result:
        raise web.HTTPUnauthorized(text="Incorrect username or password")

    # add an expire time to access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    session = await new_session(request)
    user_credits = await user_info(request.app['db'], data[0])

    # creating a new access token for user with his uuid and username
    access_token = await tokens.create_access_token(
        data={"uuid": user_credits[0], "username": user_credits[1]},
        expires_delta=access_token_expires,
    )

    # add an access token to session and decode from bytes
    session["access_token"] = access_token.decode("utf-8")
    # generate a refresh token
    session["refresh_token"] = secrets.token_hex(32)
    # add an expire time for refresh token start from current time and end in one month
    session["refresh_token_exp"] = math.ceil(
        (datetime.utcnow() + timedelta(days=30)).timestamp()
    )
    # convert timestamp to float
    num_ac_tok_exp = tokens.time_to_float(access_token_expires)

    return web.Response(
        content_type="application/json",
        text=tokens.convert_json_tokens(
            session["access_token"],
            num_ac_tok_exp,
            session["refresh_token"],
            session["refresh_token_exp"],
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
    access_token = request.headers["Authorization"]
    if access_token is None:
        raise web.HTTPForbidden(reason="Access key is empty")

    await tokens.del_session(request)
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
    access_token = request.headers["Authorization"]

    try:
        decoded_jwt = await tokens.decode_jwt(access_token)
    except jwt.exceptions.DecodeError as dec:
        return web.json_response(text=f'Something went wrong: {dec}')

    try:
        username = decoded_jwt["username"]
    except KeyError:
        return web.json_response(text='Refresh your tokens')

    user_credits = await user_info(request.app['db'], username)
    username = user_credits[1]
    name = user_credits[2]
    age = user_credits[3]

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
    refresh_token = request.headers["Authorization"]
    session = await get_session(request)
    rfr = session["refresh_token"]
    access_token = session["access_token"]
    rfr_exp = session["refresh_token_exp"]
    if refresh_token != rfr:
        return web.Response(
            content_type="application/json",
            text=tokens.convert_json_status("Incorrect refresh token"),
        )

    # check if refresh token expires
    if rfr_exp - math.ceil(datetime.utcnow().timestamp()) > 0:
        decoded_access = jwt.decode(
            access_token, SECRET_KEY, verify=False, algorithms=ALGORITHM
        )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        ac_tok = await tokens.create_access_token(
            data={"uuid": decoded_access["uuid"], "username": decoded_access["username"]},
            expires_delta=access_token_expires,
        )

        session["access_token"] = ac_tok.decode("utf-8")
        session["refresh_token"] = secrets.token_hex(32)
        num_ac_tok_exp = tokens.time_to_float(access_token_expires)

        return web.Response(
            content_type="application/json",
            text=tokens.convert_json_tokens(
                session["access_token"],
                num_ac_tok_exp,
                session["refresh_token"],
                session["refresh_token_exp"],
            ),
            status=200,
        )

    session.clear()
    await logout(request)
    return web.Response(
        content_type="application/json",
        text=tokens.convert_json_status("Refresh token has expired"),
    )
