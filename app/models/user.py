from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    
    def set_password(self, password):
        self.contrasena = generate_password_hash(password)
        
    def check_password(self, password):
        return self.contrasena == password

