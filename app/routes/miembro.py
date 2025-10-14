from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Project, ProjectTask
from flask import request

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


@miembro_bp.route('/tareas/actualizar/<int:tarea_id>', methods=['POST'])
@login_required
def actualizar_estado_tarea(tarea_id):
    """Permite al miembro cambiar el estado de su tarea."""
    tarea = ProjectTask.query.get_or_404(tarea_id)

    # Verifica que el usuario sea el responsable de la tarea
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
