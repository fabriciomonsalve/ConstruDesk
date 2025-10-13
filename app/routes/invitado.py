from flask import Blueprint, render_template

# Crear blueprint para 'invitado'
invitado_bp = Blueprint('invitado', __name__, url_prefix='/invitado')

# Ruta de inicio para el invitado
@invitado_bp.route('/')
def invitado_dashboard():
    return render_template('invitado/inicio.html')

