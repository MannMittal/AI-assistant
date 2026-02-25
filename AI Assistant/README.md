# Project AI Assistant

**Project AI Assistant** is a modular, JARVIS-style AI assistant built in Python with a PyQt5 GUI. It allows both **text and voice interaction**, can perform **automation tasks**, generate AI images, and optionally interface with hardware devices. The assistant is designed to be highly extensible, so you can add new modules, automation commands, and hardware integrations easily. This project was inspired by @theshreshthkaushik YouTube channel, whose tutorials guided the design, architecture, and core concepts of this assistant, while all the code here has been independently implemented and extended.

---

## Features

* **GUI Interface**

  * PyQt5-based with animated chat and dynamic messages
  * Microphone and speech status indicators

* **Voice Interaction**

  * Speech-to-Text (STT) for commands
  * Text-to-Speech (TTS) for assistant responses

* **Command Automation**

  * System app control (launch apps, open files, web search)
  * YouTube playback automation
  * Custom command triggers

* **AI Integration**

  * Uses Groq LLaMA-3 for reasoning and response generation
  * Cohere for command categorization
  * AI image generation module via subprocess calls

* **Hardware Integration (Optional)**

  * Microcontrollers (Raspberry Pi, Arduino) via Python APIs
  * IoT devices (smart lights, plugs) via REST/MQTT
  * Robotics, LED notifications, and peripheral control

* **Modular & Extensible**

  * Separate modules for chat, automation, speech, and image generation
  * Easily add new modules without modifying core logic
  * Configuration via `.env` for API keys and sensitive data

---

## How It Works

1. **Startup:** Run `main.py` to launch the PyQt5 GUI.
2. **Text or Voice Commands:**

   * Type commands in the chatbox or use the microphone toggle for voice input.
   * Speech is converted to text, analyzed, and categorized using Cohere.
3. **AI Processing:**

   * Commands requiring reasoning are passed to Groq LLaMA-3.
   * Responses are returned as text and optionally spoken via TTS.
4. **Automation:**

   * The assistant executes system commands, opens apps, or runs scripts.
   * YouTube or web search automation is handled via predefined modules.
5. **Image Generation:**

   * Use prompts to generate AI images via subprocess calls.
6. **Hardware Interaction (Optional):**

   * Control devices via APIs, GPIO, or network interfaces.

---

## Setup & Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/Project-AI-Assistant.git
cd Project-AI-Assistant
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:

```
GROQ_API_KEY=your-groq-llama3-key
COHERE_API_KEY=your-cohere-key
OTHER_API_KEYS=...
```

4. Run the assistant:

```bash
python main.py
```

---

## Folder Structure

* `main.py` — Entry point for the GUI
* `modules/` — Contains chat, automation, speech, and image modules
* `resources/` — GIFs, icons, and other UI assets
* `.env` — Configuration file for API keys and sensitive data
* `requirements.txt` — Python dependencies

---

## Contribution

We welcome contributions! Feel free to modify, improve, and extend this project.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## Credits & License

This project was inspired by tutorials and demonstrations by **@theshreshthkaushik** YouTube channel, which guided the design and architecture of this assistant. All code here has been independently implemented and extended by the author.

This project is licensed under the **MIT License**. You are free to use, copy, modify, and redistribute the code.
