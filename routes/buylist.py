from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated
from datetime import date, timedelta

import database
import utils
from . import analytics

router = APIRouter(prefix='/buylist')


@router.get('/get')
async def get_buylist(token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)
        result = await session.execute(select(database.BuyList))
        buylist = result.scalars().all()
        return utils.json_responce(buylist)


class BuylistAdd(BaseModel):
    prod_type_id: int
    count: int


@router.post('/add')
async def add_to_buylist(data: BuylistAdd, token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        req = await session.execute(select(database.ProductTypes).where(database.ProductTypes.id == data.prod_type_id))
        if req.scalar_one_or_none() is None:
            raise HTTPException(400, {'error': 'Такого типа не существует'})

        existing_item = await session.execute(
            select(database.BuyList).where(database.BuyList.prod_type_id == data.prod_type_id))
        res = existing_item.scalar_one_or_none()

        if res is not None:
            res.count += data.count
            await session.commit()
        else:
            await session.execute(insert(database.BuyList).values(prod_type_id=data.prod_type_id, count=data.count))
            await session.commit()
        return utils.json_responce({"message": "Продукт успешно добавлен в список покупок"})


@router.delete('/remove')
async def remove_from_buylist(buylist_id: int, token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)
        existing_item = await session.execute(select(database.BuyList).where(database.BuyList.id == buylist_id))
        if not existing_item.scalar_one_or_none():
            raise HTTPException(404, {"error": "Продукт не найден в списке покупок"})
        await session.execute(delete(database.BuyList).where(database.BuyList.id == buylist_id))
        await session.commit()
        return utils.json_responce({"message": "Продукт успешно удален из списка покупок"})


@router.delete('/clear')
async def clear_all(token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        await session.execute(delete(database.BuyList))

        return utils.json_responce({'message': 'Продукты успешно удалены'})
