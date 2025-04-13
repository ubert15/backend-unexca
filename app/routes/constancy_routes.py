from flask import Blueprint, request, jsonify, Response
from app.services.pdf_generator.constancy_generator import ConstancyPDFGenerator

constancy_bp = Blueprint('constancy', __name__, url_prefix='/api/constancy')

@constancy_bp.route('/generate', methods=['POST'])
def generate_constancy():
    try:
        # Obtener datos del formulario
        data = request.json
        required_fields = ['nombre', 'apellido', 'cedula', 'nucleo', 'periodo', 'carrera', 'seccion', 'turno']
        
        # Verificar que todos los campos requeridos estén presentes
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'El campo {field} es obligatorio'}), 400
        
        # Generar el PDF
        pdf_generator = ConstancyPDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(data)
        
        # Devolver el PDF como respuesta
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': 'inline; filename=constancia.pdf',
                'Content-Type': 'application/pdf'
            }
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500