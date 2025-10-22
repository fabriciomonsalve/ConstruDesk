from datetime import datetime
from tokenize import generate_tokens
from zoneinfo import ZoneInfo
from flask import Blueprint, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
import pytz
from app.forms import AssignUserForm, CreateUserForm, ProjectForm
from app.models import AdminUser, ContactMessage, IncidentReport, Project, ProjectInvitation, ProjectUserRole, Role
from app import db
from werkzeug.security import generate_password_hash
from flask import request

# PDF generation imports
from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Ruta de inicio para el admin

@admin_bp.route('/')
@login_required
def admin_dashboard():
    return render_template('admin/inicio.html')

# Ruta para ver los mensajes de contacto
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    mensajes = ContactMessage.query.order_by(ContactMessage.fecha.desc()).all()
    return render_template("mesajes.html", mensajes=mensajes)

# Ruta para marcar un mensaje como leído/no leído
@admin_bp.route("/mensaje/<int:id>/toggle", methods=["POST"])
@login_required
def toggle_mensaje(id):
    mensaje = ContactMessage.query.get_or_404(id)
    mensaje.leido = not mensaje.leido
    db.session.commit()
    flash("📩 Estado de mensaje actualizado", "success")  
    return redirect(url_for("admin.dashboard"))

# Ruta para eliminar un mensaje
@admin_bp.route("/mensaje/<int:id>/delete", methods=["POST"])
@login_required
def delete_mensaje(id):
    mensaje = ContactMessage.query.get_or_404(id)
    db.session.delete(mensaje)
    db.session.commit()
    flash("🗑️ Mensaje eliminado", "info")  
    return redirect(url_for("admin.dashboard"))

# Ruta para ver todos los usuarios
@admin_bp.route('/usuarios')
@login_required
def usuarios():
    # Obtener todos los usuarios con sus roles
    usuarios = AdminUser.query.all()  
    # Renderizar la plantilla con la lista de usuarios
    return render_template('admin/usuarios.html', usuarios=usuarios)  

# Ruta para crear un nuevo usuario
@admin_bp.route('/admin/crear_usuario', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    # Solo el admin puede crear usuarios
    if not current_user.has_role('admin'):
        flash("No tienes permisos para acceder a esta página.", 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    form = CreateUserForm()

    form.rol.choices = [(role.id, role.name) for role in Role.query.all()]

    if form.validate_on_submit():
        # Verificar si el correo ya existe
        user_exists = AdminUser.query.filter_by(email=form.email.data).first()
        if user_exists:
            flash("El correo electrónico ya está en uso.", 'danger')
            return redirect(url_for('admin.crear_usuario'))
        
        # Crear el usuario
        new_user = AdminUser(
            nombre=form.nombre.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        
        # Asignar rol al usuario
        role = Role.query.get(form.rol.data)
        new_user.roles.append(role)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Usuario creado con éxito!', 'success')
        return redirect(url_for('admin.admin_dashboard'))  

    return render_template('admin/crear_usuario.html', form=form)

# Ruta para crear proyectos
@admin_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            progress=form.progress.data,
            status=form.status.data,
            admin_comment=form.admin_comment.data,
            creator_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Proyecto creado exitosamente.', 'success')
        return redirect(url_for('admin.list_projects'))
    return render_template('admin/crear_proyecto.html', form=form)


# Ruta para listar los proyectos
@admin_bp.route('/list')
@login_required
def list_projects():
    projects = Project.query.filter_by(creator_id=current_user.id).all()
    return render_template('admin/ver_proyecto.html', projects=projects)

# Ruta para editar un proyecto
@admin_bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.creator_id != current_user.id:
        flash('No tienes permiso para editar este proyecto.', 'danger')
        return redirect(url_for('admin.ver_proyecto'))

    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.progress = form.progress.data
        project.status = form.status.data
        project.admin_comment = form.admin_comment.data
        db.session.commit()
        flash('Proyecto actualizado exitosamente.', 'success')
        return redirect(url_for('admin.list_projects'))
    return render_template('admin/editar_proyecto.html', form=form, project=project)

# Ruta para archivar un proyecto
@admin_bp.route('/archive/<int:project_id>', methods=['POST'])
@login_required
def archive_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.creator_id != current_user.id:
        flash('No tienes permiso para archivar este proyecto.', 'danger')
        return redirect(url_for('admin.list_projects'))

    project.archived = True
    db.session.commit()
    flash('Proyecto archivado correctamente.', 'success')
    return redirect(url_for('admin.list_projects'))


# Ruta para desarchivar un proyecto
@admin_bp.route('/unarchive/<int:project_id>', methods=['POST'])
@login_required
def unarchive_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if project.creator_id != current_user.id:
        flash('No tienes permiso para desarchivar este proyecto.', 'danger')
        return redirect(url_for('admin.list_projects'))

    project.archived = False
    db.session.commit()

    flash('Proyecto desarchivado correctamente.', 'success')
    return redirect(url_for('admin.list_projects'))

# Ruta para asignar usuarios a proyectos con roles específicos
@admin_bp.route('/assign_user_to_project', methods=['GET', 'POST'])
@login_required
def assign_user_to_project():
    users = AdminUser.query.all()  
    projects = Project.query.all() 
    roles = Role.query.all() 

    if request.method == 'POST':
        user_id = request.form.get('user_id')  
        project_id = request.form.get('project_id')  
        role_id = request.form.get('role_id') 

        if user_id and project_id and role_id:
            # Buscar el usuario, proyecto y rol en la base de datos
            user = AdminUser.query.get_or_404(user_id)
            project = Project.query.get_or_404(project_id)
            role = Role.query.get_or_404(role_id)

            # Verificar si el usuario ya está asignado a este proyecto
            existing_assignment = ProjectUserRole.query.filter_by(user_id=user.id, project_id=project.id).first()

            if existing_assignment:
                # Si ya está asignado, actualizamos el rol
                existing_assignment.role_id = role.id
                db.session.commit()
                flash('El rol del usuario ha sido actualizado.', 'success')
            else:
                new_assignment = ProjectUserRole(user_id=user.id, project_id=project.id, role_id=role.id)
                db.session.add(new_assignment)
                db.session.commit()
                flash('Usuario asignado correctamente al proyecto.', 'success')

            return redirect(url_for('admin.assign_user_to_project'))

        flash('Por favor, selecciona un usuario, un proyecto y un rol.', 'danger')
        return redirect(url_for('admin.assign_user_to_project'))

    return render_template('admin/usuarios_a_proyectos.html', users=users, projects=projects, roles=roles)

# Ruta para ver los detalles de un proyecto, incluyendo usuarios asignados y sus roles
@admin_bp.route('/project_details/<int:project_id>', methods=['GET'])
@login_required
def project_details(project_id):
    project = Project.query.get_or_404(project_id)
    users_in_project = ProjectUserRole.query.filter_by(project_id=project.id).all()  # Obtener los usuarios asignados
    roles = Role.query.all()  # Obtener todos los roles disponibles
    return render_template('admin/detalles_proyecto.html', project=project, users_in_project=users_in_project, roles=roles)











# Listar todas las incidencias
@admin_bp.route('/incidencias', methods=['GET'])
@login_required
def listar_incidencias():
    estado = request.args.get('estado')
    gravedad = request.args.get('gravedad')

    query = IncidentReport.query.join(Project).order_by(IncidentReport.report_datetime.desc())

    if estado:
        query = query.filter(IncidentReport.status == estado)
    if gravedad:
        query = query.filter(IncidentReport.severity == gravedad)

    incidencias = query.all()
    usuarios = AdminUser.query.all()  

    return render_template('admin/incidencias.html', incidencias=incidencias, usuarios=usuarios, estado=estado, gravedad=gravedad)


# Actualizar una incidencia (estado, gravedad, responsable)
@admin_bp.route('/incidencias/actualizar/<int:incident_id>', methods=['POST'])
@login_required
def actualizar_incidencia(incident_id):
    incidencia = IncidentReport.query.get_or_404(incident_id)

    incidencia.status = request.form.get('status')
    incidencia.severity = request.form.get('severity')
    incidencia.responsible_user_id = request.form.get('responsible_user_id') or None

    # Si la incidencia se marca como cerrada SE registra UNA fecha de cierre
    if incidencia.status == 'cerrado':

        chile_tz = pytz.timezone("America/Santiago")
        ahora_chile = datetime.now(chile_tz)

        incidencia.closure_date = ahora_chile
    else:
        incidencia.closure_date = None

    db.session.commit()
    flash('Incidencia actualizada correctamente.', 'success')
    return redirect(url_for('admin.listar_incidencias'))

# Ver detalles de una incidencia
@admin_bp.route('/incidencias/ver/<int:incident_id>')
@login_required
def ver_incidencia(incident_id):
    incidencia = IncidentReport.query.get_or_404(incident_id)
    proyecto = Project.query.get(incidencia.project_id)
    return render_template('admin/ver_incidencia.html', incidencia=incidencia, proyecto=proyecto)


# Descargar reporte de incidencia en PDF
@admin_bp.route('/incidencias/pdf/<int:incident_id>')
@login_required
def descargar_incidencia_pdf(incident_id):
    incidencia = IncidentReport.query.get_or_404(incident_id)
    proyecto = Project.query.get(incidencia.project_id)

    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph(f"<b>Reporte de Incidencia #{incidencia.id}</b>", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Proyecto:</b> {proyecto.name}", styles['Normal']))
    story.append(Paragraph(f"<b>Fecha de reporte:</b> {incidencia.report_datetime.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Información básica
    data_info = [
        ["Reportado por", incidencia.reporter_name],
        ["Cargo", incidencia.reporter_role or "No especificado"],
        ["Correo", incidencia.reporter_email],
        ["Teléfono", incidencia.reporter_phone or "No especificado"],
        ["Ubicación", incidencia.location],
        ["Tipo de incidente", incidencia.incident_type],
        ["Fecha y hora del incidente", incidencia.incident_datetime.strftime("%d/%m/%Y %H:%M")],
    ]
    table = Table(data_info, colWidths=[6*cm, 10*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Descripción
    story.append(Paragraph("<b>Descripción del incidente:</b>", styles['Heading3']))
    story.append(Paragraph(incidencia.description, styles['Normal']))
    story.append(Spacer(1, 12))

    # Acciones
    story.append(Paragraph("<b>Acciones correctivas inmediatas:</b>", styles['Heading3']))
    story.append(Paragraph(incidencia.corrective_actions or "No registradas", styles['Normal']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Causa raíz:</b>", styles['Heading3']))
    story.append(Paragraph(incidencia.root_cause or "No determinada", styles['Normal']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Acciones preventivas:</b>", styles['Heading3']))
    story.append(Paragraph(incidencia.preventive_actions or "No registradas", styles['Normal']))
    story.append(Spacer(1, 12))

    # Seguimiento
    story.append(Paragraph("<b>Seguimiento</b>", styles['Heading2']))
    responsable = incidencia.responsible_user.nombre if incidencia.responsible_user else "No asignado"
    cierre = incidencia.closure_date.strftime("%d/%m/%Y %H:%M") if incidencia.closure_date else "No cerrada"
    data_seguimiento = [
        ["Gravedad", incidencia.severity.capitalize()],
        ["Estado", incidencia.status.capitalize()],
        ["Responsable asignado", responsable],
        ["Fecha de cierre", cierre],
    ]
    table2 = Table(data_seguimiento, colWidths=[6*cm, 10*cm])
    table2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(table2)

    # Generar PDF
    doc.build(story)
    buffer.seek(0)

    filename = f"incidencia_{incidencia.id}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')








