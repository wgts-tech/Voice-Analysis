import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import sounddevice as sd
import numpy as np
import wave
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class AudioRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Recorder and Analyzer")

        # Variables
        self.fs = 44100  # Sampling frequency
        self.recording = False
        self.paused = False
        self.audio_data = np.array([])  # Initialize as an empty array
        self.start_time = None
        self.elapsed_time = 0

        # Add Logo
        logo_frame = tk.Frame(root, pady=10)
        logo_frame.pack(side=tk.TOP, fill=tk.BOTH)

        logo_image = Image.open("WGTS_Logo.png")  # Path to your logo file
        logo_image = logo_image.resize((100, 100))  # Resize if needed
        self.logo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(logo_frame, image=self.logo)
        logo_label.pack()

        # Create Frames
        self.record_frame = tk.Frame(root, padx=10, pady=10, relief=tk.GROOVE, borderwidth=2)
        self.record_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.analysis_frame = tk.Frame(root, padx=10, pady=10, relief=tk.GROOVE, borderwidth=2)
        self.analysis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Recording Panel
        tk.Label(self.record_frame, text="Recording Panel", font=("Arial", 14)).pack(pady=5)
        self.record_button = tk.Button(self.record_frame, text="Start Recording", command=self.start_recording)
        self.record_button.pack(pady=10)

        self.pause_button = tk.Button(self.record_frame, text="Pause", command=self.pause_recording, state=tk.DISABLED)
        self.pause_button.pack(pady=10)

        self.stop_button = tk.Button(self.record_frame, text="Stop", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.timer_label = tk.Label(self.record_frame, text="Elapsed Time: 00:00", font=("Arial", 12))
        self.timer_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.record_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(pady=10)

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
        self.paused = False
        self.audio_data = np.array([])  # Clear previous data
        self.start_time = time.time() - self.elapsed_time
        self.update_timer()
        self.update_progress_bar()
        self.record_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.save_audio_button.config(state=tk.DISABLED)
        self.waveform_button.config(state=tk.DISABLED)
        self.spectrogram_button.config(state=tk.DISABLED)
        self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=self.fs)
        self.stream.start()

    def pause_recording(self):
        if self.recording and not self.paused:
            self.paused = True
            self.stream.stop()
            self.pause_button.config(text="Resume")
        elif self.recording and self.paused:
            self.paused = False
            self.start_time = time.time() - self.elapsed_time
            self.stream.start()
            self.pause_button.config(text="Pause")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.stream.stop()
            self.stream.close()
            self.elapsed_time = 0
            self.record_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED, text="Pause")
            self.stop_button.config(state=tk.DISABLED)
            self.save_audio_button.config(state=tk.NORMAL)
            self.waveform_button.config(state=tk.NORMAL)
            self.spectrogram_button.config(state=tk.NORMAL)

    def save_audio(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
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
        self.ax.legend(loc="upper right")
        self.canvas.draw()

    def show_spectrogram(self):
        self.create_plot_window("Spectrogram")
        Pxx, freqs, bins, im = self.ax.specgram(self.audio_data, Fs=self.fs, NFFT=2048, noverlap=1024, cmap='viridis')
        self.ax.set_title("Spectrogram")
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Frequency [Hz]")
        cbar = self.fig.colorbar(im, ax=self.ax)
        cbar.set_label("Intensity [dB]")
        self.canvas.draw()

    def create_plot_window(self, title):
        self.plot_window = tk.Toplevel(self.root)
        self.plot_window.title(title)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_window)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()

    def audio_callback(self, indata, frames, time, status):
        if self.recording and not self.paused:
            if self.audio_data.size == 0:
                self.audio_data = indata[:, 0]
            else:
                self.audio_data = np.concatenate((self.audio_data, indata[:, 0]))
            volume = np.linalg.norm(indata)  # محاسبه شدت صوت
            self.progress_bar["value"] = min(volume * 100, 100)  # تنظیم مقدار نوار پیشرفت

    def update_timer(self):
        if self.recording and not self.paused:
            self.elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(self.elapsed_time), 60)
            self.timer_label.config(text=f"Elapsed Time: {minutes:02}:{seconds:02}")
        if self.recording:
            self.root.after(500, self.update_timer)

    def update_progress_bar(self):
        if self.recording:
            self.root.after(100, self.update_progress_bar)  # به‌روزرسانی مداوم نوار پیشرفت


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
