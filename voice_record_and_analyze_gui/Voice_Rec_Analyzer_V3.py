import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import sounddevice as sd
import numpy as np
import wave
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import whisper


class AudioRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Recorder and Analyzer")

        # Variables
        self.fs = 16000  # Sampling frequency
        self.recording = False
        self.paused = False
        self.audio_data = np.array([])  # Initialize as an empty array
        self.start_time = None
        self.elapsed_time = 0
        self.word_timestamps = []  # Store word timestamps

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

        # Main Frames with Borders
        self.left_main_frame = tk.Frame(root, padx=10, pady=10, relief=tk.GROOVE, borderwidth=2)
        self.left_main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_main_frame = tk.Frame(root, padx=10, pady=10, relief=tk.GROOVE, borderwidth=2)
        self.right_main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left Frame: All Left Panels (Recording, Transcript, Processing)
        self.record_frame = tk.Frame(self.left_main_frame, padx=10, pady=10, relief=tk.GROOVE, borderwidth=2)
        self.record_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(self.record_frame, text="Recording Panel", font=("Arial", 14)).pack(pady=5)
        self.record_button = tk.Button(self.record_frame, text="Start Recording", command=self.start_recording, font=("Arial", 12), width=20, height=1)
        self.record_button.pack(pady=10)

        self.pause_button = tk.Button(self.record_frame, text="Pause", command=self.pause_recording, state=tk.DISABLED, font=("Arial", 12), width=20, height=1)
        self.pause_button.pack(pady=10)

        self.stop_button = tk.Button(self.record_frame, text="Stop", command=self.stop_recording, state=tk.DISABLED, font=("Arial", 12), width=20, height=1)
        self.stop_button.pack(pady=10)

        self.timer_label = tk.Label(self.record_frame, text="Elapsed Time: 00:00", font=("Arial", 12))
        self.timer_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.record_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.save_audio_button = tk.Button(self.record_frame, text="Save Audio", command=self.save_audio, state=tk.DISABLED, font=("Arial", 12), width=20, height=1)
        self.save_audio_button.pack(pady=10)

        # Transcript Panel
        self.transcript_frame = tk.Frame(self.left_main_frame, relief=tk.GROOVE, borderwidth=2)
        self.transcript_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(self.transcript_frame, text="Transcript", font=("Arial", 12)).pack(pady=5)

        self.transcript_text = tk.Text(self.transcript_frame, wrap=tk.WORD, height=5, font=("Arial", 14))
        self.transcript_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        transcript_scrollbar = ttk.Scrollbar(self.transcript_frame, command=self.transcript_text.yview)
        transcript_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transcript_text.config(yscrollcommand=transcript_scrollbar.set)

        # Text Processing Panel
        self.text_processing_frame = tk.Frame(self.left_main_frame, relief=tk.GROOVE, borderwidth=2, padx=5, pady=5)
        self.text_processing_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(self.text_processing_frame, text="Text Processing", font=("Arial", 12)).pack(pady=5)

        self.word_listbox = tk.Listbox(self.text_processing_frame, height=10, font=("Arial", 14))
        self.word_listbox.pack(fill=tk.BOTH, expand=True)
        self.word_listbox.bind("<<ListboxSelect>>", self.on_word_select)

        self.word_count_label = tk.Label(self.text_processing_frame, text="Word Count: 0", font=("Arial", 10))
        self.word_count_label.pack(pady=5)

        # Right Frame: All Analysis Panels (Waveform, Spectrogram)
        tk.Label(self.right_main_frame, text="Analysis Panel", font=("Arial", 14)).pack(pady=5)

        self.waveform_panel = tk.Frame(self.right_main_frame, relief=tk.GROOVE, borderwidth=2)
        self.waveform_panel.pack(fill=tk.BOTH, expand=True, pady=10)

        self.spectrogram_panel = tk.Frame(self.right_main_frame, relief=tk.GROOVE, borderwidth=2)
        self.spectrogram_panel.pack(fill=tk.BOTH, expand=True, pady=10)

        # Initialize Plot Panels
        self.reset_waveform_panel()
        self.reset_spectrogram_panel()

    def reset_waveform_panel(self):        
        for widget in self.waveform_panel.winfo_children():
            widget.destroy()

        self.waveform_fig, self.waveform_ax = plt.subplots(figsize=(5, 2.5))
        self.waveform_canvas_agg = FigureCanvasTkAgg(self.waveform_fig, master=self.waveform_panel)
        self.waveform_canvas_agg.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.waveform_canvas_agg, self.waveform_panel)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def reset_spectrogram_panel(self):       
        for widget in self.spectrogram_panel.winfo_children():
            widget.destroy()

        self.spectrogram_fig, self.spectrogram_ax = plt.subplots(figsize=(5, 2.5))
        self.spectrogram_canvas_agg = FigureCanvasTkAgg(self.spectrogram_fig, master=self.spectrogram_panel)
        self.spectrogram_canvas_agg.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.spectrogram_canvas_agg, self.spectrogram_panel)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

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

    def on_word_select(self, event):        
        selection = self.word_listbox.curselection()
        if selection:
            index = selection[0]
            word_info = self.word_timestamps[index]
            start, end = word_info["start"], word_info["end"]

            self.highlight_waveform(start, end)
            self.highlight_spectrogram(start, end)
            self.play_segment(start, end)

    def highlight_waveform(self, start, end):        
        self.waveform_ax.clear()
        time = np.linspace(0, len(self.audio_data) / self.fs, len(self.audio_data))
        self.waveform_ax.plot(time, self.audio_data, label="Waveform")
        self.waveform_ax.axvspan(start, end, color="red", alpha=0.3, label="Selected Word")
        self.waveform_ax.legend()
        self.waveform_canvas_agg.draw()

    def highlight_spectrogram(self, start, end):        
        self.spectrogram_ax.clear()
        Pxx, freqs, bins, im = self.spectrogram_ax.specgram(
            self.audio_data, Fs=self.fs, NFFT=2048, noverlap=1024, cmap='viridis'
        )
        self.spectrogram_ax.axvspan(start, end, color="red", alpha=0.3, label="Selected Word")
        self.spectrogram_ax.legend()
        self.spectrogram_canvas_agg.draw()

    def play_segment(self, start, end):        
        start_idx = int(start * self.fs)
        end_idx = int(end * self.fs)
        segment = self.audio_data[start_idx:end_idx]
        sd.play(segment, self.fs)

    def save_audio(self):        
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.fs)
                wf.writeframes((self.audio_data * 32767).astype(np.int16).tobytes())

    def generate_transcript(self):        
        try:            
            temp_file = "temp_audio.wav"
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.fs)
                wf.writeframes((self.audio_data * 32767).astype(np.int16).tobytes())
            
            model = whisper.load_model("medium")
            result = model.transcribe(temp_file, word_timestamps=True)
            
            transcript = result["text"]
            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.insert(tk.END, transcript)
            
            self.word_listbox.delete(0, tk.END)
            self.word_timestamps = []
            for segment in result["segments"]:
                for word in segment["words"]:
                    self.word_timestamps.append(word)
                    self.word_listbox.insert(tk.END, word["word"])
            
            self.word_count_label.config(text=f"Word Count: {len(self.word_timestamps)}")

        except Exception as e:
            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.insert(tk.END, f"Error: {e}")
            self.word_count_label.config(text="Word Count: 0")

    def start_recording(self):        
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
            
            self.show_waveform()
            self.show_spectrogram()
            self.generate_transcript()

    def audio_callback(self, indata, frames, time, status):        
        if self.recording and not self.paused:
            if self.audio_data.size == 0:
                self.audio_data = indata[:, 0]
            else:
                self.audio_data = np.concatenate((self.audio_data, indata[:, 0]))
            volume = np.linalg.norm(indata)  
            self.progress_bar["value"] = min(volume * 100, 100)

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

    def on_closing(self):        
        if self.recording:
            self.stream.stop()
            self.stream.close()
        plt.close("all")
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
