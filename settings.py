"""
Global settings for the GUI.
"""

class Settings:
    """
    Guitar Tuner global app configuration.
    """
    APP_NAME = "Guitar Tuner"
    YEAR = "2024"

    SOURCE_GITHUB_URL_README = "https://github.com/TomSchimansky/GuitarTuner#readme"
    USER_SETTINGS_PATH = "/assets/user_settings/user_settings.json"

    ABOUT_TEXT = f"{APP_NAME} for Linear Algebra Course Project {YEAR}"

    WIDTH = 450
    HEIGHT = 440

    MAX_WIDTH = 600
    MAX_HEIGHT = 500

    # canvas update rate
    FPS = 60
    # size of the audio-display
    CANVAS_SIZE = 300

    NEEDLE_BUFFER_LENGTH = 30
    HITS_TILL_NOTE_NUMBER_UPDATE = 15
