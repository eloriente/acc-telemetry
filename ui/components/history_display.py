# ui/components/history_display.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime

def format_time(seconds):
    """Formatear tiempo en segundos a mm:ss.ms"""
    if seconds is None or seconds <= 0:
        return '--:--.---'
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"

def render_history_display(lap_storage):
    """Renderizar el historial de sesiones"""

    st.markdown("## 📚 Historial de Sesiones")

    # Obtener circuitos disponibles
    available_tracks = lap_storage.get_available_tracks()

    if not available_tracks:
        st.info("No hay circuitos en el historial. ¡Comienza a grabar!")
        return

    # Selector de circuito
    selected_track = st.selectbox(
        "Selecciona circuito",
        ["Selecciona..."] + available_tracks
    )

    if selected_track == "Selecciona...":
        return

    # Obtener sesiones del circuito seleccionado
    sessions = lap_storage.get_track_sessions(selected_track)

    if not sessions:
        st.info(f"No hay sesiones para {selected_track}")
        return

    # Selector de sesión
    session_options = []
    for session in sessions:
        timestamp = session['timestamp']
        dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
        formatted_date = dt.strftime('%d/%m/%Y %H:%M')
        lap_count = session['data']['total_laps']
        best_lap = format_time(session['data']['best_lap']) if session['data']['best_lap'] else '--'
        session_options.append(
            f"{formatted_date} - {lap_count} vueltas - Mejor: {best_lap}"
        )

    selected_session_idx = st.selectbox(
        "Selecciona sesión",
        range(len(session_options)),
        format_func=lambda x: session_options[x]
    )

    if selected_session_idx is None:
        return

    # Cargar sesión seleccionada
    selected_session = sessions[selected_session_idx]
    session_data = lap_storage.load_session(selected_session['path'])

    if not session_data:
        st.error("Error cargando la sesión")
        return

    # Mostrar información de la sesión
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Circuito", selected_track)

    with col2:
        dt = datetime.strptime(selected_session['timestamp'], '%Y%m%d_%H%M%S')
        st.metric("Fecha", dt.strftime('%d/%m/%Y'))

    with col3:
        st.metric("Hora", dt.strftime('%H:%M'))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Vueltas", session_data['session']['total_laps'])

    with col2:
        best_lap = format_time(session_data['session']['best_lap'])
        st.metric("Mejor vuelta", best_lap)

    with col3:
        if session_data['session']['best_sectors']:
            best_sectors = [format_time(s) for s in session_data['session']['best_sectors'] if s]
            st.metric("Mejores sectores", f"S1:{best_sectors[0]} S2:{best_sectors[1]} S3:{best_sectors[2]}")

    # Tabla de vueltas
    st.markdown("### 📊 Vueltas de la sesión")

    if session_data['laps']:
        lap_data = []
        for lap in session_data['laps']:
            lap_data.append({
                'Vuelta': lap['lap_number'],
                'Tiempo': format_time(lap['total_time']),
                'Sector 1': format_time(lap['sector_splits'][0]) if lap['sector_splits'][0] > 0 else '--',
                'Sector 2': format_time(lap['sector_splits'][1]) if lap['sector_splits'][1] > 0 else '--',
                'Sector 3': format_time(lap['sector_splits'][2]) if lap['sector_splits'][2] > 0 else '--'
            })

        df = pd.DataFrame(lap_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Selector de vuelta para ver detalles
        with st.expander("📈 Ver detalles de vuelta"):
            lap_numbers = [f"Vuelta {lap['lap_number']} - {format_time(lap['total_time'])}"
                           for lap in session_data['laps']]
            selected_lap = st.selectbox("Selecciona vuelta", ["Selecciona..."] + lap_numbers)

            if selected_lap != "Selecciona...":
                lap_num = int(selected_lap.split()[1].split('-')[0].strip())
                lap_detail = next((l for l in session_data['laps'] if l['lap_number'] == lap_num), None)

                if lap_detail and 'data' in lap_detail:
                    st.markdown(f"#### Datos detallados - Vuelta {lap_num}")

                    # Mostrar gráficos de la vuelta
                    df_lap = pd.DataFrame(lap_detail['data'])

                    tab1, tab2, tab3 = st.tabs(["Velocidad", "Gas/Freno", "RPM"])

                    with tab1:
                        if 'speed' in df_lap.columns and 'time' in df_lap.columns:
                            st.line_chart(df_lap.set_index('time')['speed'])
                        elif 'speed_kmh' in df_lap.columns and 'time' in df_lap.columns:
                            st.line_chart(df_lap.set_index('time')['speed_kmh'])

                    with tab2:
                        gas_col = next((col for col in ['gas', 'throttle'] if col in df_lap.columns), None)
                        if gas_col and 'brake' in df_lap.columns and 'time' in df_lap.columns:
                            st.line_chart(df_lap.set_index('time')[[gas_col, 'brake']])

                    with tab3:
                        if 'rpm' in df_lap.columns and 'time' in df_lap.columns:
                            st.line_chart(df_lap.set_index('time')['rpm'])
    else:
        st.info("No hay datos de vueltas en esta sesión")