from aiohttp import web
from models import User, users
from aiohttp_session import get_session, new_session
import jwt
from datetime import timedelta, datetime
import sqlalchemy as sa
import secrets
import math
from settings import JWT
import tokens

SECRET_KEY = JWT["SECRET"]
ALGORITHM = JWT["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


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
    data = [request.rel_url.query['username'],
            request.rel_url.query['password'],
            request.rel_url.query['name'],
            request.rel_url.query['age']]

    user = User(request.app['db'], data)
    result = await user.create_user()
    if result:
        return web.Response(content_type='application/json', text=tokens.convert_json_status('Success'))
    else:
        return web.Response(content_type='application/json', text=tokens.convert_json_status('User exists'))


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
    data = [request.rel_url.query['username'],
            request.rel_url.query['password']]

    user = User(request.app['db'], data)
    result = await user.login_user()
    if not result:
        raise web.HTTPUnauthorized(
            text='Incorrect username or password'
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    session = await new_session(request)
    user_info = await user.user_info()
    access_token = await tokens.create_access_token(data={'uuid': user_info[0], 'name': user_info[2]},
                                                    expires_delta=access_token_expires)

    session['access_token'] = access_token.decode('utf-8')
    session['refresh_token'] = secrets.token_hex(32)
    session['refresh_token_exp'] = math.ceil((datetime.utcnow() + timedelta(days=30)).timestamp())
    num_ac_tok_exp = tokens.time_to_float(access_token_expires)

    return web.Response(content_type='application/json',
                        text=tokens.convert_json_tokens(session['access_token'], num_ac_tok_exp,
                                                        session['refresh_token'], session['refresh_token_exp']),
                        status=200)


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
    access_token = request.headers['Authorization']
    if access_token is None:
        raise web.HTTPForbidden(reason='Access key is empty')

    await tokens.del_session(request)
    return web.Response(content_type='application/json', text=tokens.convert_json_status('You are logged out'))


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
    access_token = request.headers['Authorization']
    decoded_jwt = tokens.decode_jwt(access_token)

    uuid = decoded_jwt['uuid']
    async with request.app['db'].acquire() as conn:
        s = sa.select([users]).where(users.c.UUID == uuid)
        execute_query = await conn.execute(s)
        fetch_res = await execute_query.fetchone()
    username = fetch_res[1]
    name = fetch_res[3]
    age = fetch_res[4]

    return web.Response(content_type='application/json',
                        text=tokens.convert_json_info(username, name, age))


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
    refresh_token = request.headers['Authorization']
    session = await get_session(request)
    rfr = session['refresh_token']
    access_token = session['access_token']
    rfr_exp = session['refresh_token_exp']
    if refresh_token != rfr:
        return web.Response(content_type='application/json',
                            text=tokens.convert_json_status('Incorrect refresh token'))

    if rfr_exp - math.ceil(datetime.utcnow().timestamp()) > 0:
        decoded_access = jwt.decode(access_token, SECRET_KEY, verify=False, algorithms=ALGORITHM)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        ac_tok = await tokens.create_access_token(data={'uuid': decoded_access['uuid'], 'name': decoded_access['name']},
                                                  expires_delta=access_token_expires)

        session['access_token'] = ac_tok.decode('utf-8')
        session['refresh_token'] = secrets.token_hex(32)
        num_ac_tok_exp = tokens.time_to_float(access_token_expires)

        return web.Response(content_type='application/json',
                            text=tokens.convert_json_tokens(session['access_token'], num_ac_tok_exp,
                                                            session['refresh_token'], session['refresh_token_exp']),
                            status=200)

    session.clear()
    await logout(request)
    return web.Response(content_type='application/json',
                        text=tokens.convert_json_status('Refresh token has expired'))


