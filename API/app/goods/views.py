import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from API.app.config import goods_url, user_url
from API.app.user_auth.responses import main_response

goods_routes = APIRouter()


class Ad(BaseModel):
    title: str
    description: str
    price: int
    tag: str
    jwt: str


class AdId(BaseModel):
    id: int


class AdDelete(BaseModel):
    id: int
    jwt: str


@goods_routes.post("/api/v1/goods/add", tags=["goods"])
async def goods_add(ad: Ad):
    check_req = {"jwt_token": ad.jwt}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{user_url}/api/v1/validate", data=check_req)
        if resp.status_code == 200:
            user = resp.json()
            req = dict(
                title=ad.title,
                description=ad.description,
                price=ad.price,
                tag=ad.tag,
                user_id=user["user_id"],
            )
            resp = await client.post(f"{goods_url}/api/v1/ad/create/", data=req)
            resp_json = await main_response(resp)
            return JSONResponse(content=resp_json)
        return JSONResponse(content="Something went wrong")


@goods_routes.get("/api/v1/goods/all", tags=["goods"])
async def goods_all():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{goods_url}/api/v1/ad/all/")
        return await main_response(resp)


@goods_routes.get("/api/v1/goods/tags", tags=["goods"])
async def tags_all():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{goods_url}/api/v1/tag/all/")
        return await main_response(resp)


@goods_routes.post("/api/v1/goods/entiread", tags=["goods"])
async def goods_ad(id_ad: AdId):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{goods_url}/api/v1/ad/full/{id_ad.id}/")
        return await main_response(resp)


@goods_routes.post("/api/v1/goods/fastlook", tags=["goods"])
async def goods_fast(id_ad: AdId):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{goods_url}/api/v1/ad/{id_ad.id}/")
        return await main_response(resp)


@goods_routes.put("/api/v1/goods/edit", tags=["goods"])
async def goods_edit_put(ad: Ad, ad_id: AdId):
    check_req = {"jwt_token": ad.jwt}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{user_url}/api/v1/validate", data=check_req)
        if resp.status_code == 200:
            user = resp.json()
            req = dict(
                title=ad.title,
                description=ad.description,
                price=ad.price,
                tag=ad.tag,
                user_id=user["user_id"],
            )
            resp = await client.put(f"{goods_url}/api/v1/ad/edit/{ad_id.id}/", data=req)
            resp_json = await main_response(resp)
            return JSONResponse(content=resp_json)
        return JSONResponse(content="Something went wrong")


@goods_routes.delete("/api/v1/goods/edit", tags=["goods"])
async def goods_edit_delete(ad: AdDelete):
    check_req = {"jwt_token": ad.jwt}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{user_url}/api/v1/validate", data=check_req)
        if resp.status_code == 200:
            resp = await client.delete(f"{goods_url}/api/v1/ad/edit/{ad.id}/")
            resp_json = await main_response(resp)
            return JSONResponse(content=resp_json)
        return JSONResponse(content="Something went wrong")
