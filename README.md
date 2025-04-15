# Random MP3 Player with Server Control

Python-based random MP3 player server that supports basic playback control (play/pause, next, previous) and sends desktop notifications about the current track. The server communicates using TCP commands, and it can be controlled using simple command-line utilities like `nc` (Netcat).

## Features

- Play random audio files from a specified folder.
- Pause, resume, skip to the next track, or return to the previous track.
- Send desktop notifications with the current track title.
- Runs as a background server process for continuous playback control.
- Automatically clears the log file if it exceeds a certain size.

## Requirements

### System Tools

Ensure the following tools are installed on your Linux system:

- **Python** with the `python-vlc` library (`pip install python-vlc`).
- **VLC** for media playback.
- **Netcat (nc)** for sending TCP commands to the server.
- **`nohup`** for running the server in the background.
- **`notify-send`** for desktop notifications.
- **Bash** for running the provided shell script.

### Installing Required Tools (For Arch Linux)

Run the following commands to install the necessary tools on Arch-based systems:

```bash
sudo pacman -Syu
sudo pacman -S python vlc gnu-netcat libnotify
```

Additionally, install `python-vlc` via the Arch User Repositories (AUR):

```bash
yay -S python-vlc
```

Alternatively, you can use other AUR helpers like paru or trizen.

> It's better to install python-vlc via the AUR for better system integration. The AUR version is optimized for VLC on Arch, while the pip version may require extra configuration and may not work as seamlessly.

For other distributions, install the equivalents for `Python`, `python-vlc`, `vlc`, `libnotify`, and `netcat`.

## Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/HarkushaVlad/RandomTrack.git
   cd random-track
   ```

2. **Prepare `.env` File**:

   Create a `.env` file with the following variables:

   ```env
   SCRIPT_PATH=/path/to/random_track_server.py
   FOLDER_PATH=/path/to/your/mp3/folder
   LOG_PATH=/path/to/server.log
   ```

   - Replace `/path/to/random_track_server.py` with the full path to the `random_track_server.py` file.
   - Replace `/path/to/your/mp3/folder` with the directory containing your MP3 files.
   - Replace `/path/to/server.log` with the path where you want the server logs to be saved.

3. **Run the Shell Script**:
   Use the provided shell script to manage the server:

   ```bash
   chmod +x ./start_random_track_server.sh
   ./start_random_track_server.sh
   ```

   - If the server is already running, this script will stop it.
   - If the server is not running, it will start the server.

## Commands for Playback Control

Use `nc` to send commands to the server:

- **Play/Pause**:

  ```bash
  echo "play" | nc 127.0.0.1 65432
  ```

- **Show Current Track**:

  ```bash
  echo "title" | nc 127.0.0.1 65432
  ```

- **Next Track**:

  ```bash
  echo "next" | nc 127.0.0.1 65432
  ```

- **Previous Track**:

  ```bash
  echo "prev" | nc 127.0.0.1 65432
  ```

- **Stop Playback**:

  ```bash
  echo "stop" | nc 127.0.0.1 65432
  ```

## Integration with Kando

For a graphical menu interface, you can use [Kando](https://github.com/kando-menu/kando).

![photo_2024-12-22_17-22-08](https://github.com/user-attachments/assets/8e2cf4c5-937e-430f-987e-2f0e851e49e9)

Simply add the commands provided above to a Kando menu for easy access and control. This will allow you to manage playback directly from a graphical interface.

## Troubleshooting

### Port Already in Use

If the server fails to start because the port is in use, terminate the process:

```bash
lsof -i :65432
kill -9 <PID>
```

Replace `<PID>` with the process ID returned by the `lsof` command.

### Log File Too Large

If the log file becomes too large, the server will automatically clear it before starting new logs. You can also manually clear the log file by running:

```bash
> /path/to/server.log
```

This will truncate the log file to zero bytes without deleting it.

---

## License

This project is licensed under the MIT License. See
the [LICENSE](https://github.com/HarkushaVlad/Random-Track-Player/blob/main/LICENSE) file for details.
