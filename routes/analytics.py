from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from datetime import datetime, date, timedelta

import database
import utils

router = APIRouter(prefix='/analytics')


async def create_new_record(session: AsyncSession):
    req = await session.execute(insert(database.Analytics).values(date=date.today(), data={'added': {}, 'used': {}, 'expired': {}}))
    return req.inserted_primary_key[0]


async def change_values(count: dict, action: str):
    async with database.sessions.begin() as session:
        req = await session.execute(select(database.Analytics).where(database.Analytics.date == date.today()))
        row = req.scalar_one_or_none()
        if row is None:
            row_id = await create_new_record(session)
            current = {'added': {}, 'used': {}, 'expired': {}}
        else:
            current = row.data
            row_id = row.id

        for k, v in count.items():
            if k in current[action]:
                current[action][k] += v
            else:
                current[action][k] = v

        await session.execute(update(database.Analytics).where(database.Analytics.id == row_id).values(data=current))


@router.get('/get')
async def get_analytics(start_date: datetime, end_date: datetime, token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        req = await session.execute(select(database.Analytics).where(start_date <= database.Analytics.date).where(database.Analytics.date <= end_date))
        res: list[database.Analytics] = req.scalars().all()

        ret = {
            'total': {
                'added': {},
                'used': {},
                'expired': {}
            },
            'days': []
        }

        for z in res:
            obj = {'date': z.date}
            for val in ('added', 'used', 'expired'):
                obj[val] = sum(z.data[val].values())
                for type_id, amount in z.data[val].items():
                    if type_id in ret['total'][val]:
                        ret['total'][val][type_id] += amount
                    else:
                        ret['total'][val][type_id] = amount
            ret['days'].append(obj)
        
        return utils.json_responce(ret)


async def update_expired_products():
    async with database.sessions.begin() as session:
        print('Updating expired products')

        yesterday = date.today() - timedelta(days=1)
        req = await session.execute(select(database.Products).where(database.Products.expiry_date == yesterday))
        data = req.scalars().all()

        res = {}
        for z in data:
            tid = str(z.type_id)
            if tid not in res:
                res[tid] = 1
            else:
                res[tid] += 1
        await change_values(res, 'expired')
