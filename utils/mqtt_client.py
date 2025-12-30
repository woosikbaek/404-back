import paho.mqtt.client as mqtt
import os
import json
import base64
from datetime import datetime
from dotenv import load_dotenv

from models.car import Car
from models.sensor_result import SensorResult
from models.camera_result import CameraResult
from models.defect_image import DefectImage
from extensions import db
from sqlalchemy import func

# .env 파일 불러오기
load_dotenv()

broker = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))

TOPIC_CAMERA01_RESULT = os.getenv("MQTT_TOPIC_CAMERA01_RESULT")
TOPIC_SENSOR_RESULT = os.getenv("MQTT_TOPIC_SENSOR_RESULT")
TOPIC_SENSOR_CONTROL = os.getenv("MQTT_TOPIC_SENSOR_CONTROL", "sensor/control")
TOPIC_ULT01 = os.getenv("MQTT_TOPIC_ULT01")
TOPIC_ULT02 = os.getenv("MQTT_TOPIC_ULT02")
TOPIC_ULT03 = os.getenv("MQTT_TOPIC_ULT03")

client = mqtt.Client()

_flask_app = None
_socketio = None
current_car_id = None


# ==================== 통계 계산 함수 ====================


def calc_rate(defect_count, total_count):
    """불량률 계산"""
    if total_count == 0:
        return 0
    return round((defect_count / total_count) * 100, 2)


def calculate_stats():
    """전체 통계 데이터 계산"""

    # 전체 자동차 수
    total_count = Car.query.count()

    # ===== 센서 통계 =====
    # 센서 불량 차량 수 (중복 제거)
    sensor_defect_car_count = (
        db.session.query(func.count(func.distinct(SensorResult.car_id)))
        .filter(SensorResult.result == "DEFECT")
        .scalar()
    ) or 0

    # 센서 불량 로그 수 (전체)
    sensor_defect_log_count = (
        SensorResult.query.filter(SensorResult.result == "DEFECT").count()
    ) or 0

    # 센서 장치별 통계
    sensor_by_device_raw = (
        db.session.query(
            SensorResult.device,
            func.count(func.distinct(SensorResult.car_id)),  # 장치별 불량 차량 수
            func.count(SensorResult.id),  # 장치별 불량 로그 수
        )
        .filter(SensorResult.result == "DEFECT")
        .group_by(SensorResult.device)
        .all()
    )

    sensor_by_device = {}
    for device, car_count, log_count in sensor_by_device_raw:
        sensor_by_device[device] = {
            "defect_car_count": car_count,
            "car_defect_rate": calc_rate(
                car_count, sensor_defect_car_count
            ),  # 센서 불량 차량 중 비율
            "defect_log_count": log_count,
            "log_defect_rate": calc_rate(
                log_count, sensor_defect_log_count
            ),  # 센서 불량 로그 중 비율
        }

    # ===== 외관 통계 =====
    # 외관 불량 차량 수 (중복 제거)
    camera_defect_car_count = (
        db.session.query(func.count(func.distinct(CameraResult.car_id)))
        .filter(CameraResult.result == "DEFECT")
        .scalar()
    ) or 0

    # 외관 불량 로그 수
    camera_defect_log_count = (
        CameraResult.query.filter(CameraResult.result == "DEFECT").count()
    ) or 0

    # ===== 전체 통계 =====
    # 전체 불량 차량 수 (센서 ∪ 외관 - 합집합)
    overall_defect_car_count = (
        db.session.query(func.count(func.distinct(Car.id)))
        .filter(
            Car.id.in_(
                db.session.query(SensorResult.car_id)
                .filter(SensorResult.result == "DEFECT")
                .union(
                    db.session.query(CameraResult.car_id).filter(
                        CameraResult.result == "DEFECT"
                    )
                )
            )
        )
        .scalar()
    ) or 0

    # 전체 불량 로그 수 (센서 + 외관)
    overall_defect_log_count = sensor_defect_log_count + camera_defect_log_count

    # 전체 정상 차량 수 (전체 - 불량)
    overall_normal_car_count = total_count - overall_defect_car_count

    return {
        "total_count": total_count,
        "overall": {
            "normal_car_count": overall_normal_car_count,
            "defect_car_count": overall_defect_car_count,
            "defect_rate": calc_rate(overall_defect_car_count, total_count),
            "defect_log_count": overall_defect_log_count,
        },
        "sensor": {
            "defect_car_count": sensor_defect_car_count,
            "defect_rate": calc_rate(sensor_defect_car_count, total_count),
            "defect_log_count": sensor_defect_log_count,
            "by_device": sensor_by_device,
        },
        "camera": {
            "defect_car_count": camera_defect_car_count,
            "defect_rate": calc_rate(camera_defect_car_count, total_count),
            "defect_log_count": camera_defect_log_count,
        },
    }


def emit_stats_update():
    """통계 업데이트 WebSocket 발송"""
    if _socketio:
        stats = calculate_stats()
        _socketio.emit("stats_update", stats)
        print(f"[WebSocket] 통계 업데이트 발송")


def emit_sensor_defect(sensor_data):
    """센서 불량 WebSocket 이벤트 발송"""
    if _socketio:
        _socketio.emit("sensor_defect", sensor_data)
        emit_stats_update()
        print(f"[WebSocket] 센서 불량 발송: {sensor_data}")


def emit_camera_defect(camera_data):
    """카메라 불량 WebSocket 이벤트 발송"""
    if _socketio:
        _socketio.emit("camera_defect", camera_data)
        emit_stats_update()
        print(f"[WebSocket] 카메라 불량 발송: {camera_data}")


# MQTT 연결 성공
def on_connect(client, userdata, flags, rc):
    print("MQTT 연결됨")
    client.subscribe(TOPIC_CAMERA01_RESULT)
    client.subscribe(TOPIC_SENSOR_RESULT)
    client.subscribe(TOPIC_ULT01)
    client.subscribe(TOPIC_ULT02)
    client.subscribe(TOPIC_ULT03)
    print(
        f"[MQTT] 구독 토픽: {TOPIC_ULT01}, {TOPIC_ULT02}, {TOPIC_ULT03} {TOPIC_SENSOR_RESULT}, {TOPIC_CAMERA01_RESULT}"
    )


# 센서 결과 저장
def save_sensor_result(data):
    global current_car_id

    device = data["device"].upper()
    result = data["result"].upper()  # ok / defect

    # 안전장치: 차량이 생성되지 않았으면 저장 안 함
    if current_car_id is None:
        print(f"[경고] current_car_id가 None입니다. {device} 저장 안 함")
        return

    sensor = SensorResult(car_id=current_car_id, device=device, result=result)
    db.session.add(sensor)
    db.session.commit()

    # 🔔 WebSocket 이벤트 발송
    sensor_data = {
        "car_id": sensor.car_id,
        "device": sensor.device,
        "result": sensor.result,
        "created_at": sensor.created_at.isoformat(),
    }

    if device == "WHEEL":
        if sensor.result == "OK":
            emit_drive_ok()

    if sensor.result == "DEFECT":
        emit_sensor_defect(sensor_data)
    else:
        emit_stats_update()



# 외관 이미지 저장
def save_camera_result_image(base64_str):
    save_dir = "uploads/camera01"
    os.makedirs(save_dir, exist_ok=True)

    filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".jpg"
    file_path = os.path.join(save_dir, filename)

    # Robustly strip base64 header if present
    if base64_str.startswith("data:image"):
        try:
            base64_str = base64_str.split(",", 1)[1]
        except Exception as e:
            print(f"[에러] base64 헤더 분리 실패: {e}")
            return None

    try:
        image_bytes = base64.b64decode(base64_str)
    except Exception as e:
        print(f"[에러] base64 디코딩 실패: {e}")
        return None

    try:
        with open(file_path, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        print(f"[에러] 이미지 파일 저장 실패: {e}")
        return None

    return file_path


# 외관 결과 저장
def save_camera_result(data):
    global current_car_id

    car = Car()
    db.session.add(car)
    db.session.commit()
    current_car_id = car.id

    if current_car_id is None:
        print("[경고] save_camera_result: current_car_id가 None입니다.")
        return

    # 검사 결과 저장 (이미지 없음)
    camera = CameraResult(car_id=current_car_id, result=data["result"].upper())
    db.session.add(camera)
    db.session.commit()  # camera.id 필요

    # 이미지 여러 장 저장
    image = data.get("detection", {}).get("result_image", [])
    image_urls = []

    for base64_img in image:
        image_path = save_camera_result_image(base64_img)
        if image_path:
            defect_image = DefectImage(
                camera_result_id=camera.id,
                car_id = camera.car_id,
                image_path=image_path
            )
            db.session.add(defect_image)

            image_urls.append("/" + image_path.replace("\\", "/"))

    db.session.commit()

    # WebSocket 이벤트 (images 배열)
    camera_data = {
        "car_id": camera.car_id,
        "result": camera.result,
        "images": image_urls,
        "created_at": camera.created_at.isoformat(),
    }

    if camera.result == "DEFECT":
        emit_camera_defect(camera_data)
    else:
        emit_case_ok()
        emit_stats_update()

def emit_sensor_start():
    if _socketio:
        _socketio.emit('progress', {'start': 'ok', 'car_id': current_car_id})

def emit_sensor_end():
    if _socketio:
        _socketio.emit('progress', {'sensor': 'ok'})

def emit_case_ok():
    if _socketio:
        _socketio.emit('progress', {'case': 'ok'})

def emit_drive_ok():
    if _socketio:
        _socketio.emit('progress', {'drive': 'ok'})

# 메시지 수신
def on_message(client, userdata, msg):
    with _flask_app.app_context():
        try:
            # sensor/control 토픽: 기능검사 시작 신호
            if msg.topic == TOPIC_ULT01:
                data = msg.payload.decode()
                print(f"[ult01] 수신: {data}")

                if data.lower() == "true":
                    start_car_inspection()
                return

            # 검사 결과 토픽
            data = json.loads(msg.payload.decode())

            if msg.topic == TOPIC_SENSOR_RESULT:
                save_sensor_result(data)
                print(f"[센서 결과] {data}")

            elif msg.topic == TOPIC_CAMERA01_RESULT:
                # MQTT payload는 bytes → str → dict
                if isinstance(msg.payload, bytes):
                    try:
                        data = json.loads(msg.payload.decode())
                    except Exception as e:
                        print(f"[에러] JSON 파싱 실패: {e}")
                        return

                # 'result'가 없으면 경고
                if 'result' not in data:
                    print("[경고] result 키 없음:", data)
                    return

                save_camera_result(data)
                print(f"[카메라 결과] {data}")

            elif msg.topic == TOPIC_ULT01:
                if data == True:
                    emit_sensor_start()
            
            elif msg.topic == TOPIC_ULT02:
                if data == True:
                    emit_sensor_end()

        except Exception as e:
            print(f"[에러] on_message 처리 실패: {e}")


def start_car_inspection():
    """기능검사 시작 - 새로운 차량 생성"""
    global current_car_id

    car = Car()
    db.session.add(car)
    db.session.commit()
    current_car_id = car.id

    print(f"[기능검사 시작] Car ID: {current_car_id}")

    # WebSocket 알림
    if _socketio:
        _socketio.emit("car_added", {"car_id": current_car_id})
        # 통계 업데이트 발송 (차량 수 증가 반영)
        emit_stats_update()


client.on_connect = on_connect
client.on_message = on_message


def mqtt_connect(app, socketio):
    global _flask_app, _socketio
    _flask_app = app
    _socketio = socketio

    client.connect(broker, port)
    client.loop_start()


def publish(topic, message):
    client.publish(topic, message)