import json
import re
from utils.llm import get_llm


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Could not parse JSON from model response.")


def analyze_energy_usage(building_name: str, appliance_breakdown: dict) -> dict:
    """Classifies current energy usage level from a breakdown of appliance
    consumption (in kWh), e.g. {"Air Conditioner": 8, "Lights": 2, "Computers": 5}."""
    llm = get_llm(temperature=0.2)
    breakdown_lines = "\n".join(f"- {k}: {v} kWh" for k, v in appliance_breakdown.items())
    total = sum(appliance_breakdown.values())
    prompt = f"""You are an AI energy monitoring agent for "{building_name}".

Current consumption breakdown:
{breakdown_lines}
Total: {total} kWh

Return ONLY valid JSON in this exact format:
{{
  "usage_level": "Low" | "Medium" | "High",
  "analysis": "1-2 sentence explanation of what is driving current consumption",
  "recommended_action": "1 short sentence on what should happen next"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)


def predict_consumption(building_name: str, recent_daily_kwh: list) -> dict:
    """Predicts tomorrow's electricity consumption from a short history of
    recent daily totals, e.g. [120, 115, 130, 125, 140]."""
    llm = get_llm(temperature=0.4)
    history = ", ".join(f"{v} kWh" for v in recent_daily_kwh)
    prompt = f"""You are an AI energy prediction agent for "{building_name}".

Recent daily consumption history (oldest to newest): {history}

Based on this trend, predict tomorrow's likely consumption.

Return ONLY valid JSON in this exact format:
{{
  "predicted_kwh_tomorrow": <number>,
  "trend": "Rising" | "Falling" | "Stable",
  "reasoning": "1-2 sentence explanation",
  "proactive_recommendation": "1 short sentence on what to adjust in advance"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)
