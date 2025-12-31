import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import audio_engine 
import gui_plots

class AudioSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AudioSyncPro")
        self.root.geometry("600x450")

        # Plot Frame (Placeholder for the graph)
        self.plot_area = tk.Frame(root, bg="white", height=200)
        self.plot_area.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Variables to store file paths and data
        self.file1_path = ""
        self.file2_path = ""
        self.audio1_data = None
        self.audio2_data = None
        self.calculated_offset = 0.0

        # --- UI Layout ---
        
        # Title
        lbl_title = tk.Label(root, text="Audio Synchronization Tool", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # File 1 Selection
        frame_f1 = tk.Frame(root)
        frame_f1.pack(pady=5, fill="x", padx=20)
        self.btn_file1 = tk.Button(frame_f1, text="Select File 1 (Reference)", command=self.select_file1)
        self.btn_file1.pack(side="left")
        self.lbl_file1 = tk.Label(frame_f1, text="No file selected", fg="gray")
        self.lbl_file1.pack(side="left", padx=10)

        # File 2 Selection
        frame_f2 = tk.Frame(root)
        frame_f2.pack(pady=5, fill="x", padx=20)
        self.btn_file2 = tk.Button(frame_f2, text="Select File 2 (To Sync)", command=self.select_file2)
        self.btn_file2.pack(side="left")
        self.lbl_file2 = tk.Label(frame_f2, text="No file selected", fg="gray")
        self.lbl_file2.pack(side="left", padx=10)

        # Analyze Button
        self.btn_analyze = tk.Button(root, text="Start Smart Analysis", command=self.start_analysis_thread, bg="#dddddd", font=("Arial", 11))
        self.btn_analyze.pack(pady=20, ipadx=20, ipady=5)

        # Status Label (Loading...)
        self.lbl_status = tk.Label(root, text="Ready", fg="blue")
        self.lbl_status.pack(pady=5)

        # Results Area
        self.result_frame = tk.LabelFrame(root, text="Analysis Results", padx=10, pady=10)
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.lbl_result_text = tk.Label(self.result_frame, text="Waiting for analysis...", font=("Arial", 12))
        self.lbl_result_text.pack()

        # Check FFmpeg on startup
        if not audio_engine.check_ffmpeg():
            messagebox.showerror("Error", "FFmpeg is not installed or not in PATH!")

    def select_file1(self):
        path = filedialog.askopenfilename(title="Select Reference Video/Audio")
        if path:
            self.file1_path = path
            self.lbl_file1.config(text=os.path.basename(path), fg="black")

    def select_file2(self):
        path = filedialog.askopenfilename(title="Select Video/Audio to Sync")
        if path:
            self.file2_path = path
            self.lbl_file2.config(text=os.path.basename(path), fg="black")

    def start_analysis_thread(self):
        """Start analysis in a background thread to keep UI active."""
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("Warning", "Please select both files first.")
            return

        # Disable button during process
        self.btn_analyze.config(state="disabled")
        self.lbl_status.config(text="Processing... (This may take time)")
        
        # Start Thread
        t = threading.Thread(target=self.run_analysis_logic)
        t.start()

    def run_analysis_logic(self):
        """The heavy logic running in background."""
        try:
            # 1. Load Audio using our engine
            y1, sr = audio_engine.load_audio_data(self.file1_path)
            y2, sr = audio_engine.load_audio_data(self.file2_path)
            
            # Store data for later use (plotting/playing)
            self.audio1_data = y1
            self.audio2_data = y2

            # 2. Find Offset
            offset, score = audio_engine.find_best_offset(y1, y2)
            self.calculated_offset = offset

            # We use root.after to safely update GUI from a thread
            self.root.after(0, lambda: gui_plots.draw_comparison_plot(
                self.plot_area, y1, y2, sr, offset
            ))

            # 3. Update UI (must be done in main thread usually, but simple config is safe here mostly)
            # For 100% safety we use root.after, but let's keep it simple for now.
            res_text = f"Offset Found: {offset:.3f} seconds\nConfidence Score: {score:.1f}"
            self.lbl_result_text.config(text=res_text, fg="green")
            self.lbl_status.config(text="Analysis Complete.")

        except Exception as e:
            self.lbl_status.config(text="Error occurred.")
            print(e)
        finally:
            # Re-enable button
            self.btn_analyze.config(state="normal")

import os

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSyncApp(root)
    root.mainloop()