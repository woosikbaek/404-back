import paho.mqtt.client as mqtt
from models.device_status import DeviceStatus
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from services.auto_process import device_status, check_next_device

load_dotenv()

device_status = DeviceStatus()

broker = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))

client = mqtt.Client()

# .env에서 토픽 불러오기
DEVICE_TOPICS = {
    "belt": (os.getenv("MQTT_TOPIC_BELT"), os.getenv("MQTT_TOPIC_BELT") + "/response"),
    "led": (os.getenv("MQTT_TOPIC_LED"), os.getenv("MQTT_TOPIC_LED") + "/response"),
    "buzzer": (os.getenv("MQTT_TOPIC_BUZZER"), os.getenv("MQTT_TOPIC_BUZZER") + "/response"),
    "wheel": (os.getenv("MQTT_TOPIC_WHEEL"), os.getenv("MQTT_TOPIC_WHEEL") + "/response"),
    "sensor": (os.getenv("MQTT_TOPIC_SENSOR"), os.getenv("MQTT_TOPIC_SENSOR") + "/response"),
}

def send_ws_update(data):
    # 함수 안에서 import: 순환 참조 방지
    from routes.socket_events import send_device_update
    send_device_update(data)

def on_connect(client, userdata, flags, rc):
    print("MQTT 연결됨")
    for _, (_, resp_topic) in DEVICE_TOPICS.items():
        client.subscribe(resp_topic)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(f"토픽 {msg.topic} 수신: {payload}")

    for device, (_, resp_topic) in DEVICE_TOPICS.items():
        if msg.topic == resp_topic and device in payload:
            status = payload[device]

            if status in ("ON_OK", "OFF_OK"):
                setattr(device_status, device, status.startswith("ON"))
                send_ws_update({
                    "device": device.upper(),
                    "result": "OK",
                    "stage": "READY",
                    "state": "on" if status.startswith("ON") else "off",
                    "timestamp": datetime.now().isoformat(),
                })

                # 여기서 AI 불량검출 요청 후 결과를 받았다고 가정
                ai_ok = True  # 실제 구현에서는 AI 서버 HTTP 요청 및 응답 필요
                if ai_ok:
                    # 다음 장치 점검으로 이동
                    device_status.auto_index += 1
                    check_next_device()

            elif status in ("ON_FAIL", "OFF_FAIL"):
                setattr(device_status, device, False)
                send_ws_update({
                    "device": device.upper(),
                    "result": "NG",
                    "stage": "READY",
                    "state": "on" if status.startswith("ON") else "off",
                    "timestamp": datetime.now().isoformat(),
                })

client.on_connect = on_connect
client.on_message = on_message

def mqtt_connect():
    client.connect(broker, port)
    client.loop_start()

def publish(topic, message):
    client.publish(topic, message)