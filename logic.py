import os
import time
from typing import List
from audit_log import ActionAudit


class SelfImprovingLogic:
    def __init__(self, project_root="project_files"):
        self.project_root = project_root
        os.makedirs(self.project_root, exist_ok=True)
        self.reflection_log_path = os.path.join(self.project_root, "reflections.txt")
        self.audit_logger = ActionAudit(project_root)

        if not os.path.exists(self.reflection_log_path):
            with open(self.reflection_log_path, 'w') as f:
                f.write(f"--- J.A.R.V.I.S. Reflection Log (Start: {time.ctime()}) ---\n")

    def read_file(self, filepath: str) -> str:
        full_path = os.path.join(self.project_root, filepath)
        if not os.path.exists(full_path):
            stub = f"# {filepath}\n# Stub created by J.A.R.V.I.S.\n"
            with open(full_path, 'w') as f:
                f.write(stub)
            return stub
        with open(full_path, 'r') as f:
            return f.read()

    def list_files(self) -> List[str]:
        hidden_files = [
            os.path.basename(self.reflection_log_path),
            os.path.basename(self.audit_logger.audit_log_path)
        ]
        return [f for f in os.listdir(self.project_root)
                if os.path.isfile(os.path.join(self.project_root, f)) and f not in hidden_files]

    def save_proposal(self, filepath: str, new_code: str) -> str:
        new_filepath = os.path.join(self.project_root, f"{filepath}.new")
        try:
            with open(new_filepath, 'w') as f:
                f.write(new_code)

            msg = f"[SUCCESS] Saved proposal to {new_filepath}"
            self.audit_logger.log_action("save_code_proposal", "SUCCESS", msg)
            return msg
        except Exception as e:
            msg = f"[FAILURE] Error saving {filepath}: {str(e)}"
            self.audit_logger.log_action("save_code_proposal", "FAILURE", msg)
            return msg

    def delete_file(self, filepath: str) -> str:
        full_path = os.path.join(self.project_root, filepath)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                msg = f"[SUCCESS] Deleted {filepath}"
                self.audit_logger.log_action("delete_project_file", "SUCCESS", msg)
                return msg
            except Exception as e:
                msg = f"[FAILURE] Could not delete {filepath}: {str(e)}"
                self.audit_logger.log_action("delete_project_file", "FAILURE", msg)
                return msg
        else:
            msg = f"[FAILURE] File {filepath} not found."
            self.audit_logger.log_action("delete_project_file", "FAILURE", msg)
            return msg

    def log_reflection(self, reflection: str):
        entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {reflection}\n"
        with open(self.reflection_log_path, 'a') as f:
            f.write(entry)

    def get_reflections(self) -> str:
        try:
            with open(self.reflection_log_path, 'r') as f:
                return f.read()
        except:
            return "No reflections found."

    def get_audit_log(self) -> str:
        return self.audit_logger.get_audit_log()