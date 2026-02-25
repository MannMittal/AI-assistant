import sys
import os
import subprocess
import threading
import json
import time
import concurrent.futures
from asyncio import run
from dotenv import dotenv_values

from Frontend.GUI import (
    GraphicalUserInterface,
    GetAssistantStatus,
    SetAssistantStatus,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    ShowToTextScreen
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech


# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")
FRONTEND_FILES = os.path.join(BASE_DIR, "Frontend", "Files")
BACKEND_DIR = os.path.join(BASE_DIR, "Backend")

CHATLOG_FILE = os.path.join(DATA_DIR, "ChatLog.json")
IMAGEGEN_FILE = os.path.join(FRONTEND_FILES, "ImageGeneration.data")

# ---------------- ENV ----------------
env_vars = dotenv_values(".env")
username = env_vars.get("Username", "User")
assistantname = env_vars.get("Assistantname", "Aurora")

DefaultMessage = f"{username} : Hello {assistantname}, How are you?"
assistant_welcome_message = f"{assistantname} : Welcome {username}, I am doing well. How may I help you?"

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


# ---------------- HELPER ----------------
def safe_call(func, *args, timeout=15, fallback=None):
    """Run a blocking function safely with timeout."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"Timeout: {func.__name__} took too long.")
            return fallback or "Sorry, I’m having trouble processing that."
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            return fallback or "Something went wrong while processing."


# ---------------- INIT ----------------
def ShowDefaultChatIfNoChats():
    if not os.path.exists(CHATLOG_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CHATLOG_FILE, "w", encoding="utf-8") as f:
            f.write("[]")

    with open(CHATLOG_FILE, "r", encoding="utf-8") as File:
        if len(File.read().strip()) < 5:
            with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
                file.write("")
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
                file.write(DefaultMessage)


def ReadChatLogJson():
    with open(CHATLOG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", assistantname + " ")

    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    with open(TempDirectoryPath("Database.data"), "r", encoding="utf-8") as File:
        Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split("\n")
        result = "\n".join(lines)
        with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as File:
            File.write(result)


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowToTextScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


InitialExecution()


# ---------------- MAIN LOGIC ----------------
def MainExecution():
    try:
        TaskExecution = False
        ImageExecution = False

        SetAssistantStatus("Listening ...")

        # --- Modified Listening Logic with Mute Interrupt ---
        Query = ""
        def listen_wrapper():
            nonlocal Query
            Query = SpeechRecognition()

        listener_thread = threading.Thread(target=listen_wrapper, daemon=True)
        listener_thread.start()
    
        # Keep checking if user muted while listening
        while listener_thread.is_alive():
            if GetMicrophoneStatus() == "False":
                print("DEBUG: Mute pressed → stopping SpeechRecognition")
                SetAssistantStatus("Muted.")
                return  # Exit immediately — don’t reset state
            time.sleep(0.2)

        # Stop mic after listening completes
        SetMicrophoneStatus("False")

        # --- Handle empty or timeout speech ---
        if not Query or Query.strip() == "" or "having trouble processing" in Query.lower():
            if GetMicrophoneStatus() == "True":
                SetAssistantStatus("No speech detected. Listening again...")
                time.sleep(0.8)
                SetMicrophoneStatus("True")  # Restart listening automatically
            return

        ShowToTextScreen(f"{username} : {Query}")
        SetAssistantStatus("Thinking ...")
        print("DEBUG: Query captured →", Query)

        # --- Classification Layer ---
        Decision = safe_call(FirstLayerDMM, Query, timeout=10, fallback=None)
        if not Decision or not isinstance(Decision, list):
            Decision = []

        print("DEBUG: Raw Decision from DMM →", Decision)

        lower_q = Query.lower().strip()

        # --- Improved fallback classification ---
        if any(word in lower_q for word in ["open", "close", "launch", "start", "play", "system", "youtube", "google", "exit","led","alarm","buzzer","bell"]):
            Decision = [f"automation:{Query}"]
        elif any(word in lower_q for word in ["search", "current", "who is", "what is", "weather", "when", "how to", "latest"]):
            Decision = [f"realtime:{Query}"]
        elif any(word in lower_q for word in ["generate", "make an image", "create picture", "draw", "generate art"]):
            Decision = [f"generate:{Query}"]
        elif not Decision:
            Decision = [f"general:{Query}"]

        # Normalize decisions
        Decision = [d.lower().strip() for d in Decision]
        print("DEBUG: Final Decision after fallback →", Decision)

        # --- Category detection ---
        is_general = any(d.startswith("general") for d in Decision)
        is_realtime = any(d.startswith("realtime") for d in Decision)
        is_automation = any(d.startswith("automation") for d in Decision)
        is_imagegen = any("generate" in d for d in Decision)

        print(f"DEBUG: Category Flags → automation={is_automation}, realtime={is_realtime}, imagegen={is_imagegen}, general={is_general}")

        # --- AUTOMATION HANDLER ---
        if is_automation:
            print(f"DEBUG: Running automation task → {Query}")
            try:
                import asyncio
                asyncio.run(Automation([f"automation:{Query}"]))
                TaskExecution = True
            except RuntimeError:
                threading.Thread(target=lambda: run(Automation([f"automation:{Query}"])), daemon=True).start()
                TaskExecution = True
            except Exception as e:
                print(f"Error running Automation: {e}")

        # --- IMAGE GENERATION ---
        if is_imagegen:
            print(f"DEBUG: Triggering image generation → {Query}")
            ImageExecution = True
            with open(IMAGEGEN_FILE, "w") as file:
                file.write(f"{Query},True")
            try:
                p1 = subprocess.Popen(
                    [sys.executable, os.path.join(BACKEND_DIR, "ImageGeneration.py")],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )
                subprocesses.append(p1)
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")

        # --- GENERAL / REALTIME ---
        if not TaskExecution and not ImageExecution:
            if is_realtime:
                SetAssistantStatus("Searching ...")
                Answer = safe_call(RealtimeSearchEngine, QueryModifier(Query), timeout=10)
            else:
                SetAssistantStatus("Thinking ...")
                Answer = safe_call(ChatBot, QueryModifier(Query), timeout=15)

            ShowToTextScreen(f"{assistantname} : {Answer}")
            SetAssistantStatus("Answering ...")
            TextToSpeech(Answer)

        # --- Do NOT reset to Available if muted ---
        time.sleep(1)
        if GetMicrophoneStatus() == "True":
            SetAssistantStatus("Available...")
        else:
            print("DEBUG: Staying muted — skipping Available reset")

        SetMicrophoneStatus("True")

    except Exception as e:
        print(f"MainExecution error: {e}")
        SetAssistantStatus("Error occurred.")
        time.sleep(1)
        if GetMicrophoneStatus() == "True":
            SetAssistantStatus("Available...")
        SetMicrophoneStatus("True")


# ---------------- THREADS ----------------
def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                time.sleep(0.1)



def SecondThread(): 
    GraphicalUserInterface()


if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
