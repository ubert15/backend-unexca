import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from ...models.carnet import Carnet
from ...models.student import Student
from ...models.user import User, db

class CarnetGenerator:
    """
    Servicio para la generación de carnets estudiantiles.
    """
    def __init__(self, app=None):
        self.app = app
        
        # Definir rutas relativas a la raíz de la aplicación
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.app_root = os.path.abspath(os.path.join(self.base_dir, "..", ".."))
        
        # Definir rutas de recursos
        self.fondo = os.path.join(self.app_root, "assets", "card", "carnet.png")
        self.fuente_bold = os.path.join(self.app_root, "assets", "fonts", "Poppins-Bold.ttf")
        self.fuente_regular = os.path.join(self.app_root, "assets", "fonts", "Poppins-Regular.ttf")
        
        # Carpeta para guardar carnets generados
        self.carnets_dir = os.path.join(self.app_root, "assets", "carnets")
        os.makedirs(self.carnets_dir, exist_ok=True)
        
        # Configuraciones de posición
        self.tam_foto = (230, 260)
        self.pos_foto = (180, 324)
        self.pos_nombre = (200, 600)
        self.pos_ci = (200, 640)
        self.pos_carrera = (200, 670)
        self.pos_rol = (140, 920)
        self.pos_vence = (30, 870)
    
    def generar_carnet(self, cedula, foto_path=None):
        """
        Generar un carnet para un estudiante basado en su cédula.
        """
        try:
            # Buscar estudiante en la base de datos
            estudiante = Student.query.filter_by(cedula=cedula).first()
            if not estudiante:
                raise ValueError(f"No se encontró estudiante con cédula {cedula}")
                
            # Buscar información de usuario para determinar el rol
            usuario = User.query.filter_by(cedula=cedula).first()
            if not usuario:
                rol = "ESTUDIANTE"  # Por defecto
            else:
                rol = usuario.rol
                
            # Crear formato de nombre completo
            nombre_completo = f"{estudiante.nombre} {estudiante.apellido}".strip()
            
            # Si no se proporciona foto, usar una por defecto
            if not foto_path or not os.path.exists(foto_path):
                foto_path = os.path.join(self.app_root, "assets", "default_profile.png")
                
            # Fecha de vencimiento (1 año a partir de hoy)
            fecha_vence = datetime.now().replace(year=datetime.now().year + 1).strftime("%d/%m/%Y")
            
            # Generar la imagen del carnet
            ruta_imagen = self._generar_imagen(
                nombre=nombre_completo,
                cedula=estudiante.cedula,
                foto=foto_path,
                rol=rol,
                carrera=estudiante.carrera,
                vence=fecha_vence
            )
            
            # Registrar el carnet en la base de datos
            carnet = Carnet(cedula=estudiante.cedula)
            carnet.ruta_imagen = ruta_imagen  # Actualizar con la ruta real generada
            db.session.add(carnet)
            db.session.commit()
            
            return carnet
        except Exception as e:
            # Registrar excepción para depuración
            print(f"Error en generación de carnet: {str(e)}")
            # Re-lanzar excepción para que sea manejada por la ruta
            raise
        
    def _generar_imagen(self, nombre, cedula, foto, rol, carrera, vence):
        """
        Genera la imagen del carnet con todos los datos proporcionados.
        Versión simplificada sin esquinas redondeadas.
        """
        try:
            # Verificar que existan los archivos necesarios
            if not os.path.exists(self.fondo):
                raise FileNotFoundError(f"No se encontró la imagen de fondo en {self.fondo}")
            
            if not os.path.exists(self.fuente_bold):
                raise FileNotFoundError(f"No se encontró la fuente bold en {self.fuente_bold}")
                
            if not os.path.exists(self.fuente_regular):
                raise FileNotFoundError(f"No se encontró la fuente regular en {self.fuente_regular}")
            
            # Se abren las imágenes de fondo y la foto del usuario
            try:
                # Verificar tipos de las posiciones
                print(f"self.pos_foto: {self.pos_foto}, tipo: {type(self.pos_foto)}")
                print(f"self.pos_nombre: {self.pos_nombre}, tipo: {type(self.pos_nombre)}")
                print(f"self.pos_ci: {self.pos_ci}, tipo: {type(self.pos_ci)}")
                print(f"self.pos_carrera: {self.pos_carrera}, tipo: {type(self.pos_carrera)}")
                print(f"self.pos_rol: {self.pos_rol}, tipo: {type(self.pos_rol)}")
                print(f"self.pos_vence: {self.pos_vence}, tipo: {type(self.pos_vence)}")
                            
                img = Image.open(self.fondo).convert('RGBA')
                print(f"Fondo cargado: {self.fondo}")
            except Exception as e:
                print(f"Error al cargar el fondo: {str(e)}")
                raise
            
            try:
                foto_img = Image.open(foto).convert('RGBA')
                print(f"Foto cargado: {foto}")
            except Exception as e:
                print(f"Error al cargar la foto: {str(e)}")
                raise

            # Redimensionar la foto para que encaje correctamente
            foto_img = foto_img.resize(self.tam_foto)
            
            # VERSIÓN SIMPLIFICADA: Sin esquinas redondeadas
            # Simplemente pegamos la foto directamente
            img.paste(foto_img, self.pos_foto)

            try:
                # Se definen las fuentes y tamaños
                fnt_nombre = ImageFont.truetype(self.fuente_bold, 30)
                fnt_ci = ImageFont.truetype(self.fuente_regular, 25)
                fnt_carrera = ImageFont.truetype(self.fuente_bold, 26)
                fnt_rol = ImageFont.truetype(self.fuente_bold, 50)
                fnt_vence = ImageFont.truetype(self.fuente_regular, 22)
            except Exception as e:
                print(f"Error al cargar las fuentes: {str(e)}")
                raise

            # Se prepara el área de dibujo
            draw = ImageDraw.Draw(img)

            # Se dibujan los textos en sus posiciones ajustadas
            fill_nombre = (7, 41, 115, 255)
            print(f"fill_nombre: {fill_nombre}, tipo: {type(fill_nombre)}")
            draw.text(self.pos_nombre, nombre, font=fnt_nombre, fill=fill_nombre)

            fill_ci = (7, 41, 115, 255)
            print(f"fill_ci: {fill_ci}, tipo: {type(fill_ci)}")
            draw.text(self.pos_ci, str(cedula), font=fnt_ci, fill=fill_ci)

            rol_text = str(rol).upper()  # Forzar a cadena y convertir a mayúsculas
            print(f"rol_text después de upper: {rol_text}, tipo: {type(rol_text)}")
            fill_rol = (255, 255, 255, 255)
            print(f"fill_rol: {fill_rol}, tipo: {type(fill_rol)}")
            draw.text(self.pos_rol, rol_text, font=fnt_rol, fill=fill_rol)

            fill_carrera = (7, 41, 115, 255)
            print(f"fill_carrera: {fill_carrera}, tipo: {type(fill_carrera)}")
            draw.text(self.pos_carrera, carrera.upper(), font=fnt_carrera, fill=fill_carrera)

            fill_vence = (0, 0, 0, 255)
            print(f"fill_vence: {fill_vence}, tipo: {type(fill_vence)}")
            draw.text(self.pos_vence, vence, font=fnt_vence, fill=fill_vence)

            # Se guarda la imagen final con la cédula formateada correctamente
            ruta_destino = os.path.join(self.carnets_dir, f"{cedula}.png")
            
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
            
            # Guardar imagen
            img.save(ruta_destino)
            print(f"Carnet guardado en: {ruta_destino}")
            
            # Retornar la ruta relativa para almacenar en la base de datos
            return ruta_destino
        except Exception as e:
            import traceback
            print(f"Error generando imagen del carnet: {str(e)}")
            traceback.print_exc()  # Imprime el traceback completo
            raise