from app import socketio

# 클라이언트 연결되었을 때
@socketio.on('connect')
def handle_connect():
  print("클라이언트 연결됨")

# 장치 상태 업데이트 전송 함수
def send_device_update(data):
  """
  data 예시:
  {
    'device': 'LED',
    'result': 'OK',
    'stage': 'READY',
    'timestamp': '2025-12-15T12:34:56'
  }
  """
  socketio.emit('device_update', data)