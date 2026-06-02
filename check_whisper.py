import os
import imageio_ffmpeg
os.environ["PATH"] += os.pathsep + os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())

import whisper
import warnings
warnings.filterwarnings("ignore")

print("1. Whisper import ho gaya, aur Jugaad FFmpeg set ho gaya!")
try:
    print("2. Model load ho raha hai...")
    model = whisper.load_model("base")
    print("3. Model load ho gaya! Ab aawaz sun raha hai...")
    
    result = model.transcribe("test_voice.mp3")
    print("\n✅ Asli Whisper ekdum chal raha hai! Result:")
    print(result["text"])
    
except Exception as e:
    print("\n❌ Error aa gaya:")
    print(e)