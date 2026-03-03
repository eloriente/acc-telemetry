import streamlit as st

def init_kpis():
    """Initialize KPI columns"""
    kpi_cols = st.columns(3)
    for col in kpi_cols:
        col.metric("", 0)  # placeholders
    return kpi_cols

def update_kpis(data, kpi_cols):
    """Update KPI metrics"""
    speed_val = round(data["speed_kmh"], 1)
    rpm_val = int(data["rpm"])
    gear_val = data["gear"]

    kpi_cols[0].metric("Speed (km/h)", speed_val)
    kpi_cols[1].metric("RPM", rpm_val)
    kpi_cols[2].metric("Gear", gear_val)