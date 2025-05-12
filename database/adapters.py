from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from motor.motor_asyncio import AsyncIOMotorClient

class IDatabase(ABC):
    @abstractmethod
    async def get_nf(self, chave: str) -> dict:
        pass

class PostgresRepository(IDatabase):
    def __init__(self, conn_str: str):
        self.engine = create_engine(conn_str)

    async def get_nf(self, chave: str) -> dict:
        print(f"Buscando NF {chave} no PostgreSQL (simulado)")
        return {"chave": chave, "dados": "dados do postgresql"}

class MongoRepository(IDatabase):
    def __init__(self, conn_str: str):
        self.client = AsyncIOMotorClient(conn_str)

    async def get_nf(self, chave: str) -> dict:
        print(f"Buscando NF {chave} no MongoDB (simulado)")
        return {"chave": chave, "dados": "dados do mongodb"}

class DatabaseFactory:
    @staticmethod
    def get_repository(db_type: str, conn_str: str) -> IDatabase:
        if db_type == "postgresql":
            return PostgresRepository(conn_str)
        elif db_type == "mongodb":
            return MongoRepository(conn_str)
        else:
            raise ValueError(f"Tipo de banco de dados desconhecido: {db_type}")