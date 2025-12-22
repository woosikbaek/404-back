from flask import Flask
from extensions import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO
import os
from flask_jwt_extended import JWTManager
from datetime import timedelta

jwt = JWTManager()
migrate = Migrate()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'sqlite:///result.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  # 토큰 만료 시간 설정
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # 리프레시 토큰 만료 시간 설정

    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins='*')

    from routes import front_bp, sensor_bp, camera_bp, dashboard_bp, car_bp, auth_bp
    from routes.socket_events import handle_connect, handle_disconnect

    app.register_blueprint(front_bp, url_prefix='/front')
    app.register_blueprint(sensor_bp, url_prefix='/sensor')
    app.register_blueprint(camera_bp, url_prefix='/camera')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(car_bp, url_prefix='/car')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app


if __name__ == '__main__':
    app = create_app()

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        from utils.mqtt_client import mqtt_connect
        mqtt_connect(app, socketio)

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
