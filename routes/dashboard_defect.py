from flask import Blueprint, jsonify
from models.car import Car
from models.sensor_result import SensorResult
from models.camera_result import CameraResult
from extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

bp = dashboard_bp

def calc_rate(defect_count, total_count):
    """불량률 계산"""
    if total_count == 0:
        return 0
    return round((defect_count / total_count) * 100, 2)


@bp.get('/summary')
def get_dashboard_summary():
    """대시보드 통계 조회"""
    # 전체 자동차 수
    total_count = Car.query.count()

    # =========== 센서 검사 통계 ===========
    
    # 센서 불량 차량 수 (중복 제거)
    sensor_defect_car_count = (
        db.session.query(func.count(func.distinct(SensorResult.car_id)))
        .filter(SensorResult.result == 'defect')
        .scalar()
    ) or 0

    # 센서 불량 로그 수 (전체)
    sensor_defect_log_count = (
        SensorResult.query.filter(SensorResult.result == 'defect').count()
    ) or 0

    # 센서 장치별 통계
    sensor_by_device_raw = (
        db.session.query(
            SensorResult.device,
            func.count(func.distinct(SensorResult.car_id)),  # 장치별 불량 차량 수
            func.count(SensorResult.id)  # 장치별 불량 로그 수
        )
        .filter(SensorResult.result == 'defect')
        .group_by(SensorResult.device)
        .all()
    )

    sensor_by_device = {}
    for device, car_count, log_count in sensor_by_device_raw:
        sensor_by_device[device] = {
            "defect_car_count": car_count,
            "car_defect_rate": calc_rate(car_count, sensor_defect_car_count),  # 센서 불량 차량 중 비율
            "defect_log_count": log_count,
            "log_defect_rate": calc_rate(log_count, sensor_defect_log_count)  # 센서 불량 로그 중 비율
        }

    # =========== 외관 검사 통계 ===========
    
    # 외관 불량 차량 수 (중복 제거)
    camera_defect_car_count = (
        db.session.query(func.count(func.distinct(CameraResult.car_id)))
        .filter(CameraResult.result == 'defect')
        .scalar()
    ) or 0

    # 외관 불량 로그 수
    camera_defect_log_count = (
        CameraResult.query.filter(CameraResult.result == 'defect').count()
    ) or 0

    # =========== 전체 통계 ===========
    
    # 전체 불량 차량 수 (센서 ∪ 외관 - 합집합)
    overall_defect_car_count = (
        db.session.query(func.count(func.distinct(Car.id)))
        .filter(
            Car.id.in_(
                db.session.query(SensorResult.car_id)
                .filter(SensorResult.result == 'defect')
                .union(
                    db.session.query(CameraResult.car_id)
                    .filter(CameraResult.result == 'defect')
                )
            )
        )
        .scalar()
    ) or 0

    # 전체 불량 로그 수 (센서 + 외관)
    overall_defect_log_count = sensor_defect_log_count + camera_defect_log_count

    # 전체 정상 차량 수 (전체 - 불량)
    overall_normal_car_count = total_count - overall_defect_car_count

    response = {
        "total_count": total_count,
        
        "overall": {
            "normal_car_count": overall_normal_car_count,
            "defect_car_count": overall_defect_car_count,
            "defect_rate": calc_rate(overall_defect_car_count, total_count),
            "defect_log_count": overall_defect_log_count
        },
        
        "sensor": {
            "defect_car_count": sensor_defect_car_count,
            "defect_rate": calc_rate(sensor_defect_car_count, total_count),
            "defect_log_count": sensor_defect_log_count,
            "by_device": sensor_by_device
        },

        "camera": {
            "defect_car_count": camera_defect_car_count,
            "defect_rate": calc_rate(camera_defect_car_count, total_count),
            "defect_log_count": camera_defect_log_count
        }
    }

    return jsonify(response)
