from typing import TypedDict, Optional, Any, Dict
from langgraph.graph import StateGraph, END

from agents.monitor_agent import analyze_energy_usage, predict_consumption
from agents.optimization_agent import detect_wastage, recommend_optimization
from agents.appliance_agent import analyze_appliance_efficiency
from agents.peak_load_agent import manage_peak_load
from agents.analytics_agent import generate_report


class EnergyState(TypedDict):
    intent: str
    payload: Dict[str, Any]
    result: Optional[Any]


def route_intent(state: EnergyState) -> EnergyState:
    # The Streamlit UI already decides intent via tabs (monitor / optimize /
    # appliance / peak_load / analytics). This node exists so you can later
    # swap in an LLM-based intent classifier here for free-text/voice routing
    # without changing the rest of the graph.
    return state


def monitor_node(state: EnergyState) -> EnergyState:
    p = state["payload"]
    usage = analyze_energy_usage(p["building_name"], p["appliance_breakdown"])
    prediction = predict_consumption(p["building_name"], p["recent_daily_kwh"])
    state["result"] = {"usage": usage, "prediction": prediction}
    return state


def optimize_node(state: EnergyState) -> EnergyState:
    p = state["payload"]
    wastage = detect_wastage(
        p["building_name"], p["area"], p["appliance_state"], p["occupancy"]
    )
    recommendation = recommend_optimization(p["building_name"], p["usage_summary"])
    state["result"] = {"wastage": wastage, "recommendation": recommendation}
    return state


def appliance_node(state: EnergyState) -> EnergyState:
    p = state["payload"]
    state["result"] = analyze_appliance_efficiency(
        p["appliance_name"], p["consumption_kwh"], p["rated_kwh"], p.get("age_years", 0)
    )
    return state


def peak_load_node(state: EnergyState) -> EnergyState:
    p = state["payload"]
    state["result"] = manage_peak_load(
        p["building_name"], p["current_hour"], p.get("flexible_loads", "")
    )
    return state


def analytics_node(state: EnergyState) -> EnergyState:
    p = state["payload"]
    state["result"] = generate_report(p["energy_logs"], p["wastage_alerts"])
    return state


def build_graph():
    graph = StateGraph(EnergyState)
    graph.add_node("router", route_intent)
    graph.add_node("monitor", monitor_node)
    graph.add_node("optimize", optimize_node)
    graph.add_node("appliance", appliance_node)
    graph.add_node("peak_load", peak_load_node)
    graph.add_node("analytics", analytics_node)

    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {
            "monitor": "monitor",
            "optimize": "optimize",
            "appliance": "appliance",
            "peak_load": "peak_load",
            "analytics": "analytics",
        },
    )
    graph.add_edge("monitor", END)
    graph.add_edge("optimize", END)
    graph.add_edge("appliance", END)
    graph.add_edge("peak_load", END)
    graph.add_edge("analytics", END)

    return graph.compile()


energy_graph = build_graph()


def run_agent(intent: str, payload: Dict[str, Any]):
    result_state = energy_graph.invoke({"intent": intent, "payload": payload, "result": None})
    return result_state["result"]
