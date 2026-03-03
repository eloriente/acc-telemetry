import subprocess
import time
import webview
import sys

STREAMLIT_PORT = "8501"

# Start Streamlit
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
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(3)

webview.create_window(
    title="ACC Telemetry Dashboard",
    url=f"http://localhost:{STREAMLIT_PORT}",
    width=1200,
    height=800
)

webview.start()

streamlit_process.terminate()