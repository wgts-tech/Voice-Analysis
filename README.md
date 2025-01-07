# Audio Recorder and Analyzer 🎤📊

Demo Video for Voice Analysis:
https://github.com/user-attachments/assets/5de70d4f-1fdf-40bd-af31-eeac1751fd78

A powerful audio recording and analysis tool with transcription and visualization features. This program allows you to record audio, visualize its waveform and spectrogram, and transcribe the audio using OpenAI's Whisper model. Additionally, you can interact with the transcription to view and play specific word segments.

Phoneme and Word Time Calculation:
![analyze_image](https://github.com/user-attachments/assets/41bfd86c-5711-4629-a637-29c198a701ed)

## Features 🌟

- **Audio Recording:**
  - Start, pause, and stop recording.
  - Visualize live recording progress using a progress bar.

- **Waveform & Spectrogram Visualization:**
  - Automatically generate and display waveform and spectrogram after recording.
  - Highlight specific time segments based on transcription.

- **Transcription:**
  - Automatically transcribe recorded audio using the Whisper model.
  - Display transcription with timestamps for each word.

- **Word-Level Interaction:**
  - Select individual words from the transcription.
  - Highlight the corresponding audio segment in waveform and spectrogram.
  - Play the selected audio segment.

- **Save Audio:**
  - Save the recorded audio in WAV format.

## Installation 🛠️

1. Clone the repository:   
   git clone https://github.com/your-username/audio-recorder-analyzer.git
   cd audio-recorder-analyzer   

2. Install the required dependencies:   
   pip install -r requirements.txt   

3. Install `ffmpeg` for audio processing:
   - On Ubuntu/Debian:     
     sudo apt install ffmpeg   
   - On macOS (via Homebrew):     
     brew install ffmpeg   
   - On Windows, download [ffmpeg](https://ffmpeg.org/download.html) and add it to your system's PATH.

4. Run the application:   
   python app.py   

## Usage 🚀

1. Click **Start Recording** to begin recording.
2. Use **Pause** to temporarily stop recording and **Resume** to continue.
3. Stop recording by clicking **Stop**.
4. View the **Waveform** and **Spectrogram** in the visualization panels.
5. Review the **Transcription** in the transcript panel.
6. Select any word from the **Word List** to:
   - Highlight the corresponding segment in the waveform and spectrogram.
   - Play the selected audio segment.
7. Save the recorded audio using the **Save Audio** button.

## Dependencies 📦

The following Python libraries and tools are required:
- [`sounddevice`](https://python-sounddevice.readthedocs.io/) - For audio recording and playback.
- [`numpy`](https://numpy.org/) - For numerical computations.
- [`matplotlib`](https://matplotlib.org/) - For waveform and spectrogram visualization.
- [`whisper`](https://github.com/openai/whisper) - For transcription using OpenAI's model.
- [`Pillow`](https://python-pillow.org/) - For image processing in the GUI.
- [`tkinter`](https://docs.python.org/3/library/tkinter.html) - For building the graphical user interface.

## Known Issues 🐛
- **Performance**: The Whisper model may take longer to transcribe large audio files, especially on CPUs.
