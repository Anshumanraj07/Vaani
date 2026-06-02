import os
import subprocess

print(f"🔍 Main yahan dhoondh raha hoon: {os.getcwd()}")

# 1. Check Audio File
if os.path.exists("test_voice.mp3"):
    print("✅ Audio file ekdum sahi jagah par hai!")
else:
    print("❌ ERROR: Audio file nahi mili! Ya toh naam galat hai ya file kisi aur folder mein hai.")

# 2. Check FFmpeg
try:
    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("✅ FFmpeg bhi system ko mil gaya!")
except FileNotFoundError:
    print("❌ ERROR: FFmpeg system ko nahi mil raha (PATH issue).")