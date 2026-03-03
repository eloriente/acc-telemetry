import sys
import os

# Asegurar que el directorio raíz está en el path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import time
from datetime import datetime

# Importaciones absolutas
from components.controls import render_controls
from components.lap_display import render_lap_display
from components.history_display import render_history_display
from components.download import download_tab
from telemetry.reader import TelemetryReader
from telemetry.lap_detector import LapDetector
from storage.session_manager import SessionManager
from storage.lap_storage import LapStorage

# Configuración de página
st.set_page_config(
    page_title="ACC Telemetry Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main > div { padding: 0rem 1rem; }
    .debug-info {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        margin: 5px 0;
    }
    @media screen and (max-width: 1200px) {
        h1 { font-size: 2rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.2rem !important; }
    }
    @media screen and (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1rem !important; }
    }
    .stMetric {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    @media screen and (max-width: 640px) {
        .row-widget.stHorizontal {
            flex-direction: column;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }
    .track-selector {
        background-color: #2D2D2D;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .best-times {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #FFD700;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏎️ ACC Telemetry Dashboard")

# ------------------------------
# Session state initialization
# ------------------------------
if "recording" not in st.session_state:
    st.session_state.recording = False
if "lap_storage_initialized" not in st.session_state:
    st.session_state.lap_storage_initialized = False
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
if "data_counter" not in st.session_state:
    st.session_state.data_counter = 0
if "last_data_time" not in st.session_state:
    st.session_state.last_data_time = None
if "current_track" not in st.session_state:
    st.session_state.current_track = None

# ------------------------------
# Global objects
# ------------------------------
reader = TelemetryReader()
lap_detector = LapDetector()
session = SessionManager()

# Crear directorio base para datos
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)

# Inicializar lap_storage
if not st.session_state.lap_storage_initialized:
    st.session_state.lap_storage = LapStorage(base_path=data_dir)
    st.session_state.lap_storage_initialized = True

lap_storage = st.session_state.lap_storage

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Configuración")

    # Selector de circuito
    st.markdown('<div class="track-selector">', unsafe_allow_html=True)
    st.markdown("### 🏁 Circuito")

    available_tracks = lap_storage.get_available_tracks()
    track_options = ["Selecciona circuito..."] + available_tracks + ["➕ Nuevo circuito..."]

    # Determinar el índice seleccionado
    current_track = st.session_state.current_track
    selected_index = 0
    if current_track and current_track in available_tracks:
        selected_index = available_tracks.index(current_track) + 1

    selected_track = st.selectbox(
        "Selecciona circuito",
        track_options,
        index=selected_index,
        key="track_selector"
    )

    if selected_track == "➕ Nuevo circuito...":
        with st.form("new_track_form"):
            new_track = st.text_input("Nombre del circuito",
                                      placeholder="ej. monza, spa, brands_hatch",
                                      help="Usa minúsculas y guiones bajos")
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ Establecer")
            with col2:
                cancelled = st.form_submit_button("❌ Cancelar")

            if submitted and new_track:
                track_name = new_track.lower().replace(" ", "_")
                lap_storage.set_track(track_name)
                st.session_state.current_track = track_name
                st.rerun()
    elif selected_track != "Selecciona circuito..." and selected_track != "➕ Nuevo circuito...":
        if selected_track != st.session_state.current_track:
            lap_storage.set_track(selected_track)
            st.session_state.current_track = selected_track
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Mostrar mejores tiempos globales si hay circuito seleccionado
    if st.session_state.current_track:
        global_bests = lap_storage.get_global_bests()
        if global_bests['best_lap'] or any(global_bests['best_sectors']):
            st.markdown('<div class="best-times">', unsafe_allow_html=True)
            st.markdown("### 🌍 Mejores globales")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Vuelta**")
                st.markdown(f"<h3 style='color: #FFD700;'>{global_bests['best_lap_formatted']}</h3>",
                            unsafe_allow_html=True)

            with col2:
                st.markdown("**Sectores**")
                sectors = global_bests['best_sectors_formatted']
                st.markdown(f"S1: {sectors[0]}<br>S2: {sectors[1]}<br>S3: {sectors[2]}",
                            unsafe_allow_html=True)

            with col3:
                st.markdown("**Última actualización**")
                st.markdown(datetime.now().strftime("%d/%m/%Y"), unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Modos de navegación
    state = st.radio(
        "📱 Modo",
        ["🏁 Live Telemetry", "📚 Historial", "📥 Download CSV"],
        key="navigation_mode"
    )

    st.markdown("---")

    # Panel de debug (colapsable)
    with st.expander("🔧 Debug", expanded=False):
        st.session_state.debug_mode = st.checkbox("Modo debug", value=False)
        show_raw_data = st.checkbox("Mostrar datos crudos", value=False)

        if st.button("🔄 Reset Sesión Actual"):
            st.session_state.recording = False
            st.session_state.data_counter = 0
            st.session_state.last_data_time = None
            lap_storage.reset()
            st.rerun()

        # Estadísticas
        st.markdown(f"**Paquetes:** {st.session_state.data_counter}")
        if st.session_state.last_data_time:
            elapsed = time.time() - st.session_state.last_data_time
            st.markdown(f"**Último dato:** {elapsed:.1f}s ago")

        if st.session_state.recording:
            st.markdown("**Estado:** 🟢 Grabando")
        else:
            st.markdown("**Estado:** ⚪ Detenido")

    with st.expander("ℹ️ Información", expanded=False):
        st.markdown(f"**Proyecto:** {os.path.basename(project_root)}")
        st.markdown(f"**Datos:** {data_dir}")
        st.markdown(f"**Streamlit:** {st.__version__}")
        if st.session_state.current_track:
            st.markdown(f"**Circuito actual:** {st.session_state.current_track}")

# ------------------------------
# Contenido principal según el modo
# ------------------------------
if state == "🏁 Live Telemetry":
    # Verificar que hay circuito seleccionado
    if not st.session_state.current_track:
        st.warning("⚠️ Por favor, selecciona un circuito en la barra lateral antes de comenzar.")
        st.stop()

    # Controles de grabación
    render_controls()

    # Layout principal
    if st.session_state.debug_mode:
        main_col, debug_col = st.columns([2, 1])
    else:
        main_col = st.container()

    with main_col:
        # Placeholder para la visualización de vueltas
        lap_display_placeholder = st.empty()

        # Mostrar estado inicial
        with lap_display_placeholder.container():
            render_lap_display(lap_storage)

    if st.session_state.debug_mode:
        with debug_col:
            st.markdown("### 🔍 Datos en tiempo real")
            debug_placeholder = st.empty()
            data_preview_placeholder = st.empty()

    # Main telemetry loop
    try:
        while True:
            data = reader.read()

            if data:
                st.session_state.data_counter += 1
                st.session_state.last_data_time = time.time()

                # Mostrar datos crudos en debug
                if st.session_state.debug_mode and show_raw_data:
                    with data_preview_placeholder.container():
                        st.markdown("**Últimos datos:**")
                        preview = {}
                        for key in ['lap_time', 'lapTime', 'currentLapTime', 'sector',
                                    'speed', 'rpm', 'completed_laps', 'lastLapTime']:
                            if key in data:
                                preview[key] = data[key]
                        st.json(preview)

                if st.session_state.recording:
                    # Debug info
                    if st.session_state.debug_mode:
                        debug_info = []

                        # Detectar campos de tiempo
                        time_fields = []
                        for field in ['lap_time', 'lapTime', 'currentLapTime']:
                            if field in data:
                                time_fields.append(f"{field}: {data[field]:.3f}")

                        if time_fields:
                            debug_info.append("⏱️ " + " | ".join(time_fields))

                        if 'sector' in data:
                            debug_info.append(f"📍 Sector: {data['sector']}")

                        if 'completed_laps' in data:
                            debug_info.append(f"🏁 Vueltas completadas: {data['completed_laps']}")

                        if 'lastLapTime' in data and data['lastLapTime'] > 0:
                            debug_info.append(f"🏆 Última vuelta: {data['lastLapTime']:.3f}")

                        with debug_placeholder.container():
                            if debug_info:
                                st.markdown("### 📊 Estado actual")
                                for info in debug_info:
                                    st.markdown(f"- {info}")
                            else:
                                st.info("Esperando datos de ACC...")

                    # Detección de vueltas completadas
                    completed_laps = data.get("completed_laps", 0)
                    new_lap = lap_detector.update(completed_laps)

                    if new_lap:
                        if st.session_state.debug_mode:
                            print(f"\n{'='*50}")
                            print(f"NUEVA VUELTA: {lap_detector.current_lap}")
                            print(f"{'='*50}\n")

                        # Guardar vuelta anterior
                        if hasattr(lap_storage, 'current_lap_number') and lap_storage.current_lap_number > 0:
                            try:
                                lap_storage.save_lap()
                                if session:
                                    session.increment_lap()
                            except Exception as e:
                                if st.session_state.debug_mode:
                                    print(f"Error guardando vuelta: {e}")

                        # Iniciar nueva vuelta
                        lap_storage.start_new_lap(lap_detector.current_lap)

                    # Añadir datos actuales
                    try:
                        lap_storage.append(data)
                    except Exception as e:
                        if st.session_state.debug_mode:
                            print(f"Error añadiendo datos: {e}")

                    # Actualizar visualización
                    with lap_display_placeholder.container():
                        render_lap_display(lap_storage)

            time.sleep(0.1)

    except KeyboardInterrupt:
        reader.close()
    except Exception as e:
        if st.session_state.debug_mode:
            st.error(f"Error: {e}")
        time.sleep(1)

elif state == "📚 Historial":
    render_history_display(lap_storage)

elif state == "📥 Download CSV":
    download_tab()

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: #666; padding: 1rem; font-size: 0.8rem;">
        ACC Telemetry Dashboard | Desarrollado con Streamlit 
        {f'| Circuito: {st.session_state.current_track}' if st.session_state.current_track else ''}
    </div>
    """,
    unsafe_allow_html=True
)