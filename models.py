from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MarketOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.BigInteger, unique=True, nullable=False)
    type_id = db.Column(db.Integer, nullable=False)
    region_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume_remain = db.Column(db.Integer, nullable=False)
    volume_total = db.Column(db.Integer, nullable=False)
    is_buy_order = db.Column(db.Boolean, nullable=False)
    issued = db.Column(db.DateTime, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MarketOrder {self.order_id}>"
    
class MarketHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, nullable=False)
    region_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    average_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<MarketHistory {self.type_id} {self.date}>"