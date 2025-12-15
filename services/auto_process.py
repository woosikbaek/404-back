import json
from utils.mqtt_client import publish, DEVICE_TOPICS
from routes.socket_events import send_device_update
from datetime import datetime
from models.device_status import device_status

# 점검 장치 순서
CHECK_ORDER = ["led", "buzzer", "wheel", "sensor"]

def power_on():
    """
    전원 켜기 시뮬레이션 (대시보드 표시)
    """
    print("전원 켜짐, 대시보드 표시 시작")
    # 필요하면 MQTT 요청도 여기서 보낼 수 있음

def start_auto_process():
    """
    자동 점검 시작.
    MQTT 응답 + AI 불량검출 결과 이벤트에서
    다음 장치 점검으로 이동
    """
    device_status.auto_index = 0  # 처음 장치부터 시작
    check_next_device()

def check_next_device():
    """
    순서대로 다음 장치 점검 요청
    """
    if device_status.auto_index >= len(CHECK_ORDER):
        print("모든 장치 점검 완료")
        return

    device = CHECK_ORDER[device_status.auto_index]
    topic = DEVICE_TOPICS[device][0]
    publish(topic, json.dumps({device: "on"}))
    print(f"{device} 켜기 요청 발송")

def emergency_stop():
    """
    모든 장치 긴급 정지
    """
    for device, (topic, _) in DEVICE_TOPICS.items():
        if device == "belt":
            # 컨베이어벨트는 OFF
            publish(topic, json.dumps({device: "off"}))
        else:
            # 점검 장치도 OFF
            publish(topic, json.dumps({device: "off"}))
    print("모든 장치 긴급 정지 발송")
