from extensions import db
from datetime import datetime

class CameraResult(db.Model):
    __tablename__ = 'camera_result'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    result = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    defect_images = db.relationship(
        'DefectImage',
        backref='camera_result',
        lazy=True,
        cascade='all, delete-orphan'
    )