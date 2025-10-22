from datetime import datetime
import os
from flask import Blueprint, abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from app import db
from app.models import IncidentReport, Project, ProjectTask, ProjectUserRole
from flask import request
from app.models import ProjectProgress, ProgressPhoto, DailyChecklist, ChecklistCompletion
from app.forms import IncidentReportForm, ProgressForm, ChecklistForm
from werkzeug.utils import secure_filename
from app.models import Comment
from datetime import datetime
import pytz

# Crear blueprint para 'miembro'
miembro_bp = Blueprint('miembro', __name__, url_prefix='/miembro')

@miembro_bp.route('/')
@login_required
def miembro_dashboard():
    # Solo permitir a usuarios con rol 'miembro'
    if not any(role.name == 'miembro' for role in current_user.roles):
        flash('Acceso denegado. Solo los miembros pueden ver este panel.', 'danger')
        return redirect(url_for('main.index'))

    return redirect(url_for('miembro.tareas_asignadas'))


@miembro_bp.route('/tareas')
@login_required
def tareas_asignadas():
    # Verifica si el usuario tiene rol de miembro
    if not any(role.name == 'miembro' for role in current_user.roles):
        flash('Acceso denegado. Solo los miembros pueden ver sus tareas.', 'danger')
        return redirect(url_for('main.index'))

    # Obtener tareas asignadas al usuario
    tareas = (
        db.session.query(ProjectTask)
        .join(Project)
        .filter(ProjectTask.responsible_user_id == current_user.id)
        .order_by(ProjectTask.start_date.desc())
        .all()
    )

    # Agrupar tareas por proyecto
    tareas_por_proyecto = {}
    for tarea in tareas:
        tareas_por_proyecto.setdefault(tarea.project.name, []).append(tarea)

    return render_template('miembro/tareas.html', tareas_por_proyecto=tareas_por_proyecto)

# Ruta para actualizar el estado de una tarea
@miembro_bp.route('/tareas/actualizar/<int:tarea_id>', methods=['POST'])
@login_required
def actualizar_estado_tarea(tarea_id):
    tarea = ProjectTask.query.get_or_404(tarea_id)
    if tarea.responsible_user_id != current_user.id:
        flash('No tienes permiso para modificar esta tarea.', 'danger')
        return redirect(url_for('miembro.tareas_asignadas'))

    nuevo_estado = request.form.get('estado')

    if nuevo_estado not in ['pendiente', 'en progreso', 'completada']:
        flash('Estado no válido.', 'warning')
        return redirect(url_for('miembro.tareas_asignadas'))

    tarea.status = nuevo_estado
    db.session.commit()

    flash(f'El estado de la tarea "{tarea.name}" se actualizó a "{nuevo_estado}".', 'success')
    return redirect(url_for('miembro.tareas_asignadas'))


# Ruta para ver avances de un proyecto
@miembro_bp.route('/proyecto/<int:project_id>/avances')
@login_required
def listar_avances(project_id):
    from flask_login import current_user

    project = Project.query.get_or_404(project_id)

    # Mostrar solo los avances del usuario actual
    avances = ProjectProgress.query.filter_by(
        project_id=project_id,
        user_id=current_user.id
    ).order_by(ProjectProgress.date.desc()).all()

    return render_template(
        "miembro/avances.html",
        project=project,
        avances=avances
    )

from datetime import datetime
import pytz

# Ruta para registrar avance
@miembro_bp.route('/proyecto/<int:project_id>/avances/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_avance(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProgressForm()

    if form.validate_on_submit():
        # ⏰ Obtener hora de Chile
        chile_tz = pytz.timezone("America/Santiago")
        ahora_chile = datetime.now(chile_tz)

        # Crear registro del avance
        avance = ProjectProgress(
            project_id=project.id,
            user_id=current_user.id,
            description=form.description.data,
            date=ahora_chile   # 👈 aquí se guarda la hora local
        )
        db.session.add(avance)
        db.session.commit()

        # Guardar fotos
        if form.photos.data:
            upload_folder = os.path.join(current_app.root_path, "static/uploads")
            os.makedirs(upload_folder, exist_ok=True)

            for photo in form.photos.data:
                if photo:
                    filename = secure_filename(photo.filename)
                    file_path = os.path.join(upload_folder, filename)
                    photo.save(file_path)

                    foto = ProgressPhoto(
                        progress_id=avance.id,
                        file_path=f"uploads/{filename}"
                    )
                    db.session.add(foto)

        db.session.commit()
        flash("Avance registrado correctamente ✅", "success")
        return redirect(url_for('miembro.listar_avances', project_id=project.id))

    return render_template("miembro/nuevo_avance.html", form=form, project=project)


# Ruta para ver y completar checklist diaria
@miembro_bp.route('/proyecto/<int:project_id>/checklist', methods=['GET', 'POST'])
@login_required
def checklist(project_id):
    project = Project.query.get_or_404(project_id)
    items = DailyChecklist.query.filter_by(project_id=project.id, is_active=True).all()
    form = ChecklistForm()

    from datetime import date
    today = date.today()

    # Crear un diccionario con el estado de cada ítem para este usuario
    completions = {
        c.checklist_id: c.completed
        for c in ChecklistCompletion.query.filter_by(
            user_id=current_user.id,
            date=today
        ).all()
    }

    if request.method == 'POST':
        for item in items:
            checked = request.form.get(f"item_{item.id}") == "on"

            completion = ChecklistCompletion.query.filter_by(
                checklist_id=item.id,
                user_id=current_user.id,
                date=today
            ).first()

            if completion:
                completion.completed = checked
            else:
                completion = ChecklistCompletion(
                    checklist_id=item.id,
                    user_id=current_user.id,
                    date=today,
                    completed=checked
                )
                db.session.add(completion)

        db.session.commit()
        flash("Checklist guardado ✅", "success")
        return redirect(url_for('miembro.checklist', project_id=project.id))

    return render_template("miembro/checklist.html", form=form, project=project, items=items, completions=completions)


# Ruta para ver proyectos del ROL miembro
@miembro_bp.route('/proyectos')
@login_required
def mis_proyectos():
    proyectos = (
        Project.query
        .join(ProjectUserRole)
        .filter(ProjectUserRole.user_id == current_user.id)
        .all()
    )

    return render_template("miembro/mis_proyectos.html", proyectos=proyectos)

# Ruta para ver y agregar comentarios a una tarea
@miembro_bp.route('/tarea/<int:tarea_id>/comentarios', methods=['GET', 'POST'])
@login_required
def comentarios_tarea(tarea_id):
    tarea = ProjectTask.query.get_or_404(tarea_id)

    if tarea.responsible_user_id != current_user.id:
        abort(403, description="No tienes permiso para acceder a esta tarea.")

    # Envío de nuevo comentario
    if request.method == 'POST':
        content = request.form.get('content')
        if not content or not content.strip():
            flash("El comentario no puede estar vacío.", "warning")
            return redirect(url_for('miembro.comentarios_tarea', tarea_id=tarea.id))

        chile_tz = pytz.timezone("America/Santiago")
        ahora_chile = datetime.now(chile_tz)

        nuevo_comentario = Comment(
            content=content.strip(),
            user_id=current_user.id,
            project_id=tarea.project_id,
            task_id=tarea.id,
            created_at=ahora_chile
        )
        db.session.add(nuevo_comentario)
        db.session.commit()

        flash("Comentario agregado correctamente.", "success")
        return redirect(url_for('miembro.comentarios_tarea', tarea_id=tarea.id))

    comentarios = Comment.query.filter_by(task_id=tarea.id).order_by(Comment.created_at.asc()).all()

    if request.args.get("ajax"):
        return render_template('miembro/_comentarios_partial.html', comentarios=comentarios)

    return render_template('miembro/tarea_comentarios.html', tarea=tarea, comentarios=comentarios)

# Configuración para subir archivos
UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "incidencias")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "xls", "xlsx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para crear nueva incidencia
@miembro_bp.route('/incidencias/nueva/<int:project_id>', methods=['GET', 'POST'])
@login_required
def nueva_incidencia(project_id):
    proyecto = Project.query.get_or_404(project_id)
    form = IncidentReportForm()
    form.project_id.data = project_id

    if form.validate_on_submit():
        # Archivos
        photo_file = form.photo.data
        attachment_file = form.attachment.data
        photo_path, attachment_path = None, None

        upload_dir = os.path.join(current_app.root_path, "static", "uploads", "incidencias")
        os.makedirs(upload_dir, exist_ok=True)

        if photo_file and allowed_file(photo_file.filename):
            filename = secure_filename(photo_file.filename)
            abs_path = os.path.join(upload_dir, filename)
            photo_file.save(abs_path)
            photo_path = f"uploads/incidencias/{filename}" 

        if attachment_file and allowed_file(attachment_file.filename):
            filename = secure_filename(attachment_file.filename)
            abs_path = os.path.join(upload_dir, filename)
            attachment_file.save(abs_path)
            attachment_path = f"uploads/incidencias/{filename}"

        incidencia = IncidentReport(
            reporter_id=current_user.id,
            reporter_name=form.reporter_name.data,
            reporter_role=form.reporter_role.data,
            reporter_email=form.reporter_email.data,
            reporter_phone=form.reporter_phone.data,
            project_id=project_id,
            location=form.location.data,
            incident_datetime=form.incident_datetime.data,
            incident_type=form.incident_type.data,
            description=form.description.data,
            environment_conditions=form.environment_conditions.data,
            affected_persons=form.affected_persons.data,
            injuries=form.injuries.data,
            witnesses=form.witnesses.data,
            equipment_involved=form.equipment_involved.data,
            property_damage=form.property_damage.data,
            corrective_actions=form.corrective_actions.data,
            emergency_services_contacted=form.emergency_services_contacted.data,
            emergency_details=form.emergency_details.data,
            root_cause=form.root_cause.data,
            preventive_actions=form.preventive_actions.data,
            photo_path=photo_path,
            attachment_path=attachment_path,
            evidence_comment=form.evidence_comment.data
        )

        db.session.add(incidencia)
        db.session.commit()
        flash("✅ Incidencia registrada exitosamente", "success")
        return redirect(url_for("miembro.ver_incidencias_proyecto", project_id=project_id))

    if form.errors:
        print("❌ Errores del formulario:", form.errors)

    return render_template("miembro/nueva_incidencia.html", form=form, proyecto=proyecto)

# Ruta para ver incidencias reportadas por el miembro
@miembro_bp.route('/incidencias')
@login_required
def incidencias_home():
    proyectos = (
        Project.query
        .join(ProjectUserRole)
        .filter(ProjectUserRole.user_id == current_user.id)
        .all()
    )

    return render_template("miembro/incidencias.html", proyectos=proyectos)

# Ruta para ver incidencias de un proyecto específico
@miembro_bp.route('/incidencias/ver/<int:project_id>')
@login_required
def ver_incidencias_proyecto(project_id):
    proyecto = Project.query.get_or_404(project_id)
    incidencias = (
        IncidentReport.query
        .filter_by(project_id=project_id, reporter_id=current_user.id)
        .order_by(IncidentReport.report_datetime.desc())
        .all()
    )

    return render_template(
        'miembro/ver_incidencias.html',
        incidencias=incidencias,
        proyecto=proyecto
    )

# Ruta para ver detalle de una incidencia
@miembro_bp.route('/incidencias/detalle/<int:incident_id>')
@login_required
def ver_incidencia_detalle(incident_id):
    incidencia = IncidentReport.query.get_or_404(incident_id)
    proyecto = incidencia.project
    return render_template(
        "miembro/ver_incidencia_detalle.html",
        incidencia=incidencia,
        proyecto=proyecto
    )

