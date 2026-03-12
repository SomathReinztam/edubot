from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


if __name__=="__main__":
    print(ROOT)


"""
python3 -m src.settings

"""