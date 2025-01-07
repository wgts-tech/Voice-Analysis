import torch
import whisper

# بررسی اینکه GPU در دسترس است
if torch.cuda.is_available():
    print("CUDA is available. Using GPU.")
else:
    print("CUDA is not available. Using CPU.")

# بارگذاری مدل Whisper
#model = whisper.load_model("medium").to("cuda") # مدل‌های دیگر: "tiny", "small", "medium", "large"
model = whisper.load_model("medium", device="cuda" if torch.cuda.is_available() else "cpu")

# پردازش فایل صوتی
result = model.transcribe("temp_audio.wav", word_timestamps=True)

# نمایش کلمات همراه با بازه‌های زمانی
for segment in result["segments"]:
    print(f"Segment: {segment['text']}")
    for word in segment["words"]:
        print(f"  Word: {word['word']}, Start: {word['start']}s, End: {word['end']}s")