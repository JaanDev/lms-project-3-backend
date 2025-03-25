from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert, update, text, delete
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime, date

import database
import utils
from . import analytics

router = APIRouter(prefix='/products')


@router.get('/all')
async def get_all(token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        stmt = text("""
        SELECT products.id AS prod_id, products.production_date, products.expiry_date,
        product_types.name AS type_name, product_types.amount, product_types.units, product_types.id AS type_id,
        product_types.nutritional, product_types.measure_type, product_types.allergens,
        product_categories.name AS cat_name, product_categories.id AS cat_id, product_types.expiry_days
        FROM products
        JOIN product_types ON products.type_id = product_types.id
        JOIN product_categories ON product_types.category_id = product_categories.id
        """)

        req = await session.execute(stmt)
        data = req.mappings().all()

        # print(data)

        res = {}

        for x in data:
            # print('!!!', x)
            cat_name = x['cat_name']
            type_name = x['type_name']
            if cat_name not in res:
                res[cat_name] = {}
            if type_name not in res[cat_name]:
                z = {'amount': x['amount'], 'units': x['units'], 'nutritional': x['nutritional'],
                     'measure_type': x['measure_type'], 'allergens': x['allergens'], 'type_id': x['type_id'],
                     'items': []}
                res[cat_name][type_name] = z
            res[cat_name][type_name]['items'].append({
                'prod_id': x['prod_id'],
                'production_date': x['production_date'],
                'expiry_date': x['expiry_date']
            })

        # print(res)

        return utils.json_responce(res)


@router.get('/product')
async def get_product(token: Annotated[str, Header()], id: int) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        stmt = text("""
        SELECT products.id AS prod_id, products.production_date, products.expiry_date,
        product_types.name AS type_name, product_types.amount, product_types.units, product_types.id AS type_id,
        product_types.nutritional, product_types.measure_type, product_types.allergens,
        product_categories.name AS cat_name, product_categories.id AS cat_id, product_types.expiry_days
        FROM products
        JOIN product_types ON products.type_id = product_types.id
        JOIN product_categories ON product_types.category_id = product_categories.id
        WHERE products.id = :prod_id
        """)

        req = await session.execute(stmt, {'prod_id': id})
        data = req.mappings().first()

        # print(data)

        if data is None:
            raise HTTPException(404, {'error': 'Продукт с этим id не найден'})

        return utils.json_responce(data)


@router.delete('/remove')
async def remove_product(
    product_id: int,
    token: Annotated[str, Header()]
) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)
        product = await session.execute(
            select(database.Products)
            .where(database.Products.id == product_id)
        )
        product = product.scalar_one_or_none()

        if not product:
            raise HTTPException(404, {'error': 'Продукт не найден'})
        await session.delete(product)
#         await session.execute(
#             insert(database.Analytics).values(
#                 action="removed",
#                 product_id=product_id,
#                 details={
#                     "type_id": product.type_id,
#                     "production_date": str(product.production_date),
#                     "expiry_date": str(product.expiry_date)
#                 }
#             )
#         )
#         await session.commit()
        return utils.json_responce({"message": "Продукт успешно удален"})


@router.post('/add')
async def add_product(type_id: int, prod_date: date, exp_date: date, token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        req = await session.execute(select(database.ProductTypes).where(database.ProductTypes.id == type_id))
        if not req.scalar_one_or_none():
            raise HTTPException(404, {'error': 'Такого типа продуктов не существует'})

        if exp_date < prod_date:
            raise HTTPException(400, {'error': 'Конечная дата меньше начальной'})

        await session.execute(insert(database.Products).values(type_id=type_id, production_date=prod_date, expiry_date=exp_date))

        await analytics.change_values({str(type_id): 1}, 'added')

        return utils.json_responce({'message': 'Продукт успешно добавлен'})


@router.post('/use')
async def use_product(prod_id: int, token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        req = await session.execute(select(database.Products).where(database.Products.id == prod_id))
        product = req.scalar_one_or_none()
        if not product:
            raise HTTPException(404, {'error': 'Такого продукта не существует'})
        type_id = product.type_id

        req = await session.execute(delete(database.Products).where(database.Products.id == prod_id))

        await analytics.change_values({str(type_id): 1}, 'used')

        return utils.json_responce({'message': 'Продукт усепшно использован'})
