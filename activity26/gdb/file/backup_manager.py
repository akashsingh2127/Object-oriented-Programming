import os
import shutil
from datetime import datetime

class BackupManager:
    """
    Manager for timestamped rolling file backups and retention policy enforcement.
    """

    @staticmethod
    def backup(file_path: str, max_backups: int = 5) -> None:
        """Creates a timestamped backup of file_path and prunes backups exceeding max_backups."""
        if not os.path.exists(file_path):
            return

        dir_name = os.path.dirname(os.path.abspath(file_path))
        base_name = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = f"{file_path}.bak.{timestamp}"

        try:
            shutil.copy2(file_path, backup_path)
        except Exception:
            return

        # Enforce retention limit
        try:
            prefix = f"{base_name}.bak."
            backups = []
            for entry in os.listdir(dir_name):
                if entry.startswith(prefix):
                    full_p = os.path.join(dir_name, entry)
                    if os.path.isfile(full_p):
                        backups.append(full_p)

            # Sort by modification time ascending (oldest first)
            backups.sort(key=lambda p: (os.path.getmtime(p), p))

            if len(backups) > max_backups:
                to_remove = len(backups) - max_backups
                for p in backups[:to_remove]:
                    try:
                        os.remove(p)
                    except Exception:
                        pass
        except Exception:
            pass

    @staticmethod
    def create_backup(file_path: str, max_backups: int = 5) -> None:
        """Alias for backup(file_path, max_backups)."""
        BackupManager.backup(file_path, max_backups)
