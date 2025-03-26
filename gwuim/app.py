import os
import subprocess
import sys
import webbrowser
import time
import ctypes
import socket
import pystray
from pystray import MenuItem as item
from PIL import Image

# Function to load the icon from the file
def create_image():
    return Image.open(r"C:\workspace\gwuim\gwuim\app_icon.ico")

# Function to stop the server and exit
def on_exit(icon, item):
    icon.stop()

    # Terminate any running Django servers
    subprocess.call('taskkill /F /IM python.exe /T', shell=True)

    os._exit(0)

# Function to check if port 8000 is already in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Hide the terminal window
if sys.platform == "win32":
    ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 0x80)

# Navigate to the Django project folder
os.chdir(r"C:\workspace\gwuim\gwuim")

# Check if the server is already running
if is_port_in_use(8000):
    print("Server is already running. Restarting server...")

    # Kill any running Django servers
    subprocess.call('taskkill /F /IM python.exe /T', shell=True)
    time.sleep(2)  # Small delay to ensure processes are properly closed

# Start the Django server
print("Starting server...")
server_process = subprocess.Popen(
    r'venv\Scripts\activate.bat && python manage.py runserver',
    shell=True,
    creationflags=subprocess.CREATE_NO_WINDOW
)

# Give the server a few seconds to start
time.sleep(5)

# Open the default web browser
webbrowser.open("http://localhost:8000")

# Create system tray icon
icon = pystray.Icon("Django Server", create_image(), menu=pystray.Menu(item("Exit", on_exit)))

# Run the system tray icon
icon.run()
