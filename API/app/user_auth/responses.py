from fastapi.encoders import jsonable_encoder


async def main_response(resp):
    return jsonable_encoder(
        {"status": resp.status_code, "body": resp.text, "headers": resp.headers}
    )


async def cut_response(status, text):
    return jsonable_encoder({"status": status, "text": text})
