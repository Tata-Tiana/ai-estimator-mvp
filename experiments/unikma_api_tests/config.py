from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
REFERENCE_UNIKMA_DIR = DATA_DIR / "reference" / "unikma"
LOG_DIR = DATA_DIR / "output" / "logs"
SAMPLES_DIR = Path(__file__).resolve().parent / "samples"

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

BASE_URL = "https://unikma.ru"
UNIKMA_API_KEY = os.getenv("UNIKMA_API_KEY", "").strip()
