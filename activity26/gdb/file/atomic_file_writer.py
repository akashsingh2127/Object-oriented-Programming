import os
import time
from typing import List

class AtomicFileWriter:
    """
    Crash-resilient file writer implementing the Atomic Write Pattern.
    Writes content to a temporary file first, flushes and syncs buffers to disk,
    and then atomically renames the temp file to the target destination using os.replace().
    """

    @staticmethod
    def write(file_path: str, lines: List[str]) -> None:
        """Writes lines to file_path atomically."""
        dir_name = os.path.dirname(os.path.abspath(file_path))
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        temp_path = f"{file_path}.tmp.{time.time_ns()}"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                for line in lines:
                    if not line.endswith("\n"):
                        f.write(line + "\n")
                    else:
                        f.write(line)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, file_path)
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            raise

    @staticmethod
    def write_lines(file_path: str, lines: List[str]) -> None:
        """Alias for write(file_path, lines)."""
        AtomicFileWriter.write(file_path, lines)
