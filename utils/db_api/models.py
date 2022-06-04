from tortoise.models import Model
from tortoise import fields, Tortoise

from data.config import TORTOISE_ORM


class Master(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField(unique=True)
    name = fields.CharField(max_length=100)
    phone = fields.CharField(max_length=13)
    info = fields.CharField(max_length=200)
    photo_id = fields.CharField(max_length=200, null=True)
    is_active = fields.BooleanField(default=True)

    timeslots: fields.ReverseRelation["Timeslot"]
    portfoliophotos: fields.ReverseRelation["PortfolioPhoto"]

    def __repr__(self):
        return f"<Master {self.id}>"


class Customer(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField(unique=True, null=True)
    name = fields.CharField(max_length=100)
    phone = fields.CharField(max_length=13)

    timeslots: fields.ReverseRelation["Timeslot"]

    def __repr__(self):
        return f"<Customer {self.id}>"


class Timeslot(Model):
    id = fields.IntField(pk=True)
    date = fields.DateField(null=True)
    time = fields.TimeField(null=True)
    datetime = fields.DatetimeField(null=True)
    customer: fields.ForeignKeyRelation[Customer] = fields.ForeignKeyField(
        "models.Customer", related_name="timeslots", ondelete=fields.CASCADE, null=True
    )
    master: fields.ForeignKeyRelation[Master] = fields.ForeignKeyField(
        "models.Master", related_name="timeslots", ondelete=fields.CASCADE
    )

    class Meta:
        unique_together = (
            ("date", "time", "master"),
            ("date", "time", "customer"),
        )

    def __repr__(self):
        return f"<Timeslot {self.id}>"


class PortfolioPhoto(Model):
    id = fields.IntField(pk=True)
    photo_id = fields.CharField(max_length=200)
    master: fields.ForeignKeyRelation[Master] = fields.ForeignKeyField(
        "models.Master", related_name="portfoliophotos", ondelete=fields.CASCADE
    )

    def __repr__(self):
        return f"<Portfolio photo {self.id}>"


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
