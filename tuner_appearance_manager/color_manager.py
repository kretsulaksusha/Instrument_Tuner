"""
Managing GUI colors.
"""

class ColorManager:
    """
    Selecting GUI color.
    """
    def __init__(self):
        self.set_mode("Dark")

    def set_mode(self, mode):
        """
        Setting different color modes.
        """
        if mode == "Dark":
            self.background_layer_1 = self.rgb_to_hex((50, 50, 50))
            self.background_layer_0 = self.rgb_to_hex((33, 33, 33))
            self.text_main = self.rgb_to_hex((255, 255, 255))
            self.text_2 = self.rgb_to_hex((169, 169, 169))
            self.text_2_highlight = self.rgb_to_hex((240, 240, 240))
            self.theme_main = self.rgb_to_hex((134, 39, 189))
            self.theme_dark = self.rgb_to_hex((69, 0, 110))
            self.theme_light = self.rgb_to_hex((85, 140, 200))
            self.needle = self.rgb_to_hex((189, 39, 84))
            self.needle_hit = self.rgb_to_hex((43, 113, 53))

        elif mode == "Light":
            self.background_layer_1 = self.rgb_to_hex((241, 239, 238))
            self.background_layer_0 = self.rgb_to_hex((209, 208, 206))
            self.text_main = self.rgb_to_hex((0, 0, 0))
            self.text_2 = self.rgb_to_hex((36, 36, 36))
            self.text_2_highlight = self.rgb_to_hex((0, 0, 0))
            self.theme_main = self.rgb_to_hex((83, 147, 213))
            self.theme_dark = self.rgb_to_hex((94, 51, 146))
            self.theme_light = self.rgb_to_hex((128, 175, 223))
            self.needle = self.rgb_to_hex((107, 42, 28))
            self.needle_hit = self.rgb_to_hex((43, 113, 53))

    def rgb_to_hex(self, rgb):
        """
        Translating rgb to hex.
        """
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
