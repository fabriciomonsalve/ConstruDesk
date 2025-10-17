import datetime
from flask_wtf import FlaskForm
from wtforms import DateTimeField, IntegerField, MultipleFileField, SelectField, StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional, Length
from datetime import datetime  # Cambiar esta línea



class ContactoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=20)])
    empresa = StringField("Empresa", validators=[Optional(), Length(max=120)])
    mensaje = TextAreaField("Mensaje", validators=[DataRequired()])

class LoginForm(FlaskForm):
    identifier = StringField("Usuario o Correo Electrónico", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Clave", validators=[DataRequired(), Length(min=4, max=128)])

class CreateUserForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=255)])
    rol = SelectField('Rol', coerce=int, validators=[DataRequired()])


class ProjectForm(FlaskForm):
    name = StringField('Nombre del Proyecto', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    start_date = DateTimeField('Fecha de Inicio', default=datetime.utcnow, format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    end_date = DateTimeField('Fecha de Fin', format='%Y-%m-%d %H:%M:%S', validators=[Optional()])
    progress = IntegerField('Progreso (%)', default=0, validators=[Optional()])
    status = SelectField('Estado', choices=[('activo', 'Activo'), ('suspendido', 'Suspendido'), ('finalizado', 'Finalizado')], default='activo')
    admin_comment = TextAreaField('Comentario del Administrador', validators=[Optional()])
    submit = SubmitField('Guardar Proyecto')


class AssignUserForm(FlaskForm):
    user_id = SelectField('Seleccionar Usuario', coerce=int, validators=[DataRequired()])
    project_id = SelectField('Seleccionar Proyecto', coerce=int, validators=[DataRequired()])




# Formulario de avance
class ProgressForm(FlaskForm):
    description = TextAreaField("Descripción del avance", validators=[DataRequired()])
    photos = MultipleFileField("Subir fotos (opcional)")
    submit = SubmitField("Guardar avance")

# Formulario checklist (dinámico)
class ChecklistForm(FlaskForm):
    submit = SubmitField("Guardar checklist")


class NuevoChecklistItemForm(FlaskForm):
    item_text = StringField('Texto del ítem', validators=[DataRequired(), Length(min=3, max=200)])
    submit = SubmitField('Agregar ítem')