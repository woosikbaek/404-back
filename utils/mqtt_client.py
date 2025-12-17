import paho.mqtt.client as mqtt
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# MQTT 접속 정보
broker = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))

# 토픽들
TOPIC_CAMERA_RESULT = os.getenv("MQTT_TOPIC_FIRST_CAMERA_RESULT")   # camera01/result
TOPIC_SENSOR_RESULT = os.getenv("MQTT_TOPIC_SENSOR_RESULT")         # sensor/result
TOPIC_POWER = os.getenv("MQTT_TOPIC_POWER")                  # power/control
TOPIC_CAPTURE = os.getenv("MQTT_TOPIC_CAPTURE") # camera/capture

# MQTT 클라이언트 생성
client = mqtt.Client()


# MQTT 연결 성공 시 실행되는 함수
def on_connect(client, userdata, flags, rc):
    print("MQTT 연결됨")

    # 결과 받는 토픽 2개 구독
    client.subscribe(TOPIC_CAMERA_RESULT)
    client.subscribe(TOPIC_SENSOR_RESULT)


# 메시지 수신 시 실행되는 함수
def on_message(client, userdata, msg):
    topic = msg.topic                      # 어떤 토픽인지
    payload = msg.payload.decode()         # 받은 데이터 (문자열)

    # JSON 문자열 → 파이썬 dict
    data = json.loads(payload)

    if topic == TOPIC_CAMERA_RESULT:
        print(data)
    elif topic == TOPIC_SENSOR_RESULT:
        print(data)


# 콜백 함수 등록
client.on_connect = on_connect
client.on_message = on_message

# MQTT 연결 시작
def mqtt_connect():
    client.connect(broker, port)
    client.loop_start()


def publish(topic, message):
    client.publish(topic, message)