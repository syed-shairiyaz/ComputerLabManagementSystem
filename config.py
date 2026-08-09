import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "clms_super_secret_key_2026"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "clms.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False