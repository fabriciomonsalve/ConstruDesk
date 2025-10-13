from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import ContactoForm
from .models import db, ContactMessage

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
    # Muestra la landing con el formulario
    form = ContactoForm()
    return render_template("index.html", form=form)


@main.route("/contacto", methods=["POST"])
def contacto():
    form = ContactoForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            nombre=form.nombre.data,
            email=form.email.data,
            telefono=form.telefono.data,
            empresa=form.empresa.data,
            mensaje=form.mensaje.data,
        )
        db.session.add(msg)
        db.session.commit()
        flash("✅ Tu mensaje fue enviado con éxito", "success")
        return redirect(url_for("main.index") + "#contacto")

    # 👇 esto imprime los errores de validación
    print(form.errors)  
    flash("⚠️ Hay errores en el formulario", "danger")
    return render_template("index.html", form=form), 400



@main.route("/ser")
def services():
    form = ContactoForm()
    return render_template("servicios.html", form=form)

