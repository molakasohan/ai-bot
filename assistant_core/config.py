from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "assistant.db"
NOTES_FILE = BASE_DIR / "notes.txt"

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
