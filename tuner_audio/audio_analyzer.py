"""
Analysing input signal.
"""
import sys
import copy
from threading import Thread
from pyaudio import PyAudio, paInt16
import numpy as np
from scipy.fft import fft as scipy_fft

# CONSTANTS
# (One of 2 methods: FFT or AUTOCORR should be enabled!)
DEBUGGING_EN = False
FFT_EN = False
AUTOCORR_EN = True


class AudioAnalyzer(Thread):
    """
    AudioAnalyzer reads the microphone and finds the frequency of the loudest tone.
    To use it, you also need the ProtectedList class from the file threading_helper.py.
    You need to created an instance of the ProtectedList, which acts as a queue, and you
    have to pass this queue to the AudioAnalyzer.
    """

    SAMPLING_RATE = 48000              # sample frequency in Hz
    CHUNK_SIZE = 3000                  # number of samples
    BUFFER_LENGTH = CHUNK_SIZE * 16    # window size in samples
    NUM_HPS = 5                        # HPS (Harmonic Product Spectrum)
    WHITE_NOISE_THRESH = 0.2   # values under WHITE_NOISE_THRESH*avg_energy_per_freq is cut off

    #              buffer length in seconds:  BUFFER_LENGTH / SAMPLING_RATE sec
    # length between two samples in seconds:  1 / SAMPLING_RATE sec
    DELTA_FREQ = SAMPLING_RATE / BUFFER_LENGTH
    OCTAVE_BANDS = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600]

    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def __init__(self, queue, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)

        self.queue = queue  # instance of ProtectedList
        self.buffer = np.zeros(self.BUFFER_LENGTH)
        self.hanning_window = np.hanning(self.BUFFER_LENGTH)
        self.running = False

        try:
            self.audio_object = PyAudio()
            self.stream = self.audio_object.open(format=paInt16,
                                                 channels=1,
                                                 rate=self.SAMPLING_RATE,
                                                 input=True,
                                                 output=False,
                                                 frames_per_buffer=self.CHUNK_SIZE)
        except Exception as e:
            sys.stderr.write(f'Error: Line {sys.exc_info()[-1].tb_lineno} {type(e).__name__} {e}\n')
            return

    @staticmethod
    def frequency_to_number(freq, a4_freq):
        """
        Converting a frequency to a note number. For example: A4 is 69.
        """
        if freq == 0:
            sys.stderr.write("Error: No frequency data. No access to microphone\n")
            return 0

        return 12 * np.log2(freq / a4_freq) + 69

    @staticmethod
    def number_to_frequency(number, a4_freq):
        """
        Converting a note number to a frequency. For example: 69 is A4.
        """
        return a4_freq * 2.0**((number - 69) / 12.0)

    @staticmethod
    def number_to_note_name(number):
        """
        Converts a note number to a note name. For example:
        - 69 is 'A',
        - 70 is 'A#',
        - ...
        """
        return AudioAnalyzer.NOTE_NAMES[int(round(number) % 12)]

    @staticmethod
    def frequency_to_note_name(frequency, a4_freq):
        """ converts frequency to note name (for example: 440 returns 'A') """

        number = AudioAnalyzer.frequency_to_number(frequency, a4_freq)
        note_name = AudioAnalyzer.number_to_note_name(number)
        return note_name

    @staticmethod
    def fft(x):
        """
        FFT.
        https://pythonnumericalmethods.studentorg.berkeley.edu/notebooks/chapter24.03-Fast-Fourier-Transform.html
        """
        n = len(x)
        if n == 1:
            return x

        x_even = AudioAnalyzer.fft(x[::2])
        x_odd = AudioAnalyzer.fft(x[1::2])
        factor = np.exp(-2j * np.pi * np.arange(n) / n)

        total = np.concatenate([x_even + factor[:int(n/2)] * x_odd,
                            x_even + factor[int(n/2):] * x_odd])
        return total

    @staticmethod
    def acf(f, w, t, lag):
        """
        Autocorrelation function.
        """
        return np.sum(f[t : t + w] * f[lag + t : lag + t + w])

    @staticmethod
    def auto_corr_detect_pitch(f, W, t, sample_rate, bounds):
        """
        Detecting pitch in autocorrelation algorithm.
        """
        ACF_vals = [AudioAnalyzer.acf(f, W, t, i) for i in range(*bounds)]
        sample = np.argmax(ACF_vals) + bounds[0]
        return sample_rate / sample

    def run(self):
        """
        Main function where the microphone buffer gets read and the FFT gets applied.
        """
        self.running = True
        if DEBUGGING_EN:
            percent_corr = []

        while self.running:
            try:
                # read microphone data
                data = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                data = np.frombuffer(data, dtype=np.int16)

                # append data to audio buffer
                self.buffer[:-self.CHUNK_SIZE] = self.buffer[self.CHUNK_SIZE:]
                self.buffer[-self.CHUNK_SIZE:] = data

                if FFT_EN:
                    # Zero-padding to the nearest power of 2.
                    # It allows one to use a longer FFT, which will produce a longer
                    # FFT result vector. A longer FFT result has more frequency bins that are
                    # more closely spaced in frequency.
                    nearest_power_of_2 = int(2 ** np.ceil(np.log2(self.BUFFER_LENGTH)))

                    # apply the FFT on the whole buffer (with zero-padding + hanning window)
                    # - Hanning window helps to control leakage, thereby increasing the dynamic
                    #   range of the analysis.
                    magnitude_data = abs(
                        AudioAnalyzer.fft(np.pad(self.buffer * self.hanning_window,
                                                (0, nearest_power_of_2 - self.BUFFER_LENGTH),
                                                "constant")))

                    # ----- Debugging part -----
                    if DEBUGGING_EN:
                        nump = abs(np.fft.fft(np.pad(self.buffer * self.hanning_window,
                                                    (0, nearest_power_of_2 - self.BUFFER_LENGTH),
                                                    "constant")))
                        sci = abs(scipy_fft(np.pad(self.buffer * self.hanning_window,
                                                (0, nearest_power_of_2 - self.BUFFER_LENGTH),
                                                "constant")))

                        print(f"Raw data:  {data[:6]}")
                        print(f"Numpy:     {nump[:6]}")
                        print(f"Scipy:     {sci[:6]}")
                        print(f"Custom:    {magnitude_data[:6]}")

                        true_values = np.sum(np.isclose(magnitude_data, nump))
                        percents = round(true_values / len(magnitude_data) * 100, 2)
                        percent_corr.append(percents)
                        print(f"FFT calculated for  {len(percent_corr)}  \
    samples: {round(np.mean(percent_corr), 2)}% of values are close to true (atol 1e-8).")

                    # use only the first half of the FFT output data
                    magnitude_data = magnitude_data[:len(magnitude_data) // 2]

                    # HPS: multiply data by itself with different scalings (Harmonic Product Spectrum)
                    magnitude_data_orig = np.copy(magnitude_data)
                    for i in range(2, self.NUM_HPS + 1):
                        hps_len = int(np.ceil(len(magnitude_data) / i))
                        magnitude_data[:hps_len] *= magnitude_data_orig[::i]  # multiply every i element

                    # get the corresponding frequency array
                    frequencies = np.fft.fftfreq(int((len(magnitude_data) * 2)),
                                                1. / self.SAMPLING_RATE)

                    # calculate the frequency
                    # N = len(magnitude_data)
                    # n = np.arange(N)
                    # T = N / self.SAMPLING_RATE
                    # freq1 = n / T
                    # print(frequencies[:5])
                    # print(freq1[:5])

                    # set magnitude of all frequencies below 60Hz to zero
                    for i, freq in enumerate(frequencies):
                        if freq > 60:
                            magnitude_data[:i - 1] = 0
                            break

                    # put the frequency of the loudest tone into the queue
                    self.queue.put(round(frequencies[np.argmax(magnitude_data)], 2))

                if AUTOCORR_EN:
                    self.queue.put(round(AudioAnalyzer.auto_corr_detect_pitch(self.buffer, self.BUFFER_LENGTH // 2,
                                                                    1, self.SAMPLING_RATE, [109, len(data) // 2]), 2))

            except Exception as e:
                sys.stderr.write(f'Error: Line {sys.exc_info()[-1].tb_lineno} {type(e).__name__} {e}\n')

        self.stream.stop_stream()
        self.stream.close()
        self.audio_object.terminate()


if __name__ == "__main__":
    # Testing:
    from threading_helper import ProtectedList
    import time

    DEBUGGING_EN = False

    q = ProtectedList()
    a = AudioAnalyzer(q)
    a.start()

    while True:
        q_data = q.get()
        if q_data is not None:
            print(f"""Loudest frequency: {q_data:7.2f}\t\
Nearest note: {a.frequency_to_note_name(q_data, 440)}""")
            time.sleep(0.01)
