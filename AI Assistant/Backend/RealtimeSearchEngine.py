from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os
import json
import tiktoken  # ✅ Token counter added

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Validate API key
if not GroqAPIKey:
    raise Exception("GroqAPIKey not found! Please check your .env file.")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, using full stops, commas, question marks, and proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Ensure ChatLog file exists
if not os.path.exists("Data"):
    os.makedirs("Data")

chatlog_path = r"Data\ChatLog.json"
response_path = r"Data\Responses.data"  # ✅ Add this path

# Load previous chat history or create a new one if file not found
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except (FileNotFoundError, json.JSONDecodeError):
    with open(chatlog_path, "w") as f:
        dump([], f)
    messages = []

# Token handling setup
encoding = tiktoken.get_encoding("cl100k_base")  # Use cl100k_base for compatibility

def count_tokens(messages):
    total = 0
    for message in messages:
        total += len(encoding.encode(message.get("role", ""))) + len(encoding.encode(message.get("content", ""))) + 4
    return total

def trim_messages(messages, max_tokens=8192, forget_tokens=500):
    while count_tokens(messages) > max_tokens - forget_tokens:
        if len(messages) > 1:
            messages.pop(0)
        else:
            break
    return messages

# Function to perform Google search
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The search results for '{query}' are:\n[start]\n"
        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"Error during Google search: {e}"

# Function to clean up the answer
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# ✅ Function to show answer to chat UI
def ShowToTextScreen(answer):
    try:
        with open(response_path, "w", encoding="utf-8") as file:
            file.write(answer)
    except Exception as e:
        print(f"Failed to write to Responses.data: {e}")

# Function to provide real-time date and time info
def Information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = "Use this Real-time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour}:{minute}:{second}\n"
    return data

# Main function to interact with Groq
def RealtimeSearchEngine(prompt):
    global messages

    # Load previous chat history
    try:
        with open(chatlog_path, "r") as f:
            messages = load(f)
    except:
        messages = []

    # Add user message to the chat history
    messages.append({"role": "user", "content": prompt})

    # ✅ Trim if token count is too high
    messages = trim_messages(messages)

    # Ask Groq for a response
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": System},
                {"role": "system", "content": Information()}
            ] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        # Process the chunks received from the API
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("<|>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat history
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)

        modified = AnswerModifier(Answer)

        ShowToTextScreen(modified)  # ✅ Write to Responses.data so GUI shows answer

        return modified

    except Exception as e:
        print(f"Error: {e}")
        error_message = "An error occurred. Please try again."
        ShowToTextScreen(error_message)  # ✅ Show error message in UI too
        return error_message

# Main loop for CLI testing
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
