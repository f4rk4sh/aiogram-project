from data.config import POSTGRES_URI
from gino import Gino
from gino.schema import GinoSchemaVisitor

db = Gino()


async def create_db():
    await db.set_bind(POSTGRES_URI)
    db.gino: GinoSchemaVisitor

    # drop tables

    await db.gino.drop_all()

    # create tables

    await db.gino.create_all()
