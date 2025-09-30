import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / "../.env"

class Settings:
    def __init__(self):
        load_dotenv()
        self.oauth_token = os.getenv("YWM_OAUTH_TOKEN")
        self.output_dir = os.getenv("YWM_OUTPUT_DIR")
        self.host_domain = os.getenv("YWM_HOST_DOMAIN")
        self.limit = int(os.getenv("YWM_LIMIT", "100"))
        self.offset = int(os.getenv("YWM_OFFSET", "0"))

    @staticmethod
    def save_env(key: str, value: str) -> None:
        os.environ[key] = value
        lines = []
        if ENV_PATH.exists():
            lines = ENV_PATH.read_text(encoding="utf-8").splitlines(True)

        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
                break
        if not found:
            lines.append(f"{key}={value}\n")

        ENV_PATH.write_text("".join(lines), encoding="utf-8")