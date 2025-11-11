from flask import redirect, render_template, url_for
from flask_login import login_required, current_user
from . import admin
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import AdminUser, ContactMessage
from app import db, login_manager
from app.forms import LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')



# Función de ayuda para redirigir según rol
def redirect_by_role(user):
    if user.has_role('admin'):
        return redirect(url_for('admin.admin_dashboard'))
    elif user.has_role('editor'):
        return redirect(url_for('editor.editor_dashboard'))
    elif user.has_role('miembro'):
        return redirect(url_for('miembro.miembro_dashboard'))
    elif user.has_role('lector'):
        return redirect(url_for('lector.inicio'))
    elif user.has_role('mensajero'):
        return redirect(url_for('mensajero.dashboard'))
    elif user.has_role('invitado'):
        return redirect(url_for('invitado.dashboard_invitado'))
    else:
        flash("No tienes acceso a ninguna sección", "danger")
        return redirect(url_for('auth.login'))

# Ruta de login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # 👇 Si ya está autenticado, no mostrar login, redirigir directo
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if form.validate_on_submit():
        email_or_username = form.identifier.data
        password = form.password.data

        user = AdminUser.query.filter(
            (AdminUser.email == email_or_username) | 
            (AdminUser.nombre == email_or_username)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect_by_role(user)
        else:
            flash("Correo o contraseña incorrectos", "danger")
    
    return render_template('login.html', form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))

