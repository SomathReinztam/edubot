from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent.parent

# Credenciales de edubot ----------------

EDUBOTDB_USER=os.getenv("EDUBOTDB_USER")
EDUBOTDB_PASS=os.getenv("EDUBOTDB_PASS")
EDUBOTDB_HOST=os.getenv("EDUBOTDB_HOST")
EDUBOTDB_PORT=os.getenv("EDUBOTDB_PORT")
EDUBOTDB_NAME=os.getenv("EDUBOTDB_NAME")


# api keys ----------------

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")

