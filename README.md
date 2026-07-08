# Energy Optimization Agent (Phase 1 MVP)

AI-powered smart energy management system built with Python, LangChain, LangGraph, GROQ,
Streamlit, and SQLite. Contributes to **SDG 13 – Climate Action** by reducing electricity
consumption, cutting costs, and lowering carbon emissions.

## Features included (Phase 1)
1. **AI Energy Monitoring** — classifies current usage level from appliance/department breakdown
2. **Consumption Prediction** — forecasts tomorrow's usage from recent daily history
3. **Smart Energy Optimization** — detects wastage (e.g. lights/AC on with no occupancy) and
   recommends prioritized savings actions
4. **Appliance Efficiency Analysis** — flags appliances consuming more than their rated load
5. **Peak Load Management** — detects peak-demand windows and recommends shifting flexible loads
6. **Energy Analytics** — total consumption, estimated cost, estimated CO2 emissions, AI summary

## Project structure
```
energy_optimization_agent/
├── app.py                     # Streamlit dashboard (entry point)
├── requirements.txt
├── .env.example
├── database/
│   └── db.py                   # SQLite: energy logs, wastage alerts, appliance checks, peak actions
├── agents/
│   ├── monitor_agent.py         # Usage analysis + consumption prediction
│   ├── optimization_agent.py    # Wastage detection + optimization recommendations
│   ├── appliance_agent.py       # Appliance efficiency analysis
│   ├── peak_load_agent.py       # Peak demand detection + load shifting
│   └── analytics_agent.py       # Reports: cost/CO2 estimates, summaries
└── graph/
    └── workflow.py              # LangGraph router connecting the agents
```

## Setup in VS Code

### 1. Get a free GROQ API key
Sign up at https://console.groq.com and create an API key under "API Keys".

### 2. Open the project folder
In VS Code: File → Open Folder → select `energy_optimization_agent`.

### 3. Create a virtual environment
Open the VS Code terminal (`` Ctrl+` ``) and run:

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

VS Code may prompt "Select Interpreter" — choose the one inside `venv`.

### 4. Install dependencies
```
pip install -r requirements.txt
```

### 5. Add your API key
Copy `.env.example` to a new file named `.env`, then paste your key:
```
GROQ_API_KEY=gsk_your_actual_key_here
```
`.env` should never be committed to GitHub — it's already in `.gitignore`.

### 6. Run the app
```
streamlit run app.py
```
This opens the dashboard in your browser at `http://localhost:8501`.

## How it works
- Enter a **building/site name** in the sidebar — this is what's currently being managed.
- **Live Monitoring** tab → enter appliance-level consumption (kWh), get an AI usage
  classification + a next-day prediction based on recent history; logs get saved for analytics.
- **Optimization** tab → describe an area's appliance state and occupancy to flag wastage,
  then get a prioritized list of energy-saving actions with an estimated savings percentage.
- **Appliance Efficiency** tab → compare an appliance's actual vs. rated consumption to catch
  units that may need servicing or replacement.
- **Peak Load** tab → checks whether the current hour falls in the peak-demand window
  (6 PM–9 PM by default) and recommends shifting flexible loads if so.
- **Analytics** tab → aggregates logged data into total kWh, estimated cost, estimated CO2
  emissions, plus an AI-written summary for facility managers.

## Data source note (Phase 1 vs. real deployment)
This MVP uses **manually entered consumption values** (kWh) as a stand-in for live smart-meter
feeds, and the AI reasons over that data to make decisions. This keeps the system fully
runnable with no hardware. The cost-per-kWh and CO2-per-kWh figures in `analytics_agent.py`
are placeholder constants — swap them for your local utility tariff and grid emissions factor.

## Next steps (Phase 2 ideas from the concept note)
- **Renewable Energy Integration**: add fields for solar/battery output and let the
  optimization agent prefer renewable sources during peak windows before recommending load
  shifting.
- **Smart Alerts and Notifications**: add a notifications table + a lightweight API
  (FastAPI) that a mobile app or email/SMS service can poll for wastage and peak-demand alerts.
- **Smart meter integration**: replace manual kWh entry with real feeds from IoT smart
  meters — the agents already expect the same `appliance_breakdown` / `consumption_kwh`
  inputs, so only the data-collection layer needs to change.
- **Free-text/voice routing**: the `graph/workflow.py` router node already has a comment
  marking where to add an LLM-based intent classifier for non-tab-based input.
- **Multi-building comparison**: extend analytics to compare consumption and savings across
  multiple buildings/sites side by side.

## Troubleshooting
- **`GROQ_API_KEY not found`** → check your `.env` file exists in the project root and
  has no quotes around the key.
- **`ModuleNotFoundError`** → make sure your venv is activated (you should see `(venv)`
  in the terminal prompt) and you ran `pip install -r requirements.txt` inside it.
- **JSON parsing errors from an agent** → the model occasionally wraps JSON in extra
  text; the parsing helpers already strip common cases, but if it persists, lower
  `temperature` in the relevant agent file or retry.
