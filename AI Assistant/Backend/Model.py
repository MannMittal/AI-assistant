import cohere  # Import the Cohere library for AI services.
from rich import print  # Import the Rich library to enhance terminal outputs.
from dotenv import dotenv_values  # Import dotenv to load environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve API key.
CohereAPIKey = env_vars.get('CohereAPIKey')

# Create a Cohere client using the provided API key.
co = cohere.Client(api_key=CohereAPIKey)

# Define a list of recognized function keywords for task categorization.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# Initialize an empty list to store user messages.
messages = []

# Define the preamble that guides the AI model on how to categorize queries.
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open chrome' etc.
** Do not answer any query, just decide what kind of query is given to you. **

-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up-to-date information.
-> Respond with 'realtime ( query )' if a query cannot be answered by a llm model (because they don't have realtime data) and requires current information.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open chrome'.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook'.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate an image with a given prompt like 'generate image of sunset in mountains'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down, etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails, or anything text-based.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube.

** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp', respond with 'open facebook, open telegram, close whatsapp' separately. **

** If the user is saying goodbye or wants to end the conversation like 'bye jarvis', respond with 'exit'. **

** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not categorized. **
"""

# Example chat history to provide context to the model
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and remind me that I have a dancing performance on 5th August, reminder 11:00 PM 5th Aug dancing performance"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

# Define the main function for decision-making on queries.
def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to the messages list.
    messages.append({"role": "user", "content": prompt})

    # Create a streaming chat session with the Cohere model.
    stream = co.chat_stream(
        model="command-r-plus",  # Specify the Cohere model to use.
        message=prompt,  # Pass the user's query.
        temperature=0.7,  # Set the creativity level of the model.
        chat_history=ChatHistory,  # Provide the predefined chat history for context.
        prompt_truncation="OFF",  # Ensure the prompt is not truncated.
        connectors=[],  # No additional connectors are used.
        preamble=preamble  # Pass the detailed instruction preamble.
    )

    # Initialize an empty string to store the generated response.
    response = ""

    # Collect the response from the stream
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    # Process the response
    response = response.replace("\n", " ").split(".")
    response = [i.strip() for i in response if i]

    # Filter only recognized function-based tasks
    temp = []
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    response = temp

    # Handle if model returns a clarification request or undefined query
    if "query" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    else:
        # Ensure response is in a useful format (separated by commas if there are multiple tasks)
        return ", ".join(response) if len(response) > 1 else response[0]

# Entry point for the script
if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        categorized_response = FirstLayerDMM(user_input)
        print(categorized_response)
