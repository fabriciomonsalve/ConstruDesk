from asyncio import Task
from datetime import datetime
import os
from flask import Blueprint, app, current_app, flash, redirect, render_template, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.models import AdminUser, Project, ProjectDocument, ProjectTask, ProjectUserRole
from flask import request

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'dwg', 'dxf', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

editor_bp = Blueprint('editor', __name__, url_prefix='/editor')

# Ruta de inicio para el editor
@editor_bp.route('/')
@login_required
def editor_dashboard():
    projects = Project.query.all()  
    return render_template('editor/editor_dashboard.html', projects=projects)

# Ruta para subir un documento
@editor_bp.route('/project/<int:project_id>/upload_document', methods=['GET', 'POST'])
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
            return redirect(url_for('editor.view_documents', project_id=project.id)) 

    return render_template('editor/upload_document.html', project=project)

# Ruta para ver los documentos del proyecto
@editor_bp.route('/project/<int:project_id>/documents', methods=['GET', 'POST'])
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
            return redirect(url_for('editor.view_documents', project_id=project.id))

    return render_template('editor/view_documents.html', project=project, documents=documents)

# Ruta para editar el documento
@editor_bp.route('/project/<int:project_id>/document/<int:document_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(project_id, document_id):
    document = ProjectDocument.query.get_or_404(document_id)
    project = Project.query.get_or_404(project_id)  
    if request.method == 'POST':
        
        description = request.form.get('description')
        file = request.files.get('file')

        # Actualizar solo la descripción si no se sube un nuevo archivo
        document.description = description

        # Si se sube un nuevo archivo, reemplazar el anterior
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('app','static', 'uploads', filename)  
            
            file.save(file_path)
                          
            document.file_path = file_path
            document.file_name = filename

        # Guardar los cambios en la base de datos
        db.session.commit()

        flash('Documento actualizado correctamente.', 'success')
        return redirect(url_for('editor.view_documents', project_id=project_id)) 

    return render_template('editor/edit_document.html', document=document, project=project)

# Ruta para descargar el documento
@editor_bp.route('/project/<int:project_id>/documents/<document_id>/download')
@login_required
def download_document(project_id, document_id):
    document = ProjectDocument.query.get_or_404(document_id)

    if document.project_id != project_id:
        flash('No tienes permiso para descargar este documento.', 'danger')
        return redirect(url_for('editor.view_documents', project_id=project_id))

    # Recupera el nombre del archivo desde el path guardado
    filename = os.path.basename(document.file_path) 

    # Verificar si el archivo realmente existe
    file_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
    if not os.path.exists(file_path):
        flash('El archivo no existe.', 'danger')
        return redirect(url_for('editor.view_documents', project_id=project_id))

    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'uploads'), filename, as_attachment=True
    )

# Ruta para ver las tareas del proyecto
@editor_bp.route('/project/<int:project_id>/tasks')
@login_required
def view_tasks(project_id):
    project = Project.query.get_or_404(project_id)

    # Obtener las tareas del proyecto
    tasks = ProjectTask.query.filter_by(project_id=project.id).all()

    return render_template('editor/view_tasks.html', project=project, tasks=tasks)


# Ruta para crear una nueva tarea
@editor_bp.route('/project/<int:project_id>/create_task', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)

    # Obtener los usuarios asignados al proyecto
    users_in_project = AdminUser.query.join(ProjectUserRole).filter(ProjectUserRole.project_id == project_id).all()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')  
        end_date = request.form.get('end_date') 
        responsible_user_id = request.form.get('responsible_user') 
        status = request.form.get('status', 'pendiente')  

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None  

        # Crear la nueva tarea
        new_task = ProjectTask(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=status,  
            project_id=project.id,
            responsible_user_id=responsible_user_id 
        )

        db.session.add(new_task)
        db.session.commit()

        flash('Tarea creada exitosamente', 'success')# Redirigir a la li
        return redirect(url_for('editor.view_tasks', project_id=project.id))

    return render_template('editor/create_task.html', project=project, users_in_project=users_in_project)


# Ruta para editar una tarea existente
@editor_bp.route('/project/<int:project_id>/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(project_id, task_id):
    task = ProjectTask.query.get_or_404(task_id)

    # Obtener los usuarios asignados al proyecto
    users_in_project = AdminUser.query.join(ProjectUserRole).filter(ProjectUserRole.project_id == project_id).all()

    if request.method == 'POST':
        task.name = request.form.get('name')
        task.description = request.form.get('description')

        task.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')  
        task.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d') if request.form.get('end_date') else None 

        task.status = request.form.get('status')
        task.responsible_user_id = request.form.get('responsible_user')  # Actualizar el responsable

        db.session.commit()

        flash('Tarea actualizada correctamente.', 'success')
        return redirect(url_for('editor.view_tasks', project_id=project_id))

    return render_template('editor/edit_task.html', task=task, users_in_project=users_in_project)


# Ruta para eliminar una tarea
@editor_bp.route('/project/<int:project_id>/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(project_id, task_id):
    task = ProjectTask.query.get_or_404(task_id)

    # Verificar que la tarea pertenezca al proyecto
    if task.project_id != project_id:
        flash('La tarea no pertenece a este proyecto.', 'danger')
        return redirect(url_for('editor.view_tasks', project_id=project_id))

    # Eliminar la tarea de la base de datos
    db.session.delete(task)
    db.session.commit()

    flash('Tarea eliminada exitosamente.', 'success')
    return redirect(url_for('editor.view_tasks', project_id=project_id))
