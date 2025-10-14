# 🏗️ Construdesk

**Construdesk** es una aplicación desarrollada con **Flask** para la gestión y administración de proyectos de construcción.  
Incluye módulos para manejo de usuarios, control de tareas, reportes y panel de administración.

---

## 🚀 Estructura del Proyecto

```
Construdesk/
├── .env
├── config.py
├── crearusers.py
├── kodesk.db
├── querybd.py
├── readme.md
├── requirements.txt
├── run.py
├── ventas.py
├── app/
│   ├── __init__.py
│   ├── forms.py
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── editor.py
│   │   ├── invitado.py
│   │   ├── lector.py
│   │   ├── miembro.py
│   ├── static/
│   │   ├── gruas.mp4
│   │   ├── kodesk.png
│   │   ├── logo.png
│   │   ├── video.mp4
│   │   ├── logos/
│   │   │   ├── agrodesk.png
│   │   │   ├── indepsalud.png
│   │   │   ├── kodesk.png
│   │   │   ├── leucodeops.png
│   │   │   ├── ptraker.png
│   │   │   ├── vet.png
│   │   ├── uploads/
│   │   │   ├── Diamante.jpg
│   │   │   ├── Diamante_1.jpg
│   │   │   ├── MaderaAntigua.jpg
│   │   │   ├── prueba12.jfif
│   │   │   ├── resort.jpeg
│   ├── templates/
│   │   ├── index.html
│   │   ├── layout.html
│   │   ├── login.html
│   │   ├── services.html
│   │   ├── admin/
│   │   │   ├── crear_proyecto.html
│   │   │   ├── crear_usuario.html
│   │   │   ├── detalles_proyecto.html
│   │   │   ├── editar_proyecto.html
│   │   │   ├── inicio.html
│   │   │   ├── mensajes.html
│   │   │   ├── usuarios.html
│   │   │   ├── usuarios_a_proyectos.html
│   │   │   ├── ver_proyecto.html
│   │   ├── editor/
│   │   │   ├── create_task.html
│   │   │   ├── edit_document.html
│   │   │   ├── edit_task.html
│   │   │   ├── editor_dashboard.html
│   │   │   ├── upload_document.html
│   │   │   ├── view_documents.html
│   │   │   ├── view_tasks.html
│   │   ├── invitado/
│   │   ├── lector/
│   │   │   ├── inicio.html
│   │   │   ├── inicio01.html
│   │   ├── miembro/
│   │   │   ├── inicio01.html
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   ├── versions/
│   │   ├── c90b4d4a43ae_nueva_migrationsss.py
```

---

## ⚙️ Instalación y configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPO>
   cd Construdesk
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Linux / Mac
   venv\Scripts\activate    # En Windows
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```bash
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=tu_clave_secreta
   DATABASE_URL=sqlite:///construdesk.db
   ```

---

## ▶️ Ejecución del proyecto

Para iniciar el servidor Flask:
```bash
flask run
```

El servidor se ejecutará por defecto en:
```
http://127.0.0.1:5000
```

---

## 📁 Estructura básica esperada

- **app/** – Lógica principal de la aplicación Flask.  
- **templates/** – Archivos HTML para las vistas.  
- **static/** – Archivos estáticos (CSS, JS, imágenes).  
- **models/** – Definición de modelos y base de datos.  
- **routes/** – Rutas y controladores del proyecto.  
- **.env** – Variables de entorno.  
- **requirements.txt** – Dependencias del proyecto.  

---

## 🧩 Tecnologías utilizadas

- **Python 3.x**
- **Flask**
- **SQLAlchemy / SQLite**
- **Bootstrap / HTML / CSS / JS**
- **Jinja2**

---

## 🧑‍💻 Contribución

1. Haz un *fork* del proyecto.  
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).  
3. Realiza tus cambios y haz commit (`git commit -m 'Agrega nueva funcionalidad'`).  
4. Sube la rama (`git push origin feature/nueva-funcionalidad`).  
5. Crea un *Pull Request*.  

---

## 🪪 Licencia

Este proyecto está bajo la licencia MIT.  


---

## 📧 Contacto

Si tienes dudas o sugerencias:
**Email:** soporte@construdesk.com  
**Autor:** Equipo Construdesk
