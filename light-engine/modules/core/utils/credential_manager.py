import os
import threading

_cred_lock = threading.Lock()

def update_credentials_file(file_path: str, email: str, new_password: str):
    """
    Updates the password for an email in the credentials file.
    Format: email:password
    Thread-safe.
    """
    try:
        with _cred_lock:
            lines = []
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            
            updated = False
            new_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if ":" in line:
                    stored_email = line.split(":", 1)[0].strip()
                    if stored_email == email:
                        new_lines.append(f"{email}:{new_password}\n")
                        updated = True
                        continue
                new_lines.append(line + "\n")
            
            if not updated:
                new_lines.append(f"{email}:{new_password}\n")
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
                
    except Exception as e:
        print(f"Error updating credentials file: {e}")

def update_processed_log(file_path: str, email: str, password: str, recovery_email: str = None):
    """
    Updates or appends a log entry in the processed log file.
    Format: email|password|recovery_email
    If recovery_email is provided, it updates it. If None, it preserves the existing one.
    Thread-safe.
    """
    try:
        with _cred_lock:
            lines = []
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            
            updated = False
            new_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if "|" in line:
                    parts = line.split("|")
                    stored_email = parts[0].strip()
                    if stored_email == email:
                        # Update password and optionally recovery email
                        current_recovery = parts[2].strip() if len(parts) > 2 else ""
                        new_recovery = recovery_email if recovery_email is not None else current_recovery
                        new_lines.append(f"{email}|{password}|{new_recovery}\n")
                        updated = True
                        continue
                new_lines.append(line + "\n")
            
            if not updated:
                rec_email = recovery_email if recovery_email is not None else ""
                new_lines.append(f"{email}|{password}|{rec_email}\n")
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
                
    except Exception as e:
        print(f"Error updating processed log: {e}")
