from app import create_app, db
from sqlalchemy import text

def drop_alembic_version():
    """Elimina la tabla alembic_version para reiniciar migraciones."""
    app = create_app()

    # Activar el contexto de aplicación
    with app.app_context():
        try:
            db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
            db.session.commit()
            print("✅ Tabla 'alembic_version' eliminada correctamente.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al eliminar la tabla: {e}")

if __name__ == "__main__":
    drop_alembic_version()
