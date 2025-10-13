from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import AdminUser
from app import db, login_manager
from app.forms import LoginForm

admin = Blueprint("admin", __name__, template_folder="templates")

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

@admin.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("✅ Bienvenido al panel de administración", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("❌ Usuario o contraseña incorrectos", "danger")
    return render_template("login.html", form=form)

@admin.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin.html")

@admin.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("admin.login"))
