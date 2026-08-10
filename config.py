import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_DIR = os.path.join(BASE_DIR, "database")

# Make sure the database folder exists
os.makedirs(DATABASE_DIR, exist_ok=True)


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "clms_super_secret_key_2026"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(DATABASE_DIR, "clms.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False