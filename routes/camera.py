from flask import Blueprint, jsonify, request
from models.camera_result import CameraResult
from extensions import db
from routes.socket_events import send_camera_defect, send_stats_update

camera_bp = Blueprint('camera', __name__)

bp = camera_bp

@bp.get('/result')
def get_camera_results():
  results = CameraResult.query.order_by(
    CameraResult.id.asc()
  ).all()

  data = []
  for r in results:
    data.append({
      'car_id': r.car_id,
      'device': r.device,
      'result': r.result,
      'image': r.image_path,
      'created_at': r.created_at
    })

  return jsonify(data)

@bp.get('/defects')
def get_camera_defects():
    results = CameraResult.query.filter(
        CameraResult.result == 'NG'
    ).order_by(
        CameraResult.id.asc()
    ).all()

    data = []
    for r in results:
        data.append({
            'car_id': r.car_id,
            'result': r.result,
            'image': r.image_path,
            'created_at': r.created_at
        })

    return jsonify(data)

@bp.post('/result')
def add_camera_result():
  """새로운 카메라 검사 결과 추가"""
  data = request.json
  
  result = CameraResult(
    car_id=data.get('car_id'),
    device=data.get('device', 'CAMERA'),
    result=data.get('result'),
    image_path=data.get('image')
  )
  
  db.session.add(result)
  db.session.commit()
  
  result_data = {
    'car_id': result.car_id,
    'device': result.device,
    'result': result.result,
    'image': result.image_path,
    'created_at': result.created_at.isoformat()
  }
  
  # 불량이면 불량 이벤트 발송, 아니면 통계 업데이트
  if result.result == 'defect':
    send_camera_defect(result_data)
  else:
    send_stats_update()
  
  return jsonify(result_data), 201