"""
Managing GUI fonts.
"""
import sys


class FontManager:
    """
    Adjusting font sizes is necessary to ensure consistent display across different OSs.
    For instance, text may appear larger on Windows compared to other OSs.
    """

    def __init__(self):
        if sys.platform == "darwin":
            self.set_darwin()
        else:
            self.set_other_os()

    def set_darwin(self):
        """
        Setting parameters for MacOs.
        """
        self.button_font = ("Avenir", 16)
        self.note_display_font = ("Avenir", 72)  # main note Text
        self.note_display_font_medium = ("Avenir", 26)  # text on left and right site
        self.frequency_text_font = ("Avenir", 15)
        self.info_text_font = ("Avenir", 14)
        self.settings_text_font = ("Avenir", 24)

    def set_other_os(self):
        """
        Setting parameters for Windows, Linux and other OSs.
        """
        self.button_font = ("Century Gothic", 14)
        self.note_display_font = ("Century Gothic", 62)
        self.note_display_font_medium = ("Century Gothic", 24)  # text on left and right site
        self.frequency_text_font = ("Century Gothic", 13)
        self.info_text_font = ("Century Gothic", 12)
        self.settings_text_font = ("Century Gothic", 20)
