# 🚗🔧 404 - back 스마트 팩토리 - 근태 관리 및 채팅 시스템

Flask 기반의 IoT 센서 데이터 수집 및 실시간 모니터링 백엔드 시스템입니다.  
MQTT 프로토콜을 통해 센서 데이터를 수집하고, WebSocket으로 실시간 대시보드에 전송합니다.

# 404found 2차 프로젝트
> **프로젝트의 모든 과정을 담은 상세 시연 영상입니다.** > 이미지 또는 버튼을 클릭하면 유튜브 페이지로 이동합니다.
<div align="center">
  <a href="https://www.youtube.com/watch?v=gPBmVkVSfhc">
    <img src="https://img.youtube.com/vi/gPBmVkVSfhc/maxresdefault.jpg" width="80%" alt="404found 2차 프로젝트 시연영상">
    <br>
    <img src="https://img.shields.io/badge/YouTube-Watch_Video-red?style=for-the-badge&logo=youtube" alt="Youtube Button">
  </a>
</div>

## 📁 프로젝트 구조

```
404-back/
├── app.py                  # Flask 애플리케이션 엔트리포인트
├── extensions.py           # SQLAlchemy, SocketIO 등 확장 초기화
├── models/                 # 데이터베이스 모델
│   ├── car.py             # 차량 정보
│   ├── employee.py        # 직원 정보
│   ├── sensor_result.py   # 센서 검사 결과
│   ├── camera_result.py   # 카메라 검사 결과
│   └── defect_image.py    # 불량 이미지
├──routes/                  # API 라우트
│   ├── auth.py            # JWT 인증
│   ├── sensor.py          # 센서 데이터 API
│   ├── camera.py          # 카메라 데이터 API
│   ├── dashboard_defect.py # 대시보드 통계
│   ├── car.py             # 차량 관리
│   └── socket_events.py   # WebSocket 이벤트 핸들러
├── utils/                  # 유틸리티
│   └── mqtt_client.py     # MQTT 클라이언트 및 메시지 핸들러
└── migrations/             # DB 마이그레이션
```

## 🛠 기술 스택

- **Backend**: Flask 3.1.2
- **ORM**: SQLAlchemy 2.0.45
- **Database**: MySQL (smart_factory)
- **Real-time**: Flask-SocketIO 5.5.1
- **MQTT**: paho-mqtt 2.1.0
- **인증**: Flask-JWT-Extended, bcrypt
- **마이그레이션**: Flask-Migrate 4.1.0

## 🔑 핵심 기능

| 기능 |  설명 |
|------|-------|
| **MQTT 데이터 수집** | 센서 및 카메라 데이터를 MQTT 토픽으로 수집 |
| **데이터 검증** | OK/DEFECT만 허용하여 통계 왜곡 방지 |
| **WebSocket 알림** | 불량 감지 시 실시간 대시보드 업데이트 |
| **통계 계산** | 차량별/장치별 불량률 및 통계 자동 집계 |
| **차량 단위 관리** | car_id 기반으로 모든 검사 결과 그룹화 |

## 🚀 Setup

1. Python 3.8+ 설치 및 가상환경 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

2. 환경 변수 설정 (.env 파일 생성)

```env
DATABASE_URL=mysql+pymysql://root:1234@127.0.0.1:3306/smart_factory
JWT_SECRET_KEY=your-secret-key

MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC_SENSOR_RESULT=sensor/result
MQTT_TOPIC_CAMERA01_RESULT=camera01/result
MQTT_TOPIC_ULT01=sensor/ult01
MQTT_TOPIC_ULT02=sensor/ult02
MQTT_TOPIC_ULT03=sensor/ult03

MAX_DEFECT_IMAGE_COUNT=5
```

3. 데이터베이스 마이그레이션

```bash
flask db upgrade
```

4. 서버 실행 (포트 5000)

```bash
python app.py
```

## 📡 API 엔드포인트

### 인증
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/auth/login` | 로그인 및 JWT 토큰 발급 |

### 센서 데이터
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/sensor/result` | 센서 검사 결과 전체 조회 |
| GET | `/sensor/defects` | 불량 결과만 조회 |
| POST | `/sensor/result` | 센서 결과 수동 추가 (테스트용) |

### 카메라 데이터
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/camera/result` | 카메라 검사 결과 조회 |

### 대시보드
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/dashboard/summary` | 전체 통계 요약 |

### 차량 관리
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/car/all` | 전체 차량 목록 |

## 🔌 WebSocket 이벤트

**연결**: `http://localhost:5000`

### 클라이언트 → 서버
- `connect`: 연결 시 초기 통계 수신

### 서버 → 클라이언트
| 이벤트 | 데이터 | 설명 |
|--------|--------|------|
| `stats` | 통계 객체 | 초기 연결 시 전체 통계 |
| `stats_update` | 통계 객체 | 데이터 변경 시 통계 업데이트 |
| `sensor_defect` | 센서 데이터 | 센서 불량 감지 |
| `camera_defect` | 카메라 데이터 | 카메라 불량 감지 |
| `car_added` | `{car_id}` | 새 차량 검사 시작 |
| `progress` | 진행 상태 | 검사 단계별 진행 상황 |

## 📊 MQTT 토픽 구조

### 구독 토픽 (Subscriptions)
- `sensor/result` - 센서 검사 결과 (LED, WHEEL, BUZZER 등)
- `camera01/result` - 카메라 검사 결과 (AI 불량 판정)
- `sensor/ult01` - 초음파 센서 1 (검사 시작 트리거)
- `sensor/ult02` - 초음파 센서 2
- `sensor/ult03` - 초음파 센서 3

### 메시지 포맷

**센서 결과**:
```json
{
  "device": "LED",
  "result": "OK"  // 또는 "DEFECT"
}
```

**카메라 결과**:
```json
{
  "result": "DEFECT",
  "detection": {
    "result_image": ["base64_encoded_image_1", "base64_encoded_image_2"]
  }
}
```

## 🔐 데이터 검증 로직

**구현 위치**: `utils/mqtt_client.py:185-223`

```python
def save_sensor_result(data):
    device = data["device"].upper()
    result = data["result"].upper()
    
    # 유효한 결과(OK, DEFECT)만 저장
    if result in ['OK', 'DEFECT']:
        sensor = SensorResult(car_id=current_car_id, device=device, result=result)
        db.session.add(sensor)
        db.session.commit()
    else:
        print(f"[경고] {result} 상태는 DB에 저장하지 않습니다.")
```

**검증 효과**:
- 잘못된 MQTT 메시지 (TIMEOUT, ERROR 등) 필터링
- 통계 왜곡 방지
- 데이터 무결성 보장

## 🗄️ 데이터베이스 스키마

### car 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INT | PK, 자동 증가 |
| created_at | DATETIME | 차량 등록 시간 |

### sensor_result 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INT | PK, 자동 증가 |
| car_id | INT | FK, 차량 ID |
| device | VARCHAR(50) | 센서 종류 (LED, WHEEL 등) |
| result | VARCHAR(10) | 검사 결과 (OK, DEFECT) |
| created_at | DATETIME | 검사 시간 |

### camera_result 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INT | PK, 자동 증가 |
| car_id | INT | FK, 차량 ID |
| result | VARCHAR(10) | 검사 결과 (OK, DEFECT) |
| created_at | DATETIME | 검사 시간 |

### defect_image 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INT | PK, 자동 증가 |
| camera_result_id | INT | FK, 카메라 결과 ID |
| car_id | INT | FK, 차량 ID |
| image_path | VARCHAR(255) | 이미지 파일 경로 |

## ⚡ 성능 특징

- **실시간 처리**: MQTT 메시지 수신 즉시 DB 저장 및 WebSocket 전파
- **통계 캐싱**: 30초 TTL로 통계 쿼리 부하 감소
- **비동기 MQTT**: `client.loop_start()`로 논블로킹 처리

## 작성자
404found 2차 프로젝트 - IoT 자동차 품질 검사 시스템

## ERD 구조
- [ERD Cloud](https://www.erdcloud.com/d/rfbhh56TFNjiobguv)