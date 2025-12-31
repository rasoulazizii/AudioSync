import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import audio_engine 
import gui_plots
import audio_player

class AudioSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AudioSyncPro")
        self.root.geometry("700x700")

        # Variables
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
        self.btn_analyze.pack(pady=15, ipadx=20, ipady=5)

        # Status Label
        self.lbl_status = tk.Label(root, text="Ready", fg="blue")
        self.lbl_status.pack(pady=5)

        # Control Buttons Frame (Play / Stop / Save)
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        self.btn_play = tk.Button(btn_frame, text="▶ Play Synced", command=self.play_synced, bg="#c8e6c9", width=15)
        self.btn_play.pack(side="left", padx=5)
        
        self.btn_stop = tk.Button(btn_frame, text="⏹ Stop", command=self.stop_playback, bg="#ffcdd2", width=10)
        self.btn_stop.pack(side="left", padx=5)

        self.btn_save = tk.Button(btn_frame, text="💾 Save Output", command=self.save_output, bg="#fff9c4", width=15)
        self.btn_save.pack(side="left", padx=5)

        # Results Area
        self.result_frame = tk.LabelFrame(root, text="Analysis Results", padx=10, pady=10)
        self.result_frame.pack(fill="x", padx=20, pady=10)
        
        self.lbl_result_text = tk.Label(self.result_frame, text="Waiting for analysis...", font=("Arial", 12))
        self.lbl_result_text.pack()

        # Plot Frame (Bottom)
        self.plot_area = tk.Frame(root, bg="white", height=250)
        self.plot_area.pack(fill="both", expand=True, padx=20, pady=10)

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
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("Warning", "Please select both files first.")
            return

        self.btn_analyze.config(state="disabled")
        self.lbl_status.config(text="Processing... (This may take time)")
        
        t = threading.Thread(target=self.run_analysis_logic)
        t.start()

    def run_analysis_logic(self):
        try:
            # 1. Load Audio
            y1, sr = audio_engine.load_audio_data(self.file1_path)
            y2, sr = audio_engine.load_audio_data(self.file2_path)
            
            self.audio1_data = y1
            self.audio2_data = y2

            # 2. Find Offset
            offset, score = audio_engine.find_best_offset(y1, y2)
            self.calculated_offset = offset

            # 3. Update UI Safely
            self.root.after(0, lambda: self.update_ui_results(y1, y2, sr, offset, score))

        except Exception as e:
            print(e)
            self.root.after(0, lambda: self.lbl_status.config(text="Error occurred."))
        finally:
            self.root.after(0, lambda: self.btn_analyze.config(state="normal"))

    def update_ui_results(self, y1, y2, sr, offset, score):
        # Draw Plot
        gui_plots.draw_comparison_plot(self.plot_area, y1, y2, sr, offset)
        
        # Update Labels
        res_text = f"Offset Found: {offset:.3f} seconds\nConfidence Score: {score:.1f}"
        self.lbl_result_text.config(text=res_text, fg="green")
        self.lbl_status.config(text="Analysis Complete.")

    def play_synced(self):
        if self.audio1_data is None:
            messagebox.showwarning("Warning", "Please analyze files first.")
            return
        audio_player.mix_and_play(self.audio1_data, self.audio2_data, 16000, self.calculated_offset)

    def stop_playback(self):
        audio_player.stop_audio()

    def save_output(self):
        if self.audio1_data is None:
            messagebox.showwarning("Warning", "Nothing to save. Analyze first.")
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".wav", filetypes=[("WAV files", "*.wav")], title="Save Synced Audio"
        )
        if not save_path: return
            
        try:
            self.lbl_status.config(text="Saving file...")
            self.root.update()
            
            audio_engine.save_synced_audio(
                self.audio1_data, self.audio2_data, 16000, self.calculated_offset, save_path
            )
            
            messagebox.showinfo("Success", f"File saved!\n{save_path}")
            self.lbl_status.config(text="File Saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed:\n{e}")
            self.lbl_status.config(text="Save failed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSyncApp(root)
    root.mainloop()