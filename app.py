import streamlit as st
from database.db import (
    init_db, ensure_building, log_energy, save_wastage_alert,
    save_appliance_check, save_peak_load_action, get_dashboard_data
)
from graph.workflow import run_agent

st.set_page_config(page_title="Energy Optimization Agent", page_icon="⚡", layout="wide")
init_db()

# --- Sidebar ---
st.sidebar.title("⚡ Energy Optimization Agent")
st.sidebar.caption("AI-powered smart energy management · SDG 13")
building_name = st.sidebar.text_input("Building / site name", "Building A")

if not building_name:
    st.title("Welcome to the Energy Optimization Agent")
    st.write("Enter a building or site name in the sidebar to get started.")
    st.stop()

ensure_building(building_name)
st.sidebar.success(f"Monitoring: {building_name}")

(tab_monitor, tab_optimize, tab_appliance, tab_peak, tab_analytics) = st.tabs(
    ["📡 Live Monitoring", "💡 Optimization", "🔧 Appliance Efficiency",
     "⏰ Peak Load", "📊 Analytics"]
)

# --- Tab 1: AI Energy Monitoring + Consumption Prediction ---
with tab_monitor:
    st.header("Live energy monitoring")
    st.caption("Enter current consumption per appliance/department (kWh). "
               "In production these come from smart meters/IoT sensors.")

    col1, col2, col3 = st.columns(3)
    ac_kwh = col1.number_input("Air Conditioner (kWh)", 0.0, 100.0, 8.0, step=0.5)
    lights_kwh = col2.number_input("Lights (kWh)", 0.0, 100.0, 2.0, step=0.5)
    computers_kwh = col3.number_input("Computers (kWh)", 0.0, 100.0, 5.0, step=0.5)

    st.caption("Recent daily totals (oldest → newest), used for tomorrow's prediction:")
    hist_cols = st.columns(5)
    recent_daily_kwh = [
        hist_cols[i].number_input(f"Day {i+1}", 0.0, 500.0, v, step=1.0, key=f"hist_{i}")
        for i, v in enumerate([120.0, 115.0, 130.0, 125.0, 140.0])
    ]

    if st.button("Analyze Energy Usage", key="monitor_btn"):
        with st.spinner("AI agent analyzing consumption..."):
            result = run_agent("monitor", {
                "building_name": building_name,
                "appliance_breakdown": {
                    "Air Conditioner": ac_kwh,
                    "Lights": lights_kwh,
                    "Computers": computers_kwh,
                },
                "recent_daily_kwh": recent_daily_kwh,
            })
        usage = result["usage"]
        prediction = result["prediction"]

        level_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(
            usage["usage_level"], "⚪"
        )
        st.subheader(f"{level_icon} Current usage: {usage['usage_level']}")
        st.write(usage["analysis"])
        st.info(f"Recommended action: {usage['recommended_action']}")

        st.subheader("🔮 Consumption prediction")
        st.write(
            f"Predicted tomorrow: **{prediction['predicted_kwh_tomorrow']} kWh** "
            f"({prediction['trend']})"
        )
        st.caption(prediction["reasoning"])
        st.info(f"Proactive step: {prediction['proactive_recommendation']}")

        total_kwh = ac_kwh + lights_kwh + computers_kwh
        log_energy(building_name, total_kwh, usage["usage_level"], usage["analysis"])

# --- Tab 2: Smart Energy Optimization ---
with tab_optimize:
    st.header("Detect wastage & get recommendations")

    st.subheader("Wastage detection")
    col1, col2, col3 = st.columns(3)
    area = col1.text_input("Area", placeholder="e.g. Conference Room")
    appliance_state = col2.selectbox("Appliance state", ["Lights ON", "AC ON", "Lights & AC ON", "All OFF"])
    occupancy = col3.selectbox("Occupancy", ["Occupied", "Not Occupied", "Unknown"])

    if st.button("Check for Wastage"):
        with st.spinner("Checking for energy wastage..."):
            result = run_agent("optimize", {
                "building_name": building_name,
                "area": area or "Unspecified area",
                "appliance_state": appliance_state,
                "occupancy": occupancy,
                "usage_summary": f"{appliance_state} in {area or 'an area'}, occupancy: {occupancy}",
            })
        wastage = result["wastage"]
        recommendation = result["recommendation"]

        if wastage["wastage_detected"]:
            st.error(f"⚠️ Wastage detected: {wastage['issue']}")
        else:
            st.success("✅ No wastage detected.")
        st.info(f"Recommendation: {wastage['recommendation']}")

        if wastage["wastage_detected"]:
            save_wastage_alert(building_name, area or "Unspecified area",
                                wastage["issue"], wastage["recommendation"])

        st.subheader("💡 Optimization recommendations")
        st.write(recommendation["summary"])
        for rec in recommendation["recommendations"]:
            st.write(f"- {rec}")
        st.metric("Estimated savings", f"{recommendation['estimated_savings_percent']}%")

# --- Tab 3: Appliance Efficiency Analysis ---
with tab_appliance:
    st.header("Appliance efficiency check")
    col1, col2 = st.columns(2)
    appliance_name = col1.text_input("Appliance name", placeholder="e.g. Air Conditioner Unit 2")
    age_years = col2.number_input("Approximate age (years)", 0.0, 30.0, 3.0, step=0.5)

    col3, col4 = st.columns(2)
    consumption_kwh = col3.number_input("Actual consumption (kWh)", 0.0, 200.0, 10.0, step=0.5)
    rated_kwh = col4.number_input("Rated/expected consumption (kWh)", 0.1, 200.0, 8.0, step=0.5)

    if st.button("Analyze Appliance"):
        if appliance_name.strip():
            with st.spinner("Analyzing appliance efficiency..."):
                result = run_agent("appliance", {
                    "appliance_name": appliance_name,
                    "consumption_kwh": consumption_kwh,
                    "rated_kwh": rated_kwh,
                    "age_years": age_years,
                })
            status_icon = {"Efficient": "🟢", "Slightly Inefficient": "🟡",
                           "Needs Attention": "🔴"}.get(result["status"], "⚪")
            st.subheader(f"{status_icon} {result['status']}")
            st.info(result["recommendation"])
            save_appliance_check(
                appliance_name, consumption_kwh, rated_kwh,
                result["status"], result["recommendation"]
            )
        else:
            st.warning("Please enter an appliance name.")

# --- Tab 4: Peak Load Management ---
with tab_peak:
    st.header("Peak load management")
    st.caption("Typical peak demand window: 6 PM – 9 PM")

    col1, col2 = st.columns(2)
    current_hour = col1.selectbox(
        "Current hour",
        ["8 AM", "10 AM", "12 PM", "2 PM", "4 PM", "6 PM", "7 PM", "8 PM", "9 PM", "11 PM"]
    )
    flexible_loads = col2.text_input(
        "Flexible/non-essential loads available", placeholder="e.g. Heavy machinery, EV charging"
    )

    if st.button("Check Peak Load Status"):
        with st.spinner("Evaluating peak load conditions..."):
            result = run_agent("peak_load", {
                "building_name": building_name,
                "current_hour": current_hour,
                "flexible_loads": flexible_loads,
            })
        if result["is_peak_period"]:
            st.error(f"🔴 Peak period at {current_hour}")
        else:
            st.success(f"🟢 Not a peak period at {current_hour}")
        st.write(f"**Action taken:** {result['action_taken']}")
        st.caption(result["reasoning"])
        st.metric("Estimated savings", f"{result['estimated_savings_kwh']} kWh")
        save_peak_load_action(
            building_name, current_hour, result["is_peak_period"],
            result["action_taken"], result["estimated_savings_kwh"]
        )

# --- Tab 5: Analytics ---
with tab_analytics:
    st.header("Energy analytics")
    data = get_dashboard_data()

    col1, col2, col3 = st.columns(3)
    col1.metric("Readings logged", len(data["energy_logs"]))
    col2.metric("Wastage alerts", len(data["wastage"]))
    col3.metric("Appliance checks", len(data["appliances"]))

    if st.button("Generate Report"):
        with st.spinner("Generating analytics report..."):
            report = run_agent("analytics", {
                "energy_logs": data["energy_logs"],
                "wastage_alerts": data["wastage"],
            })
        c1, c2 = st.columns(2)
        c1.metric("Total kWh logged", report["total_kwh_logged"])
        c1.metric("Avg. kWh per reading", report["avg_kwh_per_reading"])
        c2.metric("Estimated cost", report["estimated_cost"])
        c2.metric("Est. CO2 emissions", f"{report['estimated_co2_kg']} kg")
        st.info(report["summary"])

    if data["energy_logs"]:
        st.subheader("Recent readings")
        for row in data["energy_logs"][:10]:
            st.write(
                f"**{row['building_name']}** — {row['consumption_kwh']} kWh · "
                f"{row['usage_level']} ({row['timestamp']})"
            )
    else:
        st.write("No energy data logged yet. Try Live Monitoring first.")
