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

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Add Logo
        logo_frame = tk.Frame(root, pady=10)
        logo_frame.pack(side=tk.TOP, fill=tk.BOTH)

        logo_image = Image.open("WGTS_Logo.png")  # Path to your logo file
        logo_image = logo_image.resize((100, 100))  # Resize
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

        # Create Placeholder Panels
        self.waveform_panel = tk.Frame(self.analysis_frame, relief=tk.GROOVE, borderwidth=2)
        self.waveform_panel.pack(fill=tk.BOTH, expand=True, pady=10)

        self.spectrogram_panel = tk.Frame(self.analysis_frame, relief=tk.GROOVE, borderwidth=2)
        self.spectrogram_panel.pack(fill=tk.BOTH, expand=True, pady=10)

    def on_closing(self):
        """Handle window close."""
        if self.recording:
            self.stream.stop()
            self.stream.close()

        plt.close("all")  # Close all matplotlib figures
        self.root.quit()  # Stop the Tkinter main loop
        self.root.destroy()  # Destroy all Tkinter widgets

    def start_recording(self):
        # پاکسازی و بازسازی پنل نمودارها قبل از شروع ضبط جدید
        self.reset_waveform_panel()
        self.reset_spectrogram_panel()

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
        self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=self.fs)
        self.stream.start()

    def reset_waveform_panel(self):
        """بازسازی کامل پنل ویو فرم."""
        for widget in self.waveform_panel.winfo_children():
            widget.destroy()  # حذف کامل ویجت‌های موجود

        self.waveform_fig, self.waveform_ax = plt.subplots(figsize=(5, 2))  # ایجاد شکل جدید با ارتفاع کمتر
        self.waveform_canvas_agg = FigureCanvasTkAgg(self.waveform_fig, master=self.waveform_panel)
        self.waveform_canvas_agg.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add interactive toolbar
        toolbar = NavigationToolbar2Tk(self.waveform_canvas_agg, self.waveform_panel)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def reset_spectrogram_panel(self):
        """بازسازی کامل پنل اسپکتروم."""
        for widget in self.spectrogram_panel.winfo_children():
            widget.destroy()  # حذف کامل ویجت‌های موجود

        self.spectrogram_fig, self.spectrogram_ax = plt.subplots(figsize=(5, 2))  # ایجاد شکل جدید با ارتفاع کمتر
        self.spectrogram_canvas_agg = FigureCanvasTkAgg(self.spectrogram_fig, master=self.spectrogram_panel)
        self.spectrogram_canvas_agg.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add interactive toolbar
        toolbar = NavigationToolbar2Tk(self.spectrogram_canvas_agg, self.spectrogram_panel)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

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

            # رسم خودکار نمودارها پس از توقف ضبط
            self.show_waveform()
            self.show_spectrogram()

    def save_audio(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.fs)
                wf.writeframes((self.audio_data * 32767).astype(np.int16).tobytes())

    def show_waveform(self):
        self.waveform_ax.clear()
        time = np.linspace(0, len(self.audio_data) / self.fs, len(self.audio_data))
        self.waveform_ax.plot(time, self.audio_data, label="Waveform")
        self.waveform_ax.set_title("Waveform")
        self.waveform_ax.set_xlabel("Time [s]")
        self.waveform_ax.set_ylabel("Amplitude")
        self.waveform_ax.legend(loc="upper right")
        self.waveform_canvas_agg.draw()

    def show_spectrogram(self):
        self.spectrogram_ax.clear()
        Pxx, freqs, bins, im = self.spectrogram_ax.specgram(
            self.audio_data, Fs=self.fs, NFFT=2048, noverlap=1024, cmap='viridis'
        )
        self.spectrogram_ax.set_title("Spectrogram")
        self.spectrogram_ax.set_xlabel("Time [s]")
        self.spectrogram_ax.set_ylabel("Frequency [Hz]")
        self.spectrogram_fig.colorbar(im, ax=self.spectrogram_ax).set_label("Intensity [dB]")
        self.spectrogram_canvas_agg.draw()

    def audio_callback(self, indata, frames, time, status):
        if self.recording and not self.paused:
            if self.audio_data.size == 0:
                self.audio_data = indata[:, 0]
            else:
                self.audio_data = np.concatenate((self.audio_data, indata[:, 0]))
            volume = np.linalg.norm(indata)  # Calculate volume
            self.progress_bar["value"] = min(volume * 100, 100)

    def update_timer(self):
        if self.recording and not self.paused:
            self.elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(self.elapsed_time), 60)
            self.timer_label.config(text=f"Elapsed Time: {minutes:02}:{seconds:02}")
        if self.recording:
            self.root.after(500, self.update_timer)

    def update_progress_bar(self):
        if self.recording:
            self.root.after(100, self.update_progress_bar)


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
