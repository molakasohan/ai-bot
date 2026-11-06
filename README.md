# Voice Assistant

This is a small Python voice assistant that I’m building to learn how a real project fits together. You can speak commands to open websites or apps, search YouTube, manage tasks and notes, set timers, and do simple calculations.

## What you need

- Python 3
- A microphone
- An internet connection for speech recognition

The assistant uses Google’s online speech recognition through the `SpeechRecognition` package. It does not train its own speech model. You choose a recognition language when the assistant starts. Commands such as `help`, `open YouTube`, and `add task` are currently understood in English; choosing Hindi or Telugu changes speech recognition, but does not translate the command system or the assistant’s spoken replies.

## Install

Open PowerShell in this project folder and install the Python packages:

```powershell
py -3 -m pip install SpeechRecognition pyttsx3 PyAudio
```

If PyAudio fails to install, check the PyAudio installation instructions for your Python version and Windows setup.

## Start the assistant

```powershell
py -3 .\voice_assistant.py
```

At startup, say the name of a supported language **in English**. For example, say `Telugu` to recognize Telugu speech, or `Hindi` to recognize Hindi speech. Then say `help` to hear a few example commands. Say `stop` when you want to exit.

You can optionally require a wake word before commands are handled:

```powershell
py -3 .\voice_assistant.py --wake jarvis
```

## Commands to try

- `open YouTube`
- `open notepad`
- `search Python tutorials`
- `search YouTube for relaxing music`
- `search GitHub for Python projects`
- `find directions to the airport on Maps`
- `play relaxing music` — opens YouTube Music search results; choose a result to play it
- `play Bohemian Rhapsody on YouTube Music` — searches YouTube Music for that song
- `add task finish my homework`
- `show tasks`
- `take a note remember this idea`
- `set timer for 5 minutes`
- `calculate 12 times 8`
- `what time is it`
- `help`
- `stop`

Voice `play <song>` commands open YouTube Music search results; select a result to start playback. Site-specific search is also available for YouTube, Google, Gmail, GitHub, LinkedIn, Maps, Naukri, and Stack Overflow. For sites without a configured search link, such as WhatsApp and Claude, open the site and use its own search interface.

## Where your data goes

Tasks and custom commands are stored in the local `assistant.db` SQLite database. Notes are appended to `notes.txt`. These files are created in the project folder when the assistant saves data, and are not included in Git.

You can change their locations with environment variables. `AI_BOT_DATA_DIR` sets the data folder (relative paths are resolved from the project folder); `AI_BOT_DB_FILE` and `AI_BOT_NOTES_FILE` override individual file paths (relative paths are resolved from the data folder). For example, in PowerShell:

```powershell
$env:AI_BOT_DATA_DIR = "$HOME\Documents\ai-bot-data"
py -3 .\voice_assistant.py
```

By default, the assistant continues to use `assistant.db` and `notes.txt` in the project folder.

## Project layout

- `voice_assistant.py` starts the program.
- `assistant_core/main.py` starts the voice session and asks which language to recognize.
- `assistant_core/speech.py` handles speech input and spoken output.
- `assistant_core/assistant.py` matches commands and performs actions.
- `assistant_core/storage.py` saves tasks and custom commands in SQLite.
- `assistant_core/config.py` contains language, website, and Windows app settings.
