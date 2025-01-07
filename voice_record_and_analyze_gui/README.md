![image_1](https://github.com/user-attachments/assets/14f8e3c4-81d4-4700-bea6-67dabe30866e)

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
