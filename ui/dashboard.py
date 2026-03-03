import time
import pandas as pd
import streamlit as st
import os

from telemetry.reader import TelemetryReader
from telemetry.lap_detector import LapDetector
from storage.session_manager import SessionManager
from storage.lap_storage import LapStorage

# ------------------------------
# Page configuration
# ------------------------------
st.set_page_config(page_title="ACC Telemetry Dashboard", layout="wide")
st.title("ACC Telemetry Dashboard")

# ------------------------------
# Session state initialization
# ------------------------------
if "recording" not in st.session_state:
    st.session_state.recording = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None

# ------------------------------
# Telemetry reader and lap detection
# ------------------------------
reader = TelemetryReader()
lap_detector = LapDetector()
session = None
lap_storage = None

# ------------------------------
# Sidebar navigation
# ------------------------------
state = st.sidebar.radio("Select mode", ["Live Telemetry", "Download CSV"])

# ------------------------------
# LIVE TELEMETRY
# ------------------------------
if state == "Live Telemetry":
    st.header("Live Telemetry")

    # Recording controls
    st.subheader("Recording Control")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Start Recording"):
            st.session_state.recording = True
            st.session_state.start_time = time.time()
            session = SessionManager()
            lap_storage = LapStorage(session.laps_path)
            lap_detector = LapDetector()  # reset lap detector

    with col2:
        if st.button("⏹ Stop Recording"):
            st.session_state.recording = False
            if lap_storage and lap_storage.current_lap > 0:
                lap_storage.save_lap()
                session.increment_lap()

    if st.session_state.recording:
        st.success("Recording telemetry data...")
    else:
        st.info("Recording stopped")

    # Charts and metrics placeholders
    speed_chart = st.empty()
    rpm_chart = st.empty()
    pedal_chart = st.empty()
    steer_chart = st.empty()

    # KPIs
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    speed_val = 0
    rpm_val = 0
    gear_val = 0

    # Main loop
    try:
        while True:
            data = reader.read()

            if data and st.session_state.recording:
                # Lap detection
                new_lap = lap_detector.update(data["completed_laps"])

                if new_lap:
                    if lap_storage.current_lap > 0:
                        lap_storage.save_lap()
                        session.increment_lap()
                    lap_storage.start_new_lap(lap_detector.current_lap)
                    st.session_state.start_time = time.time()

                # Timestamp
                data["time"] = round(time.time() - st.session_state.start_time, 2)
                lap_storage.append(data)

                # Update KPIs
                speed_val = round(data["speed_kmh"], 1)
                rpm_val = int(data["rpm"])
                gear_val = data["gear"]

                kpi_col1.metric("Speed (km/h)", speed_val)
                kpi_col2.metric("RPM", rpm_val)
                kpi_col3.metric("Gear", gear_val)

                # Update charts with last 200 samples
                df_tail = lap_storage.df.tail(200)

                speed_chart.line_chart(df_tail[["time", "speed_kmh"]].set_index("time"))
                rpm_chart.line_chart(df_tail[["time", "rpm"]].set_index("time"))
                pedal_chart.line_chart(df_tail[["time", "gas", "brake"]].set_index("time"))
                steer_chart.line_chart(df_tail[["time", "steer_angle"]].set_index("time"))

            time.sleep(0.1)

    except KeyboardInterrupt:
        reader.close()

# ------------------------------
# DOWNLOAD CSV
# ------------------------------
elif state == "Download CSV":
    st.header("Download Telemetry Data")

    if not session:
        st.warning("No session recorded yet.")
    else:
        # Show list of laps
        laps = sorted(os.listdir(session.laps_path))
        st.subheader("Laps")
        st.write(laps)

        lap_choice = st.selectbox("Select lap to view/download", laps)

        if lap_choice:
            lap_path = os.path.join(session.laps_path, lap_choice)
            df = pd.read_csv(lap_path)
            st.dataframe(df)

            csv_bytes = df.to_csv(index=False).encode()
            st.download_button(
                label=f"Download {lap_choice}",
                data=csv_bytes,
                file_name=lap_choice,
                mime="text/csv"
            )