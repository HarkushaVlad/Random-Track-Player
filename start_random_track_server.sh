#!/bin/bash

send_notification() {
  local title="$1"
  local message="$2"
  notify-send "$title" "$message"
}

log_message() {
  local message="$1"
  local LOG_PATH="$2"
  echo "$(date '+%Y-%m-%d %H:%M:%S') - SCRIPT - $message" >> "$LOG_PATH"
}

MAX_LOG_SIZE=5242880  # 5 MB

check_log_file_size() {
  local log_file="$1"
  
  if [ -f "$log_file" ]; then
    FILE_SIZE=$(stat -c %s "$log_file")
    if [ "$FILE_SIZE" -gt "$MAX_LOG_SIZE" ]; then
      echo "Log file is too large ($FILE_SIZE bytes), clearing it..."
      > "$log_file"
    fi
  fi
}

SCRIPT_DIR=$(dirname "$(realpath "$0")")
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    log_message ".env file not found at $ENV_FILE" "$LOG_PATH"
    notify-send ".env file not found" "Make sure the .env file exists in $SCRIPT_DIR"
    exit 1
fi

SCRIPT_PATH=$SCRIPT_PATH
FOLDER_PATH=$FOLDER_PATH
LOG_PATH=$LOG_PATH
HOST="127.0.0.1"
PORT="65432"

# Check and clear log file if it's too large
check_log_file_size "$LOG_FILE"

PROCESS_ID=$(pgrep -af "python $SCRIPT_PATH" | awk '{print $1}')
if [ -n "$PROCESS_ID" ]; then
  log_message "Server is already running. Stopping it now..." "$LOG_PATH"
  send_notification "Random Track Server" "Server is already running. Stopping it now..."
  
  kill -9 $PROCESS_ID
  sleep 3
  
  PROCESS_ID=$(pgrep -af "python $SCRIPT_PATH" | awk '{print $1}')
  if [ -n "$PROCESS_ID" ]; then
    log_message "Failed to stop the server. Try again later." "$LOG_PATH"
    send_notification "Random Track Server" "Failed to stop the server. Try again later."
    exit 1
  fi

  PORT_USAGE=$(lsof -i tcp:$PORT | grep LISTEN | awk '{print $2}')
  if [ -n "$PORT_USAGE" ]; then
    log_message "Port $PORT is in use. Terminating processes using this port..." "$LOG_PATH"
    echo "Port $PORT is in use. Terminating processes using this port..."  >> "$LOG_PATH"
    kill -9 $PORT_USAGE
    sleep 2
  fi
  
  log_message "Server stopped successfully." "$LOG_PATH"
  send_notification "Random Track Server" "Server stopped successfully."
else
  log_message "Starting the server..." "$LOG_PATH"
  send_notification "Random Track Server" "Starting the server..."
  
  nohup python $SCRIPT_PATH $FOLDER_PATH $LOG_PATH >> $LOG_PATH 2>&1 &
  sleep 2  # Wait for the server to start
  
  PROCESS_ID=$(pgrep -af "python $SCRIPT_PATH" | awk '{print $1}')
  if [ -n "$PROCESS_ID" ]; then
    log_message "Server started successfully with PID $PROCESS_ID." "$LOG_PATH"
    send_notification "Random Track Server" "Server started successfully with PID $PROCESS_ID."
    
    # Send "play" command to the server
    echo "play" | nc $HOST $PORT
  else
    log_message "Failed to start the server. Check the logs for details." "$LOG_PATH"
    send_notification "Random Track Server" "Failed to start the server. Check the logs for details."
    cat $LOG_PATH
    exit 1
  fi
fi
