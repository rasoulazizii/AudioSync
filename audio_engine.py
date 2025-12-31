import os
import subprocess
import numpy as np
import librosa
import soundfile as sf
from scipy import signal

# Settings
SAMPLE_RATE = 16000  # Standard rate for processing

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
    base_name = os.path.basename(input_path)
    temp_name = f"temp_{base_name}.wav"
    
    cmd = [
        "ffmpeg", "-y", 
        "-i", input_path,
        "-ac", "1",           # Mono channel
        "-ar", str(SAMPLE_RATE), 
        "-vn",                # No video
        temp_name
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return temp_name

def load_audio_data(path):
    """
    Load audio file into a numpy array.
    """
    wav_path = convert_to_wav(path)
    
    try:
        y, sr = librosa.load(wav_path, sr=SAMPLE_RATE)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None, None
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
            
    return y, sr

def find_best_offset(y1, y2):
    """
    Smart Function: Finds how much 'y2' is shifted compared to 'y1'.
    Returns: offset (seconds), score (correlation value)
    """
    if y1 is None or y2 is None or len(y1) == 0 or len(y2) == 0:
        return 0, 0

    # Normalize volume
    y1 = y1 / (np.max(np.abs(y1)) + 1e-9)
    y2 = y2 / (np.max(np.abs(y2)) + 1e-9)
    
    # Calculate Cross-Correlation
    corr = signal.correlate(y1, y2, mode='full', method='fft')
    lag_index = np.argmax(np.abs(corr))
    
    # Calculate time shift
    shift_samples = lag_index - (len(y2) - 1)
    offset_seconds = shift_samples / SAMPLE_RATE
    max_score = np.abs(corr[lag_index])
    
    return offset_seconds, max_score

def save_synced_audio(y1, y2, sr, offset, output_path):
    """
    Aligns audio based on offset and saves as Stereo WAV.
    Left: Reference, Right: Synced
    """
    shift_samples = int(offset * sr)
    
    # 1. Align/Pad Audio
    if shift_samples > 0:
        # y2 is late, pad y2 start
        padding = np.zeros(shift_samples)
        y2_aligned = np.concatenate((padding, y2))
        y1_aligned = y1
    else:
        # y1 is late, pad y1 start
        padding = np.zeros(abs(shift_samples))
        y1_aligned = np.concatenate((padding, y1))
        y2_aligned = y2
        
    # 2. Make lengths equal (pad end)
    max_len = max(len(y1_aligned), len(y2_aligned))
    y1_final = np.pad(y1_aligned, (0, max_len - len(y1_aligned)))
    y2_final = np.pad(y2_aligned, (0, max_len - len(y2_aligned)))
    
    # 3. Stack for Stereo
    stereo_mix = np.column_stack((y1_final, y2_final))
    
    # 4. Save
    sf.write(output_path, stereo_mix, sr)
    return True