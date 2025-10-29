import datetime
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DateTimeField, DateTimeLocalField, FileField, FloatField, HiddenField, IntegerField, MultipleFileField, SelectField, StringField, PasswordField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, Optional, Length
from datetime import datetime  # Cambiar esta línea
from flask_wtf.file import FileAllowed
from wtforms.validators import NumberRange



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
    # Datos básicos
    name = StringField('Nombre del Proyecto', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])

    # Fechas
    start_date = DateTimeField(
        'Fecha de Inicio',
        default=datetime.utcnow,
        format='%Y-%m-%d %H:%M:%S',
        validators=[DataRequired()]
    )
    end_date = DateTimeField(
        'Fecha de Fin',
        format='%Y-%m-%d %H:%M:%S',
        validators=[Optional()]
    )

    # Estado y progreso
    progress = IntegerField(
        'Progreso (%)',
        default=0,
        validators=[Optional(), NumberRange(min=0, max=100)]
    )
    status = SelectField(
        'Estado',
        choices=[
            ('activo', 'Activo'),
            ('suspendido', 'Suspendido'),
            ('finalizado', 'Finalizado')
        ],
        default='activo'
    )

    admin_comment = TextAreaField('Comentario del Administrador', validators=[Optional()])

    total_budget = StringField('Presupuesto Total (CLP)', validators=[Optional()])

    def validate_total_budget_clp(self, field):
        value = field.data.replace('.', '').replace(',', '').strip()
        if not value.isdigit():
            raise ValidationError('Debe ingresar solo números.')
        field.data = float(value)

    # 📄 Archivo de presupuesto (PDF o Excel)
    budget_file = FileField(
        'Archivo de Presupuesto (PDF o Excel)',
        validators=[Optional(), FileAllowed(['pdf', 'xls', 'xlsx'], 'Formatos permitidos: PDF, XLS, XLSX')]
    )

    # 🗓️ Archivo de cronograma (PDF o Excel)
    schedule_file = FileField(
        'Archivo de Cronograma (PDF o Excel)',
        validators=[Optional(), FileAllowed(['pdf', 'xls', 'xlsx'], 'Formatos permitidos: PDF, XLS, XLSX')]
    )

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



class IncidentReportForm(FlaskForm):
    # Proyecto
    project_id = HiddenField(validators=[DataRequired()])

    # Reporte
    reporter_name = StringField("Nombre del reportante", validators=[DataRequired()])
    reporter_role = StringField("Cargo")
    reporter_email = StringField("Correo", validators=[DataRequired(), Email()])
    reporter_phone = StringField("Teléfono")

    # Proyecto y ubicación
    location = StringField("Ubicación del incidente", validators=[DataRequired()])

    # Detalles
    incident_datetime = DateTimeLocalField("Fecha y hora del incidente",
                                           format='%Y-%m-%dT%H:%M',
                                           validators=[DataRequired()])
    incident_type = SelectField("Tipo de incidente",
                                choices=[
                                    ('lesion', 'Lesión'),
                                    ('cuasi', 'Cuasi accidente'),
                                    ('danio', 'Daño a la propiedad'),
                                    ('seguridad', 'Incidente de seguridad')
                                ],
                                validators=[DataRequired()])
    description = TextAreaField("Descripción", validators=[DataRequired()])
    environment_conditions = TextAreaField("Condiciones ambientales")

    # Personas involucradas
    affected_persons = TextAreaField("Personas afectadas")
    injuries = TextAreaField("Lesiones")
    witnesses = TextAreaField("Testigos")

    # Equipos y daños
    equipment_involved = StringField("Equipo involucrado")
    property_damage = TextAreaField("Daños a la propiedad")

    # Acciones y análisis
    corrective_actions = TextAreaField("Acciones correctivas", validators=[DataRequired()])
    emergency_services_contacted = BooleanField("Se contactó a servicios de emergencia")
    emergency_details = StringField("Detalles de emergencia")
    root_cause = StringField("Causa raíz")
    preventive_actions = TextAreaField("Acciones preventivas")

    # Evidencia
    photo = FileField("Foto")
    attachment = FileField("Documento adjunto")
    evidence_comment = StringField("Comentario sobre evidencia")

    # Submit
    submit = SubmitField("Enviar reporte")





class TechnicalReportForm(FlaskForm):
    # Identificación
    project_id = SelectField('Proyecto', coerce=int, validators=[DataRequired()])
    report_date = DateField('Fecha', validators=[DataRequired()])
    inspector = StringField('Inspector', validators=[DataRequired()])
    period = SelectField('Periodo', choices=[('Semanal', 'Semanal'), ('Quincenal', 'Quincenal'), ('Mensual', 'Mensual')], validators=[DataRequired()])

    # Avance
    general_progress = TextAreaField('Avance General', validators=[Optional()])
    progress_percentage = FloatField('Porcentaje de Avance', validators=[Optional()])
    next_tasks = TextAreaField('Próximas Tareas', validators=[Optional()])

    # Problemas
    problems_found = TextAreaField('Problemas Encontrados', validators=[Optional()])
    actions_taken = TextAreaField('Acciones Tomadas', validators=[Optional()])
    evidence_photos = FileField('Fotos de Evidencia')

    # Recursos
    weather_conditions = StringField('Condiciones Climáticas', validators=[Optional()])
    workers_on_site = IntegerField('Personal en Obra', validators=[Optional()])

    # Resumen
    additional_notes = TextAreaField('Observaciones Adicionales', validators=[Optional()])

    # Adjuntos
    attachment_path = FileField('Documento adjunto')

    submit = SubmitField('Guardar Reporte')