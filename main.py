import sys
from PySide6.QtWidgets import QApplication

from src.utils.config import Config
from src.ui.main_controller import MainController

def load_stylesheet(app, theme_file="dark_theme.css"):
    style_path = Config.get_style_path(theme_file)
    try:
        with open(style_path, "r") as f:
            style = f.read()
            app.setStyleSheet(style)
    except FileNotFoundError:
        print(f"Warning: Theme file not found at {style_path}")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(Config.APP_NAME)
    app.setOrganizationName(Config.ORGANIZATION)
    load_stylesheet(app)
    controller = MainController(app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

