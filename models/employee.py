from extensions import db
from datetime import datetime
import bcrypt

DEFAULT_PASSWORD = 1234
DEFAULT_PASSWORD_HASH = bcrypt.hashpw(str(DEFAULT_PASSWORD).encode('utf-8'), bcrypt.gensalt())

class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(8), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False) # 부서
    position = db.Column(db.String(50), nullable=False) # 직급
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), default=DEFAULT_PASSWORD_HASH, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Employee {self.employee_number}: {self.name}>"
