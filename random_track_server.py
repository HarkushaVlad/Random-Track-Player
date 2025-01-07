import os
import random
import sys
import socket
import threading
import subprocess
import urllib.parse
import vlc
import logging

HOST = "127.0.0.1"
PORT = 65432
paused = False
player = vlc.MediaListPlayer()
media_list = None


def initialize_playlist(folder_path):
    """
    Initialize the playlist by adding all supported audio files in the folder in random order.
    """
    global media_list
    instance = vlc.Instance()
    media_list = instance.media_list_new()

    supported_formats = (".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a")

    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(supported_formats)
    ]

    if not files:
        logging.error("No supported audio files found in the specified folder.")
        return False

    random.shuffle(files)
    for file in files:
        media_list.add_media(instance.media_new(file))

    player.set_media_list(media_list)
    logging.info("Playlist initialized.")
    return True


def play_or_toggle():
    """
    Play or toggle pause/resume of the current track.
    """
    global paused
    if player.is_playing():
        player.pause()
        paused = True
        logging.info("Paused.")
    else:
        player.play()
        paused = False
        logging.info(f"Playing: {get_current_track_name()}")


def next_track():
    """
    Skip to the next track in the playlist.
    """
    if media_list:
        if player.next() == 0:
            logging.info(f"Playing next track: {get_current_track_name()}")
        else:
            logging.error("Next track not found or at the end of the playlist.")
            send_notification(
                "Next track", "Next track not found or at the end of the playlist."
            )
    else:
        logging.error("Playlist is empty.")


def previous_track():
    """
    Go to the previous track in the playlist.
    """
    if media_list:
        if player.previous() == 0:
            logging.info(f"Playing previous track: {get_current_track_name()}")
        else:
            logging.error("Previous track not found or at the start of the playlist.")
            send_notification(
                "Previous track",
                "Previous track not found or at the start of the playlist.",
            )
    else:
        logging.error("Playlist is empty.")


def stop():
    """
    Stop playback completely.
    """
    player.stop()
    logging.info("Playback stopped.")


def send_notification(title, message):
    """
    Send a desktop notification using notify-send.
    """
    subprocess.run(["notify-send", title, message])


def get_current_track_name():
    current_media = player.get_media_player().get_media()
    if current_media:
        track_name = urllib.parse.unquote(current_media.get_mrl())
        track_name = os.path.splitext(os.path.basename(track_name))[0]
        return track_name
    else:
        return None


def send_current_track_notification():
    """
    Send a notification with the current track name.
    """
    track_name = get_current_track_name()
    if track_name:
        send_notification("Now Playing", track_name)
        logging.info(f"Now Playing: {track_name}")
    else:
        send_notification("Now Playing", "No track is currently playing.")
        logging.info("Now Playing: No track is currently playing.")


def handle_client(client_socket):
    """
    Handle incoming commands from a client.
    """
    global paused
    try:
        while True:
            data = client_socket.recv(1024).decode("utf-8").strip()
            if not data:
                break

            logging.info(f"Command received: {data}")
            if data == "play":
                play_or_toggle()
            elif data == "pause":
                play_or_toggle()
            elif data == "next":
                next_track()
            elif data == "prev":
                previous_track()
            elif data == "stop":
                stop()
            elif data == "title":
                send_current_track_notification()
            elif data == "exit":
                logging.info("Exit command received. Stopping the server...")
                stop()
                break
            else:
                logging.error("Unknown command.")
    finally:
        client_socket.close()


def start_server(folder_path):
    """
    Start the server to listen for commands.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)
        logging.info(f"Server listening on {HOST}:{PORT}")

        while True:
            try:
                client_socket, addr = server.accept()
                logging.info(f"Connection from {addr}")
                client_thread = threading.Thread(
                    target=handle_client, args=(client_socket,)
                )
                client_thread.start()
            except KeyboardInterrupt:
                logging.info("Server interrupted. Shutting down...")
                break
            except Exception as e:
                logging.error(f"Error while handling client connection: {e}")
                break

    logging.info("Server has stopped.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: python script_name.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    log_path = sys.argv[2] if len(sys.argv) > 2 else "./server.log"

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filemode="a",
    )

    if not os.path.exists(folder_path) or not initialize_playlist(folder_path):
        sys.exit(1)

    server_thread = threading.Thread(target=start_server, args=(folder_path,))
    server_thread.daemon = True
    server_thread.start()

    logging.info("Server running. Use a client to send commands.")
    while True:
        pass
