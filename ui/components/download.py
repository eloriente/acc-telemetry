import streamlit as st
import os
import pandas as pd
from storage.session_manager import SessionManager

session = None

def download_tab():
    """Download CSV tab"""
    st.header("Download Telemetry Data")

    if not session:
        st.warning("No session recorded yet.")
        return

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