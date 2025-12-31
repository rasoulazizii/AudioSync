import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def draw_comparison_plot(parent_frame, y1, y2, sr, offset_seconds):
    """
    Draws two waveforms. 
    'y2' is shifted by 'offset_seconds' to show visual alignment.
    """
    # 1. Clear previous drawings in the GUI frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 2. Performance: Downsample large files for faster plotting
    # We take 1 sample every 100 samples (enough for visual check)
    step = 100 
    y1_fast = y1[::step]
    y2_fast = y2[::step]
    
    # 3. Create Time Axis (X-axis)
    # np.linspace creates numbers from 0 to Duration
    duration1 = len(y1) / sr
    time1 = np.linspace(0, duration1, len(y1_fast))
    
    duration2 = len(y2) / sr
    # HERE IS THE MAGIC: We add 'offset_seconds' to time2
    time2 = np.linspace(0, duration2, len(y2_fast)) + offset_seconds

    # 4. Plotting
    fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
    
    # Plot File 1 (Blue)
    ax.plot(time1, y1_fast, label="File 1 (Reference)", color="#007acc", alpha=0.7)
    
    # Plot File 2 (Red) - It will move left/right based on offset
    ax.plot(time2, y2_fast, label="File 2 (Shifted)", color="#e63946", alpha=0.7)

    ax.set_title(f"Visual Sync Check (Shifted by {offset_seconds:.2f}s)")
    ax.set_xlabel("Time (seconds)")
    ax.set_yticks([]) # Hide Y numbers (not important)
    ax.legend(loc="upper right")
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 5. Embed into Tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)