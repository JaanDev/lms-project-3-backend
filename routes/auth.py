from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert, update
from pydantic import BaseModel, constr

import database
import utils

router = APIRouter(prefix='/auth')


@router.get('/login')
async def login(login: str, password: str) -> JSONResponse:
    async with database.sessions.begin() as session:
        request = await session.execute(select(database.Users).where(database.Users.login == login.strip()))
        user = request.scalar_one_or_none()

        if user is None:
            raise HTTPException(403, {"error": "Пользователя с таким логином не существует"})

        if utils.hash_password(password.strip()) != user.password_hash:
            raise HTTPException(403, {"error": "Неправильный пароль"})

        return utils.json_responce({
            'token': user.token,
            'id': user.id,
            'name': user.name
        })


class RegisterModel(BaseModel):
    login: constr(min_length=5, max_length=100)
    password: constr(min_length=5, max_length=100)
    name: constr(min_length=1, max_length=100)
    secret: str


@router.post('/register')
async def register(data: RegisterModel) -> JSONResponse:
    async with database.sessions.begin() as session:
        login, password, name, secret = data.login, data.password, data.name, data.secret
        request = await session.execute(select(database.Users).where(database.Users.login == login.strip()))
        user = request.scalar_one_or_none()

        if secret.strip() != 'saslo228':
            raise HTTPException(403, {"error": "Неверный пароль доступа"})

        if user is not None:
            raise HTTPException(418, {"error": "Пользователь с таким логином уже существует"})

        token = utils.gen_token()

        req = await session.execute(insert(database.Users).values(login=login.strip(), name=name.strip(),
                                                                  password_hash=utils.hash_password(password),
                                                                  token=token))
        await session.commit()

        return utils.json_responce({
            'token': token,
            'id': req.inserted_primary_key[0]
        })


@router.get('/verify')
async def verify(token: str) -> JSONResponse:
    async with database.sessions.begin() as session:
        request = await session.execute(select(database.Users).where(database.Users.token == token.strip()))
        user = request.scalar_one_or_none()
        if user is None:
            raise HTTPException(403, {"error": "Токен не найден"})
        return utils.json_responce({
            'id': user.id,
            'login': user.login,
            'name': user.name
        })
