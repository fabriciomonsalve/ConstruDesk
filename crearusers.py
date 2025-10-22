from app import create_app, db
from app.models import AdminUser, Role
from werkzeug.security import generate_password_hash

# Lista de usuarios a crear con los nuevos roles (sin el rol 'usuario')
USERS = [
    ("ventas@kodesk.cl", "leucodeops", "admin"),  
    ("soporte@kodesk.cl", "support123", "admin"),
    ("editor@kodesk.cl", "editorpass", "editor"),
    ("miembro@kodesk.cl", "miembro123", "miembro"),
    ("lector@kodesk.cl", "lectorpass", "lector"),
    ("invitado@kodesk.cl", "invitadopass", "invitado"),
]

def create_users():
    """Agrega usuarios con roles específicos si no existen."""

    # Crear la app
    app = create_app()

    # Crear la base de datos y las tablas si no existen
    with app.app_context():
        db.create_all()
        print("Base de datos y tablas creadas o verificadas")

        # Insertar roles predeterminados (solo si no existen)
        roles = {}
        for role_name in ["admin", "editor", "miembro", "lector", "invitado"]:  # Sin "usuario"
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
                db.session.commit()
                roles[role_name] = role
                print(f"Rol '{role_name}' agregado")

        # Crear los usuarios con roles (solo si no existen)
        for email, password, role_name in USERS:
            user = AdminUser.query.filter_by(email=email).first()
            if user:
                print(f"🔄 Usuario con email {email} ya existe. No se actualizará.")
            else:
                # Crear un nuevo usuario
                user = AdminUser(nombre=email.split('@')[0], email=email)
                user.set_password(password)
                if role_name in roles:
                    user.roles.append(roles[role_name])  # Asignar el rol correcto
                db.session.add(user)
                print(f"✅ Usuario creado: {email} con rol {role_name}")
        
        db.session.commit()
        print("🎉 Proceso terminado.")

if __name__ == "__main__":
    create_users()

