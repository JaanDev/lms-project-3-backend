from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

from .database import *

load_dotenv()

engine = create_async_engine(f'postgresql+asyncpg://root:{os.getenv("DB_PASSWORD")}@localhost:5432/smartfridge')
sessions = async_sessionmaker(engine)
