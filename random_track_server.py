import os
import random
import pygame
import sys
import socket
import threading
import subprocess

pygame.mixer.init()
current_file = None
paused = False
firstLaunch = True
mp3_files = []
current_index = -1
HOST = "127.0.0.1"
PORT = 65432


def initialize_folder(folder_path):
    """
    Initialize the MP3 folder and load file list.
    """
    global mp3_files
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return False

    mp3_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]
    if not mp3_files:
        print("No MP3 files found in the specified folder.")
        return False
    return True


def play_track(index, folder_path):
    """
    Play a track based on the index.
    """
    global current_file, paused, current_index
    if not mp3_files:
        if not initialize_folder(folder_path):
            return

    pygame.mixer.music.stop()

    current_index = index
    current_file = os.path.join(folder_path, mp3_files[current_index])

    pygame.mixer.music.load(current_file)
    pygame.mixer.music.play()
    paused = False
    print(f"Now playing: {mp3_files[current_index].replace('.mp3', '')}")


def send_notification(title, message):
    """
    Send a desktop notification using notify-send.
    """
    subprocess.run(["notify-send", title, message])


def send_current_track_notification():
    """
    Send a notification with the current track name.
    """
    if current_file:
        track_name = os.path.basename(current_file).replace(".mp3", "")
        send_notification("Now Playing", track_name)
    else:
        send_notification("Now Playing", "No track is currently playing.")


def play_or_toggle(folder_path):
    """
    Play a random MP3 file if none is playing, or toggle pause/resume if a track is already playing.
    """
    global paused, current_index, firstLaunch

    if firstLaunch:
        play_random(folder_path)
        firstLaunch = False
    else:
        if paused:
            pygame.mixer.music.unpause()
            paused = False
            print("Resumed.")
        else:
            pygame.mixer.music.pause()
            paused = True
            print("Paused.")


def play_random(folder_path):
    """
    Play a random MP3 file from the folder.
    """
    index = random.randint(0, len(mp3_files) - 1)
    play_track(index, folder_path)


def next(folder_path):
    """
    Skip the current track and play the next one.
    """
    global current_index
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    # Play next track in the list
    current_index = (current_index + 1) % len(mp3_files)
    play_track(current_index, folder_path)


def previous(folder_path):
    """
    Go to the previous track in the playlist.
    """
    global current_index
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    current_index = (current_index - 1) % len(mp3_files)
    play_track(current_index, folder_path)


def stop():
    """
    Stop playback completely.
    """
    pygame.mixer.music.stop()
    print("Playback stopped.")


def handle_client(client_socket, folder_path):
    """
    Handle incoming commands from a client.
    """
    global paused
    try:
        while True:
            data = client_socket.recv(1024).decode("utf-8").strip()
            if not data:
                break

            print(f"Command received: {data}")
            if data == "play":
                play_or_toggle(folder_path)
            elif data == "pause":
                play_or_toggle(folder_path)
            elif data == "next":
                next(folder_path)
            elif data == "prev":
                previous(folder_path)
            elif data == "stop":
                stop()
            elif data == "title":
                send_current_track_notification()
            elif data == "exit":
                stop()
                break
            else:
                print("Unknown command.")
    finally:
        client_socket.close()


def start_server(folder_path):
    """
    Start the server to listen for commands.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server.accept()
            print(f"Connection from {addr}")
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, folder_path)
            )
            client_thread.start()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]

    if not initialize_folder(folder_path):
        sys.exit(1)

    # Start the server
    try:
        start_server(folder_path)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        stop()
        sys.exit(0)
