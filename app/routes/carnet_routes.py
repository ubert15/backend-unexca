# routes/carnet_routes.py
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from ..services.card_generator.carnet_service import CarnetGenerator
from ..models.carnet import Carnet
from ..models.user import db
import datetime

carnet_bp = Blueprint('carnet', __name__)

# Configuración para subir archivos
UPLOAD_FOLDER = 'uploads/fotos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@carnet_bp.route('/generar', methods=['POST'])
@jwt_required()
def generar_carnet():
    """
    Endpoint para generar un carnet estudiantil
    """
    # Verificar que la solicitud tenga la parte 'file'
    if 'foto' not in request.files:
        return jsonify({'error': 'No se proporcionó archivo de foto'}), 400
    
    foto = request.files['foto']
    cedula = request.form.get('cedula')
    
    if not cedula:
        return jsonify({'error': 'Se requiere la cédula del estudiante'}), 400
    
    # Si el usuario no seleccionó un archivo
    if foto.filename == '':
        return jsonify({'error': 'No se seleccionó ninguna foto'}), 400
    
    if foto and allowed_file(foto.filename):
        # Guardar la foto con un nombre seguro basado en la cédula
        filename = secure_filename(f"{cedula}_{foto.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(filepath)
        
        try:
            # Generar el carnet
            carnet_generator = CarnetGenerator()
            carnet = carnet_generator.generar_carnet(cedula, filepath)
            
            return jsonify({
                'message': 'Carnet generado exitosamente',
                'carnet_id': carnet.id,
                'ruta_imagen': carnet.ruta_imagen
            }), 201
             
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'Error al generar carnet: {str(e)}'}), 500
    
    return jsonify({'error': 'Formato de archivo no permitido'}), 400

@carnet_bp.route('/descargar/<string:cedula>', methods=['GET'])
@jwt_required()
def descargar_carnet(cedula):
    """
    Endpoint para descargar un carnet generado
    """
    # Buscar el carnet más reciente para esta cédula
    carnet = Carnet.query.filter_by(cedula=cedula).order_by(Carnet.fecha_emision.desc()).first()
    
    if not carnet:
        return jsonify({'error': 'No se encontró carnet para esta cédula'}), 404
    
    # Verificar que el archivo exista
    if not os.path.exists(carnet.ruta_imagen):
        return jsonify({'error': 'El archivo de carnet no existe'}), 404
    
    try:
        # Enviar el archivo al cliente
        return send_file(carnet.ruta_imagen, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Error al descargar carnet: {str(e)}'}), 500

@carnet_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_carnets():
    """
    Endpoint para listar todos los carnets generados para un estudiante
    """
    cedula = request.args.get('cedula')
    
    if not cedula:
        return jsonify({'error': 'Se requiere la cédula del estudiante'}), 400
    
    carnets = Carnet.query.filter_by(cedula=cedula).order_by(Carnet.fecha_emision.desc()).all()
    
    return jsonify({
        'carnets': [
            {
                'id': c.id,
                'fecha_emision': c.fecha_emision.strftime('%Y-%m-%d'),
                'fecha_vencimiento': c.fecha_vencimiento.strftime('%Y-%m-%d'),
                'ruta_imagen': c.ruta_imagen
            } for c in carnets
        ]
    }), 200
    
@carnet_bp.route('/carnet/verificar-vigencia/<string:cedula>', methods=['GET'])
@jwt_required()
def verificar_vigencia(cedula):
    """
    Endpoint para verificar si un estudiante tiene un carnet vigente
    """
    try:
        # Buscar el carnet más reciente del estudiante
        carnet = Carnet.query.filter_by(cedula=cedula).order_by(Carnet.fecha_emision.desc()).first()
        
        if not carnet:
            return jsonify({
                'vigente': False,
                'mensaje': 'No se encontró ningún carnet para este estudiante'
            }), 200
        
        # Verificar si el carnet está vigente (menos de 6 meses desde su emisión)
        hoy = datetime.now()
        fecha_emision = carnet.fecha_emision
        fecha_vencimiento = carnet.fecha_vencimiento
        
        # Calcular la diferencia en meses
        diff_meses = (hoy.year - fecha_emision.year) * 12 + (hoy.month - fecha_emision.month)
        
        # Un carnet es vigente si tiene menos de 6 meses desde su emisión
        vigente = fecha_emision <= 6
        
        # Calcular fecha de vencimiento (6 meses después de la emisión)
        fecha_vencimiento = carnet.fecha_vencimiento if hasattr(carnet, 'fecha_vencimiento') else None
        if not fecha_vencimiento:
            # Si no tiene fecha de vencimiento explícita, calcularla
            fecha_vencimiento = fecha_emision.replace(
                month=fecha_emision.month + 6 if fecha_emision.month <= 6 else (fecha_emision.month + 6) % 12,
                year=fecha_emision.year if fecha_emision.month <= 6 else fecha_emision.year + 1
            )
        
        return jsonify({
            'vigente': vigente,
            'mensaje': 'El carnet está vigente' if vigente else 'El carnet ha expirado',
            'fecha_emision': fecha_emision.strftime('%Y-%m-%d'),
            'fecha_vencimiento': fecha_vencimiento.strftime('%Y-%m-%d'),
            'meses_restantes': 6 - diff_meses if vigente else 0
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error al verificar la vigencia del carnet',
            'detalle': str(e)
        }), 500
    
@carnet_bp.route('/imagen/<int:carnet_id>', methods=['GET'])
def mostrar_imagen_carnet(carnet_id):
    """
    Endpoint para mostrar la imagen del carnet
    """
    # Buscar el carnet por ID
    carnet = Carnet.query.get(carnet_id)
    
    if not carnet:
        return jsonify({'error': 'Carnet no encontrado'}), 404
    
    # Verificar si el archivo existe
    if not os.path.exists(carnet.ruta_imagen):
        # Si la ruta es relativa, convertirla a absoluta
        if not os.path.isabs(carnet.ruta_imagen):
            # Intentar buscar en diferentes ubicaciones
            posibles_rutas = [
                carnet.ruta_imagen,  # Ruta relativa original
                os.path.join('app', carnet.ruta_imagen),  # Desde directorio app
                os.path.join('app/assets', 'carnets', f"{carnet.cedula}.png")  # Directorio específico
            ]
            
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    return send_file(ruta, mimetype='image/png')
        
        # Si no se encuentra en ninguna parte
        return jsonify({'error': 'Imagen del carnet no encontrada'}), 404
    
    # Devolver la imagen
    return send_file(carnet.ruta_imagen, mimetype='image/png')