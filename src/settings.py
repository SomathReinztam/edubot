from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if __name__=="__main__":
    print(ROOT)


"""
python3 -m src.settings

"""