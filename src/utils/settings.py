from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent.parent

# Credenciales de edubot ----------------

EDUBOTDB_USER = os.getenv("EDUBOTDB_USER")
EDUBOTDB_PASS = os.getenv("EDUBOTDB_PASS")
EDUBOTDB_HOST = os.getenv("EDUBOTDB_HOST")
EDUBOTDB_PORT = os.getenv("EDUBOTDB_PORT")
EDUBOTDB_NAME = os.getenv("EDUBOTDB_NAME")


# Credenciales de la base de datos de la app ----------------

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# api keys ----------------

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


