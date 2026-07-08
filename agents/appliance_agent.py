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


def analyze_appliance_efficiency(appliance_name: str, consumption_kwh: float,
                                  rated_kwh: float, age_years: float = 0) -> dict:
    """Compares actual consumption against rated/expected consumption to flag
    appliances that may need maintenance or replacement."""
    llm = get_llm(temperature=0.2)
    variance_pct = round(((consumption_kwh - rated_kwh) / rated_kwh) * 100, 1) if rated_kwh else 0
    prompt = f"""You are an AI appliance-efficiency agent.

Appliance: {appliance_name}
Actual consumption: {consumption_kwh} kWh
Rated/expected consumption: {rated_kwh} kWh
Variance from rated: {variance_pct}%
Approximate age: {age_years} years

Return ONLY valid JSON in this exact format:
{{
  "status": "Efficient" | "Slightly Inefficient" | "Needs Attention",
  "recommendation": "1-2 sentence recommendation (e.g. servicing, replacement, no action needed)"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)
