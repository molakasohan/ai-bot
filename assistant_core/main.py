import argparse
import re

from .assistant import VoiceAssistant
from .config import DB_FILE, LANGUAGES
from .speech import SpeechEngine
from .storage import Storage


def choose_language(speech):
    language_names = ", ".join(name.title() for name in LANGUAGES)
    speech.speak(
        "Choose a speech recognition language. Say its name in English: "
        + language_names
        + ". Say stop to quit."
    )
    get_selection = speech.make_voice_input(LANGUAGES["english"])

    while True:
        try:
            selection = get_selection().strip().lower()
        except KeyboardInterrupt:
            return None

        if selection in {"stop", "quit", "exit"}:
            return None

        selected_name = selection.removesuffix(" language").strip()
        if selected_name in LANGUAGES:
            speech.speak(f"{selected_name.title()} recognition selected.")
            return speech.make_voice_input(LANGUAGES[selected_name])

        speech.speak("I didn't recognize that language. Say one of the listed names in English.")


def main():
    parser = argparse.ArgumentParser(description="Voice command assistant")
    parser.add_argument("--wake", help="wake word, for example: jarvis")
    args = parser.parse_args()

    storage = Storage(DB_FILE)
    speech = SpeechEngine()
    assistant = VoiceAssistant(storage, speech)
    get_input = choose_language(speech)
    if get_input is None:
        speech.speak("Goodbye.")
        return

    speech.speak("Voice assistant ready. Say help to hear what I can do.")

    while True:
        try:
            text = get_input()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if args.wake:
            if args.wake.lower() not in text.lower():
                continue
            text = re.sub(args.wake, "", text, flags=re.I).strip()
            if not text:
                speech.speak("Yes?")
                try:
                    text = get_input()
                except (EOFError, KeyboardInterrupt):
                    print("\nSession ended.")
                    break

        if not assistant.handle(text, get_input):
            break


if __name__ == "__main__":
    main()
