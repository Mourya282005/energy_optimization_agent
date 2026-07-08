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


PEAK_WINDOW = "6 PM - 9 PM"


def manage_peak_load(building_name: str, current_hour: str, flexible_loads: str) -> dict:
    """Decides whether the current hour falls in a peak-demand window and, if
    so, recommends shifting flexible/non-essential loads to reduce cost and grid strain."""
    llm = get_llm(temperature=0.3)
    prompt = f"""You are an AI peak-load management agent for "{building_name}".

Current hour: {current_hour}
Typical peak demand window: {PEAK_WINDOW}
Flexible/non-essential loads available to shift: {flexible_loads or "none specified"}

Decide if this is a peak period and what action (if any) to take.

Return ONLY valid JSON in this exact format:
{{
  "is_peak_period": true | false,
  "action_taken": "1 short sentence describing the load-shifting action (or 'No action needed')",
  "estimated_savings_kwh": <number>,
  "reasoning": "1-2 sentence explanation"
}}"""
    response = llm.invoke(prompt)
    return _extract_json(response.content)
