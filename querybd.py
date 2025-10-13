from app import create_app, db
from sqlalchemy import text

def drop_tables():
    """Elimina las tablas tasks y schedules de la base de datos."""
    # Crear la app
    app = create_app()

    # Crear el contexto de la app para interactuar con la base de datos
    with app.app_context():
        # Eliminar las tablas directamente usando la sesión de base de datos y envolviendo el SQL en text()
        db.session.execute(text('DROP TABLE IF EXISTS tasks'))      # Eliminar la tabla tasks
        db.session.commit()  # Confirmar los cambios

        print("🎉 Las tablas 'tasks' y 'schedules' han sido eliminadas.")

if __name__ == "__main__":
    drop_tables()
