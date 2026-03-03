# ui/components/debug_display.py
import streamlit as st
import pandas as pd

def render_debug_display(lap_storage):
    """Versión debug que muestra todos los datos disponibles"""

    st.markdown("## 🔍 DEBUG - Datos crudos")

    # Mostrar estado de session_state
    st.markdown("### 📌 Session State")
    st.json({
        "recording": st.session_state.get("recording", False),
        "data_counter": st.session_state.get("data_counter", 0),
    })

    # Mostrar información de LapStorage
    st.markdown("### 📊 LapStorage Data")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Atributos:**")
        attrs = [attr for attr in dir(lap_storage) if not attr.startswith('_') and not callable(getattr(lap_storage, attr))]
        st.write(attrs)

    with col2:
        st.markdown("**Métodos:**")
        methods = [method for method in dir(lap_storage) if not method.startswith('_') and callable(getattr(lap_storage, method))]
        st.write(methods)

    # Intentar obtener información actual
    st.markdown("### 🏁 Información Actual")

    try:
        if hasattr(lap_storage, 'get_current_lap_info'):
            current_info = lap_storage.get_current_lap_info()
            st.json(current_info)
        else:
            st.error("No tiene método get_current_lap_info")

            # Mostrar atributos relevantes manualmente
            info = {}
            if hasattr(lap_storage, 'current_lap_time'):
                info['current_lap_time'] = lap_storage.current_lap_time
            if hasattr(lap_storage, 'current_lap_number'):
                info['current_lap_number'] = lap_storage.current_lap_number
            if hasattr(lap_storage, 'current_sector'):
                info['current_sector'] = lap_storage.current_sector
            if hasattr(lap_storage, 'current_sector_times'):
                info['current_sector_times'] = lap_storage.current_sector_times
            st.json(info)
    except Exception as e:
        st.error(f"Error obteniendo current_info: {e}")

    # Mostrar mejores tiempos
    st.markdown("### 🏆 Mejores Tiempos")

    try:
        if hasattr(lap_storage, 'get_best_times'):
            best_times = lap_storage.get_best_times()
            st.json(best_times)
        else:
            best = {}
            if hasattr(lap_storage, 'best_lap_time'):
                best['best_lap_time'] = lap_storage.best_lap_time
            if hasattr(lap_storage, 'best_sectors'):
                best['best_sectors'] = lap_storage.best_sectors
            st.json(best)
    except Exception as e:
        st.error(f"Error obteniendo best_times: {e}")

    # Mostrar historial de vueltas
    st.markdown("### 📋 Historial de Vueltas")

    try:
        if hasattr(lap_storage, 'get_lap_summary'):
            summary = lap_storage.get_lap_summary()
            if summary:
                df = pd.DataFrame(summary)
                st.dataframe(df)
            else:
                st.info("No hay vueltas en el historial")
        else:
            if hasattr(lap_storage, 'laps'):
                st.write(f"Vueltas almacenadas: {len(lap_storage.laps)}")
                if lap_storage.laps:
                    st.json(lap_storage.laps[-1])  # Mostrar la última vuelta
    except Exception as e:
        st.error(f"Error obteniendo historial: {e}")

    # Mostrar últimos datos recibidos
    st.markdown("### 📈 Últimos datos en current_lap_data")

    try:
        if hasattr(lap_storage, 'current_lap_data'):
            data_len = len(lap_storage.current_lap_data)
            st.write(f"Cantidad de puntos: {data_len}")

            if data_len > 0:
                # Mostrar los últimos 5 puntos
                last_points = lap_storage.current_lap_data[-5:] if data_len > 5 else lap_storage.current_lap_data

                # Extraer campos relevantes
                points_data = []
                for point in last_points:
                    point_info = {}
                    for key in ['time', 'lap_time', 'sector', 'speed', 'rpm']:
                        if key in point:
                            point_info[key] = point[key]
                    points_data.append(point_info)

                st.json(points_data)
    except Exception as e:
        st.error(f"Error mostrando datos: {e}")