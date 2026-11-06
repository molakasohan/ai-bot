import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AssistantConfig:
    base_dir: Path
    data_dir: Path
    db_file: Path
    notes_file: Path


def _resolve_path(value: str, relative_to: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = relative_to / path
    return path.resolve()


def _environment_path(
    environment: Mapping[str, str], name: str, relative_to: Path
) -> Optional[Path]:
    value = environment.get(name)
    if value is None:
        return None
    if not value.strip():
        raise ValueError(f"{name} must not be empty.")
    return _resolve_path(value, relative_to)


def load_config(environ: Optional[Mapping[str, str]] = None) -> AssistantConfig:
    """Build path settings from environment variables."""
    environment = os.environ if environ is None else environ
    base_dir = BASE_DIR.resolve()
    data_dir = _environment_path(environment, "AI_BOT_DATA_DIR", base_dir) or base_dir
    db_file = _environment_path(environment, "AI_BOT_DB_FILE", data_dir)
    notes_file = _environment_path(environment, "AI_BOT_NOTES_FILE", data_dir)
    db_file = db_file or data_dir / "assistant.db"
    notes_file = notes_file or data_dir / "notes.txt"

    if db_file == notes_file:
        raise ValueError("AI_BOT_DB_FILE and AI_BOT_NOTES_FILE must be different paths.")

    return AssistantConfig(
        base_dir=base_dir,
        data_dir=data_dir,
        db_file=db_file,
        notes_file=notes_file,
    )


CONFIG = load_config()
DB_FILE = CONFIG.db_file
NOTES_FILE = CONFIG.notes_file

LANGUAGES = {
    "english": "en-IN",
    "hindi": "hi-IN",
    "telugu": "te-IN",
    "tamil": "ta-IN",
    "kannada": "kn-IN",
    "malayalam": "ml-IN",
    "bengali": "bn-IN",
    "marathi": "mr-IN",
    "gujarati": "gu-IN",
    "punjabi": "pa-IN",
    "urdu": "ur-IN",
    "spanish": "es-ES",
    "french": "fr-FR",
    "german": "de-DE",
    "japanese": "ja-JP",
    "chinese": "zh-CN",
    "arabic": "ar-SA",
}

SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "maps": "https://maps.google.com",
    "claude": "https://claude.ai",
    "naukri": "https://www.naukri.com",
    "stackoverflow": "https://stackoverflow.com",
}

WIN_APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "chrome": "chrome",
    "edge": "msedge",
    "vs code": "code",
    "command prompt": "cmd",
    "file explorer": "explorer",
    "power bi": "pbidesktop",
    "task manager": "taskmgr",
}

NUM_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "fifteen": 15,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "sixty": 60,
    "a": 1,
    "an": 1,
}
