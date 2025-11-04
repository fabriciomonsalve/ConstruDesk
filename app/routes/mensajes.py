from flask import Blueprint
from flask import render_template
from flask_login import login_required
from app.models import ContactMessage
from app import db
from flask import redirect, url_for, flash

mensajero_bp = Blueprint('mensajero', __name__, url_prefix='/mensajero')

# Ruta para ver los mensajes de contacto
@mensajero_bp.route("/")
@login_required
def dashboard():
    mensajes = ContactMessage.query.order_by(ContactMessage.fecha.desc()).all()
    return render_template("admin/inicio.html", mensajes=mensajes)

# Ruta para marcar un mensaje como leído/no leído
@mensajero_bp.route("/mensaje/<int:id>/toggle", methods=["POST"])
@login_required
def toggle_mensaje(id):
    mensaje = ContactMessage.query.get_or_404(id)
    mensaje.leido = not mensaje.leido
    db.session.commit()
    flash("📩 Estado de mensaje actualizado", "success")  
    return redirect(url_for("mensajero.dashboard"))

# Ruta para eliminar un mensaje
@mensajero_bp.route("/mensaje/<int:id>/delete", methods=["POST"])
@login_required
def delete_mensaje(id):
    mensaje = ContactMessage.query.get_or_404(id)
    db.session.delete(mensaje)
    db.session.commit()
    flash("🗑️ Mensaje eliminado", "info")  
    return redirect(url_for("mensajero.dashboard"))