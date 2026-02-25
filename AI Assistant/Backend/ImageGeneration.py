import asyncio
import random
import io
from PIL import Image
from random import randint
import requests
import os
from dotenv import get_key
from time import sleep

# Function to open and display images based on a given prompt
def open_images(prompt: str):
    folder_path = "Data"
    prompt_safe = prompt.replace(" ", "_")
    files = [f"{prompt_safe}({i}).jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except Exception as e:
            print(f"Unable to open {image_path}: {e}")

# API details for Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Asynchronous function to send a query
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error from API: {response.status_code} - {response.text}")
        return None
    return response.content

# Asynchronous function to generate images
async def generate_images(prompt: str):
    os.makedirs("Data", exist_ok=True)
    tasks = []
    prompt_safe = prompt.replace(" ", "_")

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 100000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is None:
            continue  # Skip if API failed

        file_path = fr"Data\{prompt_safe}({i+1}).jpg"
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.save(file_path)
            print(f"Saved {file_path}")
        except Exception as e:
            print(f"Error saving image {file_path}: {e}")

# Wrapper to generate + open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Main loop
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()

        if "," in Data:
            Prompt, Status = Data.split(",")
        else:
            sleep(1)
            continue

        if Status.strip() == "True":
            print("Generating Images ...")
            GenerateImages(prompt=Prompt.strip())

            # Reset the status
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False, False")
            break  # Done
        else:
            sleep(1)

    except Exception as e:
        print(f"Error occurred: {e}")
        sleep(1)
