from flask import Flask, render_template, request, jsonify, Response
import pyaudio
import wave
import os
import requests
from datetime import datetime
import threading
import time
import json

app = Flask(__name__)

# Audio recording settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORDING_FILE = "audio.wav"

# Global variables
recording = False
audio_frames = []

# Groq API settings
API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

def record_audio():
    """Record audio from microphone"""
    global recording, audio_frames
    
    # Reset audio frames
    audio_frames = []
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # Open stream
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    print("Recording started...")
    
    # Record audio in chunks
    while recording:
        data = stream.read(CHUNK)
        audio_frames.append(data)
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    print("Recording stopped...")
    
    # Save recorded audio
    if audio_frames:
        try:
            wf = wave.open(RECORDING_FILE, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(audio_frames))
            wf.close()
            print(f"Audio saved to {RECORDING_FILE}, size: {os.path.getsize(RECORDING_FILE)} bytes")
            return True
        except Exception as e:
            print(f"Error saving audio: {str(e)}")
            return False
    else:
        print("No audio frames captured")
        return False

def transcribe_audio():
    """Transcribe audio using Groq API"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        
        with open(RECORDING_FILE, "rb") as f:
            files = {
                "file": (RECORDING_FILE, f, "audio/wav")
            }
            data = {
                "model": "distil-whisper-large-v3-en",
                "temperature": 0,
                "response_format": "verbose_json",
                "prompt": ""
            }
            
            print("Sending audio to Groq API...")
            response = requests.post(API_URL, headers=headers, files=files, data=data)
            
            print(f"Transcription response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                return {"text": result.get("text", "No transcription available")}
            else:
                return {"text": f"Error: {response.status_code} - {response.text}"}
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return {"text": f"Error: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording
    if not recording:
        recording = True
        threading.Thread(target=record_audio).start()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Already recording"})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording
    if recording:
        recording = False
        time.sleep(0.5)  # Wait for recording to finish
        
        # Check if the recording was successful
        if not os.path.exists(RECORDING_FILE) or os.path.getsize(RECORDING_FILE) == 0:
            print("Recording file does not exist or is empty")
            return jsonify({
                "status": "error",
                "message": "No audio data was recorded or saved"
            })
        
        # Transcribe audio
        transcription = transcribe_audio()
        
        # Include the current time
        current_time = datetime.now().strftime("%H:%M:%S")
        
        return jsonify({
            "status": "success",
            "transcription": transcription,
            "time": current_time
        })
    return jsonify({"status": "error", "message": "Not recording"})

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'})
    
    # Save uploaded file
    file_path = "uploaded_audio.wav"
    file.save(file_path)
    print(f"Uploaded file saved to {file_path}, size: {os.path.getsize(file_path)} bytes")
    
    try:
        # First save the original recording file if it exists
        original_recording = None
        if os.path.exists(RECORDING_FILE):
            with open(RECORDING_FILE, "rb") as f:
                original_recording = f.read()
        
        # Replace the recording file with the uploaded file
        os.rename(file_path, RECORDING_FILE)
        
        # Transcribe using the common function
        transcription = transcribe_audio()
        
        # Restore the original recording file if it existed
        if original_recording:
            with open(RECORDING_FILE, "wb") as f:
                f.write(original_recording)
        else:
            # Remove the recording file if there was no original
            os.remove(RECORDING_FILE)
        
        return jsonify({
            'status': 'success',
            'transcription': transcription,
            'time': datetime.now().strftime("%H:%M:%S")
        })
    except Exception as e:
        print(f"Error processing uploaded file: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'Error processing file: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True) 