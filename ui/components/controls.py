# ui/components/controls.py
import streamlit as st
import time  # Asegurar que time está importado

def render_controls():
    """Render start/stop recording controls"""
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if not st.session_state.recording:
            if st.button("Start Recording", type="primary"):
                st.session_state.recording = True
                st.session_state.start_time = time.time()
                st.rerun()
        else:
            if st.button("Stop Recording", type="secondary"):
                st.session_state.recording = False
                st.rerun()

    with col2:
        if st.button("Reset Session"):
            st.session_state.recording = False
            st.session_state.start_time = None
            if "lap_storage" in st.session_state:
                # Resetear pero mantener la instancia
                st.session_state.lap_storage.current_lap_data = []
                st.session_state.lap_storage.current_lap_number = 0
                st.session_state.lap_storage.current_lap_sectors = [None, None, None]
            st.rerun()

    with col3:
        if st.session_state.recording:
            elapsed = time.time() - st.session_state.start_time
            mins = int(elapsed // 60)
            secs = elapsed % 60
            st.info(f"⏱️ Recording... {mins}:{secs:05.2f}")