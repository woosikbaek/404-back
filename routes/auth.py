from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from models.employee import Employee
import bcrypt

auth_bp = Blueprint("auth", __name__)

bp = auth_bp


@bp.post("/login")
def login():
    data = request.get_json()
    print(data)
    employee_number = data.get("employeeNumber")
    password = str(data.get("password"))
    employee = Employee.query.filter_by(employee_number=employee_number).first()
    if employee and bcrypt.checkpw(
        password.encode("utf-8"), employee.password_hash.encode("utf-8")
    ):
        access_token = create_access_token(identity=employee.id)
        refresh_token = create_refresh_token(identity=employee.id)
        return (
            jsonify(
                access_token=access_token,
                refresh_token=refresh_token,
                employee={
                    "id": employee.id,
                    "employeeNumber": employee.employee_number,
                    "name": employee.name,
                    "department": employee.department,
                    "position": employee.position,
                    "phone": employee.phone,
                    "monthly_salary": employee.monthly_salary,
                    "hourly_rate": employee.hourly_rate,
                    "annual_leave": employee.annual_leave,
                    "sick_leave": employee.sick_leave,
                },
            ),
            200,
        )
    return jsonify({"message": "사원번호 또는 비밀번호가 틀렸습니다."}), 401


@bp.post("/refresh")
@jwt_required()
def refresh():
    employee_id = get_jwt_identity()

    new_access_token = create_access_token(identity=employee_id)
    return jsonify(access_token=new_access_token), 200


@bp.get("/info/all")
def get_info_all():
    employee = Employee.query.all()

    result = []
    for emp in employee:
        result.append(
            {
                "id": emp.id,
                "employeeNumber": emp.employee_number,
                "name": emp.name,
                "department": emp.department,
                "position": emp.position,
                "phone": emp.phone,
                "monthly_salary": emp.monthly_salary,
                "hourly_rate": emp.hourly_rate,
                "annual_leave": emp.annual_leave,
                "sick_leave": emp.sick_leave,
            }
        )

    return jsonify(result), 200
