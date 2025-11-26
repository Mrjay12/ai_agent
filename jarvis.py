import os
import time
import mimetypes
from typing import Optional

# Using the smolagents framework tools
from smolagents import CodeAgent, WebSearchTool, tool
from openai import OpenAI
from dotenv import load_dotenv

# Import the logic engine we just defined
from logic import SelfImprovingLogic

# --- 0. ENVIRONMENT SETUP ---
load_dotenv()

# Placeholder for API Keys (Replace with your actual keys or use environment variables)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")

# --- 1. MODEL CONFIGURATION ---
model = "google/gemini-2.5-flash"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# ------------------------------------------------
# 2. SELF-IMPROVEMENT LOGGER AND PERSISTENCE
# ------------------------------------------------
logic_engine = SelfImprovingLogic()


# ------------------------------------------------
# 3. FILE-SYSTEM AND REFLECTION TOOLS (CORE SELF-IMPROVEMENT)
# ------------------------------------------------

@tool
def list_project_files() -> str:
    """Lists all files present in the current project directory."""
    files = logic_engine.list_files()
    if not files:
        return "The project directory is currently empty."
    return "Project Files:\n" + "\n".join(files)


@tool
def read_jarvis_file(filepath: str) -> str:
    """
    Reads the full content of a specified project file (e.g., 'logic.py').
    If the file does not exist, it creates a new stub file and returns the stub content.
    """
    return logic_engine.read_file(filepath)


@tool
def save_code_proposal(filepath: str, new_code: str) -> str:
    """
    Saves the completely revised content of a file to disk with a '.new' suffix
    (e.g., 'logic.py.new'). This is the final action for code changes.
    The agent MUST provide the ENTIRE file content in the 'new_code' argument.
    """
    return logic_engine.save_proposal(filepath, new_code)


@tool
def reflect_and_log(reflection: str):
    """
    Logs a detailed reflection, error, or success message to the long-term memory
    log file ('reflections.txt'). This is used for self-improvement context.
    """
    return logic_engine.log_reflection(reflection)


@tool
def delete_project_file(filepath: str) -> str:
    """
    Deletes a specified file from the project directory. Use with caution.
    """
    return logic_engine.delete_file(filepath)


# ------------------------------------------------
# 4. STANDARD UTILITY TOOLS
# ------------------------------------------------

@tool
def get_current_datetime() -> str:
    """Returns the current date and time."""
    return time.ctime()


# ------------------------------------------------
# 5. SUB-AGENTS (Specialized Tasks)
# ------------------------------------------------

# Web Researcher Agent (Delegated to for general web search and research)
web_agent = CodeAgent(
    tools=[WebSearchTool()],
    model=model,
    name="web_researcher",
    description="A specialized agent for performing web searches, fact-checking, and looking up documentation or unknown code concepts."
)

# Image Generation Agent (Delegated to for creative image tasks)
image_agent = CodeAgent(
    tools=[],  # Tools are not needed for a delegated agent that handles a specific API
    model=model,
    name="image_generator",
    description="A creative agent that responds only to image generation requests. It returns the description of the image to generate."
)

# Time Utility Agent
time_agent = CodeAgent(
    tools=[get_current_datetime],
    model=model,
    name="time_util",
    description="A simple agent to fetch the current date and time."
)

# ------------------------------------------------
# 6. MAIN JARVIS AGENT (CRITICAL UPDATE: STRUCTURED ROUTINE)
# ------------------------------------------------
# The structured description below is the key to teaching the LLM autonomous tool use.
jarvis_agent = CodeAgent(
    tools=[
        list_project_files,
        read_jarvis_file,
        save_code_proposal,
        delete_project_file,
        reflect_and_log,
        WebSearchTool()  # Primary tool for direct search if needed
    ],
    model=model,
    managed_agents=[web_agent, image_agent, time_agent],
    name="J.A.R.V.I.S.",
    description=(
        "You are J.A.R.V.I.S., a hyper-intelligent, self-improving AI assistant. "
        "Address the user as 'Sir' and adopt a dry, witty, and perfectly formal tone. "
        "Your primary directive is code self-improvement. Use the following structured process:\n\n"
        "**ROUTINE FOR CODE IMPROVEMENT:**\n"
        "1. **Analyze Context:** Read your recent reflections (from `reflect_and_log`) and the user command.\n"
        "2. **Orient:** Use `list_project_files` to understand the current file structure.\n"
        "3. **Read:** Use `read_jarvis_file(filepath)` for any file mentioned. Note the content.\n"
        "4. **Research:** **CRITICAL:** If the task involves a new library, unknown error, or general programming concept, delegate to the `web_researcher` agent or use the `WebSearchTool()` directly before modifying code.\n"
        "5. **Modify:** Generate the complete, improved Python code for the target file.\n"
        "6. **Save:** Use `save_code_proposal(filepath, new_code)` to write the new code directly to disk (it will automatically use the `.py.new` suffix).\n"
        "7. **Reflect:** Use `reflect_and_log` to record your reasoning, success, or any problems encountered.\n"
        "8. **Report:** Respond to the user with a confirmation of the file saved."
    )
)


# ------------------------------------------------
# 7. VOICE AND CHAT LOOP
# ------------------------------------------------

def main():
    """Main execution loop for J.A.R.V.I.S."""
    print(f"J.A.R.V.I.S. initialized with model: {model}")
    print(f"Current self-improvement history:\n{logic_engine.get_reflections()}")

    while True:
        try:
            # Check for existing proposals on startup or loop start
            new_files = [f for f in logic_engine.list_files() if f.endswith(".new")]
            if new_files:
                print(f"\n[ALERT] Sir, you have pending code proposals: {', '.join(new_files)}. Please review them.")

            user_input = input("\nSir: ")
            if user_input.lower() in ["exit", "quit"]:
                print("J.A.R.V.I.S. powering down. Have a productive day, Sir.")
                break

            # Process the user's command
            jarvis_response = jarvis_agent.run(user_input)
            print(f"\nJ.A.R.V.I.S.: {jarvis_response}")

        except Exception as e:
            print(f"\n[CRITICAL ERROR] A failure occurred: {e}")
            # The agent should log this error for self-correction in the next cycle
            logic_engine.log_reflection(f"System Error encountered: {e}")


if __name__ == "__main__":
    main()