import os
import subprocess
import numpy as np
import librosa
from scipy import signal

# Settings
SAMPLE_RATE = 16000  # Good balance for speed and quality
Thinking_SR = 8000   # Lower quality for fast sync calculation

def check_ffmpeg():
    """
    Check if FFmpeg is installed on the system.
    Returns True if installed, False if not.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def convert_to_wav(input_path):
    """
    Convert video/audio to a temporary WAV file using FFmpeg.
    """
    # Create a temp filename
    base_name = os.path.basename(input_path)
    temp_name = f"temp_{base_name}.wav"
    
    # Command to convert to mono wav
    cmd = [
        "ffmpeg", "-y", 
        "-i", input_path,
        "-ac", "1",           # Mono channel
        "-ar", str(SAMPLE_RATE), 
        "-vn",                # No video
        temp_name
    ]
    
    # Run command and hide output
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return temp_name

def load_audio_data(path):
    """
    Load audio file into a numpy array.
    """
    # 1. Convert to wav first
    wav_path = convert_to_wav(path)
    
    # 2. Load with librosa
    try:
        y, sr = librosa.load(wav_path, sr=SAMPLE_RATE)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None, None
    finally:
        # 3. Delete temp file to keep folder clean
        if os.path.exists(wav_path):
            os.remove(wav_path)
            
    return y, sr

def find_best_offset(y1, y2):
    """
    Smart Function: Finds how much 'y2' is shifted compared to 'y1'.
    
    Returns:
        offset (float): Time difference in seconds.
        correlation (float): How good the match is (score).
    """
    # Safety check for empty files
    if y1 is None or y2 is None or len(y1) == 0 or len(y2) == 0:
        return 0, 0

    # Downsample for faster calculation (optional but recommended for long files)
    # We use slices to keep it simple for now, but in real usage we might resample.
    
    # Normalize volume (amplitudes)
    y1 = y1 / (np.max(np.abs(y1)) + 1e-9)
    y2 = y2 / (np.max(np.abs(y2)) + 1e-9)
    
    # Calculate Cross-Correlation (The heavy math part)
    # This checks every possible position of y2 sliding over y1
    corr = signal.correlate(y1, y2, mode='full', method='fft')
    
    # Find the position with the highest match score
    lag_index = np.argmax(np.abs(corr))
    
    # Convert index to time (seconds)
    # The center of correlation is at len(y1) - 1
    shift_samples = lag_index - (len(y2) - 1)
    offset_seconds = shift_samples / SAMPLE_RATE
    
    # Get the max score
    max_score = np.abs(corr[lag_index])
    
    return offset_seconds, max_score