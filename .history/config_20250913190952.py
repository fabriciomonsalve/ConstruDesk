# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'kodesk.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'tu-clave-super-secreta'
WHATSAPP_PHONE = "56992"
