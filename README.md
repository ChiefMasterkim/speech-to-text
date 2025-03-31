# Voice to Text Converter

A Streamlit application that converts voice to text using the Groq API. You can either record audio directly or upload audio/video files for transcription.

## Features

- Record audio directly from your microphone
- Upload audio files (MP3, WAV)
- Upload video files (MP4, AVI, MOV)
- Real-time transcription
- Simple and intuitive user interface

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Recording Audio**:
   - Click "Start Recording" to begin recording
   - Speak into your microphone
   - Click "Stop Recording" when done
   - Click "Transcribe Recording" to convert to text

2. **Uploading Files**:
   - Use the file uploader to select an audio or video file
   - Click "Transcribe Uploaded File" to convert to text

## Requirements

- Python 3.7+
- Microphone (for recording)
- Internet connection (for Groq API)

## Note

Make sure you have a working microphone connected to your computer for the recording feature to work. 