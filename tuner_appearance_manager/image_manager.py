"""
Managing GUI images.
"""
from PIL import Image, ImageTk


class ImageManager:
    """
    Setting images.
    """
    def __init__(self, main_path):
        # Image.LANCZOS -> a high-quality downsampling filter.

        self.guitar_image = ImageTk.PhotoImage(
            Image.open(main_path + "/assets/images/guitar.png").resize((50, 50), Image.LANCZOS))

        self.guitar_hovered_image = ImageTk.PhotoImage(
            Image.open(main_path + "/assets/images/ukulele.png").resize((50, 50), Image.LANCZOS))

        self.ukulele_image = ImageTk.PhotoImage(
            Image.open(main_path + "/assets/images/ukulele.png").resize((50, 50), Image.LANCZOS))

        self.ukulele_hovered_image = ImageTk.PhotoImage(
            Image.open(main_path + "/assets/images/guitar.png").resize((50, 50), Image.LANCZOS))

        self.arrowUp_image = ImageTk.PhotoImage(
            Image.open(main_path + "/assets/images/arrowUp.png").resize((147, 46), Image.LANCZOS))

        self.arrowUp_image_hovered = ImageTk.PhotoImage(
            Image.open(main_path + "/assets/images/arrowUp_hovered.png").resize((147, 46), Image.LANCZOS))

        self.arrowDown_image = ImageTk.PhotoImage(
            Image.open(main_path + "/assets/images/arrowDown.png").resize((147, 46), Image.LANCZOS))

        self.arrowDown_image_hovered = ImageTk.PhotoImage(
            Image.open(main_path + "/assets/images/arrowDown_hovered.png").resize((147, 46), Image.LANCZOS))
