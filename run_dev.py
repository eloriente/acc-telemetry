import subprocess
import time
import webview
import sys
import os
import requests

STREAMLIT_PORT = "8501"

# Get the absolute path of the project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Start Streamlit process with project root as working directory
streamlit_process = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "ui/dashboard.py",
        "--server.port",
        STREAMLIT_PORT,
        "--server.headless",
        "true"
    ],
    cwd=ROOT_DIR  # Set working directory to project root
)

# Function to check if Streamlit server is up
def wait_for_streamlit(url, timeout=30):
    # Wait for Streamlit to start and respond
    start_time = time.time()
    while True:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                break
        except:
            pass
        if time.time() - start_time > timeout:
            print("Streamlit server did not start in time.")
            break
        time.sleep(0.5)

# Wait until Streamlit server is ready
wait_for_streamlit(f"http://localhost:{STREAMLIT_PORT}")

# Create native window
webview.create_window(
    title="ACC Telemetry Dashboard (DEV)",
    url=f"http://localhost:{STREAMLIT_PORT}",
    width=1200,
    height=800
)

# Start the WebView loop
webview.start()

# Stop Streamlit when window closes
streamlit_process.terminate()