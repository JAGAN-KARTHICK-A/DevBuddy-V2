# DevBuddy 🦅

DevBuddy is a modern, lightweight, and AI-powered desktop code editor built from the ground up using Python and web technologies. At its core is an integrated chat interface that connects to your favorite large language models (e.g., Google Gemini), transforming your workflow from simple text editing to a dynamic conversation with your AI coding partner.

Ask your AI assistant to scaffold entire projects, run and debug code, or generate tests, all from a natural language chat interface seamlessly integrated into your development environment.



## ✨ Features

DevBuddy is a comprehensive tool designed for an AI-first workflow.

### 🤖 AI-Powered Workflow

* **Conversational Coding:** Chat with your chosen AI model directly within the editor. Ask questions, get code snippets, and debug collaboratively without ever leaving your workspace.
* **AI Project Scaffolding:** Initiate complex projects with a single prompt. Ask the AI to create a new Python web server, a data analysis script, or a simple frontend project, and watch as it generates the necessary files and folders.
* **AI-Assisted Execution:** Instruct the AI to run the current script or execute specific shell commands in the integrated terminal. The AI can interpret the results and provide feedback.
* **AI-Driven Testing:** Request that the AI write unit tests or integration tests for your code, and then command it to run those tests and report back on the results.

### 💻 Core IDE Features

* **Full-Featured Code Editor:** Powered by the Monaco Editor (the engine behind VS Code).
* **Integrated File Explorer:** Full support for creating, renaming, and deleting files and folders, with professional file-type icons.
* **Advanced Tab Management:** Open multiple files in tabs with unsaved-changes indicators and drag-and-drop rearranging.
* **Interactive Multi-Tab Terminal:** A real, interactive shell with support for multiple, independent sessions.
* **Comprehensive Settings Panel:**
    * **Appearance:** Customize fonts, font size, weight, and line height.
    * **Dynamic Theming:** Switch between beautiful, pre-built professional themes (dark and light modes). All settings are saved and persist between sessions.

## 🛠️ Tech Stack

* **Backend:** **Python 3**
* **GUI Framework:** **pywebview**
* **AI Integration:** **Google Gemini API**, **OpenAI API**, etc.
* **Terminal Bridge:** **websockets** & **pywinpty** (on Windows)
* **Frontend:** **HTML5**, **Tailwind CSS**, **JavaScript**
* **Code Editor Component:** **Monaco Editor**
* **Terminal Component:** **xterm.js**

## 🚀 Getting Started

Follow these steps to get DevBuddy running on your local machine.

### 1. Prerequisites

* Python 3.8+
* `pip` for installing packages

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/JAGAN-KARTHICK-A/DevBuddy-V2.git](https://github.com/JAGAN-KARTHICK-A/DevBuddy-V2.git)
    cd DevBuddy-V2
    ```
    
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running the Application

1.  **Run the main application script:**
    ```bash
    python main.py
    ```
2.  The splash screen will appear, followed by the project launcher. You're ready to start coding with AI!

## 📄 License

This project is licensed under the MIT License.
