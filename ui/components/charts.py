import streamlit as st
import pandas as pd

def init_charts():
    """Initialize chart columns"""
    chart_cols = st.columns(3)
    return chart_cols

def update_charts(data, chart_cols, lap_storage=None):
    """Update all charts in columns"""
    col1, col2, col3 = chart_cols

    # Si no hay lap_storage, mostrar mensajes placeholder
    if lap_storage is None:
        col1.info("No data available")
        col2.info("No data available")
        col3.info("No data available")
        return

    # Obtener datos de la vuelta actual
    lap_data = lap_storage.get_current_lap_data()

    if lap_data and len(lap_data) > 0:
        # Convertir a DataFrame para facilitar el manejo
        df = pd.DataFrame(lap_data)

        # Asegurarse de que tenemos las columnas necesarias
        # Mapear nombres de columnas según tu estructura de datos
        df_display = df.copy()

        # Columna 1: Speed y RPM
        col1.subheader("Speed (km/h)")
        if 'speed' in df_display.columns:
            # Si el campo se llama 'speed' en lugar de 'speed_kmh'
            col1.line_chart(df_display[["time", "speed"]].set_index("time") if 'time' in df_display.columns else df_display[["speed"]])
        elif 'speed_kmh' in df_display.columns:
            col1.line_chart(df_display[["time", "speed_kmh"]].set_index("time") if 'time' in df_display.columns else df_display[["speed_kmh"]])
        else:
            col1.write("No speed data")

        col1.subheader("RPM")
        if 'rpm' in df_display.columns:
            col1.line_chart(df_display[["time", "rpm"]].set_index("time") if 'time' in df_display.columns else df_display[["rpm"]])
        else:
            col1.write("No RPM data")

        # Columna 2: Gas & Brake
        col2.subheader("Gas & Brake")
        gas_brake_data = []
        if 'gas' in df_display.columns:
            gas_brake_data.append('gas')
        if 'brake' in df_display.columns:
            gas_brake_data.append('brake')
        if 'throttle' in df_display.columns and 'throttle' not in gas_brake_data:
            gas_brake_data.append('throttle')

        if gas_brake_data:
            columns_to_plot = ['time'] + gas_brake_data if 'time' in df_display.columns else gas_brake_data
            col2.line_chart(df_display[columns_to_plot].set_index("time") if 'time' in df_display.columns else df_display[gas_brake_data])
        else:
            col2.write("No gas/brake data")

        # Columna 3: Steer Angle
        col3.subheader("Steer Angle")
        if 'steer_angle' in df_display.columns:
            col3.line_chart(df_display[["time", "steer_angle"]].set_index("time") if 'time' in df_display.columns else df_display[["steer_angle"]])
        elif 'steer' in df_display.columns:
            col3.line_chart(df_display[["time", "steer"]].set_index("time") if 'time' in df_display.columns else df_display[["steer"]])
        else:
            col3.write("No steer angle data")
    else:
        col1.info("Waiting for lap data...")
        col2.info("Waiting for lap data...")
        col3.info("Waiting for lap data...")