# Random MP3 Player with Server Control

Python-based random MP3 player server that supports basic playback control (play/pause, next, previous) and sends desktop notifications about the current track. The server communicates using TCP commands, and it can be controlled using simple command-line utilities like `nc` (Netcat).

## Features

- Play random MP3 files from a specified folder.
- Pause, resume, skip to the next track, or return to the previous track.
- Send desktop notifications with the current track title.
- Runs as a background server process for continuous playback control.

## Requirements

### System Tools

Ensure the following tools are installed on your Linux system:

- **Python 3.12+** with the `pygame` library (`pip install pygame`).
- **Netcat (nc)** for sending TCP commands to the server.
- **`nohup`** for running the server in the background.
- **`notify-send`** for desktop notifications.
- **Bash** for running the provided shell script.

### Installing Required Tools (For Arch Linux)

Run the following commands to install the necessary tools on Arch-based systems:

```bash
sudo pacman -Syu
sudo pacman -S python python-pip gnu-netcat libnotify python-pygame
```

For other distributions, install the equivalents for `Python`, `netcat`, `libnotify`, `python-pygame` and `nohup`.

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
   ```

   Replace `/path/to/random_track_server.py` with the full path to the `random_track_server.py` file, and `/path/to/your/mp3/folder` with the directory containing your MP3 files.

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

## Running the Server in the Background

To start the server as a background process, use:

```bash
nohup ./start_random_track_server.sh > server.log 2>&1 &
```

- `nohup`: Ensures the process keeps running even after you log out.
- `./start_random_track_server.sh`: The script that manages the server.
- `>`: Redirects standard output to a file (`server.log`).
- `2>&1`: Combines standard error with standard output.
- `&`: Runs the command in the background.

## Integration with Kando

For a graphical menu interface, you can use [Kando](https://github.com/kando-menu/kando)

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
