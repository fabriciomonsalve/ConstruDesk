from flask import abort, request
from app.models import Project
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import ProjectUserRole, ProjectTask, ProjectDocument, ProjectProgress
from datetime import datetime    
import os
from werkzeug.utils import secure_filename
from app import db
from flask import flash, redirect, url_for

# Crear blueprint para 'invitado'
invitado_bp = Blueprint('invitado', __name__, url_prefix='/invitado')

@invitado_bp.route('/dashboard')
@login_required
def dashboard_invitado():
    """Panel del invitado: lista todos los proyectos asignados con métricas básicas."""

    relaciones = ProjectUserRole.query.filter_by(user_id=current_user.id).all()
    relaciones_validas = [
        rel for rel in relaciones if rel.role.name.lower() in ('invitado', 'guest')
    ]

    # Si no tiene proyectos asignados
    if not relaciones_validas:
        return render_template('invitado/dashboard_invitado.html', no_projects=True)

    # Crear lista con métricas por proyecto
    proyectos_data = []
    for rel in relaciones_validas:
        proyecto = rel.project

        tareas_total = ProjectTask.query.filter_by(project_id=proyecto.id).count()
        tareas_completadas = ProjectTask.query.filter_by(project_id=proyecto.id, status='completada').count()
        tareas_pendientes = tareas_total - tareas_completadas

        progreso = proyecto.progress or 0
        documentos_total = ProjectDocument.query.filter_by(project_id=proyecto.id).count()
        ultimo_avance = ProjectProgress.query.filter_by(project_id=proyecto.id).order_by(ProjectProgress.date.desc()).first()

        proyectos_data.append({
            "proyecto": proyecto,
            "progreso": progreso,
            "tareas_total": tareas_total,
            "tareas_completadas": tareas_completadas,
            "tareas_pendientes": tareas_pendientes,
            "documentos_total": documentos_total,
            "ultimo_avance": ultimo_avance.date.strftime('%d/%m/%Y') if ultimo_avance else "—"
        })

    return render_template(
        'invitado/dashboard_invitado.html',
        no_projects=False,
        proyectos_data=proyectos_data
    )

@invitado_bp.route('/proyecto/<int:project_id>')
@login_required
def ver_proyecto(project_id):
    """Detalle del proyecto específico al que el invitado tiene acceso."""
    rel = ProjectUserRole.query.filter_by(user_id=current_user.id, project_id=project_id).first()

    # Seguridad: si el usuario no está asignado como invitado a este proyecto, mostramos mensaje
    if not rel or rel.role.name.lower() not in ('invitado', 'guest'):
        return render_template('invitado/dashboard_invitado.html', no_projects=True)

    proyecto = rel.project

    # Consultas a la BD
    tareas_total = ProjectTask.query.filter_by(project_id=proyecto.id).count()
    tareas_completadas = ProjectTask.query.filter_by(project_id=proyecto.id, status='completada').count()
    tareas_pendientes = tareas_total - tareas_completadas

    progreso = proyecto.progress or 0
    documentos_total = ProjectDocument.query.filter_by(project_id=proyecto.id).count()
    documentos = ProjectDocument.query.filter_by(project_id=proyecto.id).order_by(ProjectDocument.upload_date.desc()).limit(5).all()

    ultimos_avances = ProjectProgress.query.filter_by(project_id=proyecto.id).order_by(ProjectProgress.date.desc()).limit(10).all()

    # Gráfico de progreso en el tiempo
    avances = ProjectProgress.query.filter_by(project_id=proyecto.id).order_by(ProjectProgress.date.asc()).all()
    fechas = [a.date.strftime('%d/%m') for a in avances]
    progreso_por_fecha = list(range(1, len(fechas) + 1))

    return render_template(
        'invitado/detalle_proyecto.html',
        proyecto=proyecto,
        progreso=progreso,
        tareas_total=tareas_total,
        tareas_completadas=tareas_completadas,
        tareas_pendientes=tareas_pendientes,
        documentos_total=documentos_total,
        documentos=documentos,
        ultimos_avances=ultimos_avances,
        fechas=fechas,
        progreso_por_fecha=progreso_por_fecha
    )





# Ruta para subir un documento
@invitado_bp.route('/project/<int:project_id>/upload_document', methods=['GET', 'POST'])
@login_required
def upload_document(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        file = request.files.get('file')
        description = request.form.get('description')

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('app','static', 'uploads', filename) 

            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

            # Crear el nuevo registro en la base de datos para el archivo subido
            document = ProjectDocument(
                project_id=project.id,
                user_id=current_user.id,
                file_path=file_path,  
                file_name=filename, 
                description=description
            )
            db.session.add(document)
            db.session.commit()

            flash('Documento cargado correctamente.', 'success')
            return redirect(url_for('invitado.view_documents', project_id=project.id)) 

    return render_template('invitado/upload_document.html', project=project)

# Ruta para ver los documentos del proyecto
@invitado_bp.route('/project/<int:project_id>/documents', methods=['GET', 'POST'])
@login_required
def view_documents(project_id):
    project = Project.query.get_or_404(project_id)

    documents = ProjectDocument.query.filter_by(project_id=project.id).all()

    if request.method == 'POST':
        file = request.files.get('file')
        description = request.form.get('description')

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', str(project.id), filename)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

            document = ProjectDocument(
                project_id=project.id,
                user_id=current_user.id,
                file_path=file_path,
                file_name=filename,
                description=description
            )
            db.session.add(document)
            db.session.commit()

            flash('Documento cargado correctamente.', 'success')
            return redirect(url_for('invitado.view_documents', project_id=project.id))

    return render_template('invitado/view_documents.html', project=project, documents=documents)

# Ruta de inicio para el editor
@invitado_bp.route('/documentos')
@login_required
def documentos_invitado():
    projects = Project.query.all()  
    return render_template('invitado/documentos.html', projects=projects)



# Listar avances de todos los proyectos
@invitado_bp.route('/avances/proyectos')
@login_required
def listar_proyectos():
    if not current_user.has_role("invitado"):
        abort(403)

    proyectos = Project.query.all() 
    return render_template("invitado/avance_obra.html", proyectos=proyectos)


# Listar avances de un proyecto específico
@invitado_bp.route('/avances/proyecto/<int:project_id>')
@login_required
def listar_avances(project_id):
    if not current_user.has_role("invitado"):
        abort(403)

    project = Project.query.get_or_404(project_id)
    avances = ProjectProgress.query.filter_by(project_id=project.id).order_by(ProjectProgress.date.desc()).all()
    return render_template("invitado/avances.html", project=project, avances=avances)
