from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

import database
import utils

router = APIRouter(prefix='/product_types')


@router.get('/all')
async def get_types(token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        req = await session.execute(select(database.ProductTypes))
        data = {}
        for z in req.scalars():
            zz = z.__dict__
            zz.pop('_sa_instance_state')
            n = zz.pop('id')
            data[n] = zz

        return utils.json_responce(data)


@router.get('/get')
async def get_type(token: Annotated[str, Header()], id: int) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        req = await session.execute(select(database.ProductTypes).where(database.ProductTypes.id == id))
        res = req.scalar_one_or_none()
        if res is None:
            raise HTTPException(400, {'error': 'Типа не существует'})
        data = res.__dict__
        data.pop('_sa_instance_state')

        return utils.json_responce(data)


@router.post('/add')
async def add_product_type(
        token: Annotated[str, Header()],
        name: str,
        category_id: int,
        amount: float,
        units: str,
        nutritional: int,
        measure_type: str,
        expiry_days: int,
        allergens: str = ""
) -> str:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        category = await session.execute(
            select(database.ProductCategories).where(database.ProductCategories.id == category_id)
        )
        if not category.scalar_one_or_none():
            raise HTTPException(400, {"error": "Категория не существует"})
        existing = await session.execute(
            select(database.ProductTypes).where(database.ProductTypes.name == name.strip()).where(database.ProductTypes.category_id == category_id)
        )
        fff = existing.scalar_one_or_none()
        if fff:
            raise HTTPException(400, {"error": "Вид продукта уже существует", "id": fff.id})
        res = await session.execute(
            insert(database.ProductTypes).values(
                name=name.strip(),
                category_id=category_id,
                amount=amount,
                units=units,
                nutritional=nutritional,
                measure_type=measure_type,
                allergens=allergens,
                expiry_days=expiry_days
            ).returning(database.ProductTypes.id)
        )
        return utils.json_responce({"message": "Вид продукта успешно добавлен", "id": res.scalar()})


@router.delete('/remove')
async def remove_product_type(token: Annotated[str, Header()], product_type_id: int) -> str:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        product_type = await session.execute(
            select(database.ProductTypes).where(database.ProductTypes.id == product_type_id)
        )
        if not product_type.scalar_one_or_none():
            raise HTTPException(404, {"error": "Вид продукта не найден"})
        await session.execute(delete(database.ProductTypes).where(database.ProductTypes.id == product_type_id))
        await session.commit()
        return utils.json_responce({"message": "Вид продукта успешно удален"})
