import librosa
import numpy as np

# Load audio file
audio_path = "data/interview_audio.wav"
y, sr = librosa.load(audio_path, sr=None)

# Duration
duration = librosa.get_duration(y=y, sr=sr)

# Speech rate (words per second)
with open("data/transcript.txt", "r") as f:
    words = f.read().split()

speech_rate = len(words) / duration

# Pitch (fundamental frequency)
pitch = librosa.yin(y, fmin=50, fmax=300)
pitch_mean = np.mean(pitch)

# Volume consistency
volume = np.abs(y)
volume_std = np.std(volume)

print("🎤 AUDIO FEATURE REPORT")
print("----------------------")
print(f"Audio Duration: {duration:.2f} seconds")
print(f"Speech Rate: {speech_rate:.2f} words/sec")
print(f"Average Pitch: {pitch_mean:.2f} Hz")
print(f"Volume Variation: {volume_std:.4f}")
