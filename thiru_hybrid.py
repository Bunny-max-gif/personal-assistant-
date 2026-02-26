
# =====================================================
# THIRU - HYBRID PERSONAL ASSISTANT
# Offline + Online | Wake Word | Memory | Coding | Info
# =====================================================

import os, json, queue, sqlite3, datetime, requests
import pyttsx3, sounddevice as sd, wikipedia
from vosk import Model, KaldiRecognizer

# ---------------- CONFIG ----------------
WAKE_WORD = "hey thiru"
MODEL_PATH = "model"

# ---------------- MEMORY ----------------
conn = sqlite3.connect("thiru_memory.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY,
    category TEXT,
    content TEXT
)
""")
conn.commit()

def remember(cat, text):
    cur.execute("INSERT INTO memory VALUES (NULL, ?, ?)", (cat, text))
    conn.commit()

def recall(cat):
    cur.execute("SELECT content FROM memory WHERE category=?", (cat,))
    return cur.fetchall()

# ---------------- VOICE OUT ----------------
engine = pyttsx3.init()
engine.setProperty("rate", 155)

def speak(text):
    print("THIRU:", text)
    engine.say(text)
    engine.runAndWait()

# ---------------- OFFLINE VOICE IN ----------------
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000)
audio_q = queue.Queue()

def callback(indata, frames, time, status):
    audio_q.put(bytes(indata))

def listen():
    with sd.RawInputStream(
        samplerate=16000, blocksize=8000,
        dtype='int16', channels=1, callback=callback
    ):
        while True:
            data = audio_q.get()
            if rec.AcceptWaveform(data):
                return json.loads(rec.Result()).get("text", "")

# ---------------- INTERNET CHECK ----------------
def online():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

# ---------------- ONLINE BRAIN ----------------
def online_info(query):
    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(query, sentences=2)
    except:
        return "I could not find clear information online."

# ---------------- OFFLINE BRAIN ----------------
def offline_brain(cmd):
    if "time" in cmd:
        speak(datetime.datetime.now().strftime("Time is %H:%M"))
        return True

    if "remember that" in cmd:
        remember("note", cmd.replace("remember that", ""))
        speak("I will remember that.")
        return True

    if "what do you remember" in cmd:
        mem = recall("note")
        if mem:
            speak("Here is what I remember.")
            for m in mem:
                print("-", m[0])
        else:
            speak("I don't remember anything yet.")
        return True

    if "python" in cmd:
        speak("Python starter code printed.")
        print("""
def main():
    print("Hello from THIRU")

if __name__ == "__main__":
    main()
""")
        return True

    if "machine learning" in cmd or "ml" in cmd:
        speak("Machine learning steps printed.")
        print("""
1. Dataset
2. Preprocessing
3. Train
4. Evaluate
""")
        return True

    if "sad" in cmd or "broken" in cmd:
        speak("Pain made you deeper. Depth makes you powerful.")
        return True

    return False

# ---------------- COMMAND HANDLER ----------------
def handle(cmd):

    if "sleep" in cmd or "exit" in cmd:
        speak("Sleeping. Call me when needed.")
        exit()

    # Try offline first
    if offline_brain(cmd):
        return

    # Use online if available
    if online() and any(x in cmd for x in ["who", "what", "search", "explain", "latest"]):
        speak("Let me check online.")
        info = online_info(cmd)
        speak(info)
        return

    speak("I am listening.")

# ---------------- MAIN LOOP ----------------
if __name__ == "__main__":
    speak("THIRU initialized. Say hey thiru.")

    while True:
        text = listen()
        if WAKE_WORD in text:
            speak("I am here.")
            while True:
                cmd = listen()
                handle(cmd)
