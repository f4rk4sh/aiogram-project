from utils.db_api.database import db


class Master(db.Model):
    __tablename__ = 'master'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.BigInteger, unique=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(13), unique=True)
    info = db.Column(db.String(200))
    photo_id = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Master {self.id}>'


class Customer(db.Model):
    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.BigInteger, unique=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(13), unique=True)

    def __repr__(self):
        return f'<Customer {self.id}>'


class Timeslot(db.Model):
    __tablename__ = 'timeslot'
    __table_args__ = (db.UniqueConstraint('date', 'time', 'master_id'),
                      db.UniqueConstraint('date', 'time', 'customer_id'),)

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    datetime = db.Column(db.DateTime)
    is_free = db.Column(db.Boolean, default=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='CASCADE'))
    master_id = db.Column(db.Integer, db.ForeignKey('master.id', ondelete='SET NULL'))

    def __repr__(self):
        return f'<Timeslot {self.id}>'


class PortfolioPhoto(db.Model):
    __tablename__ = 'portfoliophoto'

    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.String(200))
    master_id = db.Column(db.Integer, db.ForeignKey('master.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<Portfolio photo {self.id}>'
