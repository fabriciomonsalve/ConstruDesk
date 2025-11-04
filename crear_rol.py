# crear_rol.py
from app import create_app  # o desde donde importes tu fábrica de app
from app.models import Role  # o desde donde importes tu modelo Role
from app import db  # o desde donde importes tu instancia de db

def main():
    # Crear la app y su contexto
    app = create_app()
    with app.app_context():
        # Verificar si el rol ya existe
        rol_existente = Role.query.filter_by(name="mensajero").first()
        if rol_existente:
            print("✅ El rol 'mensajero' ya existe en la base de datos.")
            return
        
        # Crear y guardar el nuevo rol
        nuevo_rol = Role(name="mensajero")
        db.session.add(nuevo_rol)
        db.session.commit()
        
        print("🎉 Rol 'mensajero' creado exitosamente.")

if __name__ == "__main__":
    main()
