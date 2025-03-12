import os
import sys
import queue
import sounddevice as sd
import vosk
import json
import threading
from word2number import w2n

def callback(indata, frames, time, status):
    """Callback function to process audio input."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# Initialize Vosk model (ensure the model is downloaded and available)
MODEL_PATH = "C:\\Users\\tmkir\\OneDrive\\Documents\\Year 3\\Group Design and Business Project\\Voice Recognition\\vosk-model-small-en-us-0.15"

if not os.path.exists(MODEL_PATH):
    print("Please download a Vosk model and place it in the 'model' directory.")
    sys.exit(1)

model = vosk.Model(MODEL_PATH)
q = queue.Queue()
stop_event = threading.Event()
command_queue = queue.Queue()  # Shared queue for commands

def convert_numbers_in_text(text):
    """Converts spoken number words (e.g., 'ninety') into digits (e.g., '90')."""
    words = text.split()
    converted_words = []
    
    for word in words:
        try:
            # Convert word to number if possible
            converted_words.append(str(w2n.word_to_num(word)))
        except ValueError:
            converted_words.append(word)  # Keep original if not a number
    
    return " ".join(converted_words)

def recognize_speech():
    """Function to recognize and process speech commands."""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        print("Listening for commands...")
        
        while not stop_event.is_set():
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                command = result.get("text", "").strip()
                
                if command:
                    command = convert_numbers_in_text(command)  # Convert words to numbers
                    print(f"Recognized: {command}")
                    command_queue.put(command)  # Store command for main.py

def start_voice_recognition():
    """Start voice recognition in a separate thread."""
    voice_thread = threading.Thread(target=recognize_speech, daemon=True)
    voice_thread.start()
    return voice_thread

def get_command():
    """Retrieve the latest command from the queue (non-blocking)."""
    try:
        return command_queue.get_nowait()  # Get latest command if available
    except queue.Empty:
        return None

def stop_voice_recognition():
    """Stop the voice recognition thread."""
    stop_event.set()
