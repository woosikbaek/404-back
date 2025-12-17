from utils.mqtt_client import publish

def power_on():
    publish("power/control", '{"command":"POWER_ON"}')
    print("전원 ON 요청 완료")

def power_off():
    publish("power/control", '{"command":"POWER_OFF"}')
    print("전원 OFF 요청 완료")

def start_camera_capture():
    publish("camera/capture", '{"command":"CAMERA_CAPTURE"}')
    print("외관검사 요청 완료")