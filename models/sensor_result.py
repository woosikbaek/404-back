from extensions import db
from datetime import datetime

class SensorResult(db.Model):
    __tablename__ = 'sensor_result'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)

    device = db.Column(db.String(50), nullable=False)   # LED, BUZZER, SUPERSONIC, WHEEL
    result = db.Column(db.String(10), nullable=False)   # OK / DEFECT
    created_at = db.Column(db.DateTime, default=datetime.now)