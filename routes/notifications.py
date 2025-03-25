from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime

import database
import utils
from . import analytics

router = APIRouter(prefix='/notifications')


@router.get('/get')
async def get_notifications(token: Annotated[str, Header()]) -> JSONResponse:
    async with database.sessions.begin() as session:
        await utils.verify_token(session, token)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        req = await session.execute(select(database.Products).where(database.Products.expiry_date <= today))
        data = req.scalars().all()

        res = {
            'expired': [],
            'expires_today': []
        }

        for prod in data:
            if prod.expiry_date == today:
                res['expires_today'].append({'id': prod.id, 'type_id': prod.type_id})
            else:
                res['expired'].append({'id': prod.id, 'type_id': prod.type_id})

        return utils.json_responce(res)
