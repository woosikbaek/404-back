import json
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

load_dotenv()

# MQTT 브로커 설정
broker = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))
TOPIC_CAMERA01_RESULT = os.getenv("MQTT_TOPIC_CAMERA01_RESULT")

current_car_id = None

# MQTT 클라이언트 생성
client = mqtt.Client()

# 브로커 연결
client.connect(broker, port, 60)

# JSON 파일 읽기
with open("test_images.json", "r") as f:
    data = json.load(f)

# JSON 데이터를 문자열로 변환
payload = json.dumps(data)



# 토픽으로 발행
client.publish(TOPIC_CAMERA01_RESULT, payload)
print(f"[MQTT] {TOPIC_CAMERA01_RESULT} 토픽으로 JSON 발행 완료")

# 연결 종료
client.disconnect()