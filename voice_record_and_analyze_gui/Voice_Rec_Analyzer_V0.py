import tkinter as tk
import sounddevice as sd
import numpy as np
import wave
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class AudioRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Recorder and Analyzer")

        # Variables
        self.fs = 16000  # Sampling frequency
        self.recording = False
        self.audio_data = []
        self.current_xlim = None

        # Create Frames
        self.record_frame = tk.Frame(root, padx=10, pady=10, relief=tk.GROOVE, borderwidth=2)
        self.record_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.analysis_frame = tk.Frame(root, padx=10, pady=10, relief=tk.GROOVE, borderwidth=2)
        self.analysis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Recording Panel
        tk.Label(self.record_frame, text="Recording Panel", font=("Arial", 14)).pack(pady=5)
        self.record_button = tk.Button(self.record_frame, text="Start Recording", command=self.start_recording)
        self.record_button.pack(pady=10)

        self.stop_button = tk.Button(self.record_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.save_audio_button = tk.Button(self.record_frame, text="Save Audio", command=self.save_audio, state=tk.DISABLED)
        self.save_audio_button.pack(pady=10)

        # Analysis Panel
        tk.Label(self.analysis_frame, text="Analysis Panel", font=("Arial", 14)).pack(pady=5)
        self.waveform_button = tk.Button(self.analysis_frame, text="Show Waveform", command=self.show_waveform, state=tk.DISABLED)
        self.waveform_button.pack(pady=10)

        self.spectrogram_button = tk.Button(self.analysis_frame, text="Show Spectrogram", command=self.show_spectrogram, state=tk.DISABLED)
        self.spectrogram_button.pack(pady=10)

    def start_recording(self):
        self.recording = True
        self.audio_data = []  # Clear previous data
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_audio_button.config(state=tk.DISABLED)
        self.waveform_button.config(state=tk.DISABLED)
        self.spectrogram_button.config(state=tk.DISABLED)
        self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=self.fs)
        self.stream.start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.stream.stop()
            self.stream.close()
            self.audio_data = np.concatenate(self.audio_data, axis=0).flatten()
            self.audio_data = self.audio_data / np.max(np.abs(self.audio_data))  # Normalize
            self.record_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.save_audio_button.config(state=tk.NORMAL)
            self.waveform_button.config(state=tk.NORMAL)
            self.spectrogram_button.config(state=tk.NORMAL)

    def save_audio(self):
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.fs)
                wf.writeframes((self.audio_data * 32767).astype(np.int16).tobytes())

    def show_waveform(self):
        self.create_plot_window("Waveform")
        time = np.linspace(0, len(self.audio_data) / self.fs, len(self.audio_data))
        self.ax.plot(time, self.audio_data, label="Waveform")
        self.ax.set_title("Waveform")
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Amplitude")
        self.ax.legend(loc="upper right")  # ثابت کردن مکان لگند
        self.canvas.draw()
        self.add_navigation_controls()

    def show_spectrogram(self):
        self.create_plot_window("Spectrogram")
        Pxx, freqs, bins, im = self.ax.specgram(
            self.audio_data,
            Fs=self.fs,
            NFFT=2048,
            noverlap=1536,
            cmap="viridis"
        )
        Pxx = np.maximum(Pxx, 1e-10)  # جلوگیری از تقسیم بر صفر
        self.ax.set_title("Spectrogram")
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Frequency [Hz]")
        cbar = self.fig.colorbar(im, ax=self.ax)
        cbar.set_label("Intensity [dB]")
        self.canvas.draw()
        self.add_navigation_controls()

    def create_plot_window(self, title):
        self.plot_window = tk.Toplevel(self.root)
        self.plot_window.title(title)

        # Create figure and canvas
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_window)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def add_navigation_controls(self):
        # Add navigation buttons
        move_left_btn = tk.Button(self.plot_window, text="Move Left", command=self.move_left)
        move_left_btn.pack(side=tk.LEFT, padx=5)
        move_right_btn = tk.Button(self.plot_window, text="Move Right", command=self.move_right)
        move_right_btn.pack(side=tk.LEFT, padx=5)
        zoom_in_btn = tk.Button(self.plot_window, text="Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=5)
        zoom_out_btn = tk.Button(self.plot_window, text="Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=5)
        reset_zoom_btn = tk.Button(self.plot_window, text="Reset Zoom", command=self.reset_zoom)
        reset_zoom_btn.pack(side=tk.LEFT, padx=5)

        # Initialize xlim
        self.current_xlim = self.ax.get_xlim()

    def move_left(self):
        start, end = self.ax.get_xlim()
        shift = (end - start) / 4  # مقدار جابه‌جایی
        self.ax.set_xlim(start - shift, end - shift)
        self.current_xlim = self.ax.get_xlim()
        self.canvas.draw()

    def move_right(self):
        start, end = self.ax.get_xlim()
        shift = (end - start) / 4  # مقدار جابه‌جایی
        self.ax.set_xlim(start + shift, end + shift)
        self.current_xlim = self.ax.get_xlim()
        self.canvas.draw()

    def zoom_in(self):
        start, end = self.ax.get_xlim()
        center = (start + end) / 2
        range_ = (end - start) / 4
        self.ax.set_xlim(center - range_, center + range_)
        self.current_xlim = self.ax.get_xlim()
        self.canvas.draw()

    def zoom_out(self):
        start, end = self.ax.get_xlim()
        range_ = (end - start)
        self.ax.set_xlim(start - range_ / 2, end + range_ / 2)
        self.current_xlim = self.ax.get_xlim()
        self.canvas.draw()

    def reset_zoom(self):
        self.ax.autoscale()
        self.current_xlim = self.ax.get_xlim()
        self.canvas.draw()

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.audio_data.append(indata.copy())

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
