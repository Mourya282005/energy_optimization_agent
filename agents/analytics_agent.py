from utils.llm import get_llm

CO2_KG_PER_KWH = 0.71  # rough grid-average emissions factor; tune per region
COST_PER_KWH = 8.0     # placeholder currency-per-kWh rate; tune per region/currency


def _estimate_impact(energy_logs: list, wastage_alerts: list) -> dict:
    """Deterministic back-of-envelope estimates from logged energy data.
    These are simplified placeholders — swap in real tariff/emissions data
    once smart-meter integration is available (see README Phase 2 notes)."""
    if not energy_logs:
        return {
            "total_kwh_logged": 0,
            "avg_kwh_per_reading": 0,
            "wastage_events": len(wastage_alerts),
            "estimated_cost": 0,
            "estimated_co2_kg": 0,
        }

    total_kwh = sum(row["consumption_kwh"] for row in energy_logs)
    avg_kwh = round(total_kwh / len(energy_logs), 2)
    estimated_cost = round(total_kwh * COST_PER_KWH, 2)
    estimated_co2 = round(total_kwh * CO2_KG_PER_KWH, 2)

    return {
        "total_kwh_logged": round(total_kwh, 2),
        "avg_kwh_per_reading": avg_kwh,
        "wastage_events": len(wastage_alerts),
        "estimated_cost": estimated_cost,
        "estimated_co2_kg": estimated_co2,
    }


def generate_report(energy_logs: list, wastage_alerts: list) -> dict:
    """Combines deterministic metrics with an LLM-written narrative summary
    for the building/facility dashboard."""
    metrics = _estimate_impact(energy_logs, wastage_alerts)

    if not energy_logs:
        return {
            **metrics,
            "summary": "No energy data logged yet. Run some Live Monitoring checks "
                       "to start building analytics.",
        }

    llm = get_llm(temperature=0.4)
    recent = energy_logs[:10]
    log_summary = "\n".join(
        f"- {row['building_name']}: {row['consumption_kwh']} kWh, level={row['usage_level']}"
        for row in recent
    )
    prompt = f"""You are an AI energy analytics agent writing a short report for a
facility manager.

Recent logged readings:
{log_summary}

Summary metrics:
- Total logged consumption: {metrics['total_kwh_logged']} kWh
- Average per reading: {metrics['avg_kwh_per_reading']} kWh
- Wastage events flagged: {metrics['wastage_events']}
- Estimated cost: {metrics['estimated_cost']}
- Estimated CO2 emissions: {metrics['estimated_co2_kg']} kg

Write a concise 3-4 sentence summary covering: overall energy health, any area(s)
needing attention, and one concrete recommendation for reducing consumption and
emissions. Keep it under 100 words."""
    response = llm.invoke(prompt)

    return {**metrics, "summary": response.content}
