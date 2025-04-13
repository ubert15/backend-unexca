# models/carnet.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from .user import db

class Carnet(db.Model):
    __tablename__ = 'carnets'
    
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), db.ForeignKey('ESTUDIANTES.cedula'), nullable=False)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime)
    ruta_imagen = db.Column(db.String(255))
    
    def __init__(self, cedula, duracion_meses=12):
        self.cedula = cedula
        self.fecha_emision = datetime.utcnow()
        self.fecha_vencimiento = self.fecha_emision + timedelta(days=30*duracion_meses)
        self.ruta_imagen = f"img/carnets/{cedula}.png"