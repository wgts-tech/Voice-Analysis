import torch
import whisper

if torch.cuda.is_available():
    print("CUDA is available. Using GPU.")
else:
    print("CUDA is not available. Using CPU.")


#model = whisper.load_model("medium").to("cuda")
model = whisper.load_model("medium", device="cuda" if torch.cuda.is_available() else "cpu")

result = model.transcribe("temp_audio.wav", word_timestamps=True)

for segment in result["segments"]:
    print(f"Segment: {segment['text']}")
    for word in segment["words"]:
        print(f"  Word: {word['word']}, Start: {word['start']}s, End: {word['end']}s")
