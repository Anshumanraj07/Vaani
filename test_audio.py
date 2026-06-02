import os
import requests

# Dynamically get the absolute path to the same directory where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Look for the file in that exact directory (supports .mp3, .mpeg, .wav)
audio_filename = "test_voice.mp3"  # Update this if your file ends in .wav or .mpeg
audio_file_path = os.path.join(BASE_DIR, audio_filename)

url = "http://127.0.0.1:8000/api/v1/analyze-audio"

try:
    print(f"📤 Sending request to {url}...")
    with open(audio_file_path, "rb") as f:
        files = {"file": (audio_filename, f, "audio/mpeg")}
        response = requests.post(url, files=files, timeout=120)
        response.raise_for_status()
    print(f"📥 Response received!")
    print(response.json())
except FileNotFoundError:
    print(f"Error: File not found at '{audio_file_path}'")
except requests.exceptions.Timeout:
    print(f"Error: Request timed out. The server or API may be slow. Check if Uvicorn is running on {url}")
except requests.exceptions.ConnectionError:
    print(f"Error: Connection failed. Make sure Uvicorn is running on {url}")
except requests.exceptions.HTTPError as e:
    print(f"Error: HTTP {response.status_code} - {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error: Request failed - {str(e)}")
except Exception as e:
    print(f"Error: {type(e).__name__} - {str(e)}")
