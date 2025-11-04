import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"

    # Ruta para almacenar los archivos
    UPLOAD_FOLDER = os.path.join(app.root_path, 'app', 'static', 'uploads')  # Ruta correcta
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar el tamaño de archivo a 16MB


    from .main import main
    from app.routes.admin import admin_bp
    from app.routes.lector import lector_bp 
    from app.routes.invitado import invitado_bp  
    from app.routes.editor import editor_bp 
    from app.routes.miembro import miembro_bp 
    from app.routes.auth import auth_bp
    from app.routes.mensajes import mensajero_bp    



    app.register_blueprint(main)

    app.register_blueprint(admin_bp)
    app.register_blueprint(lector_bp)
    app.register_blueprint(invitado_bp) 
    app.register_blueprint(editor_bp) 
    app.register_blueprint(miembro_bp)  
    app.register_blueprint(auth_bp)
    app.register_blueprint(mensajero_bp)
    


    with app.app_context():
        from .models import AdminUser, ContactMessage  # importa aquí
        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id))

    return app
