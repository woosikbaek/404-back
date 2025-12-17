from flask import Blueprint, jsonify
from services.mqtt_service import power_on, start_camera_capture, power_off

front_bp = Blueprint(
    "front", __name__
    )
bp = front_bp

@bp.post("/power/on")
def all_power_on():
    power_on()
    return jsonify({"result": "전원 켜짐"})

@bp.post("/power/off")
def all_power_off():
    power_off()
    return jsonify({"result": "전원 꺼짐"})

@bp.post("/camera/capture")
def test_camera():
    start_camera_capture()
    return jsonify({"ok": True})
