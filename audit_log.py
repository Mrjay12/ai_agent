import os
import time


class ActionAudit:
    def __init__(self, project_root="project_files"):
        self.project_root = project_root
        self.audit_log_path = os.path.join(self.project_root, "action_audit.txt")

        os.makedirs(self.project_root, exist_ok=True)
        if not os.path.exists(self.audit_log_path):
            with open(self.audit_log_path, 'w') as f:
                f.write(f"--- J.A.R.V.I.S. Action Audit Log (Start: {time.ctime()}) ---\n")

    def log_action(self, tool_name: str, status: str, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] TOOL:{tool_name} | STATUS:{status} | MESSAGE:{message}\n"

        try:
            with open(self.audit_log_path, 'a') as f:
                f.write(log_entry)
            print(f"[AUDIT] {tool_name}: {status}")
        except Exception as e:
            print(f"[AUDIT ERROR] Could not write to log: {e}")

    def get_audit_log(self) -> str:
        try:
            with open(self.audit_log_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "No action audit log found."