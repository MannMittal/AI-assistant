import pygame  # Import pygame library for handling audio playback
import random  # Import random for generating random choices
import asyncio  # Import asyncio for asynchronous operations
import edge_tts  # Import edge_tts for text-to-speech functionality
import os  # Import os for file path handling
import time  # Import time to add a small delay
from dotenv import dotenv_values  # Import dotenv for reading environment variables from a .env file

# Load environment variables from a .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # Get the AssistantVoice from the environment variables

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"  # Define the path where the speech file will be saved
    if os.path.exists(file_path):  # Check if the file already exists
        os.remove(file_path)  # If it exists, remove it to avoid overwriting errors

    # Create the communicate object to generate speech
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)  # Save the generated speech as an MP3 file

# Function to manage Text-to-Speech (TTS) functionality
def TTS(Text, func=lambda r=None: True):
    try:
        # Convert text to an audio file asynchronously
        asyncio.run(TextToAudioFile(Text))

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        # Add a short delay to ensure the file is completely saved before playing
        time.sleep(1)

        # Load the generated speech file into pygame mixer
        pygame.mixer.music.load(r"Data\speech.mp3")

        # Play the audio
        pygame.mixer.music.play()

        # Loop until the audio is done playing or the function stops
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            pygame.time.Clock().tick(10)  # Limit the loop to 10 ticks per second

    except Exception as e:
        print(f"Error in TTS: {e}")  # Handle any exceptions during the process

    finally:
        try:
            # Call the provided function with False to signal the end of TTS
            func(False)
            pygame.mixer.music.stop()  # Stop the audio playback
            pygame.mixer.quit()  # Quit the pygame mixer
        except Exception as e:
            print(f"Error in finally block: {e}")  # Handle any exceptions during cleanup

def SplitLongText(Text, max_length=200):  # Max length before breaking into chunks
    sentences = Text.split(".")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += sentence + "."
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())  # Add the chunk if not empty
            current_chunk = sentence + "."

    if current_chunk:
        chunks.append(current_chunk.strip())  # Add any remaining chunk

    return chunks

def TextToSpeech(Text , func=lambda r=None: True ):
    # Split long text into manageable chunks
    chunks = SplitLongText(Text)

    # Loop through the chunks and pass each one to the TTS function
    for i, chunk in enumerate(chunks):
        if i > 0:
            # After a chunk, you can add a pause or special message if you prefer
            TTS(f"{random.choice(responses)}", func)  # Optionally notify the user
            break  # Exit after response is spoken, stopping further reading of text

        # Play the current chunk of text
        TTS(chunk, func)

# List of responses to be used in case of long text
responses = [
    "The rest of the result has been printed to the chat screen, kindly check it out sir.",
    "The rest of the text is now on the chat screen, sir, please check it.",
    "You can see the rest of the text on the chat screen, sir.",
    "The remaining part of the text is now on the chat screen, sir.",
    "Sir, you'll find more text on the chat screen for you to see.",
    "The rest of the answer is now on the chat screen, sir.",
    "Sir, please look at the chat screen, the rest of the answer is there.",
    "You'll find the complete answer on the chat screen, sir.",
    "Sir, please check the chat screen for more information.",
    "The next part of the text is on the chat screen, sir.",
    "There's more text on the chat screen for you, sir.",
    "Sir, take a look at the chat screen for additional text.",
    "You'll find more to read on the chat screen, sir.",
    "Sir, check the chat screen for the rest of the text.",
    "The chat screen has the rest of the text, sir.",
    "There's more to see on the chat screen, sir, please look.",
    "Sir, the chat screen holds the continuation of the text.",
    "You'll find the complete answer on the chat screen, kindly check it out sir.",
    "Please review the chat screen for the rest of the text, sir.",
    "Sir, look at the chat screen for the complete answer."
]

# Main execution loop
if __name__ == "__main__":
    while True: 
        # Prompt user for input and pass it to TextToSpeech function
        TextToSpeech(input("Enter the text: "))
