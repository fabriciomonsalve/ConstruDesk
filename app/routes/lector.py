from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func, and_
from app.models import Project, ProjectDocument, ProjectProgress, TechnicalReport
from app import db
from flask import request, redirect, url_for, flash
from flask_login import current_user
import os
from werkzeug.utils import secure_filename


# Crear blueprint para 'lector'
lector_bp = Blueprint('lector', __name__, url_prefix='/lector')

# Ruta de inicio para el lector
@lector_bp.route('/')
def lector_documentos():
    projects = Project.query.all()  
    return render_template('lector/inicio.html', projects=projects)



# Ruta para ver los documentos del proyecto
@lector_bp.route('/project/<int:project_id>/documents', methods=['GET', 'POST'])
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
            return redirect(url_for('lector.view_documents', project_id=project.id))

    return render_template('lector/documentos.html', project=project, documents=documents)


# Ruta para el dashboard del lector
@lector_bp.route('/dashboard')
@login_required
def dashboard():
    proyectos = Project.query.filter_by(archived=False).all()

    # Subquery para obtener la FECHA más reciente de avance por proyecto
    sub = (
        db.session.query(
            ProjectProgress.project_id,
            func.max(ProjectProgress.date).label('max_date')
        )
        .group_by(ProjectProgress.project_id)
        .subquery()
    )

    # Avance más reciente por proyecto
    ultimos_avances = (
        db.session.query(ProjectProgress)
        .join(
            sub,
            and_(
                ProjectProgress.project_id == sub.c.project_id,
                ProjectProgress.date == sub.c.max_date,
            ),
        )
        .all()
    )
    ultimo_por_proyecto = {a.project_id: a for a in ultimos_avances}

    # Obtener los 3 avances más recientes por proyecto
    recientes_por_proyecto = {}
    for p in proyectos:
        recent = (
            ProjectProgress.query
            .filter_by(project_id=p.id)
            .order_by(ProjectProgress.date.desc())
            .limit(3)
            .all()
        )
        recientes_por_proyecto[p.id] = recent

    # Construir resumenes para el dashboard
    resumenes = []
    for p in proyectos:
        ultimo = ultimo_por_proyecto.get(p.id)
        resumenes.append({
            "id": p.id,
            "nombre": p.name,
            "estado": p.status.capitalize(),
            "progreso_pct": p.progress or 0,               
            "presupuesto": p.total_budget or 0,           
            "cronograma_file": p.schedule_file,
            "presupuesto_file": p.budget_file,
            "ultimo_avance_desc": ultimo.description if ultimo else "Sin avances",
            "ultimo_avance_fecha": ultimo.date if ultimo else None,
            "recientes": recientes_por_proyecto.get(p.id, []),  
        })

    return render_template('lector/dashboard.html', resumenes=resumenes)