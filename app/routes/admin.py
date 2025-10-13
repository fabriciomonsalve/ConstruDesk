from tokenize import generate_tokens
from flask import Blueprint, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app.forms import AssignUserForm, CreateUserForm, ProjectForm
from app.models import AdminUser, ContactMessage, Project, ProjectInvitation, ProjectUserRole, Role
from app import db
from werkzeug.security import generate_password_hash
from flask import request

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Ruta de inicio para el admin
@admin_bp.route('/')
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


@admin_bp.route('/project_details/<int:project_id>', methods=['GET'])
@login_required
def project_details(project_id):
    project = Project.query.get_or_404(project_id)
    users_in_project = ProjectUserRole.query.filter_by(project_id=project.id).all()  # Obtener los usuarios asignados
    roles = Role.query.all()  # Obtener todos los roles disponibles
    return render_template('admin/detalles_proyecto.html', project=project, users_in_project=users_in_project, roles=roles)


















