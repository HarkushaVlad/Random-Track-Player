#!/bin/bash

send_notification() {
  local title="$1"
  local message="$2"
  notify-send "$title" "$message"
}

SCRIPT_DIR=$(dirname "$(realpath "$0")")
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo ".env file not found at $ENV_FILE"
    notify-send ".env file not found" "Make sure the .env file exists in $SCRIPT_DIR"
    exit 1
fi

SCRIPT_PATH=$SCRIPT_PATH
FOLDER_PATH=$FOLDER_PATH
LOG_FILE="server.log"
HOST="127.0.0.1"
PORT="65432"

PROCESS_ID=$(pgrep -af "python $SCRIPT_PATH" | awk '{print $1}')
if [ -n "$PROCESS_ID" ]; then
  send_notification "Random Track Server" "Server is already running. Stopping it now..."
  
  kill -9 $PROCESS_ID
  sleep 3
  
  PROCESS_ID=$(pgrep -af "python $SCRIPT_PATH" | awk '{print $1}')
  if [ -n "$PROCESS_ID" ]; then
    send_notification "Random Track Server" "Failed to stop the server. Try again later."
    exit 1
  fi

  PORT_USAGE=$(lsof -i tcp:$PORT | grep LISTEN | awk '{print $2}')
  if [ -n "$PORT_USAGE" ]; then
  echo "Port $PORT is in use. Terminating processes using this port..."
  kill -9 $PORT_USAGE
  sleep 2
  fi
  
  send_notification "Random Track Server" "Server stopped successfully."
else
  send_notification "Random Track Server" "Starting the server..."
  
  nohup python $SCRIPT_PATH $FOLDER_PATH > $LOG_FILE 2>&1 &
  sleep 2  # Wait for the server to start
  
  PROCESS_ID=$(pgrep -af "python $SCRIPT_PATH" | awk '{print $1}')
  if [ -n "$PROCESS_ID" ]; then
    send_notification "Random Track Server" "Server started successfully with PID $PROCESS_ID."
    
    # Send "play" command to the server
    echo "play" | nc $HOST $PORT
  else
    send_notification "Random Track Server" "Failed to start the server. Check the logs for details."
    cat $LOG_FILE
    exit 1
  fi
fi
