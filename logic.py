import os
import time
from typing import List, Dict, Any


# --- MOCK PERSISTENCE SETUP ---
# In a real environment, this would interface with a database (like Firestore)
# and a real file system. Here, we use simple file operations for the simulation.

class SelfImprovingLogic:
    """
    Manages the project's memory, including file content and the reflection log.
    In a real application, this class handles database/file-system persistence.
    """

    def __init__(self, project_root="project_files"):
        self.project_root = project_root
        os.makedirs(self.project_root, exist_ok=True)
        self.reflection_log_path = os.path.join(self.project_root, "reflections.txt")

        # Ensure the reflection log file exists
        if not os.path.exists(self.reflection_log_path):
            with open(self.reflection_log_path, 'w') as f:
                f.write(f"--- J.A.R.V.I.S. Reflection Log (Start: {time.ctime()}) ---\n")

    def read_file(self, filepath: str) -> str:
        """
        Reads a project file. If the file does not exist, it creates a stub
        and returns the stub content, ensuring the LLM always has content to edit.
        """
        full_path = os.path.join(self.project_root, filepath)

        if not os.path.exists(full_path):
            print(f"[LOGIC] File not found: {filepath}. Creating stub.")
            stub_content = f"# {filepath}\n# Initial stub created by J.A.R.V.I.S. at {time.ctime()}\n\n"
            with open(full_path, 'w') as f:
                f.write(stub_content)
            return stub_content

        with open(full_path, 'r') as f:
            return f.read()

    def list_files(self) -> List[str]:
        """Lists all files in the project root."""
        return [f for f in os.listdir(self.project_root)
                if
                os.path.isfile(os.path.join(self.project_root, f)) and f != os.path.basename(self.reflection_log_path)]

    def save_proposal(self, filepath: str, new_code: str) -> str:
        """
        Saves the new code to a .new file for review, simulating a code proposal.
        The agent's main file (e.g., jarvis_kimi_free.py) should never be directly overwritten.
        """
        new_filepath = os.path.join(self.project_root, f"{filepath}.new")
        with open(new_filepath, 'w') as f:
            f.write(new_code)
        return f"[SUCCESS] Proposed improvement saved to: {new_filepath}. Awaiting Sir's approval."

    def log_reflection(self, reflection: str):
        """Appends a timestamped reflection to the log file."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {reflection}\n"
        with open(self.reflection_log_path, 'a') as f:
            f.write(log_entry)
        print(f"[REFLECTION LOGGED]")

    def get_reflections(self) -> str:
        """Retrieves the full reflection log for context."""
        try:
            with open(self.reflection_log_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "No previous reflections found."

    def delete_file(self, filepath: str) -> str:
        """Deletes a file from the project root."""
        full_path = os.path.join(self.project_root, filepath)
        if os.path.exists(full_path):
            os.remove(full_path)
            return f"[SUCCESS] File '{filepath}' has been deleted."
        return f"[FAILURE] File '{filepath}' not found, nothing to delete."