from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL_1 = "postgresql+asyncpg://user:password@postgres:5432/mydatabase"
DATABASE_URL_2 = "postgresql+asyncpg://user2:password2@postgres2:5432/mydatabase2"

engine1 = create_async_engine(DATABASE_URL_1, echo=True, future=True)
engine2 = create_async_engine(DATABASE_URL_2, echo=True, future=True)

SessionLocal1 = sessionmaker(engine1, expire_on_commit=False, class_=AsyncSession)
SessionLocal2 = sessionmaker(engine2, expire_on_commit=False, class_=AsyncSession)
