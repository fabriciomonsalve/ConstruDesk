from flask import Blueprint, render_template

# Crear blueprint para 'lector'
lector_bp = Blueprint('lector', __name__, url_prefix='/lector')

# Ruta de inicio para el lector
@lector_bp.route('/')
def lector_dashboard():
    return render_template('lector/inicio.html')

