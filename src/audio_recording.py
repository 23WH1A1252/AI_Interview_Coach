import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os

os.makedirs("data", exist_ok=True)

fs = 44100
seconds = 10

print("Recording started... Speak now")

audio = sd.rec(int(seconds * fs),
               samplerate=fs,
               channels=1,
               dtype='int16')   # 🔥 THIS FIXES THE PROBLEM

sd.wait()

write("data/interview_audio.wav", fs, audio)
print("Recording saved successfully in PCM WAV format")
