from extensions import db
from datetime import datetime

class CameraResult(db.Model):
    __tablename__ = 'camera_result'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)

    result = db.Column(db.String(20), nullable=False)   # OK / DEFECT
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)