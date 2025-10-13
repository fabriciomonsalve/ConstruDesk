import os
from app import create_app, db
from app.models import AdminUser, Role

def consultar_usuarios():
    """Consulta los usuarios y muestra sus roles sin crear ni modificar nada."""
    
    # Crear la app
    app = create_app()

    # Ejecutar en el contexto de la app
    with app.app_context():
        # Obtener todos los usuarios con roles asociados
        usuarios = AdminUser.query.all()
        
        # Mostrar los usuarios y sus roles
        print("\nListado de usuarios y sus roles:")
        for usuario in usuarios:
            # Obtener los roles del usuario (esto puede ser una lista de objetos Role)
            roles_usuario = [role.name for role in usuario.roles]
            print(f"Usuario: {usuario.email} - Roles: {', '.join(roles_usuario)}")

if __name__ == "__main__":
    consultar_usuarios()
