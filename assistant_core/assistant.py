import ast
import operator
import os
import platform
import re
import subprocess
import threading
import urllib.parse
import webbrowser
from datetime import datetime

from .config import (
    NUM_WORDS,
    SITES,
    SITE_SEARCH_URLS,
    WIN_APPS,
    YOUTUBE_MUSIC_SEARCH_URL,
)


def safe_calc(expr):
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.Mod: operator.mod,
    }

    def eval_node(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](eval_node(node.operand))
        raise ValueError("Unsupported math expression")

    return eval_node(ast.parse(expr, mode="eval").body)


def to_number(word):
    return int(word) if word.isdigit() else NUM_WORDS.get(word)


class VoiceAssistant:
    def __init__(self, storage, speech):
        self.storage = storage
        self.speech = speech

    def open_url(self, url, label):
        self.speech.speak(f"Opening {label}.")
        webbrowser.open(url)

    def open_app(self, name):
        system = platform.system()
        try:
            if system == "Windows":
                target = WIN_APPS.get(name, name)
                subprocess.Popen(["cmd", "/c", "start", "", target])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", name])
            else:
                subprocess.Popen([name.replace(" ", "-")])
            self.speech.speak(f"Opening {name}.")
        except Exception:
            self.speech.speak(f"I couldn't open {name}.")

    def start_timer(self, amount, unit):
        seconds = amount * {"second": 1, "minute": 60, "hour": 3600}[unit]

        def done():
            self.speech.speak(f"Time's up! Your {amount} {unit} timer is finished.")

        threading.Timer(seconds, done).start()
        self.speech.speak(f"Timer set for {amount} {unit}{'s' if amount != 1 else ''}.")

    def ask_ai(self, question):
        if not os.getenv("ANTHROPIC_API_KEY"):
            return None

        try:
            import anthropic
        except Exception:
            return None

        try:
            response = anthropic.Anthropic().messages.create(
                model="claude-sonnet-5-5",
                max_tokens=250,
                system="You are a voice assistant. Answer in one to three short spoken sentences. No markdown.",
                messages=[{"role": "user", "content": question}],
            )
            return response.content[0].text.strip()
        except Exception:
            return None

    def teach(self, get_input):
        self.speech.speak("What phrase should trigger the new command?")
        try:
            phrase = get_input()
        except EOFError:
            return self.speech.speak("Cancelled.")

        if not phrase:
            return self.speech.speak("I didn't catch that. Cancelled.")

        self.speech.speak(
            f"Okay, when you say {phrase}. Now type the action type in the terminal."
        )
        try:
            command_type = input(
                "Action type [open = website, app = program, say = reply, task = add task]: "
            ).strip().lower()
        except EOFError:
            return self.speech.speak("Cancelled.")

        if command_type not in ("open", "app", "say", "task"):
            return self.speech.speak("Unknown action type. Cancelled.")

        try:
            value = input("Value (URL, app name, or text): ").strip()
        except EOFError:
            return self.speech.speak("Cancelled.")

        if command_type == "open" and not value.startswith("http"):
            value = "https://" + value

        self.storage.add_custom_command(phrase, command_type, value)
        self.speech.speak(f"Learned. Say {phrase} any time.")

    def run_custom_command(self, custom_command):
        command_type = custom_command["type"]
        value = custom_command["value"]

        if command_type == "open":
            self.open_url(value, custom_command["phrase"])
        elif command_type == "app":
            self.open_app(value)
        elif command_type == "say":
            self.speech.speak(value)
        elif command_type == "task":
            self.storage.add_task(value)
            self.speech.speak(f"Task added: {value}")

    def handle(self, text, get_input):
        cleaned = re.sub(r"[.?!,]", "", text).strip()
        lowered = cleaned.lower()

        if not lowered:
            return True

        if lowered in {"stop", "stop listening", "exit", "quit", "goodbye", "bye"}:
            self.speech.speak("Goodbye!")
            return False

        for command in self.storage.get_custom_commands():
            if command["phrase"] in lowered:
                self.run_custom_command(command)
                return True

        if lowered in ("teach", "learn", "teach new command", "train"):
            self.teach(get_input)
            return True

        if lowered == "help":
            self.speech.speak(
                "Try: open YouTube, open notepad, search Python tutorials, "
                "search YouTube for music, search GitHub for Python, play music, "
                "add task, show tasks, take a note, set timer for 5 minutes, "
                "what time is it, calculate 12 times 8, or teach. Say stop to finish."
            )
            return True

        match = re.match(r"(?:open|launch|start) (.+)", lowered)
        if match:
            name = match.group(1).strip()
            key = name.replace(" ", "")
            if key in SITES:
                self.open_url(SITES[key], name)
            elif name in WIN_APPS or platform.system() != "Windows":
                self.open_app(name)
            elif "." in key:
                self.open_url("https://" + key, name)
            else:
                self.open_app(name)
            return True

        match = re.match(
            r"(?:search|find|look up)(?: for)?\s+(.+?)\s+(?:on|in)\s+(.+)",
            lowered,
        )
        if match:
            query, site_name = match.groups()
            site = self._site_key(site_name)
            if site:
                self.search_site(site, query)
                return True

        match = re.match(
            r"(?:search|find|look up)\s+(.+?)\s+for\s+(.+)",
            lowered,
        )
        if match:
            site = self._site_key(match.group(1))
            if site:
                self.search_site(site, match.group(2))
                return True

        match = re.match(r"play (.+?)(?: on youtube(?: music)?)?$", lowered)
        if match:
            query = match.group(1).strip()
            search_url = YOUTUBE_MUSIC_SEARCH_URL.format(
                query=urllib.parse.quote(query, safe="")
            )
            self.open_url(search_url, f"{query} on YouTube Music")
            return True

        match = re.match(r"(?:search|google|look up|find)(?: for)? (.+)", lowered)
        if match:
            query = match.group(1)
            self.open_url(
                "https://www.google.com/search?q=" + urllib.parse.quote(query),
                f"results for {query}",
            )
            return True

        match = re.match(r"weather(?: in (.+))?", lowered)
        if match:
            location = match.group(1) or ""
            self.open_url(
                "https://www.google.com/search?q=" + urllib.parse.quote("weather " + location),
                "the weather",
            )
            return True

        match = re.match(r"(?:add task|remind me to|add to do) (.+)", cleaned, re.I)
        if match:
            task_text = match.group(1)
            self.storage.add_task(task_text)
            self.speech.speak(f"Task added: {task_text}")
            return True

        if re.match(r"(show|read|list)( my)? tasks", lowered):
            tasks = self.storage.list_tasks()
            if tasks:
                self.speech.speak("Your tasks are: " + ", ".join(tasks))
            else:
                self.speech.speak("You have no tasks.")
            return True

        if re.match(r"clear( all)?( my)? tasks", lowered):
            self.storage.clear_tasks()
            self.speech.speak("All tasks cleared.")
            return True

        match = re.match(r"(?:take a note|note down|note) ?(.*)", cleaned, re.I)
        if match:
            note = match.group(1)
            if not note:
                self.speech.speak("What should I write?")
                note = get_input()
            self.storage.save_note(note)
            self.speech.speak("Note saved.")
            return True

        match = re.match(r"(?:set (?:a )?)?timer(?: for)? (\w+) (second|minute|hour)", lowered)
        if match:
            amount = to_number(match.group(1))
            if amount:
                self.start_timer(amount, match.group(2))
            else:
                self.speech.speak("I didn't catch the duration.")
            return True

        if re.match(r"what(?:'s| is)? the time|what time", lowered):
            self.speech.speak(f"It is {datetime.now():%I:%M %p}.")
            return True

        if re.match(r"what(?:'s| is)?( the)? (date|day)|today's date", lowered):
            self.speech.speak(f"Today is {datetime.now():%A, %d %B %Y}.")
            return True

        match = re.match(r"(?:calculate|what is|what's) (.+)", lowered)
        if match:
            expr = (
                match.group(1)
                .replace("plus", "+")
                .replace("minus", "-")
                .replace("divided by", "/")
                .replace("multiplied by", "*")
                .replace("times", "*")
                .replace(" x ", "*")
            )
            try:
                result = safe_calc(expr)
                self.speech.speak(f"{match.group(1)} equals {result}")
            except Exception:
                answer = self.ask_ai(text)
                self.speech.speak(answer or "Sorry, I couldn't work that out.")
            return True

        if re.match(r"(hi|hello|hey)\b", lowered):
            self.speech.speak("Hello! What would you like me to do?")
            return True

        answer = self.ask_ai(text)
        if answer:
            self.speech.speak(answer)
            return True

        self.speech.speak("I don't know that yet. Say teach to train me, or I can search Google.")
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(text))
        return True

    @staticmethod
    def _site_key(name):
        key = re.sub(r"[^a-z0-9]", "", name.lower())
        if key == "googlemaps":
            key = "maps"
        return key if key in SITES else None

    def search_site(self, site, query):
        search_url = SITE_SEARCH_URLS.get(site)
        if search_url is None:
            self.speech.speak(f"Searching {site} isn't supported yet.")
            return

        if site == "naukri":
            encoded_query = urllib.parse.quote(query.strip().replace(" ", "-"), safe="-")
        else:
            encoded_query = urllib.parse.quote(query.strip(), safe="")
        self.open_url(
            search_url.format(query=encoded_query),
            f"{site} results for {query}",
        )
