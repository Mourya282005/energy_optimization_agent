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


def detect_wastage(building_name: str, area: str, appliance_state: str, occupancy: str) -> dict:
    """Flags likely energy wastage, e.g. lights/AC running with no occupancy."""
    llm = get_llm(temperature=0.2)
    prompt = f"""You are an AI energy-wastage detection agent for "{building_name}".

Area: {area}
Appliance state: {appliance_state}
Occupancy status: {occupancy}

Return ONLY valid JSON in this exact format:
{{
  "wastage_detected": true | false,
  "issue": "1 short sentence describing the wastage (or 'None' if not detected)",
  "recommendation": "1 short sentence on the corrective action"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)


def recommend_optimization(building_name: str, usage_summary: str) -> dict:
    """Produces a prioritized list of energy-saving actions given a free-text
    summary of current usage (from the monitoring agent or dashboard data)."""
    llm = get_llm(temperature=0.4)
    prompt = f"""You are an AI energy optimization agent for "{building_name}".

Current usage summary: {usage_summary}

Suggest 3-5 concrete, prioritized energy-saving actions (e.g. turning off idle
appliances, adjusting thermostat setpoints, shifting heavy loads off-peak,
scheduling maintenance).

Return ONLY valid JSON in this exact format:
{{
  "recommendations": ["action 1", "action 2", "action 3"],
  "estimated_savings_percent": <number>,
  "summary": "1-2 sentence overview of the optimization opportunity"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)
