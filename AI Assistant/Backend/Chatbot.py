from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from the .env file
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# Define system prompt
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time information.
*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Try loading previous chat logs
try:
    with open(r"DataChatlog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(r"DataChatlog.json", "w") as f:
        dump(messages, f, indent=4)

# Function to get real-time date and time
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed.\n"
        f"Day: {now.strftime('%A')}; Date: {now.strftime('%d')}; Month: {now.strftime('%B')}; Year: {now.strftime('%Y')};\n"
        f"Time: {now.strftime('%H:%M:%S')}"
    )

# Function to clean the AI's output
def AnswerModifier(answer):
    lines = answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Function to count tokens (approximate method based on message length)
def count_tokens(messages):
    return sum(len(message["content"].split()) for message in messages)

# Function to trim tokens by removing the oldest messages when token count is near the limit
def trim_tokens(messages, max_tokens=500, threshold=0.95):
    token_count = count_tokens(messages)
    # Trim only when token count exceeds the threshold
    if token_count >= threshold * max_tokens:
        while count_tokens(messages) > (max_tokens - 50):  # Keep a margin of 50 tokens
            messages.pop(0)  # Remove the oldest message (first item)

# Main chatbot function
def ChatBot(user_query):
    try:
        # Load previous chat messages
        try:
            with open(r"DataChatlog.json", "r") as f:
                messages = load(f)
        except FileNotFoundError:
            messages = []

        messages.append({"role": "user", "content": user_query})

        # Trim tokens if they are nearing the limit
        trim_tokens(messages, max_tokens=500, threshold=0.98)  # 95% of the token limit

        # 🚀 Corrected: using client.chat.completions.create with correct model name
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Correct model name
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=4024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=["None"]
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("<|ds|>", "")
        messages.append({"role": "assistant", "content": answer})

        # Save updated messages
        with open(r"DataChatlog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        # Reset chatlog if any error happens
        with open(r"DataChatlog.json", "w") as f:
            dump([], f, indent=4)
        return "An error occurred. Please try again."

# Entry point
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        response = ChatBot(user_input)
        print(response)
