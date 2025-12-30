from extensions import db
from datetime import datetime

class DefectImage(db.Model):
    __tablename__ = 'defect_images'

    id = db.Column(db.Integer, primary_key=True)
    camera_result_id = db.Column(
        db.Integer,
        db.ForeignKey('camera_result.id'),
        nullable=False
    )
    car_id = db.Column(
        db.Integer,
        db.ForeignKey('car.id'),
        nullable = False
    )
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)