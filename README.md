# Rebbit - Youtube Music Downloader and MP3 Player Desktop Widget

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/Rebbit-v1.0.0-orange)

Desktop widget music player and downloader that allows downloading music from youtube and offline organization, all within one sleek, frameless interface. Rebbit combines a powerful YouTube downloader with a robust local library manager.

---

## Screenshots

<img width="1919" height="1079" alt="Rebbit-Preview" src="https://github.com/user-attachments/assets/214cb2af-6a78-4318-9312-65fdb6a0d6ad" />

## Features

1. Dual Interface Modes:
   - Collapsed Widget: A compact, "Always on Top" mini-player that sits unobtrusively on your screen. Features Marquee scrolling for long song titles, album art display, and quick playback controls.
   - Expanded Manager: A comprehensive dashboard for managing your library, searching for new music, and organizing playlists. Accessible via context menu or sidebar.

2. Powerful Search & Downloader:
   - Smart Search Engine: Powered by `yt-dlp`, search for songs by name (top 5 results with thumbnails) or paste direct YouTube links.
   - Audio-Only Extraction: Automatically downloads and converts videos to high-quality MP3 format.
   - Playlist Support: Capable of detecting and downloading entire public YouTube playlists with a single click.
   - Download Queue: A dedicated tab to monitor active download progress, percentages, and status in real-time.

3. Offline Library & Metadata Management:
   - SQLite Database: Automatically indexes downloaded files into a local database for instant loading and sorting.
   - Metadata Editor: Right-click any song to open the built-in editor. Modify Song Titles, Artist Names, Album details, and even drag-and-drop new Cover Art.
   - Auto-Tagging: Downloads include embedded thumbnails and metadata from YouTube automatically.

4. Advanced Playback Controls:
   - Full Audio Engine: Built on QtMultimedia for reliable playback.
   - Shuffle & Repeat: Shuffle your library or toggle between Repeat All, Repeat One, and No Repeat modes.
   - Sync Logic: Playback state, progress sliders, and volume controls stay perfectly synchronized between the Widget and the Expanded view.
   - Global Controls: "Play All" and "Shuffle All" buttons for instant listening sessions.

5. Playlist Organization:
   - Custom Playlists: Create, rename, and delete custom playlists to organize your mood.
   - Context Menus: Easily add songs to playlists or remove them via right-click menus in the Library.
   - Visual Cards: Playlists are displayed as grid cards with song counts and visual indicators.

6. Customization & Polish:
   - Theming: Toggle between a sleek Dark Mode (Default), a crisp Light Mode and Transparent Mode instantly.
   - Responsive UI: Fixed-width sidebars and marquee labels ensure the layout remains solid regardless of song title length.
   - Settings & Updates: Dedicated section to view app version, developer info, and toggle application preferences.

## Requirements

Python 3.10+ with the following dependencies installed:
```
PySide6==6.9.1
yt-dlp==2025.10.22
mutagen==1.47.0
pillow==12.0.0
requests==2.32.4
```
**External Dependency:**
- **FFmpeg**: Required for audio conversion. `ffmpeg.exe` must be in the application folder or added to your System PATH.

## Setup and Usage

SETUP:  
1. Ensure you have Python installed on your system. (Recommended <a href="https://www.python.org/downloads/release/python-31010/">Python 3.10.XX</a>)
2. **Install FFmpeg**: Download a build of FFmpeg. Extract `ffmpeg.exe` and place it inside the root `Rebbit` folder (or ensure it is in your system PATH).
3. Download this Repository. Unzip it.
4. Install the required libraries via terminal ```pip install -r requirements.txt```
5. Run the program via terminal or run vbs ```rebbit.exe.vbs```
```
python -u main.py
Edit rebbit.exe.vbs in notepad and replace A:\Absolute\Path\to\Rebbit to actual path.
Then simply double-click rebbit.exe.vbs
```

All Set! The widget will appear on your desktop.

Usage Tips:

    Right-Click the small widget to access "Expand Widget", "Settings", or "Quit".

    Drag the widget background to move it anywhere on your screen.

    Click the Album Art in the player bar to jump to the currently playing song in the library.

<h1></h1>

*This README.md file has been improved for overall readability (grammar, sentence structure, and organization) using AI tools.
