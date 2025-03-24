import os
import subprocess
import sys
import webbrowser
import time
import ctypes
import pystray
from pystray import MenuItem as item
from PIL import Image

# Function to load the icon from the file
def create_image():
    # Load the icon from the specified path
    image = Image.open(r"C:\workspace\gwuim\gwuim\app_icon.ico")
    return image

# Function to stop the server and exit
def on_exit(icon, item):
    icon.stop()  # Stop the system tray icon
    server_process.terminate()  # Terminate the Django server process
    os._exit(0)  # Stop the program

# Hide the terminal window
if sys.platform == "win32":
    ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 0x80)

# Navigate to the Django project folder
os.chdir(r"C:\workspace\gwuim\gwuim")

# Activate virtual environment
subprocess.Popen(r'venv\Scripts\activate.bat &&  python manage.py runserver' , shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

# Start the Django server in a separate process and store the process reference
server_process = subprocess.Popen(r'python manage.py runserver ', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

# Give the server a few seconds to start before opening the browser
time.sleep(5)

# Open the default web browser and navigate to localhost:8000
webbrowser.open("http://localhost:8000")

# Create system tray icon
icon = pystray.Icon("Django Server", create_image(), menu=pystray.Menu(item("Exit", on_exit)))

# Run the system tray icon
icon.run()
