from app import create_app, db
from app.models import Project

def delete_all_projects():
    """Elimina todos los proyectos de la base de datos."""
    # Crear la app
    app = create_app()

    # Crear el contexto de la app para interactuar con la base de datos
    with app.app_context():
        # Obtener todos los proyectos
        projects = Project.query.all()

        # Verificar si hay proyectos para eliminar
        if not projects:
            print("No hay proyectos para eliminar.")
            return
        
        # Eliminar todos los proyectos
        for project in projects:
            db.session.delete(project)
            print(f"✅ Proyecto eliminado: {project.name}")

        # Confirmar los cambios en la base de datos
        db.session.commit()
        print("🎉 Todos los proyectos han sido eliminados.")

if __name__ == "__main__":
    delete_all_projects()
