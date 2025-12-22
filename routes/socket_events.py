from app import socketio
from models.car import Car
from models.sensor_result import SensorResult
from models.camera_result import CameraResult
from extensions import db
from sqlalchemy import func

# 클라이언트 연결되었을 때
@socketio.on('connect')
def handle_connect():
  print("클라이언트 연결됨")
  # 초기 데이터 전송
  send_initial_stats()

# 클라이언트 끊김
@socketio.on('disconnect')
def handle_disconnect():
  print("클라이언트 끊김")

# ==================== 통계 계산 함수 ====================

def calc_rate(defect_count, total_count):
    """불량률 계산"""
    if total_count == 0:
        return 0
    return round((defect_count / total_count) * 100, 2)


def calculate_stats():
  """전체 통계 데이터 계산"""
  
  # 전체 자동차 수
  total_count = Car.query.count()
  
  # ===== 센서 통계 =====
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
  
  # ===== 외관 통계 =====
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
  
  # ===== 전체 통계 =====
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
  
  return {
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

# ==================== 실시간 업데이트 함수 ====================

def send_initial_stats():
  """프론트 처음 접속 시 초기 통계 전송"""
  stats = calculate_stats()
  socketio.emit('stats', stats)
  print(f"[Socket] 초기 통계 전송")

def send_stats_update():
  """통계 업데이트 실시간 전송"""
  stats = calculate_stats()
  socketio.emit('stats_update', stats)
  print(f"[Socket] 통계 업데이트 전송")

def send_sensor_defect(sensor_data):
  """센서 불량 감지"""
  socketio.emit('sensor_defect', sensor_data)
  send_stats_update()
  print(f"[Socket] 센서 불량 발송: {sensor_data}")

def send_camera_defect(camera_data):
  """카메라 불량 감지"""
  socketio.emit('camera_defect', camera_data)
  send_stats_update()
  print(f"[Socket] 카메라 불량 발송: {camera_data}")