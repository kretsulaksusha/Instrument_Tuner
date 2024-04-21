"""
Guitar Tuner GUI.
"""
import time
import random
import tkinter
import tkinter.messagebox
import os
import sys
import json
import numpy as np

from tuner_audio.audio_analyzer import AudioAnalyzer
from tuner_audio.threading_helper import ProtectedList

from tuner_appearance_manager.color_manager import ColorManager
from tuner_appearance_manager.image_manager import ImageManager
from tuner_appearance_manager.font_manager import FontManager
from tuner_appearance_manager.timing import Timer

from tuner_ui_parts.main_frame import MainFrame
from tuner_ui_parts.ukulele_frame import UkuleleFrame
from tuner_ui_parts.settings_frame import SettingsFrame

from settings import Settings


def center(win: tkinter.Tk) -> None:
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry(f'{width}x{height}+{x}+{y}')
    win.deiconify()


class App(tkinter.Tk):
    """
    Guitar Tuner.
    """
    def __init__(self, *args, **kwargs):
        if sys.platform == "darwin":  # macOS
            s, m, e = map(int, tkinter.Tcl().call("info", "patchlevel").split("."))
            if (s >= 8 and m >= 6 and e >= 9):  # Tcl/Tk >= 8.6.9
                os.system("defaults write -g NSRequiresAquaSystemAppearance -bool No")

        tkinter.Tk.__init__(self, *args, **kwargs)
        self.main_path = os.path.dirname(os.path.abspath(__file__))

        self.color_manager = ColorManager()
        self.font_manager = FontManager()
        self.image_manager = ImageManager(self.main_path)
        self.frequency_queue = ProtectedList()

        # Guitar tuner
        self.main_frame = MainFrame(self)
        # Ukulele tuner
        self.ukulele_frame = UkuleleFrame(self)
        self.settings_frame = SettingsFrame(self)

        self.curr_frame = "guitar"

        self.audio_analyzer = AudioAnalyzer(self.frequency_queue)
        self.audio_analyzer.start()

        self.timer = Timer(Settings.FPS)

        self.needle_buffer_array = np.zeros(Settings.NEEDLE_BUFFER_LENGTH)
        self.tone_hit_counter = 0
        self.note_number_counter = 0
        self.nearest_note_number_buffered = 69
        self.a4_frequency = 440

        self.dark_mode_active = False

        self.title(Settings.APP_NAME)
        self.geometry(str(Settings.WIDTH) + "x" + str(Settings.HEIGHT))
        self.resizable(True, True)
        self.minsize(Settings.WIDTH, Settings.HEIGHT)
        self.maxsize(Settings.MAX_WIDTH, Settings.MAX_HEIGHT)
        self.configure(background=self.color_manager.background_layer_1)

        center(self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        if sys.platform == "darwin":  # macOS
            self.bind("<Command-q>", self.on_closing)
            self.bind("<Command-w>", self.on_closing)
            self.createcommand('tk::mac::Quit', self.on_closing)
            self.createcommand('tk::mac::ShowPreferences', self.draw_settings_frame)

            menu_bar = tkinter.Menu(master=self)
            app_menu = tkinter.Menu(menu_bar, name='apple')
            menu_bar.add_cascade(menu=app_menu)

            app_menu.add_command(label='About ' + Settings.APP_NAME, command=self.about_dialog)
            app_menu.add_separator()

            self.config(menu=menu_bar)

        elif "win" in sys.platform:  # Windows
            self.bind("<Alt-Key-F4>", self.on_closing)

        self.draw_main_frame()

        if self.read_user_setting("ukulele") is True:
            self.main_frame.button_inst.set_pressed(True)
            self.draw_ukulele_frame()

        self.open_app_time = time.time()

    @staticmethod
    def about_dialog():
        tkinter.messagebox.showinfo(title=Settings.APP_NAME,
                                    message=Settings.ABOUT_TEXT)

    def draw_settings_frame(self):
        """
        Displaying settings frame.
        """
        if self.curr_frame == "guitar":
            self.settings_frame.prev_frame = "guitar"
            self.main_frame.place_forget()
        else:
            self.settings_frame.prev_frame = "ukulele"
            self.ukulele_frame.place_forget()
        self.curr_frame = "settings"
        self.settings_frame.place(relx=0, rely=0, relheight=1, relwidth=1)

    def draw_main_frame(self):
        """
        Displaying guitar frame.
        """
        if self.curr_frame == "settings":
            self.settings_frame.place_forget()
        else:
            self.ukulele_frame.place_forget()
        self.curr_frame = "guitar"
        self.main_frame.place(relx=0, rely=0, relheight=1, relwidth=1)

    def draw_ukulele_frame(self):
        """
        Displaying ukulele frame.
        """
        if self.curr_frame == "settings":
            self.settings_frame.place_forget()
        else:
            self.main_frame.place_forget()
        self.curr_frame = "ukulele"
        self.ukulele_frame.place(relx=0, rely=0, relheight=1, relwidth=1)

    def write_user_setting(self, setting, value):
        with open(self.main_path + Settings.USER_SETTINGS_PATH, "r") as file:
            user_settings = json.load(file)

        user_settings[setting] = value

        with open(self.main_path + Settings.USER_SETTINGS_PATH, "w") as file:
            json.dump(user_settings, file)

    def read_user_setting(self, setting):
        with open(self.main_path + Settings.USER_SETTINGS_PATH) as file:
            user_settings = json.load(file)

        return user_settings[setting]

    def on_closing(self):
        """
        Handle closing app.
        """
        self.audio_analyzer.running = False
        self.destroy()

    def update_color(self):
        self.main_frame.update_color()
        self.settings_frame.update_color()

    def handle_appearance_mode(self, mode):
        """
        Select appearance mode.
        """
        if mode == "Dark":
            self.color_manager.set_mode("Dark")
        else:
            self.color_manager.set_mode("Light")

        self.update_color()

    def start(self):
        """
        Starting the app.
        """
        self.handle_appearance_mode("Dark")

        # handle new usage statistics when program is started
        if self.read_user_setting("id") is None:
            # generate random id
            self.write_user_setting("id", random.randint(10**20, (10**21)-1))

        while self.audio_analyzer.running:
            try:
                # get the current frequency from the queue
                freq = self.frequency_queue.get()
                if freq is not None:

                    # convert frequency to note number
                    number = self.audio_analyzer.frequency_to_number(freq, self.a4_frequency)

                    # calculate nearest note number, name and frequency
                    nearest_note_number = round(number)
                    nearest_note_freq = self.audio_analyzer.number_to_frequency(nearest_note_number, self.a4_frequency)

                    # calculate frequency difference from freq to nearest note
                    freq_difference = nearest_note_freq - freq

                    # calculate the frequency difference to the next note (-1)
                    semitone_step = nearest_note_freq - self.audio_analyzer.number_to_frequency(round(number-1),
                                                                                                self.a4_frequency)

                    # calculate the angle of the display needle
                    needle_angle = -90 * ((freq_difference / semitone_step) * 2)

                    # buffer the current nearest note number change
                    if nearest_note_number != self.nearest_note_number_buffered:
                        self.note_number_counter += 1
                        if self.note_number_counter >= Settings.HITS_TILL_NOTE_NUMBER_UPDATE:
                            self.nearest_note_number_buffered = nearest_note_number
                            self.note_number_counter = 0

                    # if needle in range +-5 degrees then make it green, otherwise red
                    if abs(freq_difference) < 0.25:
                        if self.curr_frame == "guitar":
                            self.main_frame.set_needle_color("green")
                        else:
                            self.ukulele_frame.set_needle_color("green")
                        self.tone_hit_counter += 1
                    else:
                        if self.curr_frame == "guitar":
                            self.main_frame.set_needle_color("red")
                        else:
                            self.ukulele_frame.set_needle_color("red")
                        self.tone_hit_counter = 0

                    # after 7 hits of the right note in a row play the sound
                    if self.tone_hit_counter > 7:
                        self.tone_hit_counter = 0

                    # update needle buffer array
                    self.needle_buffer_array[:-1] = self.needle_buffer_array[1:]
                    self.needle_buffer_array[-1:] = needle_angle

                    # update ui note labels and display needle
                    if self.curr_frame == "guitar":
                        self.main_frame.set_needle_angle(np.average(self.needle_buffer_array))
                        self.main_frame.set_note_names(note_name=self.audio_analyzer.number_to_note_name(self.nearest_note_number_buffered),
                                                    note_name_lower=self.audio_analyzer.number_to_note_name(self.nearest_note_number_buffered - 1),
                                                    note_name_higher=self.audio_analyzer.number_to_note_name(self.nearest_note_number_buffered + 1))
                    else:
                        self.ukulele_frame.set_needle_angle(np.average(self.needle_buffer_array))
                        self.ukulele_frame.set_note_names(note_name=self.audio_analyzer.number_to_note_name(self.nearest_note_number_buffered),
                                                    note_name_lower=self.audio_analyzer.number_to_note_name(self.nearest_note_number_buffered - 1),
                                                    note_name_higher=self.audio_analyzer.number_to_note_name(self.nearest_note_number_buffered + 1))


                    # calculate difference in cents
                    if semitone_step == 0:
                        diff_cents = 0
                    else:
                        diff_cents = (freq_difference / semitone_step) * 100
                    freq_label_text = f"+{round(-diff_cents, 1)} cents" if -diff_cents > 0 else f"{round(-diff_cents, 1)} cents"
                    if self.curr_frame == "guitar":
                        self.main_frame.set_frequency_difference(freq_label_text)
                    else:
                        self.ukulele_frame.set_frequency_difference(freq_label_text)

                    # set current frequency
                    if freq is not None:
                        if self.curr_frame == "guitar":
                            self.main_frame.set_frequency(freq)
                        else:
                            self.ukulele_frame.set_frequency(freq)

                self.update()
                self.timer.wait()

            except IOError as err:
                sys.stderr.write(f'Error: Line {sys.exc_info()[-1].tb_lineno} {type(err).__name__} {err}\n')
                self.update()
                self.timer.wait()


if __name__ == "__main__":
    app = App()
    app.start()
