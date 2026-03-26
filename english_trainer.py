import json
import time
import random
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, scrolledtext
from datetime import date, datetime

from openai import OpenAI

import hashlib
import uuid
import platform
import json
import os

def normalize_text(text):
    return str(text).lower().strip()

SESSION_FILE = "session.json"

def save_session(email, key, device_id, api_key):
    data = {
        "email": email,
        "key": key,
        "device_id": device_id,
        "api_key": api_key
    }
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_session():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except:
        return None

def clear_session():
    import os
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def logout(root):
    confirm = messagebox.askyesno("Logout", "Wirklich ausloggen?")
    if not confirm:
        return

    clear_session()
    root.destroy()

    login_root = tk.Tk()
    LoginWindow(login_root, start_app)
    login_root.mainloop()


def reset_all_stats(app):
    confirm = messagebox.askyesno("Reset Stats", "Alle Stats wirklich zurücksetzen?")
    if not confirm:
        return

    save_stats(DEFAULT_STATS.copy())
    save_profile(DEFAULT_PROFILE.copy())
    save_test_history([])
    save_favorites([])
    save_json_file(WRONG_FILE, [])

    try:
        app.combo_streak = 0
        app.session_actions = 0
        app.used_sentences = set()
        app.used_vocab = set()
        app.refresh_profile_labels()
        app.refresh_home_side_cards()
        app.set_result("Alle Stats wurden zurückgesetzt.")
        app.set_output("Stats reset complete.")
        app.set_status("● Stats reset", AMBER)
    except Exception:
        pass


SECRET = "xy"



def get_device_id():
    raw = f"{platform.system()}|{platform.node()}|{uuid.getnode()}"
    return hashlib.sha256(raw.encode()).hexdigest()

def validate_openai_key(api_key):
    api_key = str(api_key).strip()
    if not api_key:
        return True, "offline"
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
        return True, "ok"
    except Exception as e:
        return False, f"OpenAI API key invalid: {e}"

USERS_FILE = "users.json"

def load_saved_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_user_login(email, password):
    users = load_saved_users()
    item = {
        "email": email.strip().lower(),
        "password": password,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    exists = False
    for entry in users:
        if (
            entry.get("email", "").strip().lower() == item["email"]
            and entry.get("password", "") == item["password"]
        ):
            entry["saved_at"] = item["saved_at"]
            exists = True
            break

    if not exists:
        users.append(item)

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)



def generate_product_key(email):
    return hashlib.md5((email.strip().lower() + SECRET).encode()).hexdigest()


def generate_key_gui():
    win = tk.Toplevel()
    win.title("Key Generator")
    win.geometry("420x220")
    win.configure(bg=BG)

    wrap = tk.Frame(win, bg=BG)
    wrap.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(wrap, text="Key Generator (MD5 from Email + xy)", font=("Segoe UI", 16, "bold"), fg=TEXT, bg=BG).pack(pady=(0, 12))
    tk.Label(wrap, text="Email (we add +xy internally)", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=BG).pack(anchor="w")

    entry = tk.Entry(
        wrap,
        width=38,
        font=("Segoe UI", 11),
        bg=INPUT_BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat"
    )
    entry.pack(fill="x", pady=(6, 12))

    result = tk.Entry(
        wrap,
        font=("Consolas", 11),
        bg=INPUT_BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat"
    )
    result.pack(fill="x", pady=(0, 12))

    def gen():
        email = entry.get().strip().lower()
        if not email:
            result.delete(0, tk.END)
            result.insert(0, "Please enter an email.")
            return
        key = generate_product_key(email)
        result.delete(0, tk.END)
        result.insert(0, key)

    AccentButton(wrap, text="GENERATE", command=gen, normal_bg=BLUE, hover_bg=BLUE_HOVER, width=16).pack()
    entry.focus_set()


# =========================================================
# CONFIG
# =========================================================

import os
API_KEY = os.getenv("OPENAI_API_KEY", "")

MODEL_OPTIONS = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o",
    "gpt-4.1",
    "gpt-5.4-nano",
    "gpt-5.4-mini",
    "gpt-5.4",
]

DEFAULT_MODEL = "gpt-4o-mini"

MODEL_PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-5.4-nano": {"input": 0.05, "output": 0.40},
    "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
    "gpt-5.4": {"input": 2.50, "output": 15.00},
}

DIFFICULTIES = ["easy", "medium", "hard"]

WRONG_FILE = "wrong_answers.json"
STATS_FILE = "stats.json"
PROFILE_FILE = "profile.json"
TEST_HISTORY_FILE = "test_history.json"
FAVORITES_FILE = "favorites.json"

TOPICS = [
    "mixed",
    "school",
    "food",
    "family",
    "travel",
    "weather",
    "sports",
    "animals",
    "home",
    "friends",
    "shopping"
]

TENSES = [
    "simple present",
    "simple past",
    "present perfect",
    "future",
    "mixed"
]

IRREGULAR_VERBS = [
    {"base": "go", "past": "went", "participle": "gone", "de": "gehen"},
    {"base": "see", "past": "saw", "participle": "seen", "de": "sehen"},
    {"base": "write", "past": "wrote", "participle": "written", "de": "schreiben"},
    {"base": "eat", "past": "ate", "participle": "eaten", "de": "essen"},
    {"base": "drink", "past": "drank", "participle": "drunk", "de": "trinken"},
    {"base": "take", "past": "took", "participle": "taken", "de": "nehmen"},
    {"base": "give", "past": "gave", "participle": "given", "de": "geben"},
    {"base": "come", "past": "came", "participle": "come", "de": "kommen"},
    {"base": "speak", "past": "spoke", "participle": "spoken", "de": "sprechen"},
    {"base": "begin", "past": "began", "participle": "begun", "de": "beginnen"}
]

HUNT_WORDS = {
    "travel": ["plane", "airport", "ticket", "passport", "hotel", "suitcase", "train", "map", "flight", "gate"],
    "food": ["bread", "apple", "water", "banana", "pizza", "rice", "soup", "cheese", "milk", "juice"],
    "school": ["teacher", "book", "pen", "classroom", "homework", "exam", "desk", "student", "lesson", "notebook"],
    "sports": ["ball", "team", "goal", "run", "player", "match", "coach", "score", "swim", "tennis"],
    "home": ["kitchen", "bedroom", "window", "table", "chair", "door", "garden", "bathroom", "lamp", "sofa"],
    "animals": ["dog", "cat", "bird", "horse", "fish", "lion", "tiger", "rabbit", "mouse", "snake"],
    "weather": ["sun", "rain", "cloud", "wind", "snow", "storm", "hot", "cold", "fog", "summer"],
    "family": ["mother", "father", "sister", "brother", "grandmother", "baby", "uncle", "aunt", "parents", "cousin"],
    "friends": ["friend", "party", "chat", "laugh", "visit", "phone", "weekend", "gift", "music", "photo"],
    "shopping": ["money", "store", "price", "bag", "cash", "shirt", "shoes", "market", "buy", "sale"],
}

STORY_PACKS = [
    {
        "title": "Airport Mission",
        "steps": [
            {"de": "Ich habe meinen Pass vergessen.", "en": "I forgot my passport."},
            {"de": "Wo ist das Gate?", "en": "Where is the gate?"},
            {"de": "Ich habe Angst vor dem Flug.", "en": "I am afraid of the flight."},
            {"de": "Kann ich am Fenster sitzen?", "en": "Can I sit by the window?"},
        ]
    },
    {
        "title": "Restaurant Night",
        "steps": [
            {"de": "Ich hätte gern die Speisekarte.", "en": "I would like the menu."},
            {"de": "Was können Sie empfehlen?", "en": "What can you recommend?"},
            {"de": "Ich bin allergisch gegen Nüsse.", "en": "I am allergic to nuts."},
            {"de": "Können wir bitte bezahlen?", "en": "Can we pay, please?"},
        ]
    },
    {
        "title": "School Adventure",
        "steps": [
            {"de": "Ich habe meine Hausaufgaben gemacht.", "en": "I did my homework."},
            {"de": "Wann beginnt der Unterricht?", "en": "When does the lesson start?"},
            {"de": "Darf ich eine Frage stellen?", "en": "May I ask a question?"},
            {"de": "Ich muss für die Prüfung lernen.", "en": "I have to study for the exam."},
        ]
    },
]

BUILD_SENTENCE_POOL = {
    "easy": [
        "I am at home",
        "She likes pizza",
        "We go to school",
        "He plays football",
        "They drink water",
    ],
    "medium": [
        "I am going to school today",
        "She bought a new book yesterday",
        "We are watching a film tonight",
        "They have finished their homework",
        "He wants to visit his grandmother",
    ],
    "hard": [
        "I have never seen such a beautiful place before",
        "If it rains tomorrow we will stay at home",
        "She had already finished the test when I arrived",
        "Although he was tired he continued working",
        "We would have gone out if the weather had been better",
    ]
}


LOCAL_VOCAB = {
    "school": [("Schule", "school"), ("Lehrer", "teacher"), ("Buch", "book"), ("Stift", "pen")],
    "food": [("Apfel", "apple"), ("Brot", "bread"), ("Milch", "milk"), ("Käse", "cheese")],
    "family": [("Mutter", "mother"), ("Vater", "father"), ("Bruder", "brother"), ("Schwester", "sister")],
    "travel": [("Flughafen", "airport"), ("Koffer", "suitcase"), ("Zug", "train"), ("Hotel", "hotel")],
    "weather": [("Regen", "rain"), ("Sonne", "sun"), ("Schnee", "snow"), ("Wind", "wind")],
    "sports": [("Ball", "ball"), ("Mannschaft", "team"), ("Tor", "goal"), ("Spieler", "player")],
    "animals": [("Hund", "dog"), ("Katze", "cat"), ("Pferd", "horse"), ("Vogel", "bird")],
    "home": [("Tisch", "table"), ("Stuhl", "chair"), ("Fenster", "window"), ("Lampe", "lamp")],
    "friends": [("Freund", "friend"), ("Geschenk", "gift"), ("Foto", "photo"), ("Musik", "music")],
    "shopping": [("Geld", "money"), ("Preis", "price"), ("Markt", "market"), ("Schuhe", "shoes")],
}

LOCAL_SENTENCES = {
    "simple present": [("Ich spiele jeden Tag Fußball.", "I play football every day."), ("Sie liest am Abend ein Buch.", "She reads a book in the evening.")],
    "simple past": [("Wir gingen gestern zur Schule.", "We went to school yesterday."), ("Er kaufte ein neues Handy.", "He bought a new phone.")],
    "present perfect": [("Ich habe meine Hausaufgaben gemacht.", "I have done my homework."), ("Sie hat das Fenster geöffnet.", "She has opened the window.")],
    "future": [("Wir werden morgen reisen.", "We will travel tomorrow."), ("Ich werde später anrufen.", "I will call later.")],
    "mixed": [("Kannst du mir bitte helfen?", "Can you help me, please?"), ("Heute ist das Wetter sehr schön.", "The weather is very nice today.")],
}



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIRS = [
    os.path.join(BASE_DIR, "datasets"),
    BASE_DIR,
]

def _find_dataset_file(*names):
    for folder in DATASET_DIRS:
        for name in names:
            path = os.path.join(folder, name)
            if os.path.exists(path):
                return path
    return None

def _read_dataset_lines(*names):
    path = _find_dataset_file(*names)
    if not path:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except Exception:
        return []

def load_vocab_dataset():
    topic_map = {t: [] for t in TOPICS if t != "mixed"}
    all_pairs = []
    for line in _read_dataset_lines("vocabulary.txt", "vocab.txt"):
        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 2:
            continue
        de, en = parts[0], parts[1]
        topic = normalize_text(parts[2]) if len(parts) >= 3 else "mixed"
        pair = (de, en)
        all_pairs.append(pair)
        if topic in topic_map:
            topic_map[topic].append(pair)
    return topic_map, all_pairs

def load_sentence_dataset():
    tense_map = {t: [] for t in TENSES}
    all_pairs = []
    for line in _read_dataset_lines("sentences.txt", "sentence.txt"):
        parts = [p.strip() for p in line.split(";")]
        if len(parts) >= 4:
            tense = normalize_text(parts[0])
            de, en = parts[2], parts[3]
        elif len(parts) >= 3:
            tense = normalize_text(parts[0])
            de, en = parts[1], parts[2]
        elif len(parts) >= 2:
            tense = "mixed"
            de, en = parts[0], parts[1]
        else:
            continue
        pair = (de, en)
        all_pairs.append(pair)
        if tense in tense_map:
            tense_map[tense].append(pair)
        else:
            tense_map["mixed"].append(pair)
    return tense_map, all_pairs

def load_irregular_dataset():
    verbs = []
    for line in _read_dataset_lines("grammar.txt", "irregular_verbs.txt"):
        parts = [p.strip() for p in line.split(";")]
        if len(parts) >= 4:
            base, past, participle, de = parts[:4]
        elif len(parts) >= 3:
            base, past, participle = parts[:3]
            de = base
        else:
            continue
        verbs.append({"base": base, "past": past, "participle": participle, "de": de})
    return verbs

def load_multiple_choice_dataset():
    items = []
    for line in _read_dataset_lines("multiple_choice.txt", "multiplechoice.txt", "mc.txt"):
        parts = [p.strip() for p in line.split(";")]
        if len(parts) >= 5:
            question, correct, wrong1, wrong2, wrong3 = parts[:5]
            topic = parts[5].strip() if len(parts) >= 6 else "mixed"
            options = [correct, wrong1, wrong2, wrong3]
            random.shuffle(options)
            letters = ["A", "B", "C", "D"]
            answer_letter = letters[options.index(correct)]
            items.append({
                "Frage": question,
                "A": options[0],
                "B": options[1],
                "C": options[2],
                "D": options[3],
                "Lösung": answer_letter,
                "topic": topic or "mixed",
            })
    return items

def load_build_sentence_dataset():
    return _read_dataset_lines("build_sentence.txt", "build_sentences.txt")

def load_hunt_dataset():
    topic_map = {t: [] for t in TOPICS if t != "mixed"}
    all_words = []
    for line in _read_dataset_lines("hunt_words.txt", "hunt.txt"):
        parts = [p.strip() for p in line.split(";")]
        if len(parts) >= 2:
            topic, word = normalize_text(parts[0]), normalize_text(parts[1])
        else:
            topic, word = "mixed", normalize_text(parts[0])
        if not word:
            continue
        all_words.append(word)
        if topic in topic_map:
            topic_map[topic].append(word)
    return topic_map, list(dict.fromkeys(all_words))

FILE_VOCAB_BY_TOPIC, FILE_VOCAB_ALL = load_vocab_dataset()
FILE_SENTENCES_BY_TENSE, FILE_SENTENCES_ALL = load_sentence_dataset()
FILE_IRREGULAR_VERBS = load_irregular_dataset()
FILE_MULTIPLE_CHOICE = load_multiple_choice_dataset()
FILE_BUILD_SENTENCES = load_build_sentence_dataset()
FILE_HUNT_BY_TOPIC, FILE_HUNT_ALL = load_hunt_dataset()

DEFAULT_STATS = {
    "tasks_total": 0,
    "correct_total": 0,
    "wrong_total": 0,
    "tests_taken": 0,
    "wrong_training_runs": 0,
    "vocab_runs": 0,
    "sentence_runs": 0,
    "translation_runs": 0,
    "irregular_runs": 0,
    "multiple_choice_runs": 0,
    "story_runs": 0,
    "build_runs": 0,
    "hunt_runs": 0,
    "api_calls": 0,
    "api_input_tokens": 0,
    "api_output_tokens": 0,
    "api_cost_usd": 0.0,
    "test_questions_total": 0,
    "test_questions_correct": 0,
    "test_questions_wrong": 0,
    "wrong_training_questions": 0,
    "wrong_training_correct": 0,
    "wrong_training_wrong": 0,
    "combo_best": 0,
    "favorites_saved": 0,
}

DEFAULT_PROFILE = {
    "xp": 0,
    "level": 1,
    "daily_goal": 20,
    "today_done": 0,
    "last_day": "",
    "streak": 0,
    "best_streak": 0,
}


# =========================================================
# COLORS / NEW UI
# =========================================================

BG = "#05070d"
SIDEBAR = "#0a0f1a"
CARD = "#0c111c"
CARD_2 = "#111827"
CARD_3 = "#151f31"
INPUT_BG = "#070d18"
BORDER = "#1d2940"

TEXT = "#e6edf7"
MUTED = "#8a99b2"
SUBTLE = "#66758e"

ACCENT = "#5b9cff"
ACCENT_HOVER = "#78adff"

BLUE = "#4f8cff"
BLUE_HOVER = "#6ea2ff"

CYAN = "#06b6d4"
CYAN_HOVER = "#22d3ee"

GREEN = "#22c55e"
GREEN_HOVER = "#4ade80"

AMBER = "#f59e0b"
AMBER_HOVER = "#fbbf24"

RED = "#ef4444"
RED_HOVER = "#f87171"

PINK = "#ec4899"
PINK_HOVER = "#f472b6"

PURPLE = "#7c3aed"
PURPLE_HOVER = "#8b5cf6"

NEUTRAL = "#334155"


# =========================================================
# HELPERS
# =========================================================

def normalize_text(text):
    return " ".join(str(text).lower().strip().split())


def resolve_topic(topic):
    if topic == "mixed":
        return random.choice([t for t in TOPICS if t != "mixed"])
    return topic


def load_json_file(path, default_data):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(default_data, dict):
            merged = default_data.copy()
            if isinstance(data, dict):
                merged.update(data)
                return merged
            return default_data.copy()

        if isinstance(default_data, list):
            return data if isinstance(data, list) else list(default_data)

        return data
    except Exception:
        if isinstance(default_data, dict):
            return default_data.copy()
        return list(default_data)


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_stats():
    return load_json_file(STATS_FILE, DEFAULT_STATS)


def save_stats(stats):
    save_json_file(STATS_FILE, stats)


def load_profile():
    return load_json_file(PROFILE_FILE, DEFAULT_PROFILE)


def save_profile(profile):
    save_json_file(PROFILE_FILE, profile)


def load_test_history():
    return load_json_file(TEST_HISTORY_FILE, [])


def save_test_history(history):
    save_json_file(TEST_HISTORY_FILE, history)


def load_favorites():
    return load_json_file(FAVORITES_FILE, [])


def save_favorites(items):
    save_json_file(FAVORITES_FILE, items)


def load_wrong_answers():
    return load_json_file(WRONG_FILE, [])


def calculate_api_cost(model_name, input_tokens, output_tokens):
    price = MODEL_PRICES.get(model_name, MODEL_PRICES[DEFAULT_MODEL])
    input_cost = (input_tokens / 1_000_000) * price["input"]
    output_cost = (output_tokens / 1_000_000) * price["output"]
    return input_cost + output_cost


def add_api_usage(model_name, input_tokens, output_tokens):
    stats = load_stats()
    stats["api_calls"] += 1
    stats["api_input_tokens"] += int(input_tokens)
    stats["api_output_tokens"] += int(output_tokens)
    stats["api_cost_usd"] += calculate_api_cost(model_name, input_tokens, output_tokens)
    stats["api_cost_usd"] = round(stats["api_cost_usd"], 8)
    save_stats(stats)


def update_profile_day():
    profile = load_profile()
    today = date.today().isoformat()
    last_day = profile.get("last_day", "")

    if not last_day:
        profile["last_day"] = today
        profile["today_done"] = 0
        profile["streak"] = 1
        profile["best_streak"] = max(profile["best_streak"], profile["streak"])
    elif last_day != today:
        try:
            old = datetime.fromisoformat(last_day).date()
            now = datetime.fromisoformat(today).date()
            diff = (now - old).days
        except Exception:
            diff = 0

        if diff == 1:
            profile["streak"] += 1
        elif diff > 1:
            profile["streak"] = 1

        profile["last_day"] = today
        profile["today_done"] = 0
        profile["best_streak"] = max(profile["best_streak"], profile["streak"])

    save_profile(profile)
    return profile


def add_xp(amount):
    update_profile_day()
    profile = load_profile()
    profile["xp"] += amount
    profile["today_done"] += 1
    profile["level"] = max(1, profile["xp"] // 100 + 1)
    save_profile(profile)
    return profile


def add_result_to_stats(is_correct, mode_name):
    stats = load_stats()
    stats["tasks_total"] += 1

    if is_correct:
        stats["correct_total"] += 1
    else:
        stats["wrong_total"] += 1

    if mode_name == "vocab":
        stats["vocab_runs"] += 1
    elif mode_name == "sentence":
        stats["sentence_runs"] += 1
    elif mode_name == "irregular":
        stats["irregular_runs"] += 1
    elif mode_name == "multiple_choice":
        stats["multiple_choice_runs"] += 1
    elif mode_name == "story":
        stats["story_runs"] += 1
    elif mode_name == "build":
        stats["build_runs"] += 1
    elif mode_name == "hunt":
        stats["hunt_runs"] += 1

    save_stats(stats)


def add_translation_run():
    stats = load_stats()
    stats["translation_runs"] += 1
    save_stats(stats)


def add_test_run():
    stats = load_stats()
    stats["tests_taken"] += 1
    save_stats(stats)


def add_test_result(is_correct):
    stats = load_stats()
    stats["tasks_total"] += 1
    stats["test_questions_total"] += 1

    if is_correct:
        stats["correct_total"] += 1
        stats["test_questions_correct"] += 1
    else:
        stats["wrong_total"] += 1
        stats["test_questions_wrong"] += 1

    save_stats(stats)


def add_wrong_training_run():
    stats = load_stats()
    stats["wrong_training_runs"] += 1
    save_stats(stats)


def add_wrong_training_result(is_correct):
    stats = load_stats()
    stats["wrong_training_questions"] += 1

    if is_correct:
        stats["wrong_training_correct"] += 1
    else:
        stats["wrong_training_wrong"] += 1

    save_stats(stats)


def increment_stat(field, amount=1):
    stats = load_stats()
    stats[field] = int(stats.get(field, 0)) + amount
    save_stats(stats)


def save_wrong_answer(sentence, solution, user):
    data = load_wrong_answers()
    item = {
        "sentence": sentence,
        "solution": solution,
        "user_answer": user
    }
    if item not in data:
        data.append(item)
    save_json_file(WRONG_FILE, data)


def remove_wrong_answer(sentence, solution):
    data = load_wrong_answers()
    new_data = []
    for item in data:
        if not (item.get("sentence") == sentence and item.get("solution") == solution):
            new_data.append(item)
    save_json_file(WRONG_FILE, new_data)


def rating_to_point(rating):
    return 1 if rating in ["RICHTIG", "FAST RICHTIG"] else 0


def get_grade(points, total):
    if total <= 0:
        return 6
    percent = (points / total) * 100
    if percent >= 92:
        return 1
    elif percent >= 81:
        return 2
    elif percent >= 67:
        return 3
    elif percent >= 50:
        return 4
    elif percent >= 30:
        return 5
    return 6


# =========================================================
# UI COMPONENTS
# =========================================================

class SidebarTab(tk.Button):
    def __init__(self, master=None, active_bg=ACCENT, inactive_bg=SIDEBAR, hover_bg="#142037", **kwargs):
        super().__init__(master, **kwargs)
        self.active_bg = active_bg
        self.inactive_bg = inactive_bg
        self.hover_bg = hover_bg
        self.is_active = False

        self.configure(
            bg=self.inactive_bg,
            fg=TEXT,
            activebackground=self.hover_bg,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            anchor="w",
            padx=22,
            pady=10,
            highlightthickness=0,
            font=("Segoe UI", 11, "bold")
        )

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def set_active(self, active):
        self.is_active = active
        self.configure(bg=self.active_bg if active else self.inactive_bg)

    def on_enter(self, event):
        if not self.is_active:
            self.configure(bg=self.hover_bg)

    def on_leave(self, event):
        if not self.is_active:
            self.configure(bg=self.inactive_bg)


class AccentButton(tk.Button):
    def __init__(self, master=None, normal_bg=BLUE, hover_bg=BLUE_HOVER, text_color="white", **kwargs):
        super().__init__(master, **kwargs)
        self.normal_bg = normal_bg
        self.hover_bg = hover_bg
        self.text_color = text_color

        self.configure(
            bg=self.normal_bg,
            fg=self.text_color,
            activebackground=self.hover_bg,
            activeforeground=self.text_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=18,
            pady=12,
            font=("Segoe UI", 10, "bold"),
            highlightthickness=0
        )

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        if str(self.cget("state")) != "disabled":
            self.configure(bg=self.hover_bg)

    def on_leave(self, event):
        if str(self.cget("state")) != "disabled":
            self.configure(bg=self.normal_bg)

    def reset_style(self):
        self.configure(
            bg=self.normal_bg,
            fg=self.text_color,
            activebackground=self.hover_bg,
            activeforeground=self.text_color,
            state="normal"
        )


class QuickCard(tk.Frame):
    def __init__(self, master, title, value, accent):
        super().__init__(master, bg=CARD_2, highlightthickness=1, highlightbackground=BORDER, bd=0)
        top = tk.Frame(self, bg=accent, height=5)
        top.pack(fill="x")
        tk.Label(self, text=title, font=("Segoe UI", 11, "bold"), fg=MUTED, bg=CARD_2).pack(anchor="w", padx=18, pady=(14, 6))
        self.value_label = tk.Label(self, text=value, font=("Segoe UI", 21, "bold"), fg=TEXT, bg=CARD_2)
        self.value_label.pack(anchor="w", padx=18, pady=(0, 16))


class HomeActionCard(tk.Frame):
    def __init__(self, master, emoji, title, subtitle, accent, command):
        super().__init__(master, bg=CARD_2, highlightthickness=1, highlightbackground=BORDER, bd=0)
        self.command = command
        self.default_bg = CARD_2
        self.hover_bg = CARD_3

        left = tk.Frame(self, bg=accent, width=10)
        left.pack(side="left", fill="y")

        self.content = tk.Frame(self, bg=self.default_bg)
        self.content.pack(side="left", fill="both", expand=True)

        self.icon = tk.Label(self.content, text=emoji, font=("Segoe UI Emoji", 30), bg=self.default_bg, fg=TEXT)
        self.icon.pack(anchor="w", padx=20, pady=(18, 4))

        self.title = tk.Label(self.content, text=title, font=("Segoe UI", 16, "bold"), bg=self.default_bg, fg=TEXT)
        self.title.pack(anchor="w", padx=20)

        self.subtitle = tk.Label(
            self.content,
            text=subtitle,
            font=("Segoe UI", 11),
            bg=self.default_bg,
            fg=MUTED,
            justify="left"
        )
        self.subtitle.pack(anchor="w", padx=20, pady=(8, 18))

        for w in [self, self.content, self.icon, self.title, self.subtitle]:
            w.bind("<Button-1>", self.run)
            w.bind("<Enter>", self.enter)
            w.bind("<Leave>", self.leave)

    def run(self, event=None):
        self.command()

    def enter(self, event=None):
        self.content.configure(bg=self.hover_bg)
        self.icon.configure(bg=self.hover_bg)
        self.title.configure(bg=self.hover_bg)
        self.subtitle.configure(bg=self.hover_bg)

    def leave(self, event=None):
        self.content.configure(bg=self.default_bg)
        self.icon.configure(bg=self.default_bg)
        self.title.configure(bg=self.default_bg)
        self.subtitle.configure(bg=self.default_bg)


class InfoCard(tk.Frame):
    def __init__(self, master, title):
        super().__init__(master, bg=CARD_2, highlightthickness=1, highlightbackground=BORDER, bd=0)
        tk.Label(self, text=title, font=("Segoe UI", 13, "bold"), fg=TEXT, bg=CARD_2).pack(anchor="w", padx=16, pady=(14, 6))
        self.body = tk.Label(self, text="", justify="left", wraplength=360, font=("Segoe UI", 11), fg=MUTED, bg=CARD_2)
        self.body.pack(anchor="w", padx=16, pady=(0, 14))

    def set_text(self, text):
        self.body.config(text=text)


# =========================================================
# APP
# =========================================================

class EnglishTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English Trainer • Midnight Arcade")
        self.root.geometry("1500x920")
        self.root.minsize(1100, 760)
        self.root.configure(bg=BG)
        try:
            self.root.state("zoomed")
        except Exception:
            pass

        self.client = OpenAI(api_key=API_KEY) if API_KEY else None
        self.offline_mode = not bool(API_KEY)

        self.used_sentences = set()
        self.used_vocab = set()

        self.current_mode = None
        self.current_task = None
        self.current_mc = None
        self.busy = False

        self.test_total = 25
        self.test_index = 0
        self.test_points = 0
        self.test_tense = None
        self.test_direction = None

        self.wrong_data = []
        self.wrong_index = 0

        self.story_pack = None
        self.story_step = 0
        self.build_solution = ""
        self.hunt_target_words = []
        self.hunt_found_words = set()

        self.session_start = time.time()
        self.session_actions = 0
        self.combo_streak = 0
        self.text_size = 15

        self.mode_colors = {
            "home": ACCENT,
            "vocab": BLUE,
            "sentence": CYAN,
            "translate": GREEN,
            "irregular": AMBER,
            "multiple_choice": PINK,
            "test": RED,
            "vocab_test": AMBER,
            "wrong_training": PURPLE,
            "story": ACCENT,
            "build": CYAN,
            "hunt": GREEN,
            "favorites": AMBER,
            "stats": BLUE
        }

        update_profile_day()

        self.build_styles()
        self.build_ui()
        self.bind_keys()
        self.refresh_profile_labels()
        self.refresh_home_side_cards()
        self.start_session_clock()
        self.show_home()
        if self.offline_mode:
            try:
                self.set_status("● Offline Mode", AMBER)
            except Exception:
                pass

    # =========================
    # BUILD
    # =========================

    def build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Dark.Horizontal.TProgressbar",
            troughcolor="#162238",
            background=ACCENT,
            bordercolor="#162238",
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            thickness=12
        )

        style.configure(
            "Level.Horizontal.TProgressbar",
            troughcolor="#162238",
            background=GREEN,
            bordercolor="#162238",
            lightcolor=GREEN,
            darkcolor=GREEN,
            thickness=10
        )

    def make_card(self, parent, bg=CARD_2):
        return tk.Frame(parent, bg=bg, highlightthickness=1, highlightbackground=BORDER, bd=0)


    def build_ui(self):

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=280)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(1, weight=0)
        self.sidebar.grid_rowconfigure(2, weight=1)
        self.sidebar.grid_rowconfigure(3, weight=0)
        self.sidebar.grid_columnconfigure(0, weight=1)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 14))

        tk.Label(brand, text="MIDNIGHT", font=("Segoe UI", 17, "bold"), fg=TEXT, bg=SIDEBAR).pack(anchor="w")
        tk.Label(brand, text="ENGLISH LAB", font=("Segoe UI", 17, "bold"), fg=ACCENT, bg=SIDEBAR).pack(anchor="w")
        tk.Label(brand, text="dark • fresh • arcade vibe", font=("Segoe UI", 9), fg=MUTED, bg=SIDEBAR).pack(anchor="w", pady=(6, 0))

        self.profile_card = self.make_card(self.sidebar, bg=CARD)
        self.profile_card.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))

        tk.Label(self.profile_card, text="Profile", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=CARD).pack(anchor="w", padx=14, pady=(12, 4))
        self.level_label = tk.Label(self.profile_card, text="Level 1", font=("Segoe UI", 15, "bold"), fg=TEXT, bg=CARD)
        self.level_label.pack(anchor="w", padx=14)

        self.xp_label = tk.Label(self.profile_card, text="XP: 0", font=("Segoe UI", 11), fg=CYAN, bg=CARD)
        self.xp_label.pack(anchor="w", padx=14, pady=(4, 2))

        self.goal_label = tk.Label(self.profile_card, text="Goal: 0/20", font=("Segoe UI", 11), fg=GREEN, bg=CARD)
        self.goal_label.pack(anchor="w", padx=14)

        self.streak_label = tk.Label(self.profile_card, text="Streak: 0 | Best: 0", font=("Segoe UI", 11), fg=AMBER, bg=CARD)
        self.streak_label.pack(anchor="w", padx=14, pady=(2, 8))

        tk.Label(self.profile_card, text="Level Progress", font=("Segoe UI", 9, "bold"), fg=MUTED, bg=CARD).pack(anchor="w", padx=14)
        self.level_progress = ttk.Progressbar(self.profile_card, style="Level.Horizontal.TProgressbar", maximum=100, value=0)
        self.level_progress.pack(fill="x", padx=14, pady=(6, 8))

        self.reset_stats_button = AccentButton(
            self.profile_card,
            text="RESET STATS",
            command=lambda: reset_all_stats(self),
            normal_bg=AMBER,
            hover_bg=AMBER_HOVER,
            text_color=TEXT,
            width=16
        )
        self.reset_stats_button.pack(anchor="w", padx=14, pady=(0, 12))

        nav_wrap = tk.Frame(self.sidebar, bg=SIDEBAR)
        nav_wrap.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 8))
        nav_wrap.grid_rowconfigure(0, weight=1)
        nav_wrap.grid_columnconfigure(0, weight=1)

        self.nav_canvas = tk.Canvas(nav_wrap, bg=SIDEBAR, highlightthickness=0, bd=0)
        self.nav_canvas.grid(row=0, column=0, sticky="nsew")

        self.nav_scrollbar = tk.Scrollbar(nav_wrap, orient="vertical", command=self.nav_canvas.yview)
        self.nav_scrollbar.grid(row=0, column=1, sticky="ns")

        self.nav_canvas.configure(yscrollcommand=self.nav_scrollbar.set)
        nav = tk.Frame(self.nav_canvas, bg=SIDEBAR)
        self.nav_window = self.nav_canvas.create_window((0, 0), window=nav, anchor="nw")

        nav.bind("<Configure>", lambda e: self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all")))
        self.nav_canvas.bind("<Configure>", lambda e: self.nav_canvas.itemconfigure(self.nav_window, width=e.width))
        self.nav_canvas.bind_all("<Shift-MouseWheel>", self._on_sidebar_mousewheel)

        self.tab_buttons = []
        tabs = [
            ("🏠  Home", self.show_home),
            ("📘  Vocabulary", self.start_vocab_mode),
            ("🧩  Sentence", self.start_sentence_mode),
            ("🌍  Translate", self.start_translate_mode),
            ("🔁  Irregular Verbs", self.start_irregular_mode),
            ("✅  Multiple Choice", self.start_multiple_choice_mode),
            ("📝  Grammar Test", self.start_test_mode),
            ("📚  Vocab Test", self.start_vocab_test_mode),
            ("🎯  Wrong Training", self.start_wrong_training_mode),
            ("📖  Story Mode", self.start_story_mode),
            ("🧱  Build Sentence", self.start_build_mode),
            ("🎯  Hunt Mode", self.start_hunt_mode),
            ("⭐  Favorites", self.show_favorites_mode),
            ("📊  Statistics", self.show_statistics_mode),
        ]

        for text, command in tabs:
            btn = SidebarTab(nav, text=text, command=command)
            btn.pack(fill="x", pady=4)
            self.tab_buttons.append(btn)

        footer = self.make_card(self.sidebar, bg=CARD)
        footer.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))

        tk.Label(footer, text="Session", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=CARD).pack(anchor="w", padx=14, pady=(12, 4))
        self.session_time_label = tk.Label(footer, text="Time: 00:00", font=("Segoe UI", 11), fg=MUTED, bg=CARD)
        self.session_time_label.pack(anchor="w", padx=14)
        self.session_actions_label = tk.Label(footer, text="Actions: 0", font=("Segoe UI", 11), fg=MUTED, bg=CARD)
        self.session_actions_label.pack(anchor="w", padx=14, pady=(2, 10))

        self.logout_button = AccentButton(
            footer,
            text="LOGOUT",
            command=lambda: logout(self.root),
            normal_bg=RED,
            hover_bg=RED_HOVER,
            width=16
        )
        self.logout_button.pack(anchor="w", padx=14, pady=(0, 12))

        self.main_shell = tk.Frame(self.root, bg=BG)
        self.main_shell.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.main_shell.grid_rowconfigure(0, weight=0)
        self.main_shell.grid_rowconfigure(1, weight=0)
        self.main_shell.grid_rowconfigure(2, weight=1)
        self.main_shell.grid_columnconfigure(0, weight=1)

        self.header_card = self.make_card(self.main_shell, bg=CARD)
        self.header_card.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.header_strip = tk.Frame(self.header_card, bg=ACCENT, height=4)
        self.header_strip.pack(fill="x")

        header_body = tk.Frame(self.header_card, bg=CARD)
        header_body.pack(fill="x", padx=24, pady=(18, 18))

        header_left = tk.Frame(header_body, bg=CARD)
        header_left.pack(side="left", fill="both", expand=True)

        self.header_title = tk.Label(header_left, text="Dashboard", font=("Segoe UI", 24, "bold"), fg=TEXT, bg=CARD)
        self.header_title.pack(anchor="w", pady=(0, 4))

        self.header_subtitle = tk.Label(header_left, text="Welcome back.", font=("Segoe UI", 12), fg=MUTED, bg=CARD)
        self.header_subtitle.pack(anchor="w")

        self.status_label = tk.Label(header_body, text="● Ready", font=("Segoe UI", 11, "bold"), fg=GREEN, bg=CARD)
        self.status_label.pack(side="right", anchor="ne")

        self.stats_strip = tk.Frame(self.main_shell, bg=BG)
        self.stats_strip.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for i in range(5):
            self.stats_strip.grid_columnconfigure(i, weight=1)

        self.quick_cards = []
        qdefs = [
            ("⭐ Level", "1", ACCENT),
            ("⚡ XP", "0", BLUE),
            ("🎯 Goal", "0/20", GREEN),
            ("🔥 Streak", "0", AMBER),
            ("💸 API Cost", "$0.000000", PINK),
        ]

        for i, (title, value, accent) in enumerate(qdefs):
            card = QuickCard(self.stats_strip, title, value, accent)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 10, 0))
            self.quick_cards.append(card.value_label)

        self.content = tk.Frame(self.main_shell, bg=BG)
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.home_frame = tk.Frame(self.content, bg=BG)
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        self.home_frame.grid_rowconfigure(0, weight=1)
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_canvas = tk.Canvas(self.home_frame, bg=BG, highlightthickness=0, bd=0)
        self.home_canvas.grid(row=0, column=0, sticky="nsew")

        self.home_scrollbar = tk.Scrollbar(self.home_frame, orient="vertical", command=self.home_canvas.yview)
        self.home_scrollbar.grid(row=0, column=1, sticky="ns")

        self.home_canvas.configure(yscrollcommand=self.home_scrollbar.set)
        self.home_inner = tk.Frame(self.home_canvas, bg=BG)
        self.home_window = self.home_canvas.create_window((0, 0), window=self.home_inner, anchor="nw")

        self.home_inner.bind("<Configure>", lambda e: self.home_canvas.configure(scrollregion=self.home_canvas.bbox("all")))
        self.home_canvas.bind("<Configure>", self._on_home_canvas_configure)
        self.home_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.work_frame = tk.Frame(self.content, bg=BG)
        self.work_frame.grid(row=0, column=0, sticky="nsew")
        self.work_frame.grid_rowconfigure(0, weight=0)
        self.work_frame.grid_rowconfigure(1, weight=1)
        self.work_frame.grid_rowconfigure(2, weight=0)
        self.work_frame.grid_columnconfigure(0, weight=1)

        self.build_home()
        self.build_work()

        self.root.bind("<Configure>", self._on_root_resize)


    def build_home(self):
        for child in self.home_inner.winfo_children():
            child.destroy()

        self.home_cards = []
        self.home_inner.grid_columnconfigure(0, weight=1)

        hero = self.make_card(self.home_inner, bg=CARD)
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        top = tk.Frame(hero, bg=ACCENT, height=5)
        top.pack(fill="x")

        tk.Label(hero, text="Midnight Arcade Dashboard", font=("Segoe UI", 22, "bold"), fg=TEXT, bg=CARD).pack(anchor="w", padx=22, pady=(18, 6))
        tk.Label(
            hero,
            text="Mehr Platz, Scrollen und automatische Anordnung je nach Fenstergröße.",
            font=("Segoe UI", 11),
            fg=MUTED,
            bg=CARD
        ).pack(anchor="w", padx=22, pady=(0, 18))

        filters = self.make_card(self.home_inner, bg=CARD_2)
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for c in range(5):
            filters.grid_columnconfigure(c, weight=1)
        filters.grid_columnconfigure(5, weight=1)

        self.direction_var = tk.StringVar(value="de_to_en")
        self.tense_var = tk.StringVar(value=TENSES[0])
        self.topic_var = tk.StringVar(value=TOPICS[0])
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        self.difficulty_var = tk.StringVar(value=DIFFICULTIES[1])

        self.make_filter_label(filters, "Direction", 0, 0)
        self.make_filter_label(filters, "Tense", 0, 1)
        self.make_filter_label(filters, "Topic", 0, 2)
        self.make_filter_label(filters, "Model", 0, 3)
        self.make_filter_label(filters, "Difficulty", 0, 4)

        self.direction_menu = tk.OptionMenu(filters, self.direction_var, "de_to_en", "en_to_de")
        self.style_option_menu(self.direction_menu)
        self.direction_menu.grid(row=1, column=0, padx=(20, 10), pady=(0, 18), sticky="ew")

        self.tense_menu = tk.OptionMenu(filters, self.tense_var, *TENSES)
        self.style_option_menu(self.tense_menu)
        self.tense_menu.grid(row=1, column=1, padx=10, pady=(0, 18), sticky="ew")

        self.topic_menu = tk.OptionMenu(filters, self.topic_var, *TOPICS)
        self.style_option_menu(self.topic_menu)
        self.topic_menu.grid(row=1, column=2, padx=10, pady=(0, 18), sticky="ew")

        self.model_menu = tk.OptionMenu(filters, self.model_var, *MODEL_OPTIONS)
        self.style_option_menu(self.model_menu)
        self.model_menu.grid(row=1, column=3, padx=10, pady=(0, 18), sticky="ew")

        self.diff_menu = tk.OptionMenu(filters, self.difficulty_var, *DIFFICULTIES)
        self.style_option_menu(self.diff_menu)
        self.diff_menu.grid(row=1, column=4, padx=10, pady=(0, 18), sticky="ew")

        tip_box = tk.Frame(filters, bg=CARD_2)
        tip_box.grid(row=0, column=5, rowspan=2, sticky="e", padx=20)

        tk.Label(tip_box, text="Live Tip", font=("Segoe UI", 10, "bold"), fg=CYAN, bg=CARD_2).pack(anchor="e", pady=(10, 4))
        tk.Label(
            tip_box,
            text="Layout passt sich jetzt\\nan Breite und Höhe an.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=CARD_2,
            justify="right"
        ).pack(anchor="e")

        lower = tk.Frame(self.home_inner, bg=BG)
        lower.grid(row=2, column=0, sticky="nsew")
        lower.grid_columnconfigure(0, weight=3)
        lower.grid_columnconfigure(1, weight=1)

        left = tk.Frame(lower, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.home_cards_container = left

        right = tk.Frame(lower, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=0)
        right.grid_rowconfigure(1, weight=0)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self.mode_info_card = InfoCard(right, "Mode Spotlight")
        self.mode_info_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.challenge_card = InfoCard(right, "Challenge Ideas")
        self.challenge_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self.model_info_card = InfoCard(right, "Current Setup")
        self.model_info_card.grid(row=2, column=0, sticky="nsew")

        cards = [
            ("📘", "Vocabulary", "Single-word translation", BLUE, self.start_vocab_mode),
            ("🧩", "Sentence", "Full sentence practice", CYAN, self.start_sentence_mode),
            ("🌍", "Translate", "Your own text", GREEN, self.start_translate_mode),
            ("🔁", "Irregular", "Verb forms drill", AMBER, self.start_irregular_mode),
            ("✅", "Multi Choice", "Fast clicking mode", PINK, self.start_multiple_choice_mode),
            ("📝", "Grammar Test", "25 gap-fill tasks", RED, self.start_test_mode),
            ("📚", "Vocab Test", "10 word test", AMBER, self.start_vocab_test_mode),
            ("🎯", "Wrong Training", "Saved mistakes", PURPLE, self.start_wrong_training_mode),
            ("📖", "Story Mode", "Mini scenario mission", ACCENT, self.start_story_mode),
            ("🧱", "Build Sentence", "Rebuild shuffled words", CYAN, self.start_build_mode),
            ("🎯", "Hunt Mode", "Find theme words", GREEN, self.start_hunt_mode),
            ("⭐", "Favorites", "Saved tasks", AMBER, self.show_favorites_mode),
            ("📊", "Statistics", "Progress & cost", BLUE, self.show_statistics_mode),
        ]

        for emoji, title, subtitle, accent, command in cards:
            card = HomeActionCard(self.home_cards_container, emoji, title, subtitle, accent, command)
            self.home_cards.append(card)

        self.arrange_home_cards()

    def build_work(self):

        middle = tk.Frame(self.work_frame, bg=BG)
        middle.grid(row=1, column=0, sticky="nsew", pady=(0, 18))
        middle.grid_rowconfigure(0, weight=1)
        middle.grid_columnconfigure(0, weight=3)
        middle.grid_columnconfigure(1, weight=2)

        self.task_card = self.make_card(middle, bg=CARD)
        self.task_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        tk.Label(self.task_card, text="Mission Feed", font=("Segoe UI", 16, "bold"), fg=TEXT, bg=CARD).pack(anchor="w", padx=18, pady=(16, 8))

        self.output = scrolledtext.ScrolledText(
            self.task_card,
            font=("Consolas", 13),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            wrap="word",
            relief="flat",
            bd=0
        )
        self.output.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.output.config(state="disabled")

        self.result_card = self.make_card(middle, bg=CARD_2)
        self.result_card.grid(row=0, column=1, sticky="nsew")
        tk.Label(self.result_card, text="Feedback Panel", font=("Segoe UI", 16, "bold"), fg=TEXT, bg=CARD_2).pack(anchor="w", padx=18, pady=(16, 8))

        self.result_text = scrolledtext.ScrolledText(
            self.result_card,
            font=("Consolas", 12),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            wrap="word",
            relief="flat",
            bd=0
        )
        self.result_text.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.result_text.config(state="disabled")

        self.action_card = self.make_card(self.work_frame, bg=CARD)
        self.action_card.grid(row=2, column=0, sticky="ew")
        self.action_card.grid_columnconfigure(0, weight=1)

        self.entry_label = tk.Label(self.action_card, text="Input Console", font=("Segoe UI", 13, "bold"), fg=TEXT, bg=CARD)
        self.entry_label.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 10))

        self.answer_text = tk.Text(
            self.action_card,
            height=7,
            font=("Segoe UI", 15),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            bd=14,
            wrap="word"
        )
        self.answer_text.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 14))

        self.button_row = tk.Frame(self.action_card, bg=CARD)
        self.button_row.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 14))

        self.submit_button = AccentButton(self.button_row, text="SUBMIT", command=self.submit_action, normal_bg=BLUE, hover_bg=BLUE_HOVER, width=12)
        self.submit_button.pack(side="left", padx=(0, 8))

        self.next_button = AccentButton(self.button_row, text="NEXT", command=self.next_action, normal_bg=GREEN, hover_bg=GREEN_HOVER, width=12)
        self.next_button.pack(side="left", padx=(0, 8))

        self.clear_button = AccentButton(self.button_row, text="CLEAR", command=self.clear_entry, normal_bg=RED, hover_bg=RED_HOVER, width=12)
        self.clear_button.pack(side="left", padx=(0, 8))

        self.hint_button = AccentButton(self.button_row, text="HINT", command=self.show_hint, normal_bg=PURPLE, hover_bg=PURPLE_HOVER, width=12)
        self.hint_button.pack(side="left", padx=(0, 8))

        self.answer_button = AccentButton(self.button_row, text="SHOW ANSWER", command=self.show_answer_now, normal_bg=AMBER, hover_bg=AMBER_HOVER, text_color=TEXT, width=14)
        self.answer_button.pack(side="left", padx=(0, 8))

        self.favorite_button = AccentButton(self.button_row, text="SAVE TASK", command=self.save_current_favorite, normal_bg=AMBER, hover_bg=AMBER_HOVER, text_color=TEXT, width=12)
        self.favorite_button.pack(side="left", padx=(0, 8))

        self.zoom_in_button = AccentButton(self.button_row, text="A+", command=lambda: self.change_text_size(1), normal_bg=CYAN, hover_bg=CYAN_HOVER, width=5)
        self.zoom_in_button.pack(side="left", padx=(0, 8))

        self.zoom_out_button = AccentButton(self.button_row, text="A-", command=lambda: self.change_text_size(-1), normal_bg=CYAN, hover_bg=CYAN_HOVER, width=5)
        self.zoom_out_button.pack(side="left")

        self.progress_text = tk.Label(self.action_card, text="", font=("Segoe UI", 11), fg=MUTED, bg=CARD)
        self.progress_text.grid(row=2, column=0, sticky="e", padx=20, pady=(0, 4))

        self.progress_bar = ttk.Progressbar(self.action_card, style="Dark.Horizontal.TProgressbar", mode="determinate", maximum=100, value=0)
        self.progress_bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 14))

        self.option_frame = tk.Frame(self.action_card, bg=CARD)
        self.option_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 12))
        self.option_frame.grid_columnconfigure(0, weight=1)
        self.option_frame.grid_columnconfigure(1, weight=1)

        self.option_buttons = []
        defs = [
            (BLUE, BLUE_HOVER, "white"),
            (CYAN, CYAN_HOVER, "white"),
            (GREEN, GREEN_HOVER, "white"),
            (PINK, PINK_HOVER, "white"),
        ]

        for i, (bg, hover, fg) in enumerate(defs):
            btn = AccentButton(
                self.option_frame,
                text="",
                normal_bg=bg,
                hover_bg=hover,
                text_color=fg,
                width=28,
                height=2
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="ew")
            btn.grid_remove()
            self.option_buttons.append(btn)

        self.hunt_option_buttons = []
        for col in range(4):
            self.option_frame.grid_columnconfigure(col, weight=1)

        hunt_defs = [
            (BLUE, BLUE_HOVER),
            (CYAN, CYAN_HOVER),
            (GREEN, GREEN_HOVER),
            (PINK, PINK_HOVER),
            (AMBER, AMBER_HOVER),
            (PURPLE, PURPLE_HOVER),
            (BLUE, BLUE_HOVER),
            (CYAN, CYAN_HOVER),
            (GREEN, GREEN_HOVER),
            (PINK, PINK_HOVER),
            (AMBER, AMBER_HOVER),
            (PURPLE, PURPLE_HOVER),
        ]

        for i, (bg, hover) in enumerate(hunt_defs):
            btn = AccentButton(
                self.option_frame,
                text="",
                normal_bg=bg,
                hover_bg=hover,
                text_color="white",
                width=16,
                height=2
            )
            btn.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="ew")
            btn.grid_remove()
            self.hunt_option_buttons.append(btn)


    def _on_home_canvas_configure(self, event):
        self.home_canvas.itemconfigure(self.home_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.home_frame.winfo_ismapped():
            self.home_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_sidebar_mousewheel(self, event):
        if getattr(self, "nav_canvas", None) and self.nav_canvas.winfo_exists():
            self.nav_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_root_resize(self, event):
        if getattr(self, "home_frame", None) and self.home_frame.winfo_exists():
            self.arrange_home_cards()

    def arrange_home_cards(self):
        if not getattr(self, "home_cards", None):
            return

        width = self.home_cards_container.winfo_width()
        if width <= 1:
            self.root.after(100, self.arrange_home_cards)
            return

        if width >= 1200:
            cols = 3
        elif width >= 760:
            cols = 2
        else:
            cols = 1

        for child in self.home_cards_container.winfo_children():
            child.grid_forget()

        for c in range(4):
            self.home_cards_container.grid_columnconfigure(c, weight=0)
        for c in range(cols):
            self.home_cards_container.grid_columnconfigure(c, weight=1, uniform="homecols")

        for i, card in enumerate(self.home_cards):
            card.grid(row=i // cols, column=i % cols, sticky="nsew", padx=8, pady=8)

    # =========================
    # GENERAL UI HELPERS
    # =========================

    def bind_keys(self):
        self.root.bind("<Return>", self.on_enter)
        self.root.bind("<Control-s>", lambda e: self.save_current_favorite())
        self.root.bind("<Control-plus>", lambda e: self.change_text_size(1))
        self.root.bind("<Control-minus>", lambda e: self.change_text_size(-1))

    def on_enter(self, event):
        if self.current_mode == "multiple_choice":
            return
        self.submit_action()

    def set_active_tab(self, name):
        mapping = {
            "home": 0,
            "vocab": 1,
            "sentence": 2,
            "translate": 3,
            "irregular": 4,
            "multiple_choice": 5,
            "test": 6,
            "vocab_test": 7,
            "wrong_training": 8,
            "story": 9,
            "build": 10,
            "hunt": 11,
            "favorites": 12,
            "stats": 13
        }
        active_index = mapping.get(name, -1)
        for i, btn in enumerate(self.tab_buttons):
            btn.set_active(i == active_index)

    def refresh_profile_labels(self):
        profile = load_profile()
        stats = load_stats()

        self.level_label.config(text=f"Level {profile['level']}")
        self.xp_label.config(text=f"XP: {profile['xp']}")
        self.goal_label.config(text=f"Goal: {profile['today_done']}/{profile['daily_goal']}")
        self.streak_label.config(text=f"Streak: {profile['streak']} | Best: {profile['best_streak']}")

        level_progress = profile["xp"] % 100
        self.level_progress["value"] = level_progress

        self.quick_cards[0].config(text=str(profile["level"]))
        self.quick_cards[1].config(text=str(profile["xp"]))
        self.quick_cards[2].config(text=f"{profile['today_done']}/{profile['daily_goal']}")
        self.quick_cards[3].config(text=str(profile["streak"]))
        self.quick_cards[4].config(text=f"${stats.get('api_cost_usd', 0.0):.6f}")

    def refresh_home_side_cards(self):
        self.mode_info_card.set_text(
            "Story Mode:\nmini missions with scenes.\n\n"
            "Build Sentence:\nrebuild shuffled words.\n\n"
            "Hunt Mode:\nfind topic words as fast as you can."
        )
        favorites_count = len(load_favorites())
        stats = load_stats()
        self.challenge_card.set_text(
            "Try this today:\n"
            "• 1 Story run\n"
            "• 1 Build Sentence round\n"
            "• 1 Hunt Mode challenge\n"
            f"• Best combo: {stats.get('combo_best', 0)}\n"
            f"• Favorites saved: {favorites_count}"
        )
        self.model_info_card.set_text(
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Topic: {self.topic_var.get()}\n"
            f"Direction: {self.direction_var.get()}\n"
            f"Tense: {self.tense_var.get()}"
        )

    def set_header(self, title, subtitle):
        self.header_title.config(text=title)
        self.header_subtitle.config(text=subtitle)

    def set_mode_theme(self, mode_name):
        color = self.mode_colors.get(mode_name, ACCENT)
        self.header_strip.config(bg=color)
        self.status_label.config(fg=color)

    def set_status(self, text, color=ACCENT):
        self.status_label.config(text=text, fg=color)

    def set_progress_text(self, text=""):
        self.progress_text.config(text=text)

    def set_progress_bar(self, current=0, total=100):
        if total <= 0:
            self.progress_bar["value"] = 0
        else:
            self.progress_bar["value"] = (current / total) * 100

    def set_output(self, text):
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state="disabled")

    def set_result(self, text):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state="disabled")

    def change_text_size(self, delta):
        self.text_size = max(11, min(22, self.text_size + delta))
        self.answer_text.config(font=("Segoe UI", self.text_size))
        self.output.config(font=("Consolas", max(11, self.text_size - 2)))
        self.result_text.config(font=("Consolas", max(10, self.text_size - 3)))
        self.set_status(f"● Text size: {self.text_size}", CYAN)

    def save_current_favorite(self):
        if not self.current_task:
            self.set_result("No task loaded to save.")
            return

        favorites = load_favorites()
        item = {
            "mode": self.current_mode or "unknown",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "prompt": self.current_task.get("word") or self.current_task.get("sentence") or self.current_task.get("Frage") or self.current_task.get("text") or str(self.current_task),
            "solution": self.current_task.get("solution") or self.current_task.get("translation") or self.current_task.get("Lösung") or "",
        }
        if item not in favorites:
            favorites.insert(0, item)
            favorites = favorites[:50]
            save_favorites(favorites)
            increment_stat("favorites_saved", 1)
            self.refresh_home_side_cards()
            self.set_result(f"Saved to favorites.\n\nMode: {item['mode']}\nPrompt: {item['prompt']}\nSolution: {item['solution']}")
        else:
            self.set_result("This task is already in favorites.")

    def show_favorites_mode(self):
        self.show_work()
        self.set_active_tab("favorites")
        self.set_mode_theme("favorites")
        self.current_mode = "favorites"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="disabled")
        self.set_header("Favorites", "Your saved tasks and answers.")
        self.entry_label.config(text="Favorites")
        self.set_progress_text("")
        self.set_progress_bar(0, 100)

        favorites = load_favorites()
        if not favorites:
            self.set_output("No favorites saved yet. Use SAVE TASK during practice.")
            self.set_result("Favorites are empty.")
            return

        lines = []
        for idx, item in enumerate(favorites[:20], start=1):
            lines.append(
                f"{idx}. [{item.get('mode', 'unknown')}] {item.get('prompt', '')}\n"
                f"   Answer: {item.get('solution', '')}\n"
                f"   Saved: {item.get('created', '')}"
            )
        self.set_output("Saved favorites:\n\n" + "\n\n".join(lines))
        self.set_result("Tip: Press Ctrl+S while a task is open to save it.")

    def clear_entry(self):
        state = str(self.answer_text.cget("state"))
        if state == "disabled":
            self.answer_text.config(state="normal")
            self.answer_text.delete("1.0", tk.END)
            self.answer_text.config(state="disabled")
        else:
            self.answer_text.delete("1.0", tk.END)
            self.answer_text.focus_set()

    def get_user_text(self):
        return self.answer_text.get("1.0", tk.END).strip()

    def hide_option_buttons(self):
        for btn in self.option_buttons:
            btn.grid_remove()
        self.hide_hunt_buttons()

    def reset_option_buttons(self):
        defs = [
            (BLUE, BLUE_HOVER, "white"),
            (CYAN, CYAN_HOVER, "white"),
            (GREEN, GREEN_HOVER, "white"),
            (PINK, PINK_HOVER, "white"),
        ]
        for btn, (bg, hover, fg) in zip(self.option_buttons, defs):
            btn.normal_bg = bg
            btn.hover_bg = hover
            btn.text_color = fg
            btn.reset_style()

    def show_text_input(self):
        self.answer_text.grid()
        for widget, kwargs in [
            (self.submit_button, {"side": "left", "padx": (0, 8)}),
            (self.next_button, {"side": "left", "padx": (0, 8)}),
            (self.clear_button, {"side": "left", "padx": (0, 8)}),
            (self.hint_button, {"side": "left", "padx": (0, 8)}),
            (self.answer_button, {"side": "left", "padx": (0, 8)}),
            (self.favorite_button, {"side": "left", "padx": (0, 8)}),
            (self.zoom_in_button, {"side": "left", "padx": (0, 8)}),
            (self.zoom_out_button, {"side": "left"}),
        ]:
            try:
                widget.pack_forget()
                widget.pack(**kwargs)
            except Exception:
                pass
        self.clear_button.config(state="normal")
        self.hint_button.config(state="normal")
        self.answer_button.config(state="normal")

    def show_multiple_choice_options(self):
        self.answer_text.grid_remove()
        for widget in [
            self.submit_button,
            self.clear_button,
            self.hint_button,
            self.answer_button,
            self.favorite_button,
            self.zoom_in_button,
            self.zoom_out_button,
        ]:
            try:
                widget.pack_forget()
            except Exception:
                pass
        try:
            self.next_button.pack_forget()
            self.next_button.pack(side="left", padx=(0, 8))
        except Exception:
            pass
        self.hide_hunt_buttons()
        for btn in self.option_buttons:
            btn.grid()

    def hide_hunt_buttons(self):
        if hasattr(self, "hunt_option_buttons"):
            for btn in self.hunt_option_buttons:
                btn.grid_remove()

    def show_hunt_options(self):
        self.answer_text.grid_remove()
        self.clear_button.config(state="disabled")
        self.hint_button.config(state="disabled")
        self.answer_button.config(state="disabled")
        self.hide_option_buttons()
        for btn in getattr(self, "hunt_option_buttons", []):
            btn.grid()

    def flash_result_card(self, success=True):
        normal_color = CARD_2
        flash_color = "#12331f" if success else "#41161a"

        steps = 8
        delay = 38

        def animate(step=0):
            if step >= steps:
                self.result_card.configure(bg=normal_color)
                for child in self.result_card.winfo_children():
                    try:
                        child.configure(bg=normal_color)
                    except Exception:
                        pass
                return

            color = flash_color if step % 2 == 0 else normal_color
            self.result_card.configure(bg=color)
            for child in self.result_card.winfo_children():
                try:
                    child.configure(bg=color)
                except Exception:
                    pass

            self.root.after(delay, lambda: animate(step + 1))

        animate()

    def show_xp_popup(self, text="+10 XP", color=GREEN):
        popup = tk.Label(
            self.main_shell,
            text=text,
            font=("Segoe UI", 16, "bold"),
            fg=color,
            bg=BG
        )
        popup.place(relx=0.82, rely=0.10, anchor="center")

        steps = 18
        start_y = 0.10
        end_y = 0.04

        def animate(step=0):
            if step > steps:
                popup.destroy()
                return

            y = start_y - ((start_y - end_y) * (step / steps))
            popup.place(relx=0.82, rely=y, anchor="center")
            self.root.after(25, lambda: animate(step + 1))

        animate()

    def reward_xp(self, is_correct):
        xp = 10 if is_correct else 3
        if is_correct:
            self.combo_streak += 1
            if self.combo_streak > load_stats().get("combo_best", 0):
                stats = load_stats()
                stats["combo_best"] = self.combo_streak
                save_stats(stats)
            if self.combo_streak and self.combo_streak % 5 == 0:
                xp += 15
        else:
            self.combo_streak = 0

        add_xp(xp)
        self.session_actions += 1
        self.refresh_profile_labels()
        self.refresh_home_side_cards()
        popup_text = f"+{xp} XP" if self.combo_streak % 5 != 0 or not is_correct else f"+{xp} XP • Combo x{self.combo_streak}"
        self.show_xp_popup(popup_text, GREEN if is_correct else AMBER)

    def show_hint(self):
        if not self.current_task:
            self.set_result("No task loaded for hint.")
            return

        solution = self.current_task.get("solution", "")
        if not solution:
            self.set_result("No hint available.")
            return

        hint = self.make_hint(solution)
        old = self.result_text.get("1.0", tk.END).strip()
        self.set_result(old + f"\n\nHint:\n{hint}" if old else f"Hint:\n{hint}")

    def make_hint(self, solution):
        parts = solution.split()
        if len(parts) == 1:
            word = solution.strip()
            if len(word) <= 2:
                return f"Starts with: {word[:1]}..."
            return f"Starts with: {word[:2]}... | Length: {len(word)}"
        start = " ".join(parts[:2])
        return f"Starts like: {start}..."

    def show_answer_now(self):
        if not self.current_task:
            self.set_result("No task loaded.")
            return

        solution = self.current_task.get("solution", "")
        if not solution:
            self.set_result("No answer available.")
            return

        self.set_result(f"Answer:\n{solution}")

    def save_test_history_item(self, points, total, grade):
        history = load_test_history()
        history.insert(0, {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "points": points,
            "total": total,
            "grade": grade
        })
        history = history[:10]
        save_test_history(history)

    def start_session_clock(self):
        def update_clock():
            elapsed = int(time.time() - self.session_start)
            mins = elapsed // 60
            secs = elapsed % 60
            self.session_time_label.config(text=f"Time: {mins:02d}:{secs:02d}")
            self.session_actions_label.config(text=f"Actions: {self.session_actions}")
            self.root.after(1000, update_clock)
        update_clock()

    def style_option_menu(self, menu):
        menu.config(
            width=14,
            bg=INPUT_BG,
            fg=TEXT,
            activebackground="#19253d",
            activeforeground=TEXT,
            relief="flat",
            font=("Segoe UI", 11),
            highlightthickness=0
        )
        try:
            menu["menu"].config(
                bg=INPUT_BG,
                fg=TEXT,
                activebackground="#19253d",
                activeforeground=TEXT,
                relief="flat",
                font=("Segoe UI", 10)
            )
        except Exception:
            pass

    def make_filter_label(self, parent, text, row, col):
        tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"), fg=TEXT, bg=CARD_2).grid(
            row=row, column=col, padx=(18 if col == 0 else 10, 10), pady=(16, 6), sticky="w"
        )

    def show_home(self):
        self.current_mode = None
        self.set_active_tab("home")
        self.home_frame.tkraise()
        self.set_mode_theme("home")
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.hide_option_buttons()
        self.clear_entry()
        self.refresh_profile_labels()
        self.refresh_home_side_cards()
        self.set_header("Dashboard", "Fresh dark redesign with story, build and hunt gameplay modes.")
        self.set_progress_text("")
        self.set_progress_bar(0, 100)

        self.set_output(
            "Welcome to Midnight Arcade.\n\n"
            "New highlights:\n"
            "- Story Mode = mini scenarios\n"
            "- Build Sentence = shuffled word challenge\n"
            "- Hunt Mode = theme word hunt\n"
            "- new dark UI\n"
            "- model + difficulty filters\n"
            "- SAVE TASK favorites\n"
            "- offline fallback practice\n"
            "- text zoom A+ / A-\n\n"
            f"Current model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n\n"
            "Pick a mode from the dashboard or sidebar."
        )
        self.set_result("Result will appear here.")
        self.entry_label.config(text="Input Console")
        self.answer_text.focus_set()

    def show_work(self):
        self.work_frame.tkraise()

    # =========================
    # ASYNC / API
    # =========================

    def run_async(self, func, callback):
        if self.busy:
            return

        self.busy = True
        self.submit_button.config(state="disabled")
        self.next_button.config(state="disabled")
        self.hint_button.config(state="disabled")
        self.answer_button.config(state="disabled")
        self.set_status("● Loading...", CYAN)

        def worker():
            try:
                result = func()
                self.root.after(0, lambda: self.finish_async(callback, result))
            except Exception as e:
                self.root.after(0, lambda: self.finish_async(callback, {"error": str(e)}))

        threading.Thread(target=worker, daemon=True).start()

    def finish_async(self, callback, result):
        self.busy = False
        self.submit_button.config(state="normal")
        self.next_button.config(state="normal")

        if self.current_mode == "multiple_choice":
            self.clear_button.config(state="disabled")
            self.hint_button.config(state="disabled")
            self.answer_button.config(state="disabled")
        else:
            self.clear_button.config(state="normal")
            self.hint_button.config(state="normal")
            self.answer_button.config(state="normal")

        self.refresh_profile_labels()
        self.refresh_home_side_cards()
        self.set_status("● Ready", GREEN)
        callback(result)
        self.refresh_profile_labels()
        self.refresh_home_side_cards()

        if self.current_mode != "multiple_choice":
            self.answer_text.focus_set()

    def ask_model(self, prompt):
        if not self.client:
            return "FEHLER: OFFLINE_MODE"
        try:
            selected_model = self.model_var.get() if hasattr(self, "model_var") else DEFAULT_MODEL

            response = self.client.responses.create(
                model=selected_model,
                input=prompt
            )

            usage = getattr(response, "usage", None)
            if usage:
                input_tokens = getattr(usage, "input_tokens", 0) or 0
                output_tokens = getattr(usage, "output_tokens", 0) or 0
                add_api_usage(selected_model, input_tokens, output_tokens)
                try:
                    self.root.after(0, self.refresh_profile_labels)
                    self.root.after(0, self.refresh_home_side_cards)
                except Exception:
                    pass

            text = getattr(response, "output_text", "")
            return text.strip() if text else ""
        except Exception as e:
            return f"FEHLER: {e}"

    def is_bad_text(self, text):
        return (not text) or str(text).startswith("FEHLER:")

    def require_live_generation(self):
        if not API_KEY:
            return "Offline mode aktiv. Diese Aufgabe wird lokal erzeugt."
        return ""

    def get_local_vocab_task(self, direction, topic):
        topic = resolve_topic(topic)

        if FILE_VOCAB_BY_TOPIC or FILE_VOCAB_ALL:
            pool = []
            if topic in FILE_VOCAB_BY_TOPIC and FILE_VOCAB_BY_TOPIC.get(topic):
                pool = FILE_VOCAB_BY_TOPIC[topic]
            elif FILE_VOCAB_ALL:
                pool = FILE_VOCAB_ALL
            if pool:
                de, en = random.choice(pool)
                if direction == "de_to_en":
                    return {"word": de, "solution": en, "topic": topic}
                return {"word": en, "solution": de, "topic": topic}

        local_pool = LOCAL_VOCAB.get(topic)
        if not local_pool:
            local_pool = random.choice(list(LOCAL_VOCAB.values()))
        de, en = random.choice(local_pool)
        if direction == "de_to_en":
            return {"word": de, "solution": en, "topic": topic}
        return {"word": en, "solution": de, "topic": topic}

    def get_local_sentence_task(self, direction, tense):
        tense = tense if tense in TENSES else "mixed"

        if FILE_SENTENCES_BY_TENSE or FILE_SENTENCES_ALL:
            pool = FILE_SENTENCES_BY_TENSE.get(tense) or FILE_SENTENCES_BY_TENSE.get("mixed") or FILE_SENTENCES_ALL
            if pool:
                de, en = random.choice(pool)
                if direction == "de_to_en":
                    return {"sentence": de, "solution": en, "topic": "mixed"}
                return {"sentence": en, "solution": de, "topic": "mixed"}

        tense_key = tense if tense in LOCAL_SENTENCES else "mixed"
        de, en = random.choice(LOCAL_SENTENCES.get(tense_key, LOCAL_SENTENCES["mixed"]))
        if direction == "de_to_en":
            return {"sentence": de, "solution": en, "topic": "mixed"}
        return {"sentence": en, "solution": de, "topic": "mixed"}

    def get_local_multiple_choice(self, direction, topic):
        topic = resolve_topic(topic)

        if FILE_MULTIPLE_CHOICE:
            item = random.choice(FILE_MULTIPLE_CHOICE).copy()
            item["topic"] = item.get("topic") or topic
            return item

        pool = []
        if topic in FILE_VOCAB_BY_TOPIC and FILE_VOCAB_BY_TOPIC.get(topic):
            pool = FILE_VOCAB_BY_TOPIC[topic]
        elif FILE_VOCAB_ALL:
            pool = FILE_VOCAB_ALL
        else:
            pool = LOCAL_VOCAB.get(topic) or random.choice(list(LOCAL_VOCAB.values()))

        correct_de, correct_en = random.choice(pool)
        wrongs = random.sample([p for p in pool if p != (correct_de, correct_en)], k=min(3, max(1, len(pool)-1)))
        while len(wrongs) < 3:
            fallback_pool = FILE_VOCAB_ALL if FILE_VOCAB_ALL else random.choice(list(LOCAL_VOCAB.values()))
            wrongs.append(random.choice(fallback_pool))
        if direction == "de_to_en":
            question = correct_de
            options = [correct_en] + [en for _, en in wrongs[:3]]
        else:
            question = correct_en
            options = [correct_de] + [de for de, _ in wrongs[:3]]
        random.shuffle(options)
        letters = ["A", "B", "C", "D"]
        answer_letter = letters[options.index(correct_en if direction == "de_to_en" else correct_de)]
        return {"Frage": question, "A": options[0], "B": options[1], "C": options[2], "D": options[3], "Lösung": answer_letter, "topic": topic}

    def get_local_story_pack(self, topic):
        return random.choice(STORY_PACKS)

    def get_local_build_challenge(self, difficulty):
        pool = FILE_BUILD_SENTENCES or BUILD_SENTENCE_POOL.get(difficulty, BUILD_SENTENCE_POOL["medium"])
        sentence = random.choice(pool)
        words = sentence.split()
        random.shuffle(words)
        return {"sentence": " | ".join(words), "solution": sentence}

    def get_local_hunt_challenge(self, topic, difficulty):
        topic = resolve_topic(topic)
        goal = {"easy": 4, "medium": 5, "hard": 6}[difficulty]
        total_words = 12

        if topic in FILE_HUNT_BY_TOPIC and FILE_HUNT_BY_TOPIC.get(topic):
            correct_pool = list(dict.fromkeys(FILE_HUNT_BY_TOPIC[topic]))
        else:
            correct_pool = list(dict.fromkeys(HUNT_WORDS.get(topic, HUNT_WORDS["school"])))

        random.shuffle(correct_pool)
        correct_words = correct_pool[:goal]

        wrong_pool = []
        if FILE_HUNT_ALL:
            wrong_pool = [w for w in dict.fromkeys(FILE_HUNT_ALL) if w not in correct_words]
        else:
            for t, words in HUNT_WORDS.items():
                if t != topic:
                    wrong_pool.extend(words)
            wrong_pool = [w for w in dict.fromkeys(wrong_pool) if w not in correct_words]

        random.shuffle(wrong_pool)
        wrong_words = wrong_pool[: max(0, total_words - goal)]
        words = correct_words + wrong_words
        random.shuffle(words)
        return {
            "topic": topic,
            "goal": goal,
            "correct_words": correct_words,
            "wrong_words": wrong_words,
            "words": words,
        }

    # =========================
    # GENERATORS
    # =========================

    def generate_vocab(self, direction, topic):
        topic = resolve_topic(topic)
        difficulty = self.difficulty_var.get()

        if not self.client:
            for _ in range(30):
                task = self.get_local_vocab_task(direction, topic)
                key = normalize_text(task["word"])
                if key not in self.used_vocab:
                    self.used_vocab.add(key)
                    return task
            return self.get_local_vocab_task(direction, topic)

        if direction == "de_to_en":
            source = "German"
            target = "English"
            label_word = "Wort"
            label_solution = "Lösung"
        else:
            source = "English"
            target = "German"
            label_word = "Word"
            label_solution = "Solution"

        if difficulty == "easy":
            extra_rule = "Use a very common beginner word."
        elif difficulty == "medium":
            extra_rule = "Use a common learner-friendly word."
        else:
            extra_rule = "Use a less basic but still useful word."

        used_text = " | ".join(list(self.used_vocab)[-20:]) if self.used_vocab else "none"

        for _ in range(8):
            prompt = f"""
Create exactly one vocabulary exercise.

Rules:
- Source language: {source}
- Target language: {target}
- Category: {topic}
- Difficulty: {difficulty}
- {extra_rule}
- Use exactly one word
- Do not use articles
- Do not use "to" before verbs
- Do not repeat these words: {used_text}

Return exactly in this format:
{label_word}: ...
{label_solution}: ...
"""
            text = self.ask_model(prompt)

            if self.is_bad_text(text):
                continue

            word = ""
            solution = ""

            for line in text.splitlines():
                if line.startswith(f"{label_word}:"):
                    word = line.replace(f"{label_word}:", "").strip()
                elif line.startswith(f"{label_solution}:"):
                    solution = line.replace(f"{label_solution}:", "").strip()

            key = normalize_text(word)

            if word and solution and key not in self.used_vocab:
                self.used_vocab.add(key)
                return {"word": word, "solution": solution, "topic": topic}

        return {"error": self.require_live_generation() or "FEHLER: Keine neue Vokabelaufgabe erzeugt."}

    def generate_sentence(self, direction, tense, topic):
        topic = resolve_topic(topic)
        difficulty = self.difficulty_var.get()

        if not self.client:
            for _ in range(30):
                task = self.get_local_sentence_task(direction, tense)
                key = normalize_text(task["sentence"])
                if key not in self.used_sentences:
                    self.used_sentences.add(key)
                    task["topic"] = topic
                    return task
            task = self.get_local_sentence_task(direction, tense)
            task["topic"] = topic
            return task

        if direction == "de_to_en":
            source = "German"
            target = "English"
            label_text = "Satz"
            label_solution = "Lösung"
        else:
            source = "English"
            target = "German"
            label_text = "Sentence"
            label_solution = "Solution"

        styles = ["statement", "question", "negative sentence", "sentence with time expression"]

        if difficulty == "easy":
            diff_rule = "Keep it short and easy."
        elif difficulty == "medium":
            diff_rule = "Make it natural and medium difficulty."
        else:
            diff_rule = "Make it longer or slightly more complex."

        used_text = " | ".join(list(self.used_sentences)[-15:]) if self.used_sentences else "none"

        for _ in range(8):
            style = random.choice(styles)

            prompt = f"""
Create exactly one translation sentence exercise.

Rules:
- Source language: {source}
- Target language: {target}
- Grammar focus: {tense}
- Topic: {topic}
- Style: {style}
- Difficulty: {difficulty}
- {diff_rule}
- Do not repeat these sentences: {used_text}

Return exactly in this format:
{label_text}: ...
{label_solution}: ...
"""
            text = self.ask_model(prompt)

            if self.is_bad_text(text):
                continue

            sentence = ""
            solution = ""

            for line in text.splitlines():
                if line.startswith(f"{label_text}:"):
                    sentence = line.replace(f"{label_text}:", "").strip()
                elif line.startswith(f"{label_solution}:"):
                    solution = line.replace(f"{label_solution}:", "").strip()

            key = normalize_text(sentence)

            if sentence and solution and key not in self.used_sentences:
                self.used_sentences.add(key)
                return {"sentence": sentence, "solution": solution, "topic": topic}

        return {"error": self.require_live_generation() or "FEHLER: Keine neue Satzaufgabe erzeugt."}

    def generate_gap_fill_sentence(self, direction, tense, topic):
        topic = resolve_topic(topic)
        difficulty = self.difficulty_var.get()

        if not self.client:
            base = self.get_local_sentence_task(direction, tense)
            solution_sentence = base["solution"]
            words = solution_sentence.split()
            if not words:
                return {"error": "Keine lokale Testfrage verfügbar."}
            idx = 0
            for i, word in enumerate(words):
                clean = word.strip(".,!?")
                if clean:
                    idx = i
                    break
            missing = words[idx].strip(".,!?")
            words[idx] = "______"
            sentence = " ".join(words)
            sentence += f" ({missing.lower()})"
            return {"sentence": sentence, "solution": missing, "topic": topic}

        if direction == "de_to_en":
            source = "German"
            sentence_label = "Satz"
            solution_label = "Lösung"
        else:
            source = "English"
            sentence_label = "Sentence"
            solution_label = "Solution"

        diff_rule = {
            "easy": "Keep the sentence short.",
            "medium": "Keep the sentence natural.",
            "hard": "Make the sentence a bit more complex."
        }[difficulty]

        used_text = " | ".join(list(self.used_sentences)[-15:]) if self.used_sentences else "none"

        for _ in range(8):
            prompt = f"""
Create exactly one gap-fill exercise.

Rules:
- Source language: {source}
- Grammar focus: {tense}
- Topic: {topic}
- Difficulty: {difficulty}
- {diff_rule}
- Make one sentence with exactly one gap like this: ______
- Put the verb in infinitive form directly after the gap in brackets like this: ______ (go)
- The missing word must be the correct verb form for the tense
- Do not repeat these sentences: {used_text}

Return exactly in this format:
{sentence_label}: ...
{solution_label}: ...
"""
            text = self.ask_model(prompt)

            if self.is_bad_text(text):
                continue

            sentence = ""
            solution = ""

            for line in text.splitlines():
                if line.startswith(f"{sentence_label}:"):
                    sentence = line.replace(f"{sentence_label}:", "").strip()
                elif line.startswith(f"{solution_label}:"):
                    solution = line.replace(f"{solution_label}:", "").strip()

            key = normalize_text(sentence)

            if sentence and solution and key not in self.used_sentences and "______" in sentence and "(" in sentence and ")" in sentence:
                self.used_sentences.add(key)
                return {"sentence": sentence, "solution": solution, "topic": topic}

        return {"error": self.require_live_generation() or "FEHLER: Keine neue Lückensatz-Aufgabe erzeugt."}

    def evaluate_answer(self, correct, user, mode_name):
        if not self.client:
            correct_variants = [normalize_text(correct)]
            for sep in [" / ", "/", ",", ";"]:
                if sep in str(correct):
                    correct_variants.extend([normalize_text(x) for x in str(correct).split(sep) if normalize_text(x)])
            user_n = normalize_text(user)
            if user_n in correct_variants:
                return {
                    "rating": "RICHTIG",
                    "explanation": "Die Antwort stimmt mit der erwarteten Lösung überein.",
                    "alternatives": correct
                }
            if any(user_n == v.replace("to ", "") for v in correct_variants):
                return {
                    "rating": "FAST RICHTIG",
                    "explanation": "Die Antwort ist sehr nah an der erwarteten Lösung.",
                    "alternatives": correct
                }
            return {
                "rating": "FALSCH",
                "explanation": "Die Antwort passt nicht zur gespeicherten Lösung im Offline-Modus.",
                "alternatives": correct
            }

        prompt = f"""
Bewerte die Antwort eines Sprachlernenden.

Modus: {mode_name}

Korrekte Hauptantwort:
{correct}

Antwort des Benutzers:
{user}

Regeln:
- Schreibe auf Deutsch
- Bewerte fair
- Akzeptiere kleine harmlose Abweichungen
- Wenn die Bedeutung gleich bleibt, darf die Antwort als RICHTIG oder FAST RICHTIG gelten
- Nenne kurz, ob es auch alternative richtige Lösungen geben kann

Gib genau dieses Format zurück:
Bewertung: RICHTIG / FAST RICHTIG / FALSCH
Erklärung: ...
Alternative Lösungen: ...
"""
        text = self.ask_model(prompt)

        if self.is_bad_text(text):
            return {
                "rating": "Keine Bewertung",
                "explanation": text if text else "Die Antwort konnte nicht bewertet werden.",
                "alternatives": "Keine Alternativen verfügbar."
            }

        rating = ""
        explanation = ""
        alternatives = ""

        for line in text.splitlines():
            if line.startswith("Bewertung:"):
                rating = line.replace("Bewertung:", "").strip()
            elif line.startswith("Erklärung:"):
                explanation = line.replace("Erklärung:", "").strip()
            elif line.startswith("Alternative Lösungen:"):
                alternatives = line.replace("Alternative Lösungen:", "").strip()

        if not rating:
            rating = "Keine Bewertung"
        if not explanation:
            explanation = "Keine Erklärung erhalten."
        if not alternatives:
            alternatives = "Keine Alternativen verfügbar."

        return {
            "rating": rating,
            "explanation": explanation,
            "alternatives": alternatives
        }

    def translate_text(self, direction, user_text):
        if not self.client:
            lookup = {}
            source_pairs = FILE_VOCAB_ALL if FILE_VOCAB_ALL else [pair for group in LOCAL_VOCAB.values() for pair in group]
            for de, en in source_pairs:
                lookup[normalize_text(de)] = en
                lookup[normalize_text(en)] = de
            user_n = normalize_text(user_text)
            if user_n in lookup:
                return {
                    "translation": lookup[user_n],
                    "alternatives": "Offline mode: lokale Übersetzung"
                }
            return {
                "translation": "Keine lokale Übersetzung gefunden.",
                "alternatives": "Für freie Übersetzungen bitte optional einen OpenAI API Key eingeben."
            }

        if direction == "de_to_en":
            source = "German"
            target = "English"
        else:
            source = "English"
            target = "German"

        prompt = f"""
Translate the following text.

Rules:
- Source language: {source}
- Target language: {target}
- Translate correctly and naturally
- If it is a word, translate the word
- If it is a sentence, translate the sentence
- Also provide common alternative correct translations if useful

Return exactly like this:
Übersetzung: ...
Alternative Lösungen: ...

Text:
{user_text}
"""
        text = self.ask_model(prompt)

        if self.is_bad_text(text):
            return {"translation": "Keine Übersetzung verfügbar.", "alternatives": self.require_live_generation() or "Die Übersetzung konnte nicht erzeugt werden."}

        translation = ""
        alternatives = ""

        for line in text.splitlines():
            if line.startswith("Übersetzung:"):
                translation = line.replace("Übersetzung:", "").strip()
            elif line.startswith("Alternative Lösungen:"):
                alternatives = line.replace("Alternative Lösungen:", "").strip()

        if not translation and text.strip():
            translation = text.strip()

        if not alternatives:
            alternatives = "Keine Alternativen verfügbar."

        return {
            "translation": translation,
            "alternatives": alternatives
        }

    def generate_multiple_choice_question(self):
        topic = resolve_topic(self.topic_var.get())
        direction = self.direction_var.get()
        difficulty = self.difficulty_var.get()

        if not self.client:
            return self.get_local_multiple_choice(direction, topic)

        if direction == "de_to_en":
            source = "German"
            target = "English"
        else:
            source = "English"
            target = "German"

        prompt = f"""
Create one multiple choice vocabulary question.

Rules:
- Source language: {source}
- Target language: {target}
- Topic: {topic}
- Difficulty: {difficulty}
- One correct answer and three wrong but plausible answers
- Keep it learner-friendly

Return exactly in this format:
Frage: ...
A: ...
B: ...
C: ...
D: ...
Lösung: A/B/C/D
"""
        text = self.ask_model(prompt)

        if self.is_bad_text(text):
            return {"translation": "Keine Übersetzung verfügbar.", "alternatives": self.require_live_generation() or "Die Übersetzung konnte nicht erzeugt werden."}

        data = {"Frage": "", "A": "", "B": "", "C": "", "D": "", "Lösung": "", "topic": topic}

        for line in text.splitlines():
            if line.startswith("Frage:"):
                data["Frage"] = line.replace("Frage:", "").strip()
            elif line.startswith("A:"):
                data["A"] = line.replace("A:", "").strip()
            elif line.startswith("B:"):
                data["B"] = line.replace("B:", "").strip()
            elif line.startswith("C:"):
                data["C"] = line.replace("C:", "").strip()
            elif line.startswith("D:"):
                data["D"] = line.replace("D:", "").strip()
            elif line.startswith("Lösung:"):
                data["Lösung"] = line.replace("Lösung:", "").strip().upper()

        if all([data["Frage"], data["A"], data["B"], data["C"], data["D"], data["Lösung"]]):
            return data
        return {"error": self.require_live_generation() or "FEHLER: Keine neue Multiple-Choice-Aufgabe erzeugt."}

    def generate_story_pack_live(self):
        topic = resolve_topic(self.topic_var.get())
        difficulty = self.difficulty_var.get()
        direction = self.direction_var.get()

        if not self.client:
            return self.get_local_story_pack(topic)
        prompt = f"""
Create exactly one mini story pack for an English learning app.

Rules:
- Topic: {topic}
- Difficulty: {difficulty}
- Direction hint: {direction}
- Create a short scenario title
- Create exactly 4 steps
- Each step must contain one German sentence and its natural English solution
- Keep the sentences practical and learner-friendly
- Make every step different from the previous one

Return exactly in this format:
Title: ...
DE1: ...
EN1: ...
DE2: ...
EN2: ...
DE3: ...
EN3: ...
DE4: ...
EN4: ...
"""
        text = self.ask_model(prompt)
        if self.is_bad_text(text):
            return {"error": self.require_live_generation() or "FEHLER: Keine Story erzeugt."}

        title = ""
        steps = []
        current = {}
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            elif line.startswith("DE") and ":" in line:
                current[line.split(":",1)[0]] = line.split(":",1)[1].strip()
            elif line.startswith("EN") and ":" in line:
                current[line.split(":",1)[0]] = line.split(":",1)[1].strip()
        for i in range(1,5):
            de = current.get(f"DE{i}", "")
            en = current.get(f"EN{i}", "")
            if de and en:
                steps.append({"de": de, "en": en})
        if title and len(steps) == 4:
            return {"title": title, "steps": steps}
        return {"error": "FEHLER: Story-Format ungültig."}

    def generate_build_challenge_live(self):
        topic = resolve_topic(self.topic_var.get())
        difficulty = self.difficulty_var.get()

        if not self.client:
            return self.get_local_build_challenge(difficulty)

        prompt = f"""
Create exactly one sentence rebuild challenge for an English learning app.

Rules:
- Topic: {topic}
- Difficulty: {difficulty}
- Output one correct English sentence with 4 to 10 words
- It must be natural and learner-friendly
- Do not include quotes or numbering

Return exactly in this format:
Sentence: ...
"""
        text = self.ask_model(prompt)
        if self.is_bad_text(text):
            return {"error": self.require_live_generation() or "FEHLER: Kein Build-Satz erzeugt."}
        sentence = ""
        for line in text.splitlines():
            if line.startswith("Sentence:"):
                sentence = line.replace("Sentence:", "").strip()
        if sentence and len(sentence.split()) >= 4:
            words = sentence.split()
            random.shuffle(words)
            return {"sentence": " | ".join(words), "solution": sentence}
        return {"error": "FEHLER: Build-Format ungültig."}

    def generate_hunt_challenge_live(self):
        topic = resolve_topic(self.topic_var.get())
        difficulty = self.difficulty_var.get()
        goal = {"easy": 4, "medium": 5, "hard": 6}[difficulty]
        total_words = 12

        if not self.client:
            return self.get_local_hunt_challenge(topic, difficulty)

        prompt = f"""
Create exactly one click-based hunt mode challenge for an English learning app.

Rules:
- Topic: {topic}
- Difficulty: {difficulty}
- Goal: find {goal} correct words
- Return exactly {goal} correct single English words that match the topic
- Return exactly {total_words - goal} wrong single English words that do NOT match the topic
- All words must be common, learner-friendly, unique and one word only
- Do not use punctuation, numbering or phrases
- Mix nouns/verbs only if natural for the topic

Return exactly in this format:
Topic: ...
Correct: word1, word2, word3, word4, word5
Wrong: word6, word7, word8, word9, word10, word11, word12
"""
        text = self.ask_model(prompt)
        if self.is_bad_text(text):
            return {"error": self.require_live_generation() or "FEHLER: Keine Hunt-Wörter erzeugt."}

        parsed_topic = topic
        correct_words = []
        wrong_words = []

        for line in text.splitlines():
            line = line.strip()
            if line.startswith("Topic:"):
                parsed_topic = normalize_text(line.replace("Topic:", "").strip()) or topic
            elif line.startswith("Correct:"):
                raw = line.replace("Correct:", "").strip()
                correct_words = [normalize_text(w) for w in raw.split(",") if normalize_text(w)]
            elif line.startswith("Wrong:"):
                raw = line.replace("Wrong:", "").strip()
                wrong_words = [normalize_text(w) for w in raw.split(",") if normalize_text(w)]

        correct_words = list(dict.fromkeys(correct_words))
        wrong_words = [w for w in dict.fromkeys(wrong_words) if w not in correct_words]

        if len(correct_words) >= goal and len(wrong_words) >= total_words - goal:
            words = correct_words[:goal] + wrong_words[: total_words - goal]
            random.shuffle(words)
            return {
                "topic": parsed_topic,
                "goal": goal,
                "correct_words": correct_words[:goal],
                "wrong_words": wrong_words[: total_words - goal],
                "words": words,
            }

        return {"error": "FEHLER: Hunt-Format ungültig."}

    # =========================
    # NEW MODES
    # =========================

    def start_story_mode(self):
        self.show_work()
        self.set_active_tab("story")
        self.set_mode_theme("story")
        self.current_mode = "story"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()

        self.story_pack = None
        self.story_step = 0

        self.set_header("Story Mode", "Live story mission generated by ChatGPT.")
        self.entry_label.config(text="Translate the story line")
        self.set_progress_text("0 / 4")
        self.set_progress_bar(0, 4)
        self.set_output("Generating a fresh story...")
        self.set_result("Please wait...")
        self.run_async(self.generate_story_pack_live, self.after_story_loaded)

    def after_story_loaded(self, result):
        if not result or result.get("error"):
            message = (result or {}).get("error", "Keine Story erzeugt.")
            self.set_output(message)
            self.set_result("Bitte API-Key prüfen und erneut versuchen.")
            return
        self.story_pack = result
        self.set_header("Story Mode", f"{self.story_pack['title']} — progress through the scenario.")
        self.set_progress_text(f"0 / {len(self.story_pack['steps'])}")
        self.set_progress_bar(0, len(self.story_pack['steps']))
        self.set_result("Complete the story line by line.")
        self.load_story_step()

    def load_story_step(self):
        if not self.story_pack:
            self.set_output("No story loaded.")
            return

        if self.story_step >= len(self.story_pack["steps"]):
            self.current_task = None
            self.set_output(
                f"Story finished 🎉\n\n"
                f"Pack: {self.story_pack['title']}\n"
                "You completed the mini scenario."
            )
            self.set_result("Story complete. Press NEXT for a new story.")
            self.set_progress_text(f"{len(self.story_pack['steps'])} / {len(self.story_pack['steps'])}")
            self.set_progress_bar(len(self.story_pack['steps']), len(self.story_pack['steps']))
            return

        step_data = self.story_pack["steps"][self.story_step]
        self.current_task = {
            "sentence": step_data["de"],
            "solution": step_data["en"]
        }

        self.set_progress_text(f"{self.story_step + 1} / {len(self.story_pack['steps'])}")
        self.set_progress_bar(self.story_step + 1, len(self.story_pack["steps"]))
        self.set_output(
            f"Story Pack: {self.story_pack['title']}\n"
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n\n"
            f"Scene {self.story_step + 1}:\n"
            f"{step_data['de']}\n\n"
            "Translate the line to continue the story."
        )
        self.set_result("Continue the story...")

    def submit_story_answer(self):
        if not self.current_task:
            self.set_result("Press NEXT for a new story.")
            return

        user = self.get_user_text()
        if not user:
            self.set_result("Please enter an answer.")
            return

        sentence = self.current_task["sentence"]
        solution = self.current_task["solution"]

        self.run_async(
            lambda: self.evaluate_answer(solution, user, "Story Mode"),
            lambda result: self.after_story_evaluation(result, sentence, solution, user)
        )

    def after_story_evaluation(self, result, sentence, solution, user):
        rating = result.get("rating", "Keine Bewertung")
        explanation = result.get("explanation", "Keine Erklärung.")
        alternatives = result.get("alternatives", "Keine Alternativen verfügbar.")
        ok = rating in ["RICHTIG", "FAST RICHTIG"]

        add_result_to_stats(ok, "story")
        self.reward_xp(ok)
        self.flash_result_card(ok)

        if ok:
            self.story_step += 1
            self.set_result(
                f"Rating: {rating}\n\n"
                f"Explanation: {explanation}\n\n"
                f"Story continues...\n"
                f"Alternative answers: {alternatives}"
            )
            self.root.after(900, self.load_story_step)
        else:
            save_wrong_answer(sentence, solution, user)
            self.set_result(
                f"Rating: {rating}\n\n"
                f"Explanation: {explanation}\n\n"
                f"Correct answer: {solution}\n\n"
                f"Alternative answers: {alternatives}\n\n"
                "Try again or press SHOW ANSWER."
            )

    def start_build_mode(self):
        self.show_work()
        self.set_active_tab("build")
        self.set_mode_theme("build")
        self.current_mode = "build"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()

        self.set_header("Build Sentence", "Fresh build challenge generated by ChatGPT.")
        self.entry_label.config(text="Type the correct sentence")
        self.set_progress_text("Single challenge")
        self.set_progress_bar(1, 1)
        self.set_output("Generating a fresh build challenge...")
        self.set_result("Please wait...")
        self.run_async(self.generate_build_challenge_live, self.after_build_loaded)

    def after_build_loaded(self, result):
        if not result or result.get("error"):
            message = (result or {}).get("error", "Kein Build-Satz erzeugt.")
            self.current_task = None
            self.set_output(message)
            self.set_result("Bitte API-Key prüfen und erneut versuchen.")
            return
        self.current_task = result
        self.set_output(
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Topic: {resolve_topic(self.topic_var.get())}\n\n"
            f"Build this sentence:\n"
            f"{result['sentence']}\n\n"
            "Type the correct full sentence."
        )
        self.set_result("Rebuild the sentence.")

    def submit_build_answer(self):
        if not self.current_task:
            self.set_result("No build challenge loaded.")
            return

        user = self.get_user_text()
        if not user:
            self.set_result("Please enter a sentence.")
            return

        solution = self.current_task["solution"]
        ok = normalize_text(user) == normalize_text(solution)

        add_result_to_stats(ok, "build")
        self.reward_xp(ok)
        self.flash_result_card(ok)

        if ok:
            self.set_result(
                f"Correct 🎉\n\n"
                f"Built sentence:\n{solution}\n\n"
                "Press NEXT for another build challenge."
            )
        else:
            save_wrong_answer(self.current_task["sentence"], solution, user)
            self.set_result(
                f"Wrong\n\n"
                f"Correct sentence:\n{solution}\n\n"
                "Check word order and try another one."
            )

    def start_hunt_mode(self):
        self.show_work()
        self.set_active_tab("hunt")
        self.set_mode_theme("hunt")
        self.current_mode = "hunt"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_hunt_options()
        self.answer_text.config(state="disabled")
        self.clear_entry()

        self.hunt_found_words = set()
        self.hunt_clicked_words = set()
        self.hunt_correct_words = set()
        self.hunt_goal = 0
        self.current_task = None

        self.set_header("Hunt Mode", "Click the correct topic words generated by ChatGPT.")
        self.entry_label.config(text="Click the matching words below")
        self.set_progress_text("0 / ?")
        self.set_progress_bar(0, 1)
        self.set_output("Generating click-hunt words...")
        self.set_result("Please wait...")
        self.run_async(self.generate_hunt_challenge_live, self.after_hunt_loaded)

    def update_hunt_board(self, finished=False):
        found_text = ", ".join(sorted(self.hunt_found_words)) if self.hunt_found_words else "-"
        remaining = max(0, self.hunt_goal - len(self.hunt_found_words))
        self.set_output(
            f"Click Hunt\n"
            f"Topic: {self.current_task['topic']}\n"
            f"Difficulty: {self.difficulty_var.get()}\n\n"
            f"Goal: click {self.hunt_goal} correct words.\n"
            f"Remaining correct words: {remaining}\n\n"
            f"Already found:\n{found_text}\n\n"
            f"Tip: avoid the fake words."
        )
        self.set_progress_text(f"{len(self.hunt_found_words)} / {self.hunt_goal}")
        self.set_progress_bar(len(self.hunt_found_words), self.hunt_goal)

        if finished:
            self.set_result(
                f"Hunt complete 🔥\n\n"
                f"Found words:\n{', '.join(sorted(self.hunt_found_words))}\n\n"
                "Press NEXT for another hunt."
            )

    def after_hunt_loaded(self, result):
        if not result or result.get("error"):
            message = (result or {}).get("error", "Keine Hunt-Wörter erzeugt.")
            self.current_task = None
            self.set_output(message)
            self.set_result("Bitte API-Key prüfen und erneut versuchen.")
            self.hide_hunt_buttons()
            return

        self.hunt_correct_words = set(result["correct_words"])
        self.hunt_goal = result["goal"]
        self.current_task = {
            "topic": result["topic"],
            "solution": ", ".join(result["correct_words"]),
            "words": result["words"],
        }

        buttons = getattr(self, "hunt_option_buttons", [])
        for idx, btn in enumerate(buttons):
            if idx < len(result["words"]):
                word = result["words"][idx]
                btn.configure(text=word, command=lambda w=word, b=btn: self.handle_hunt_click(w, b), state="normal")
                btn.reset_style()
                btn.grid()
            else:
                btn.grid_remove()

        self.update_hunt_board()
        self.set_result("Click the words that match the topic.")

    def handle_hunt_click(self, word, btn):
        if not self.current_task:
            return

        word = normalize_text(word)
        if word in self.hunt_clicked_words:
            return

        self.hunt_clicked_words.add(word)
        is_correct = word in self.hunt_correct_words

        if is_correct:
            self.hunt_found_words.add(word)
            add_result_to_stats(True, "hunt")
            self.reward_xp(True)
            self.flash_result_card(True)
            btn.configure(bg=GREEN, activebackground=GREEN_HOVER, state="disabled")
            self.set_result(f"Correct: {word}")
        else:
            add_result_to_stats(False, "hunt")
            self.reward_xp(False)
            self.flash_result_card(False)
            btn.configure(bg=RED, activebackground=RED_HOVER, state="disabled")
            self.set_result(f"Wrong: {word} does not fit the topic.")

        self.update_hunt_board()

        if len(self.hunt_found_words) >= self.hunt_goal:
            for hunt_btn in getattr(self, "hunt_option_buttons", []):
                try:
                    hunt_btn.configure(state="disabled")
                except Exception:
                    pass
            self.update_hunt_board(finished=True)
            self.current_task = None

    def submit_hunt_answer(self):
        self.set_result("In Hunt Mode you click the words. No typing needed.")

    # =========================
    # MODES
    # =========================

    def start_vocab_mode(self):
        self.show_work()
        self.set_active_tab("vocab")
        self.set_mode_theme("vocab")
        self.current_mode = "vocab"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()
        self.set_header("Vocabulary Trainer", "Translate the word below.")
        self.entry_label.config(text="Your translation")
        self.set_progress_text("")
        self.set_progress_bar(0, 100)
        self.set_output("Loading vocabulary task...")
        self.set_result("Result will appear here.")
        self.run_async(lambda: self.generate_vocab(self.direction_var.get(), self.topic_var.get()), self.after_vocab_loaded)

    def after_vocab_loaded(self, result):
        if not result or result.get("error"):
            self.set_output((result or {}).get("error", "No new vocabulary task could be created."))
            self.set_result("Bitte API-Key prüfen und erneut versuchen.")
            return

        self.current_task = result
        self.set_output(
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Topic: {result.get('topic', self.topic_var.get())}\n"
            f"Direction: {self.direction_var.get()}\n\n"
            f"Word:\n{result['word']}\n\n"
            "Type your translation below and press SUBMIT or Enter."
        )
        self.set_result("Waiting for your answer.")

    def start_sentence_mode(self):
        self.show_work()
        self.set_active_tab("sentence")
        self.set_mode_theme("sentence")
        self.current_mode = "sentence"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()
        self.set_header("Sentence Trainer", "Translate the sentence below.")
        self.entry_label.config(text="Your translation")
        self.set_progress_text("")
        self.set_progress_bar(0, 100)
        self.set_output("Loading sentence task...")
        self.set_result("Result will appear here.")
        self.run_async(lambda: self.generate_sentence(self.direction_var.get(), self.tense_var.get(), self.topic_var.get()), self.after_sentence_loaded)

    def after_sentence_loaded(self, result):
        if not result or result.get("error"):
            self.set_output((result or {}).get("error", "No new sentence task could be created."))
            self.set_result("Bitte API-Key prüfen und erneut versuchen.")
            return

        self.current_task = result
        self.set_output(
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Tense: {self.tense_var.get()}\n"
            f"Topic: {result.get('topic', self.topic_var.get())}\n"
            f"Direction: {self.direction_var.get()}\n\n"
            f"Sentence:\n{result['sentence']}\n\n"
            "Type your translation below and press SUBMIT or Enter."
        )
        self.set_result("Waiting for your answer.")

    def start_translate_mode(self):
        self.show_work()
        self.set_active_tab("translate")
        self.set_mode_theme("translate")
        self.current_mode = "translate"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()
        self.set_header("Translate", "Translate your own text.")
        self.entry_label.config(text="Enter a word or sentence")
        self.set_progress_text("")
        self.set_progress_bar(0, 100)
        self.set_output(
            f"Model: {self.model_var.get()}\n"
            f"Direction: {self.direction_var.get()}\n\n"
            "Type a word or a sentence below.\n\nThen press SUBMIT or Enter."
        )
        self.set_result("Result will appear here.")
        self.answer_text.focus_set()

    def start_irregular_mode(self):
        self.show_work()
        self.set_active_tab("irregular")
        self.set_mode_theme("irregular")
        self.current_mode = "irregular"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()
        self.set_header("Irregular Verbs", "Give the correct forms.")
        self.entry_label.config(text="Your answer")
        self.set_progress_text("")
        self.set_progress_bar(0, 100)
        self.set_result("Result will appear here.")
        self.load_irregular_task()

    def load_irregular_task(self):
        verb_pool = FILE_IRREGULAR_VERBS if FILE_IRREGULAR_VERBS else IRREGULAR_VERBS
        verb = random.choice(verb_pool)
        mode = random.choice(["de_to_forms", "base_to_forms", "forms_to_de"])

        if mode == "de_to_forms":
            text = f"German: {verb['de']}\n\nType like this:\ngo / went / gone"
            solution = f"{verb['base']} / {verb['past']} / {verb['participle']}"
        elif mode == "base_to_forms":
            text = f"Infinitive: {verb['base']}\n\nType like this:\nwent / gone"
            solution = f"{verb['past']} / {verb['participle']}"
        else:
            text = f"Forms: {verb['base']} / {verb['past']} / {verb['participle']}\n\nType the German meaning."
            solution = verb["de"]

        self.current_task = {"display": text, "solution": solution}
        self.set_output(text)
        self.set_result("Waiting for your answer.")
        self.answer_text.focus_set()

    def start_multiple_choice_mode(self):
        self.show_work()
        self.set_active_tab("multiple_choice")
        self.set_mode_theme("multiple_choice")
        self.current_mode = "multiple_choice"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_multiple_choice_options()
        self.reset_option_buttons()
        self.clear_entry()
        self.answer_text.config(state="disabled")
        self.set_header("Multiple Choice", "Click the correct answer.")
        self.entry_label.config(text="Choose one answer")
        self.set_progress_text("")
        self.set_progress_bar(0, 100)
        self.set_output("Loading multiple choice task...")
        self.set_result("Result will appear here.")
        self.run_async(self.generate_multiple_choice_question, self.after_mc_loaded)

    def after_mc_loaded(self, result):
        if not result:
            self.set_output("No multiple choice question could be created.")
            self.set_result("No result yet.")
            return

        self.current_mc = result
        self.show_multiple_choice_options()
        self.reset_option_buttons()

        self.set_output(
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Topic: {result.get('topic', self.topic_var.get())}\n\n"
            f"Question:\n{result['Frage']}\n\n"
            "Click one answer below."
        )
        self.set_result("Waiting for your choice.")
        self.entry_label.config(text="Choose one answer below")

        answers = [("A", result["A"]), ("B", result["B"]), ("C", result["C"]), ("D", result["D"])]

        for i, (letter, text) in enumerate(answers):
            self.option_buttons[i].config(
                text=f"{letter}: {text}",
                command=lambda l=letter: self.answer_multiple_choice(l),
                state="normal"
            )
            self.option_buttons[i].grid()

    def answer_multiple_choice(self, letter):
        if not self.current_mc:
            return

        correct = self.current_mc["Lösung"]
        letters = ["A", "B", "C", "D"]

        for i, btn in enumerate(self.option_buttons):
            current_letter = letters[i]
            if current_letter == correct:
                btn.configure(bg=GREEN, activebackground=GREEN_HOVER, fg="white")
            elif current_letter == letter and letter != correct:
                btn.configure(bg=RED, activebackground=RED_HOVER, fg="white")
            else:
                btn.configure(bg=NEUTRAL, activebackground=NEUTRAL, fg=TEXT)
            btn.config(state="disabled")

        if letter == correct:
            add_result_to_stats(True, "multiple_choice")
            self.reward_xp(True)
            self.flash_result_card(True)
            self.set_result(f"Correct\n\nYour answer: {letter}\n\nPress NEXT for another question.")
        else:
            add_result_to_stats(False, "multiple_choice")
            self.reward_xp(False)
            self.flash_result_card(False)
            self.set_result(
                f"Wrong\n\n"
                f"Your answer: {letter}\n"
                f"Correct answer: {correct}\n\n"
                f"Press NEXT for another question."
            )

    def start_test_mode(self):
        self.show_work()
        self.set_active_tab("test")
        self.set_mode_theme("test")
        self.current_mode = "test"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()
        self.entry_label.config(text="Enter the missing verb form")
        self.test_total = 25
        self.test_index = 0
        self.test_points = 0
        self.test_tense = self.tense_var.get()
        self.test_direction = self.direction_var.get()

        add_test_run()

        self.set_header("Grammar Test", "Do 25 gap-fill questions.")
        self.set_progress_text("0 / 25")
        self.set_progress_bar(0, 25)
        self.set_output(
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Direction: {self.test_direction}\n"
            f"Tense: {self.test_tense}\n"
            f"Questions: {self.test_total}\n\n"
            "Press NEXT to start the test."
        )
        self.set_result("Press NEXT first.")
        self.answer_text.focus_set()

    def load_next_test_question(self):
        if self.test_index >= self.test_total:
            percent = round((self.test_points / self.test_total) * 100, 1)
            grade = get_grade(self.test_points, self.test_total)
            self.save_test_history_item(self.test_points, self.test_total, grade)

            self.set_header("Test Finished", "Your result is ready.")
            self.set_progress_text(f"{self.test_total} / {self.test_total}")
            self.set_progress_bar(self.test_total, self.test_total)
            self.set_output(
                f"Points: {self.test_points}/{self.test_total}\n"
                f"Percent: {percent}%\n"
                f"Grade: {grade}\n\n"
                "Wrong answers were saved.\n"
                "The test was added to your test history."
            )
            self.set_result("Test finished.")
            self.current_task = None
            return

        self.test_index += 1
        self.clear_entry()
        self.set_progress_text(f"{self.test_index} / {self.test_total}")
        self.set_progress_bar(self.test_index, self.test_total)
        self.set_output(f"Loading question {self.test_index}/{self.test_total}...")
        self.set_result("Loading...")

        self.run_async(
            lambda: self.generate_gap_fill_sentence(self.test_direction, self.test_tense, random.choice(TOPICS)),
            self.after_test_question_loaded
        )

    def after_test_question_loaded(self, result):
        if not result:
            self.set_output("No test question could be created.")
            self.set_result("No result yet.")
            self.current_task = None
            return

        self.current_task = result
        self.set_output(
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Question {self.test_index}/{self.test_total}\n\n"
            f"Tense: {self.test_tense}\n"
            f"Topic: {result.get('topic', 'mixed')}\n"
            f"Direction: {self.test_direction}\n\n"
            f"{result['sentence']}\n\n"
            "Type the missing verb form and press SUBMIT or Enter."
        )
        self.set_result("Waiting for your answer.")

    def start_vocab_test_mode(self):
        self.show_work()
        self.set_active_tab("vocab_test")
        self.set_mode_theme("vocab_test")
        self.current_mode = "vocab_test"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()
        self.entry_label.config(text="Translate the word")
        self.test_total = 10
        self.test_index = 0
        self.test_points = 0
        self.test_direction = self.direction_var.get()

        add_test_run()

        self.set_header("Vocabulary Test", "Do 10 vocabulary questions.")
        self.set_progress_text("0 / 10")
        self.set_progress_bar(0, 10)
        self.set_output(
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Direction: {self.test_direction}\n"
            f"Topic: {self.topic_var.get()}\n"
            f"Questions: {self.test_total}\n\n"
            "Press NEXT to start the vocabulary test."
        )
        self.set_result("Press NEXT first.")
        self.answer_text.focus_set()

    def load_next_vocab_test_question(self):
        if self.test_index >= self.test_total:
            percent = round((self.test_points / self.test_total) * 100, 1)
            grade = get_grade(self.test_points, self.test_total)
            self.save_test_history_item(self.test_points, self.test_total, grade)

            self.set_header("Vocabulary Test Finished", "Your result is ready.")
            self.set_progress_text(f"{self.test_total} / {self.test_total}")
            self.set_progress_bar(self.test_total, self.test_total)
            self.set_output(
                f"Points: {self.test_points}/{self.test_total}\n"
                f"Percent: {percent}%\n"
                f"Grade: {grade}\n\n"
                "Wrong answers were saved.\n"
                "The test was added to your test history."
            )
            self.set_result("Vocabulary test finished.")
            self.current_task = None
            return

        self.test_index += 1
        self.clear_entry()
        self.set_progress_text(f"{self.test_index} / {self.test_total}")
        self.set_progress_bar(self.test_index, self.test_total)
        self.set_output(f"Loading vocabulary question {self.test_index}/{self.test_total}...")
        self.set_result("Loading...")

        self.run_async(lambda: self.generate_vocab(self.test_direction, self.topic_var.get()), self.after_vocab_test_question_loaded)

    def after_vocab_test_question_loaded(self, result):
        if not result:
            self.set_output("No vocabulary test question could be created.")
            self.set_result("No result yet.")
            self.current_task = None
            return

        self.current_task = result
        self.set_output(
            f"Model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n"
            f"Question {self.test_index}/{self.test_total}\n\n"
            f"Topic: {result.get('topic', self.topic_var.get())}\n"
            f"Direction: {self.test_direction}\n\n"
            f"Word:\n{result['word']}\n\n"
            "Type your translation and press SUBMIT or Enter."
        )
        self.set_result("Waiting for your answer.")

    def start_wrong_training_mode(self):
        self.show_work()
        self.set_active_tab("wrong_training")
        self.set_mode_theme("wrong_training")
        self.current_mode = "wrong_training"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="normal")
        self.clear_entry()
        self.entry_label.config(text="Your answer")
        self.wrong_data = load_wrong_answers()
        self.wrong_index = 0

        add_wrong_training_run()

        self.set_header("Wrong Training", "Practice only your mistakes.")

        if not self.wrong_data:
            self.set_progress_text("")
            self.set_progress_bar(0, 100)
            self.set_output("No wrong answers saved yet.")
            self.set_result("Nothing to train right now.")
            return

        random.shuffle(self.wrong_data)
        self.set_progress_text(f"0 / {len(self.wrong_data)}")
        self.set_progress_bar(0, len(self.wrong_data))
        self.set_result("Waiting for your answer.")
        self.load_next_wrong_training()

    def load_next_wrong_training(self):
        if self.wrong_index >= len(self.wrong_data):
            self.set_output("Wrong training finished.\n\nNo more saved tasks in this round.")
            self.set_result("Training finished.")
            self.current_task = None
            return

        item = self.wrong_data[self.wrong_index]
        self.wrong_index += 1
        self.current_task = item
        self.clear_entry()
        self.set_progress_text(f"{self.wrong_index} / {len(self.wrong_data)}")
        self.set_progress_bar(self.wrong_index, len(self.wrong_data))

        self.set_output(
            f"Model: {self.model_var.get()}\n\n"
            f"{item['sentence']}\n\n"
            "Type your answer and press SUBMIT or Enter."
        )
        self.set_result("Waiting for your answer.")

    def show_statistics_mode(self):
        self.show_work()
        self.set_active_tab("stats")
        self.set_mode_theme("stats")
        self.current_mode = "stats"
        self.current_task = None
        self.current_mc = None
        self.hide_option_buttons()
        self.show_text_input()
        self.answer_text.config(state="disabled")
        self.set_header("Statistics", "Your learning progress.")
        self.entry_label.config(text="Statistics")
        self.set_progress_text("")
        self.set_progress_bar(0, 100)

        stats = load_stats()
        profile = load_profile()
        history = load_test_history()

        total = stats["tasks_total"]
        correct = stats["correct_total"]
        wrong = stats["wrong_total"]
        percent = round((correct / total) * 100, 1) if total > 0 else 0.0

        history_text = "No tests yet."
        if history:
            history_text = "\n".join(
                [f"{item['date']}  |  {item['points']}/{item['total']}  |  Grade {item['grade']}" for item in history[:5]]
            )

        self.set_output(
            f"Current model: {self.model_var.get()}\n"
            f"Difficulty: {self.difficulty_var.get()}\n\n"
            f"Tasks total: {total}\n"
            f"Correct: {correct}\n"
            f"Wrong: {wrong}\n"
            f"Success rate: {percent}%\n\n"
            f"Level: {profile['level']}\n"
            f"XP: {profile['xp']}\n"
            f"Daily Goal: {profile['today_done']}/{profile['daily_goal']}\n"
            f"Streak: {profile['streak']}\n"
            f"Best Streak: {profile['best_streak']}\n\n"
            f"Tests taken: {stats['tests_taken']}\n"
            f"Wrong training runs: {stats['wrong_training_runs']}\n"
            f"Vocab runs: {stats['vocab_runs']}\n"
            f"Sentence runs: {stats['sentence_runs']}\n"
            f"Translation runs: {stats['translation_runs']}\n"
            f"Irregular runs: {stats['irregular_runs']}\n"
            f"Multiple choice runs: {stats['multiple_choice_runs']}\n"
            f"Story runs: {stats['story_runs']}\n"
            f"Build runs: {stats['build_runs']}\n"
            f"Hunt runs: {stats['hunt_runs']}\n"
            f"Favorites saved: {stats.get('favorites_saved', 0)}\n"
            f"Best combo: {stats.get('combo_best', 0)}\n\n"
            f"API calls: {stats.get('api_calls', 0)}\n"
            f"API input tokens: {stats.get('api_input_tokens', 0)}\n"
            f"API output tokens: {stats.get('api_output_tokens', 0)}\n"
            f"Estimated API cost: ${stats.get('api_cost_usd', 0.0):.6f}\n\n"
            f"Recent test history:\n{history_text}"
        )
        self.set_result("Statistics loaded.")
        self.refresh_profile_labels()
        self.refresh_home_side_cards()

    # =========================
    # SUBMIT / NEXT
    # =========================

    def submit_action(self):
        if self.busy:
            return

        if self.current_mode == "vocab":
            self.submit_normal_answer("vocab", self.current_task)
        elif self.current_mode == "sentence":
            self.submit_normal_answer("sentence", self.current_task)
        elif self.current_mode == "translate":
            self.submit_translation()
        elif self.current_mode == "irregular":
            self.submit_normal_answer("irregular", self.current_task)
        elif self.current_mode == "multiple_choice":
            self.set_result("Please click one of the A, B, C or D buttons below.")
        elif self.current_mode == "test":
            self.submit_test_answer()
        elif self.current_mode == "vocab_test":
            self.submit_vocab_test_answer()
        elif self.current_mode == "wrong_training":
            self.submit_wrong_training_answer()
        elif self.current_mode == "story":
            self.submit_story_answer()
        elif self.current_mode == "build":
            self.submit_build_answer()
        elif self.current_mode == "hunt":
            self.submit_hunt_answer()
        else:
            self.set_result("Choose a mode first.")

    def next_action(self):
        if self.busy:
            return

        if self.current_mode == "vocab":
            self.start_vocab_mode()
        elif self.current_mode == "sentence":
            self.start_sentence_mode()
        elif self.current_mode == "irregular":
            self.load_irregular_task()
        elif self.current_mode == "test":
            self.load_next_test_question()
        elif self.current_mode == "vocab_test":
            self.load_next_vocab_test_question()
        elif self.current_mode == "wrong_training":
            self.load_next_wrong_training()
        elif self.current_mode == "multiple_choice":
            self.start_multiple_choice_mode()
        elif self.current_mode == "story":
            self.start_story_mode()
        elif self.current_mode == "build":
            self.start_build_mode()
        elif self.current_mode == "hunt":
            self.start_hunt_mode()
        else:
            self.set_result("Nothing to load here.")

    def submit_normal_answer(self, mode_name, task):
        if not task:
            self.set_result("No task loaded.")
            return

        user = self.get_user_text()
        if not user:
            self.set_result("Please enter an answer.")
            return

        self.run_async(
            lambda: self.evaluate_answer(task["solution"], user, mode_name),
            lambda result: self.after_normal_evaluation(result, task["solution"], mode_name)
        )

    def after_normal_evaluation(self, result, solution, mode_name):
        rating = result.get("rating", "Keine Bewertung")
        explanation = result.get("explanation", "Keine Erklärung.")
        alternatives = result.get("alternatives", "Keine Alternativen verfügbar.")

        is_correct = rating in ["RICHTIG", "FAST RICHTIG"]
        add_result_to_stats(is_correct, mode_name)
        self.reward_xp(is_correct)
        self.flash_result_card(is_correct)

        self.set_result(
            f"Rating: {rating}\n\n"
            f"Explanation: {explanation}\n\n"
            f"Correct answer: {solution}\n\n"
            f"Alternative answers: {alternatives}"
        )

    def submit_translation(self):
        user_text = self.get_user_text()
        if not user_text:
            self.set_result("Please enter text.")
            return

        add_translation_run()
        self.reward_xp(True)

        self.run_async(
            lambda: self.translate_text(self.direction_var.get(), user_text),
            self.after_translation
        )

    def after_translation(self, result):
        if not result:
            self.set_result("Translation could not be created.")
            return

        self.flash_result_card(True)
        self.set_result(
            f"Translation:\n{result['translation']}\n\n"
            f"Alternative answers:\n{result['alternatives']}"
        )

    def submit_test_answer(self):
        if not self.current_task:
            self.set_result("Press NEXT first to load a question.")
            return

        user = self.get_user_text()
        if not user:
            self.set_result("Please enter an answer.")
            return

        sentence = self.current_task["sentence"]
        solution = self.current_task["solution"]

        self.run_async(
            lambda: self.evaluate_answer(solution, user, "Test Einsetzen"),
            lambda result: self.after_test_evaluation(result, sentence, solution, user)
        )

    def after_test_evaluation(self, result, sentence, solution, user):
        rating = result.get("rating", "Keine Bewertung")
        explanation = result.get("explanation", "Keine Erklärung.")
        alternatives = result.get("alternatives", "Keine Alternativen verfügbar.")

        point = rating_to_point(rating)
        self.test_points += point
        add_test_result(point == 1)
        self.reward_xp(point == 1)
        self.flash_result_card(point == 1)

        if point == 0:
            save_wrong_answer(sentence, solution, user)

        self.set_result(
            f"Rating: {rating}\n\n"
            f"Explanation: {explanation}\n\n"
            f"Correct answer: {solution}\n\n"
            f"Alternative answers: {alternatives}\n\n"
            f"Point: {point}\n\n"
            f"Press NEXT for the next question."
        )

        self.current_task = None

    def submit_vocab_test_answer(self):
        if not self.current_task:
            self.set_result("Press NEXT first to load a question.")
            return

        user = self.get_user_text()
        if not user:
            self.set_result("Please enter an answer.")
            return

        word = self.current_task["word"]
        solution = self.current_task["solution"]

        self.run_async(
            lambda: self.evaluate_answer(solution, user, "Vokabeltest"),
            lambda result: self.after_vocab_test_evaluation(result, word, solution, user)
        )

    def after_vocab_test_evaluation(self, result, word, solution, user):
        rating = result.get("rating", "Keine Bewertung")
        explanation = result.get("explanation", "Keine Erklärung.")
        alternatives = result.get("alternatives", "Keine Alternativen verfügbar.")

        point = rating_to_point(rating)
        self.test_points += point
        add_test_result(point == 1)
        self.reward_xp(point == 1)
        self.flash_result_card(point == 1)

        if point == 0:
            save_wrong_answer(word, solution, user)

        self.set_result(
            f"Rating: {rating}\n\n"
            f"Explanation: {explanation}\n\n"
            f"Correct answer: {solution}\n\n"
            f"Alternative answers: {alternatives}\n\n"
            f"Point: {point}\n\n"
            f"Press NEXT for the next question."
        )

        self.current_task = None

    def submit_wrong_training_answer(self):
        if not self.current_task:
            self.set_result("No wrong task loaded.")
            return

        user = self.get_user_text()
        if not user:
            self.set_result("Please enter an answer.")
            return

        solution = self.current_task["solution"]
        sentence = self.current_task["sentence"]

        self.run_async(
            lambda: self.evaluate_answer(solution, user, "Fehlertraining"),
            lambda result: self.after_wrong_training_evaluation(result, sentence, solution)
        )

    def after_wrong_training_evaluation(self, result, sentence, solution):
        rating = result.get("rating", "Keine Bewertung")
        explanation = result.get("explanation", "Keine Erklärung.")
        alternatives = result.get("alternatives", "Keine Alternativen verfügbar.")

        ok = rating in ["RICHTIG", "FAST RICHTIG"]
        add_wrong_training_result(ok)
        self.reward_xp(ok)
        self.flash_result_card(ok)

        if ok:
            remove_wrong_answer(sentence, solution)
            extra = "This task was removed from the wrong list."
        else:
            extra = "This task stays in the wrong list."

        self.set_result(
            f"Rating: {rating}\n\n"
            f"Explanation: {explanation}\n\n"
            f"Correct answer: {solution}\n\n"
            f"Alternative answers: {alternatives}\n\n"
            f"{extra}"
        )


# =========================================================
# START
# =========================================================


class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success

        self.root.title("English Trainer Login")
        self.root.geometry("540x500")
        self.root.minsize(520, 470)
        self.root.configure(bg=BG)

        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill="both", expand=True, padx=22, pady=18)

        card = tk.Frame(shell, bg=CARD, highlightthickness=1, highlightbackground=BORDER, bd=0)
        card.pack(fill="both", expand=False)

        top_bar = tk.Frame(card, bg=BLUE, height=6)
        top_bar.pack(fill="x")

        body = tk.Frame(card, bg=CARD)
        body.pack(fill="both", expand=False, padx=24, pady=18)

        tk.Label(body, text="🔐", font=("Segoe UI Emoji", 32), fg=TEXT, bg=CARD).pack(anchor="center", pady=(0, 2))
        tk.Label(body, text="Welcome back", font=("Segoe UI", 22, "bold"), fg=TEXT, bg=CARD).pack()
        tk.Label(
            body,
            text="Log in with your email, product key and OpenAI API key",
            font=("Segoe UI", 11),
            fg=MUTED,
            bg=CARD
        ).pack(pady=(6, 14))

        tk.Label(body, text="Email", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=CARD).pack(anchor="w")
        email_wrap = tk.Frame(body, bg=INPUT_BG, highlightthickness=1, highlightbackground=BORDER, bd=0)
        email_wrap.pack(fill="x", pady=(6, 12))
        self.email_entry = tk.Entry(
            email_wrap,
            font=("Segoe UI", 12),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            bd=0
        )
        self.email_entry.pack(fill="x", padx=12, pady=10)

        tk.Label(body, text="Product Key", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=CARD).pack(anchor="w")
        key_wrap = tk.Frame(body, bg=INPUT_BG, highlightthickness=1, highlightbackground=BORDER, bd=0)
        key_wrap.pack(fill="x", pady=(6, 12))
        self.key_entry = tk.Entry(
            key_wrap,
            font=("Consolas", 11),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            bd=0
        )
        self.key_entry.pack(fill="x", padx=12, pady=10)

        tk.Label(body, text="OpenAI API Key (optional)", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=CARD).pack(anchor="w")
        api_wrap = tk.Frame(body, bg=INPUT_BG, highlightthickness=1, highlightbackground=BORDER, bd=0)
        api_wrap.pack(fill="x", pady=(6, 8))
        self.api_entry = tk.Entry(
            api_wrap,
            font=("Consolas", 11),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            bd=0,
            show="*"
        )
        self.api_entry.pack(fill="x", padx=12, pady=10)

        self.msg = tk.Label(body, text="", fg=RED, bg=CARD, font=("Segoe UI", 10), justify="left", wraplength=430)
        self.msg.pack(anchor="w", pady=(4, 8))

        button_row = tk.Frame(body, bg=CARD)
        button_row.pack(fill="x", pady=(4, 4))

        AccentButton(
            button_row,
            text="LOGIN",
            command=self.login,
            normal_bg=BLUE,
            hover_bg=BLUE_HOVER,
            width=16
        ).pack(side="left")

        AccentButton(
            button_row,
            text="CLEAR",
            command=self.clear_fields,
            normal_bg=NEUTRAL,
            hover_bg="#475569",
            width=12
        ).pack(side="left", padx=(10, 0))

        self.email_entry.focus_set()
        self.root.bind("<Return>", lambda e: self.login())
        self.root.bind("<Control-Shift-K>", lambda e: generate_key_gui())

    def clear_fields(self):
        self.email_entry.delete(0, tk.END)
        self.key_entry.delete(0, tk.END)
        self.api_entry.delete(0, tk.END)
        self.msg.config(text="")
        self.email_entry.focus_set()

    def login(self):
        email = self.email_entry.get().strip().lower()
        key = self.key_entry.get().strip()
        api_key = self.api_entry.get().strip()

        if not email or not key:
            self.msg.config(text="Please enter email and product key. The OpenAI API key is optional.")
            return

        expected = generate_product_key(email)

        if key != expected:
            self.msg.config(text="Invalid product key.")
            return

        if api_key:
            ok, message = validate_openai_key(api_key)
            if not ok:
                self.msg.config(text=message)
                return

        save_user_login(email, key)
        save_session(email, key, get_device_id(), api_key)
        self.root.destroy()
        self.on_success(api_key)


def start_app(api_key=None):
    global API_KEY
    API_KEY = (api_key or "").strip()
    if API_KEY:
        os.environ["OPENAI_API_KEY"] = API_KEY
    else:
        os.environ.pop("OPENAI_API_KEY", None)
    root = tk.Tk()
    app = EnglishTrainerApp(root)
    root.mainloop()



if __name__ == "__main__":
    session = load_session()
    if session:
        email = session.get("email", "").strip().lower()
        key = session.get("key", "").strip()
        device_id = session.get("device_id", "").strip()
        api_key = session.get("api_key", "").strip()

        if (
            email
            and key
            and generate_product_key(email) == key
            and device_id == get_device_id()
        ):
            start_app(api_key)
        else:
            login_root = tk.Tk()
            LoginWindow(login_root, start_app)
            login_root.mainloop()
    else:
        login_root = tk.Tk()
        LoginWindow(login_root, start_app)
        login_root.mainloop()
