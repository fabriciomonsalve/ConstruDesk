from flask import Blueprint, render_template

# Crear blueprint para 'miembro'
miembro_bp = Blueprint('miembro', __name__, url_prefix='/miembro')

# Ruta de inicio para el miembro
@miembro_bp.route('/')
def miembro_dashboard():
    return render_template('miembro/inicio.html')
