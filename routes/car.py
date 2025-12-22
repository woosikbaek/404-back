from flask import Blueprint, jsonify
from models.sensor_result import SensorResult
from models.camera_result import CameraResult

car_bp = Blueprint('car', __name__)

bp = car_bp

@bp.get('/<int:car_id>')
def get_car_defects(car_id):

    sensor_defects = SensorResult.query.filter(
        SensorResult.car_id == car_id,
        SensorResult.result == 'defect'
    ).order_by(
        SensorResult.created_at.asc()
    ).all()

    camera_defects = CameraResult.query.filter(
        CameraResult.car_id == car_id,
        CameraResult.result == 'defect'
    ).order_by(
        CameraResult.created_at.asc()
    ).all()

    return jsonify({
        "car_id": car_id,
        "sensor_defects": [
            {
                "device": r.device,
                "result": r.result,
                "created_at": r.created_at
            } for r in sensor_defects
        ],
        "camera_defects": [
            {
                "result": r.result,
                "image": r.image_path,
                "created_at": r.created_at
            } for r in camera_defects
        ]
    })

@bp.get('/defects')
def get_all_car_defects():

    car_ids = (
        SensorResult.query
        .with_entities(SensorResult.car_id)
        .distinct()
        .order_by(SensorResult.car_id.asc())
        .all()
    )

    result = []

    for (car_id,) in car_ids:
        sensor_defects = SensorResult.query.filter(
            SensorResult.car_id == car_id,
            SensorResult.result == 'defect'
        ).all()

        camera_defects = CameraResult.query.filter(
            CameraResult.car_id == car_id,
            CameraResult.result == 'defect'
        ).all()

        if not sensor_defects and not camera_defects:
            continue

        result.append({
            "car_id": car_id,
            "sensor_defects": [
                {"device": r.device, "created_at": r.created_at}
                for r in sensor_defects
            ],
            "camera_defects": [
                {"image": r.image_path, "created_at": r.created_at}
                for r in camera_defects
            ]
        })

    return jsonify(result)
