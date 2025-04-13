from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.auth.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('cedula') or not data.get('password'):
        return jsonify({"error": "Cédula y contraseña son requeridos"}), 400
    
    result = AuthService.login(data.get('cedula'), data.get('password'))
    
    if not result:
        return jsonify({"error": "Credenciales incorrectas"}), 401
    
    return jsonify(result), 200

@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def get_profile():
    cedula = get_jwt_identity()

    student_data = AuthService.get_student_data(cedula)
    
    if not student_data:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    
    return jsonify(student_data), 200