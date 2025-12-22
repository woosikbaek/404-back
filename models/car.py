from extensions import db
from datetime import datetime

class Car(db.Model):
    __tablename__ = 'car'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
