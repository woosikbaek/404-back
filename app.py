from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO
import os
from utils.mqtt_client import mqtt_connect

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

def create_app():

  app = Flask(__name__)
  CORS(app)

  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 객체 변경 추적 여부

  db.init_app(app)
  migrate.init_app(app, db)

  socketio.init_app(app, cors_allowed_origins='*')

  from routes import front_bp

  app.register_blueprint (front_bp, url_prefix='/front')

  return app

if __name__ == '__main__':
  app = create_app()

  if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    from utils.mqtt_client import mqtt_connect
    mqtt_connect()

  app.run(host="0.0.0.0", port=5000, debug=True)