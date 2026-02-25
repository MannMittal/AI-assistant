from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
from Backend.SerialConnection import ArduinoSerial
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
arduino = ArduinoSerial()

# Retrieve the Groq API key and check if it exists
GroqAPIKey = env_vars.get("GroqAPIKey")
if not GroqAPIKey:
    raise ValueError("GroqAPIKey not found in .env file. Please provide it to proceed.")

def GoogleSearch(topic):
    """Use pywhatkit's search function to perform a Google search."""
    try:
        search(topic)
        return True
    except Exception as e:
        print(f"[red]Error performing Google search: {e}[/red]")
        return False

# Predefined professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

messages = []  # List to store chatbot messages.

SystemChatBot = {
    "role": "system",
    "content": f"Hello, I am {env_vars.get('username', 'Assistant')}. You're a content writer. You have to write content like a letter."
}

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

def Content(Topic):
    """Generate content using AI and save it to a file."""
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})

        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[SystemChatBot] + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            Answer = ""

            print(f"Raw API response: {completion}")

            for chunk in completion:
                print(f"Chunk received: {chunk}")

                if 'choices' in chunk and 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                    content = chunk['choices'][0]['delta']['content']
                    print(f"Content found: {content}")
                    Answer += content
                else:
                    print("[red]Chunk content not found in the API response[/red]")

            if not Answer:
                print("[red]No content was returned by the API.[/red]")

            Answer = Answer.replace("<|ss>", "")
            messages.append({"role": "assistant", "content": Answer})
            return Answer

        except Exception as e:
            print(f"Error generating content: {e}")
            return "Error generating content."

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    if ContentByAI:
        filepath = rf"Data\{Topic.lower().replace(' ', '')}.txt"
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(ContentByAI)

        OpenNotepad(filepath)
        return True
    return False

def YouTubeSearch(Topic):
    """Search a topic on YouTube and open it."""
    try:
        Url4YouTubeSearch = f"https://www.youtube.com/results?search_query={Topic}"
        webbrowser.open(Url4YouTubeSearch)
        return True
    except Exception as e:
        print(f"[red]Error searching YouTube: {e}[/red]")
        return False

def PlayYouTube(query):
    """Play a video directly on YouTube."""
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"[red]Error playing YouTube video: {e}[/red]")
        return False

def OpenApp(app, sess=requests.session()):
    """Open an application, or fallback to a web search."""
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[red]Error opening application: {e}[/red]")

        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print("[red]Failed to retrieve search results.[/red]")
                return None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])

    return False

def CloseApp(app):
    """Close an application."""
    try:
        if "chrome" in app:
            pass
        else:
            close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[red]Error closing app: {e}[/red]")

def System(command):
    """System operations like mute, volume control."""
    try:
        def mute():
            keyboard.press_and_release("volume mute")

        def unmute():
            keyboard.press_and_release("volume mute")

        def volume_up():
            keyboard.press_and_release("volume up")

        def volume_down():
            keyboard.press_and_release("volume down")

        if command == "mute":
            mute()
        elif command == "unmute":
            unmute()
        elif command == "volume up":
            volume_up()
        elif command == "volume down":
            volume_down()

        return True
    except Exception as e:
        print(f"[red]Error with system command: {e}[/red]")

# --------------------------------------------------------
# 🔥 MINIMAL FIX APPLIED HERE (ONLY THESE 2 LINES CHANGED)
# --------------------------------------------------------

async def TranslateAndExecute(commands: list[str]):
    """Translate and execute user commands."""
    funcs = []

    for command in commands:
        command_lower = command.lower().strip()

        if "automation:" in command_lower:
            command_lower = command_lower.split("automation:", 1)[-1].strip(" .")

        command_lower = " ".join(command_lower.split())

        try:
            if command_lower.startswith("open"):
                if "open it" in command_lower or "open file" == command_lower:
                    pass
                else:
                    fun = asyncio.to_thread(OpenApp, command_lower.removeprefix("open ").strip())
                    funcs.append(fun)

            elif command_lower.startswith("close"):
                fun = asyncio.to_thread(CloseApp, command_lower.removeprefix("close ").strip())
                funcs.append(fun)

            elif command_lower.startswith("play"):
                fun = asyncio.to_thread(PlayYouTube, command_lower.removeprefix("play ").strip())
                funcs.append(fun)

            elif command_lower.startswith("content"):
                fun = asyncio.to_thread(Content, command_lower.removeprefix("content ").strip())
                funcs.append(fun)

            elif command_lower.startswith("google search"):
                fun = asyncio.to_thread(GoogleSearch, command_lower.removeprefix("google search ").strip())
                funcs.append(fun)

            elif command_lower.startswith("youtube search"):
                fun = asyncio.to_thread(YouTubeSearch, command_lower.removeprefix("youtube search ").strip())
                funcs.append(fun)

            elif command_lower.startswith("system"):
                fun = asyncio.to_thread(System, command_lower.removeprefix("system").strip())
                funcs.append(fun)

            # 🔥 LED ON (FIXED)
            elif command_lower in ("light on", "turn on light", "led on", "turn on led","turn led on","turn on bell","buzzer on","alarm on","turn on alarm","turn on buzzer","ring the bell"):
                fun = asyncio.to_thread(arduino.send, "1")
                funcs.append(fun)

            # 🔥 LED OFF (FIXED)
            elif command_lower in ("light off", "turn off light", "led off", "turn off led","turn led off","turn off bell","buzzer off","alarm off","turn off alarm","turn off buzzer"):
                fun = asyncio.to_thread(arduino.send, "0")
                funcs.append(fun)

            else:
                print(f"[red]No Function Found for:[/red] {command}")

        except Exception as e:
            print(f"[red]Error processing command '{command}': {e}[/red]")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
