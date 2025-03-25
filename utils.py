import hashlib
from uuid import uuid4
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from sqlalchemy import select

import database


async def verify_token(session, token):
    existing_item = await session.execute(select(database.Users).where(database.Users.token == token.strip()))
    if existing_item.scalar_one_or_none() is None:
        raise HTTPException(403, {"error": "Авторизация не удалась"})


def json_responce(data: dict) -> JSONResponse:
    return JSONResponse(jsonable_encoder(data), headers={'Access-Control-Allow-Origin': '*'})


def hash_password(password: str) -> str:
    return hashlib.sha512((password + 'HJn12B12!').encode("utf-8")).hexdigest()


def gen_token() -> str:
    return str(uuid4())
