import os
from pathlib import Path
from dotenv import load_dotenv


def load_config(required_keys: list[str] | None = None) -> dict:
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    config = {key: os.environ.get(key) for key in (required_keys or [])}

    missing = [k for k, v in config.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in the values."
        )

    return {**config, **{k: v for k, v in os.environ.items() if k not in config}}
