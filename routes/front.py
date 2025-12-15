from flask import Blueprint, jsonify
from services.auto_process import power_on, start_auto_process, emergency_stop
import time

front_bp = Blueprint('front', __name__)
bp = front_bp

# 전원 켜기
@bp.post('/power_on')
def power_on():
    power_on()  # 서비스 호출
    # 대시보드 준비 시간 3초 대기
    time.sleep(3)
    return jsonify({"message": "전원 켜짐, 대시보드 표시 완료"})

# 공정 시작
@bp.post('/start_process')
def start_process_api():
    start_auto_process()  # 점검 장치 자동 점검
    return jsonify({"message": "자동 공정 시작 요청 발송"})

# 긴급 중지
@bp.post('/emergency_stop')
def emergency_stop():
    emergency_stop()  # 모든 장치 정지
    return jsonify({"message": "긴급 정지 요청 발송"})
