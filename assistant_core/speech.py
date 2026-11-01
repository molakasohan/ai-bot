import threading

try:
    import pyttsx3
except ImportError:  # pragma: no cover
    pyttsx3 = None


class SpeechEngine:
    def __init__(self):
        self.engine = None
        self.lock = threading.Lock()

        if pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 175)
            except Exception:
                self.engine = None

    def speak(self, text):
        print(f"Assistant: {text}")
        if self.engine is None:
            return

        with self.lock:
            self.engine.say(text)
            self.engine.runAndWait()

    def make_voice_input(self, language):
        try:
            import speech_recognition as sr
        except ImportError as exc:
            raise RuntimeError("SpeechRecognition is not installed.") from exc

        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("Calibrating for background noise…")
            recognizer.adjust_for_ambient_noise(source, duration=1)

        def listen():
            with mic as source:
                print("Listening…")
                try:
                    audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio, language=language)
                    print(f"You: {text}")
                    return text
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    return ""
                except sr.RequestError:
                    print("Speech service unavailable. Check your internet.")
                    return ""

        return listen
