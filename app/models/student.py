from app import db

# Debería verse algo como esto
class Student(db.Model):
    __tablename__ = 'ESTUDIANTES'
    cedula = db.Column('cedula', db.String, primary_key=True)
    nombre = db.Column('nombre', db.String)  # Nota el espacio al principio
    apellido = db.Column('apellido', db.String)  # Nota el espacio
    carrera = db.Column('carrera', db.String)  # Nota el espacio
    seccion = db.Column('seccion', db.String)  # Nota el espacio
    turno = db.Column('turno', db.String)  # Nota el espacio
    periodo = db.Column('periodo', db.String)  # Nota el espacio
    nucleo = db.Column('nucleo', db.String)  # Nota el espacio