import os
import sys
from pathlib import Path

class Config:
    APP_NAME = "Rebbit"
    ORGANIZATION = "RebbitDev"
    VERSION = "v1.0.0"
    
    GITHUB_USERNAME = "SubhojitGhimire"
    GITHUB_REPO = "Rebbit"
    GITHUB_BRANCH = "main"
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    ASSETS_DIR = BASE_DIR / "assets"
    ICONS_DIR = ASSETS_DIR / "icons"
    STYLES_DIR = ASSETS_DIR / "styles"
    
    DEFAULT_MUSIC_DIR = Path(os.path.expanduser("~")) / "Music" / "Rebbit"

    @staticmethod
    def get_update_url() -> str:
        return f"https://raw.githubusercontent.com/{Config.GITHUB_USERNAME}/{Config.GITHUB_REPO}/{Config.GITHUB_BRANCH}/README.md"

    @staticmethod
    def get_icon_path(filename: str) -> str:
        return str(Config.ICONS_DIR / filename)

    @staticmethod
    def get_style_path(filename: str) -> str:
        return str(Config.STYLES_DIR / filename)

    @staticmethod
    def ensure_directories():
        if not Config.DEFAULT_MUSIC_DIR.exists():
            try:
                Config.DEFAULT_MUSIC_DIR.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creating music directory: {e}")

Config.ensure_directories()

