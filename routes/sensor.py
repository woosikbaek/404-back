from flask import Blueprint, jsonify, request
from models.sensor_result import SensorResult
from extensions import db
from routes.socket_events import send_sensor_defect, send_stats_update

sensor_bp = Blueprint('sensor', __name__)

bp = sensor_bp

@bp.get('/result')
def get_sensor_result():
  results = SensorResult.query.order_by(
    SensorResult.id.asc()
  ).all()

  data = []
  for r in results:
    data.append({
      'car_id': r.car_id,
      'device': r.device,
      'result': r.result,
      'created_at': r.created_at
    })

  return jsonify(data)

@bp.get('/defects')
def get_sensor_defects():
    results = SensorResult.query.filter(
        SensorResult.result == 'defect'
    ).order_by(
        SensorResult.id.asc()
    ).all()

    data = []
    for r in results:
        data.append({
            'car_id': r.car_id,
            'device': r.device,
            'result': r.result,
            'created_at': r.created_at
        })

    return jsonify(data)

@bp.post('/result')
def add_sensor_result():
  """새로운 센서 검사 결과 추가"""
  data = request.json
  
  result = SensorResult(
    car_id=data.get('car_id'),
    device=data.get('device'),
    result=data.get('result')
  )
  
  db.session.add(result)
  db.session.commit()
  
  result_data = {
    'car_id': result.car_id,
    'device': result.device,
    'result': result.result,
    'created_at': result.created_at.isoformat()
  }
  
  # 불량이면 불량 이벤트 발송, 아니면 통계 업데이트
  if result.result == 'defect':
    send_sensor_defect(result_data)
  else:
    send_stats_update()
  
  return jsonify(result_data), 201