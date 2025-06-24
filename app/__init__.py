from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .models.user import db
from .routes.auth_routes import auth_bp
from .routes.constancy_routes import constancy_bp
from .routes.carnet_routes import carnet_bp  # Importar el nuevo blueprint
import os

def create_app():
    app = Flask(__name__)
    
    # Calcular ruta base a partir del directorio actual donde está __init__.py
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Construir la ruta absoluta al archivo SQLite; asume que el archivo está en el directorio raíz del proyecto
    db_path = os.path.join(basedir, '..', 'Base de datos UNEXCA.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '7481592630'
    
    CORS(app)
    db.init_app(app)
    JWTManager(app)
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(constancy_bp, url_prefix='/api/constancy')
    app.register_blueprint(carnet_bp, url_prefix='/api/carnet')
    
    return app


app = create_app()
