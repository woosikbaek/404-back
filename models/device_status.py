class DeviceStatus:
    def __init__(self):
        self.belt = False
        self.led = False
        self.buzzer = False
        self.wheel = False
        self.sensor = False
        self.comm = True
        self.auto_index = 0  # 자동 점검 순서 진행 상태

    def to_dict(self):
        return {
            'belt': self.belt,
            'led': self.led,
            'buzzer': self.buzzer,
            'wheel': self.wheel,
            'sensor': self.sensor,
            'comm': self.comm
        }

device_status = DeviceStatus()