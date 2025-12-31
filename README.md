

# AudioSync

AudioSync is a professional desktop tool written in Python that automatically synchronizes two audio or video files. It uses advanced signal processing (Cross-Correlation) to mathematically find the exact time offset between a reference file and a target file, even if they have significant delays.

Designed for editors, dubbing artists, and archivists who need to align high-quality audio recordings with camera video or synchronize dual-system sound.

## 🚀 Features

* **Smart Sync Engine:** Uses FFT-based Cross-Correlation to find time lags with high precision (down to milliseconds).
* **Visual Verification:** Plots aligned waveforms using Matplotlib to visually confirm synchronization.
* **Stereo Verification Player:** intelligently mixes audio (Left Ear = Reference, Right Ear = Target) allowing users to hear the sync accuracy in real-time.
* **Export Capability:** Saves the synchronized result as a stereo WAV file for use in Premiere Pro, DaVinci Resolve, or other DAWs.
* **Multi-Threaded GUI:** Built with Tkinter and threading to ensure the interface remains responsive during heavy processing.
* **Format Support:** Supports almost any media format (MP4, MKV, AVI, MP3, WAV) via FFmpeg.

## 🛠️ Project Structure

The project follows a flat modular structure for simplicity and efficiency:

* `main_app.py`: The entry point. Handles the GUI (Tkinter) and threading.
* `audio_engine.py`: The core logic. Handles FFmpeg conversion, signal processing, and offset calculation.
* `audio_player.py`: Handles real-time audio mixing and playback using `sounddevice`.
* `gui_plots.py`: Manages the embedding of Matplotlib charts into the GUI.
* `requirements.txt`: List of dependencies.

## 📋 Prerequisites

1. **Python 3.8+** installed.
2. **FFmpeg** installed and added to your system's PATH.

   * *Windows:* Download from [ffmpeg.org](https://ffmpeg.org/), extract, and add the `bin` folder to Environment Variables.
   * *Mac/Linux:* `brew install ffmpeg` or `sudo apt install ffmpeg`.

## 📦 Installation

1. Clone this repository or download the source code.
2. Install the required Python libraries:

```bash
pip install -r requirements.txt
▶️ Usage

Run the application:

code
Bash
download
content_copy
expand_less
python main_app.py

Select Files:

Click Select File 1 (Reference) to load your master video/audio.

Click Select File 2 (To Sync) to load the file that needs adjustment.

Analyze:

Click Start Smart Analysis. The tool will convert audio in the background and calculate the offset.

Verify & Export:

Check the Visual Plot: Ideally, the peaks of both waveforms should align.

Click Play Synced Audio: Listen to check if the echo is gone (files are perfectly synced).

Click Save Output: Export the synced stereo WAV file.

⚙️ How It Works

Extraction: Extracts mono audio from inputs at 16kHz using FFmpeg.

Processing: Normalizes audio arrays and computes the Cross-Correlation of the two signals.

Peak Finding: Identifies the time lag (lag index) where the correlation signal is strongest.

Alignment: Shifts the second signal by the calculated offset (adding silence padding if necessary) during playback or export.

📄 License

This project is open-source and available for educational and personal use.

```
