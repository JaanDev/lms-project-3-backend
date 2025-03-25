from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

import database
import utils

router = APIRouter(prefix='/product_categories')


@router.get('/all')
async def get_cats(token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        req = await session.execute(select(database.ProductCategories))
        data = req.scalars()
        return utils.json_responce({x.id: x.name for x in data})


@router.post('/add')
async def add_category(name: str, token: Annotated[str, Header()]) -> str:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        existing = await session.execute(
            select(database.ProductCategories).where(database.ProductCategories.name == name.strip())
        )
        fff = existing.scalar_one_or_none()
        if fff:
            raise HTTPException(400, {"error": "Категория уже существует", "id": fff.id})
        res = await session.execute(insert(database.ProductCategories).values(name=name.strip()).returning(database.ProductCategories.id))
        return utils.json_responce({"message": "Категория успешно добавлена", "id": res.scalar()})


@router.delete('/remove')
async def remove_category(category_id: int, token: Annotated[str, Header()]) -> str:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        category = await session.execute(
            select(database.ProductCategories).where(database.ProductCategories.id == category_id)
        )
        if not category.scalar_one_or_none():
            raise HTTPException(404, {"error": "Категория не найдена"})
        await session.execute(delete(database.ProductCategories).where(database.ProductCategories.id == category_id))
        await session.commit()
        return utils.json_responce({"message": "Категория успешно удалена"})
