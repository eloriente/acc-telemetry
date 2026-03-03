# ui/components/lap_display.py
import streamlit as st
import pandas as pd

def format_time(seconds):
    """Formatear tiempo en segundos a mm:ss.ms"""
    if seconds is None or seconds <= 0:
        return "--:--.---"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"

def extract_lap_time(data_point):
    """Extraer tiempo de vuelta de diferentes formatos posibles"""
    possible_fields = ['lap_time', 'lapTime', 'currentLapTime', 'LapCurrentLapTime']
    for field in possible_fields:
        if field in data_point and data_point[field] > 0:
            return data_point[field]
    return 0

def extract_sector(data_point):
    """Extraer sector actual"""
    if 'sector' in data_point:
        return data_point['sector']
    return 0

def extract_sector_time(data_point, sector_idx):
    """Extraer tiempo de sector específico"""
    # Buscar en diferentes formatos posibles
    possible_fields = [
        f'sector{sector_idx+1}Time',
        f'sector{sector_idx+1}_time',
        'sector_time',
        'sectorTime'
    ]
    for field in possible_fields:
        if field in data_point and data_point[field] > 0:
            return data_point[field]
    return 0

def render_lap_display(lap_storage):
    """Renderizar la visualización de vueltas y sectores estilo ACC"""

    # Verificar si hay datos
    if not hasattr(lap_storage, 'current_lap_data') or len(lap_storage.current_lap_data) == 0:
        st.info("Esperando datos de ACC...")
        return

    # Obtener el último punto de datos
    last_data = lap_storage.current_lap_data[-1] if lap_storage.current_lap_data else {}

    # Extraer tiempos actuales
    current_lap_time = extract_lap_time(last_data)
    current_sector = extract_sector(last_data)

    # Calcular tiempos de sector basados en los datos históricos
    sector_times = [0, 0, 0]
    sector_splits = [0, 0, 0]

    # Buscar tiempos de sector en los datos
    for data_point in lap_storage.current_lap_data:
        for i in range(3):
            sector_time = extract_sector_time(data_point, i)
            if sector_time > 0:
                sector_times[i] = sector_time

    # Calcular splits (tiempos parciales de cada sector)
    if sector_times[0] > 0:
        sector_splits[0] = sector_times[0]
    if sector_times[1] > 0:
        sector_splits[1] = sector_times[1] - sector_times[0]
    if sector_times[2] > 0:
        sector_splits[2] = sector_times[2] - sector_times[1]

    # Mejores tiempos (usando los datos almacenados)
    best_lap_time = float('inf')
    best_sectors = [float('inf'), float('inf'), float('inf')]

    if hasattr(lap_storage, 'laps') and lap_storage.laps:
        # Buscar mejor vuelta
        for lap in lap_storage.laps:
            if lap['total_time'] < best_lap_time and lap['total_time'] > 0:
                best_lap_time = lap['total_time']

            # Buscar mejores sectores
            if 'sector_splits' in lap:
                for i in range(3):
                    if lap['sector_splits'][i] < best_sectors[i] and lap['sector_splits'][i] > 0:
                        best_sectors[i] = lap['sector_splits'][i]

    # Título principal
    st.markdown("## 🏁 ACC Telemetry")

    # ---- DIFERENCIAL PRINCIPAL ----
    if best_lap_time != float('inf') and current_lap_time > 0:
        delta = current_lap_time - best_lap_time
        delta_display = f"{'+' if delta > 0 else ''}{delta:.3f}"
        delta_color = "#4CAF50" if delta <= 0 else "#F44336"
    else:
        delta_display = "+0.000"
        delta_color = "#888"

    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #1E1E1E; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: {delta_color}; margin: 0; font-size: 64px;">{delta_display}</h1>
        <p style="color: #888; margin: 0;">diferencial</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- TIEMPOS DE VUELTA ----
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background-color: #2D2D2D; padding: 15px; border-radius: 5px;">
            <p style="color: #888; margin: 0;">TIEMPO ACTUAL</p>
            <h2 style="color: white; margin: 0; font-size: 36px;">{format_time(current_lap_time)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        best_lap_display = format_time(best_lap_time) if best_lap_time != float('inf') else "--:--.---"
        st.markdown(f"""
        <div style="background-color: #2D2D2D; padding: 15px; border-radius: 5px;">
            <p style="color: #888; margin: 0;">MEJOR TIEMPO</p>
            <h2 style="color: #FFD700; margin: 0; font-size: 36px;">{best_lap_display}</h2>
        </div>
        """, unsafe_allow_html=True)

    # ---- SECTORES ----
    st.markdown("### 📊 Sectores")

    # Crear 3 columnas para los sectores
    cols = st.columns(3)

    for i, col in enumerate(cols):
        with col:
            sector_num = i + 1
            sector_split = sector_splits[i]
            best_sector = best_sectors[i] if best_sectors[i] != float('inf') else None

            # Calcular delta del sector
            if sector_split > 0 and best_sector:
                sector_delta = sector_split - best_sector
                delta_color = "#4CAF50" if sector_delta <= 0 else "#F44336"
                delta_sign = "+" if sector_delta > 0 else ""
                delta_text = f"{delta_sign}{sector_delta:.3f}"
            else:
                delta_text = "--.---"
                delta_color = "#888"

            # Determinar si estamos en este sector actualmente
            is_current_sector = (current_sector == i)
            border_style = "2px solid #4CAF50" if is_current_sector else "none"

            # Tarjeta de sector
            st.markdown(f"""
            <div style="background-color: #2D2D2D; padding: 15px; border-radius: 5px; text-align: center; border: {border_style};">
                <h3 style="color: #888; margin: 0; font-size: 16px;">SECTOR {sector_num}</h3>
                <h2 style="color: white; margin: 5px 0; font-size: 28px;">{format_time(sector_split)}</h2>
                <p style="color: #888; margin: 0; font-size: 14px;">vs mejor {format_time(best_sector)}</p>
                <h3 style="color: {delta_color}; margin: 5px 0; font-size: 20px;">{delta_text}</h3>
            </div>
            """, unsafe_allow_html=True)

    # ---- ÚLTIMA VUELTA COMPLETADA ----
    if hasattr(lap_storage, 'laps') and lap_storage.laps:
        last_lap = lap_storage.laps[-1]
        st.markdown(f"### 🏁 Última vuelta: {format_time(last_lap['total_time'])}")

    # ---- HISTORIAL DE VUELTAS ----
    with st.expander("📋 Ver historial de vueltas"):
        if hasattr(lap_storage, 'laps') and lap_storage.laps:
            # Crear resumen de vueltas
            lap_summary = []
            for lap in lap_storage.laps:
                lap_summary.append({
                    'Vuelta': lap['lap_number'],
                    'Tiempo': format_time(lap['total_time']),
                    'S1': format_time(lap['sector_splits'][0]) if lap['sector_splits'][0] > 0 else '--',
                    'S2': format_time(lap['sector_splits'][1]) if lap['sector_splits'][1] > 0 else '--',
                    'S3': format_time(lap['sector_splits'][2]) if lap['sector_splits'][2] > 0 else '--'
                })

            df_laps = pd.DataFrame(lap_summary)

            # Función para resaltar mejores sectores
            def highlight_best(row):
                styles = [''] * len(row)
                for i, sector in enumerate(['S1', 'S2', 'S3']):
                    if sector in row.index:
                        sector_time_str = row[sector]
                        if sector_time_str != '--':
                            try:
                                minutes, secs = sector_time_str.split(':')
                                sector_seconds = int(minutes) * 60 + float(secs)
                                if best_sectors[i] != float('inf') and abs(sector_seconds - best_sectors[i]) < 0.01:
                                    col_index = list(row.index).index(sector)
                                    styles[col_index] = 'background-color: #6a0dad; color: white'
                            except:
                                pass
                return styles

            styled_df = df_laps.style.apply(highlight_best, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay vueltas registradas")