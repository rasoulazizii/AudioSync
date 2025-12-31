import numpy as np
import sounddevice as sd

# Global variable to control playback
is_playing = False

def mix_and_play(y1, y2, sr, offset):
    """
     intelligently mixes two audio arrays based on the time offset.
     Returns the mixed array ready for playback.
    """
    global is_playing
    
    # 1. Calculate shift in samples (samples = seconds * sample_rate)
    shift_samples = int(offset * sr)
    
    # 2. Align audio by padding with zeros
    # If offset > 0: y2 needs to start later -> add zeros to start of y2
    # If offset < 0: y1 needs to start later -> add zeros to start of y1
    
    if shift_samples > 0:
        # y2 is late, pad y2
        padding = np.zeros(shift_samples)
        y2_aligned = np.concatenate((padding, y2))
        y1_aligned = y1
    else:
        # y1 is late (negative offset), pad y1
        padding = np.zeros(abs(shift_samples))
        y1_aligned = np.concatenate((padding, y1))
        y2_aligned = y2
        
    # 3. Make lengths equal for mixing
    # We find the max length and pad the shorter one at the end
    max_len = max(len(y1_aligned), len(y2_aligned))
    
    y1_final = np.pad(y1_aligned, (0, max_len - len(y1_aligned)))
    y2_final = np.pad(y2_aligned, (0, max_len - len(y2_aligned)))
    
    # 4. Create Stereo Mix (Left Ear = File 1, Right Ear = File 2)
    # This helps you hear distinct differences easily.
    # Stack them: shape becomes (samples, 2)
    stereo_mix = np.column_stack((y1_final, y2_final))
    
    # 5. Play
    stop_audio() # Stop any previous sound
    is_playing = True
    sd.play(stereo_mix, sr)
    return stereo_mix

def stop_audio():
    """Stops the current playback immediately."""
    global is_playing
    sd.stop()
    is_playing = False