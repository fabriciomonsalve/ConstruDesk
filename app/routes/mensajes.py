from flask import Blueprint
from flask import render_template
from flask_login import login_required
from app.models import ContactMessage

mensajero_bp = Blueprint('mensajero', __name__, url_prefix='/mensajero')

# Ruta para ver los mensajes de contacto
@mensajero_bp.route("/")
@login_required
def dashboard():
    mensajes = ContactMessage.query.order_by(ContactMessage.fecha.desc()).all()
    return render_template("admin/inicio.html", mensajes=mensajes)