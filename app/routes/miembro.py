from datetime import datetime
import os
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Project, ProjectTask, ProjectUserRole
from flask import request
from app.models import ProjectProgress, ProgressPhoto, DailyChecklist, ChecklistCompletion
from app.forms import ProgressForm, ChecklistForm
from werkzeug.utils import secure_filename

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
    project = Project.query.get_or_404(project_id)
    avances = ProjectProgress.query.filter_by(project_id=project_id).order_by(ProjectProgress.date.desc()).all()
    return render_template("miembro/avances.html", project=project, avances=avances)


# Ruta para registrar avance
@miembro_bp.route('/proyecto/<int:project_id>/avances/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_avance(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProgressForm()

    if form.validate_on_submit():
        # Crear registro del avance
        avance = ProjectProgress(
            project_id=project.id,
            user_id=current_user.id,
            description=form.description.data,
            date=datetime.utcnow()
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





@miembro_bp.route('/proyectos')
@login_required
def mis_proyectos():
    # Buscar proyectos en los que el usuario actual tiene un rol
    proyectos = (
        Project.query
        .join(ProjectUserRole)
        .filter(ProjectUserRole.user_id == current_user.id)
        .all()
    )

    return render_template("miembro/mis_proyectos.html", proyectos=proyectos)
