from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta
from ...models.user import User
from ...models.student import Student

class AuthService:
    @staticmethod
    def login(cedula, password):
        user = User.query.filter_by(cedula=cedula).first()
        
        if not user or not user.check_password(password):
            return None
        
        # Crear token con la cédula como identidad
        access_token = create_access_token(
            identity=cedula,
            additional_claims={"rol": user.rol},
            expires_delta=timedelta(hours=24)
        )
        
        return {
            "access_token": access_token,
            "rol": user.rol
        }
    
    @staticmethod
    def get_student_data(cedula):
        from sqlalchemy import text
        from app import db  # Ajusta esta importación según tu estructura
        
        # Primero, obtén los nombres de las columnas
        column_query = db.session.execute(text("PRAGMA table_info(ESTUDIANTES)"))
        columns = [row[1] for row in column_query]
        print("Columnas en la tabla ESTUDIANTES:", columns)
        
        query = f"SELECT * FROM ESTUDIANTES WHERE cedula = :cedula"
        result = db.session.execute(text(query), {"cedula": cedula})
        row = result.fetchone()
        print("Columnas en la tabla ESTUDIANTES:", columns)

        
        if row:
            #  diccionario con los nombres de columnas y valores
            student_dict = {}
            for i, col in enumerate(result.keys()):
                student_dict[col.lower()] = row[i]
            return student_dict
        return None