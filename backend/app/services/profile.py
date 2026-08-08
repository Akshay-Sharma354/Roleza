import json
from pathlib import Path


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

PROFILE_FILE = BASE_DIR / "profile.json"


def load_application_profile():
    if not PROFILE_FILE.exists():
        return {}

    try:
        with open(
            PROFILE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {}

        return data

    except Exception:
        return {}
