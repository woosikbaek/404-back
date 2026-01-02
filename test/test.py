import json
import paho.mqtt.client as mqtt
import os
import time
from dotenv import load_dotenv

load_dotenv()

broker = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))
TOPIC_CAMERA01_RESULT = os.getenv("MQTT_TOPIC_CAMERA01_RESULT")

client = mqtt.Client()

def on_publish(client, userdata, mid):
    print(f"✅ 메시지 전송 완료! (ID: {mid})")

client.on_publish = on_publish
client.connect(broker, port, 60)
client.loop_start() # 백그라운드 루프 시작

try:
    with open("test_images.json", "r") as f:
        data = json.load(f)
    
    payload = json.dumps(data)
    print(f"데이터 크기: {len(payload) / 1024:.2f} KB") # 크기 확인용

    # 발행 (QoS 1로 설정하여 도달 보장)
    result = client.publish(TOPIC_CAMERA01_RESULT, payload, qos=1)
    
    # 전송될 때까지 최대 10초 대기
    result.wait_for_publish(timeout=10)
    
    # 전송 후 백엔드 처리 시간을 위해 2초만 더 대기
    time.sleep(2)

except Exception as e:
    print(f"❌ 에러 발생: {e}")

finally:
    client.loop_stop()
    client.disconnect()
    print("연결 종료")