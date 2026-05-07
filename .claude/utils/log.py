from datetime import datetime
from pathlib import Path


def make_logger(tag, log_path):
    log_path = Path(log_path)

    def log(detail):
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a") as f:
                f.write(f"{datetime.now().isoformat()}\t[{tag}]\t{detail}\n")
        except Exception:
            pass

    return log
