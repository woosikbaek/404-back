from flask import Blueprint, jsonify, request, send_from_directory
from models.camera_result import CameraResult
from extensions import db
from routes.socket_events import send_camera_defect, send_stats_update
import os

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
      'created_at': r.created_at.isoformat()
    })

  return jsonify(data)

@bp.get('/defects')
def get_defects():
    # 외관불량
    camera_results = CameraResult.query.filter(
        CameraResult.result == 'DEFECT'
    ).order_by(CameraResult.id.desc()).all()

    data = []
    for r in camera_results:
        # 이미지 여러 장 가져오기
        images = [ '/' + img.image_path.replace('\\','/') 
                   for img in getattr(r, 'defect_images', []) ]  # relationship 필요

        data.append({
            'car_id': r.car_id,
            'type': '외관불량',
            'result': r.result,
            'images': images,
            'created_at': r.created_at.isoformat()
        })

    # 센서불량
    from models.sensor_result import SensorResult
    sensor_results = SensorResult.query.filter(
        SensorResult.result == 'DEFECT'
    ).order_by(SensorResult.id.desc()).all()

    for s in sensor_results:
        data.append({
            'car_id': s.car_id,
            'type': f'{s.device} 센서불량',
            'result': s.result,
            'images': [],  # 이미지 없음
            'created_at': s.created_at.isoformat()
        })

    # 최신 순 정렬
    data.sort(key=lambda x: x['created_at'], reverse=True)

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

@bp.route('/uploads/camera01/<filename>')
def serve_image(filename):
   return send_from_directory('uploads/camera01', filename)

