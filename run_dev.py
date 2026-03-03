import subprocess
import time
import webview
import sys

STREAMLIT_PORT = "8501"

# Start Streamlit process
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
    ]
)

# Wait for Streamlit to start
time.sleep(3)

# Open native window
webview.create_window(
    title="ACC Telemetry Dashboard (DEV)",
    url=f"http://localhost:{STREAMLIT_PORT}",
    width=1200,
    height=800
)

webview.start()

# Stop Streamlit when window closes
streamlit_process.terminate()