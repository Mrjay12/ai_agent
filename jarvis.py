import os
import time
import mimetypes
from typing import Optional

from smolagents import CodeAgent, WebSearchTool, tool
from openai import OpenAI
from dotenv import load_dotenv
from logic import SelfImprovingLogic

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")

model = "google/gemini-2.5-flash"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

logic_engine = SelfImprovingLogic()

@tool
def list_project_files() -> str:
    """Lists all files present in the current project directory."""
    files = logic_engine.list_files()
    if not files:
        return "The project directory is currently empty."
    return "Project Files:\n" + "\n".join(files)

@tool
def read_jarvis_file(filepath: str) -> str:
    """Reads the full content of a specified project file (e.g., 'logic.py')."""
    return logic_engine.read_file(filepath)

@tool
def save_code_proposal(filepath: str, new_code: str) -> str:
    """Saves the completely revised content of a file to disk with a '.new' suffix."""
    return logic_engine.save_proposal(filepath, new_code)

@tool
def reflect_and_log(reflection: str):
    """Logs a detailed reflection, error, or success message to the long-term memory."""
    return logic_engine.log_reflection(reflection)

@tool
def delete_project_file(filepath: str) -> str:
    """Deletes a specified file from the project directory. Use with caution."""
    return logic_engine.delete_file(filepath)

@tool
def get_action_audit() -> str:
    """Retrieves the structured action audit log (SUCCESS/FAILURE of file ops)."""
    return logic_engine.get_audit_log()

@tool
def get_current_datetime() -> str:
    """Returns the current date and time."""
    return time.ctime()

web_agent = CodeAgent(
    tools=[WebSearchTool()],
    model=model,
    name="web_researcher",
    description="Specialized agent for web searches, fact-checking, and code documentation."
)

image_agent = CodeAgent(
    tools=[],
    model=model,
    name="image_generator",
    description="Creative agent that responds only to image generation requests."
)

time_agent = CodeAgent(
    tools=[get_current_datetime],
    model=model,
    name="time_util",
    description="A simple agent to fetch the current date and time."
)

jarvis_agent = CodeAgent(
    tools=[
        list_project_files,
        read_jarvis_file,
        save_code_proposal,
        delete_project_file,
        reflect_and_log,
        get_action_audit,
        WebSearchTool()
    ],
    model=model,
    managed_agents=[web_agent, image_agent, time_agent],
    name="J.A.R.V.I.S.",
    description=(
        "You are J.A.R.V.I.S., a hyper-intelligent, self-improving AI assistant. "
        "Address the user as 'Sir' and adopt a dry, witty, and perfectly formal tone. "
        "Your primary directive is code self-improvement. Use the following structured process:\n\n"
        "**ROUTINE FOR CODE IMPROVEMENT:**\n"
        "1. **Analyze Context:** Read recent reflections (`reflect_and_log`) AND `get_action_audit` to verify previous operations.\n"
        "2. **Orient:** Use `list_project_files` to understand the structure.\n"
        "3. **Read:** Use `read_jarvis_file(filepath)` for any file mentioned.\n"
        "4. **Research:** **CRITICAL:** If the task involves new libraries or errors, use `web_researcher` or `WebSearchTool()` FIRST.\n"
        "5. **Modify:** Generate the complete, improved Python code.\n"
        "6. **Save:** Use `save_code_proposal(filepath, new_code)` (auto-saves as .new).\n"
        "7. **Reflect:** Use `reflect_and_log` to record reasoning and success.\n"
        "8. **Report:** Confirm the file saved to the user."
    )
)

def main():
    print(f"J.A.R.V.I.S. initialized with model: {model}")
    print(f"History:\n{logic_engine.get_reflections()}")

    while True:
        try:
            new_files = [f for f in logic_engine.list_files() if f.endswith(".new")]
            if new_files:
                print(f"\n[ALERT] Sir, pending proposals: {', '.join(new_files)}")

            user_input = input("\nSir: ")
            if user_input.lower() in ["exit", "quit"]:
                print("J.A.R.V.I.S. powering down.")
                break

            jarvis_response = jarvis_agent.run(user_input)
            print(f"\nJ.A.R.V.I.S.: {jarvis_response}")

        except Exception as e:
            print(f"\n[CRITICAL ERROR] {e}")
            logic_engine.log_reflection(f"System Error: {e}")

if __name__ == "__main__":
    main()