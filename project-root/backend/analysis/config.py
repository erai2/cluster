from pathlib import Path
import os
import tomllib

def load_api_key() -> str:
    """Retrieve OpenAI API key from secret.toml or environment."""
    secret_file = Path(__file__).resolve().parent.parent / "secret.toml"
    if secret_file.exists():
        with open(secret_file, "rb") as f:
            data = tomllib.load(f)
            key = data.get("openai_api_key")
            if key:
                return key
    return os.getenv("OPENAI_API_KEY", "")
