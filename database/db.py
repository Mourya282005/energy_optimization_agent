import sqlite3
from contextlib import contextmanager

DB_PATH = "energy_agent.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS energy_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_name TEXT,
                consumption_kwh REAL,
                usage_level TEXT,
                analysis TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wastage_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_name TEXT,
                area TEXT,
                issue TEXT,
                recommendation TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appliance_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance_name TEXT,
                consumption_kwh REAL,
                rated_kwh REAL,
                status TEXT,
                recommendation TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS peak_load_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_name TEXT,
                current_hour TEXT,
                is_peak INTEGER,
                action_taken TEXT,
                estimated_savings_kwh REAL,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)


def ensure_building(name: str):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO buildings (name) VALUES (?)", (name,))


def log_energy(building_name, consumption_kwh, usage_level, analysis):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO energy_logs (building_name, consumption_kwh, usage_level, analysis) "
            "VALUES (?, ?, ?, ?)",
            (building_name, consumption_kwh, usage_level, analysis),
        )


def save_wastage_alert(building_name, area, issue, recommendation):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO wastage_alerts (building_name, area, issue, recommendation) "
            "VALUES (?, ?, ?, ?)",
            (building_name, area, issue, recommendation),
        )


def save_appliance_check(appliance_name, consumption_kwh, rated_kwh, status, recommendation):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO appliance_checks (appliance_name, consumption_kwh, rated_kwh, "
            "status, recommendation) VALUES (?, ?, ?, ?, ?)",
            (appliance_name, consumption_kwh, rated_kwh, status, recommendation),
        )


def save_peak_load_action(building_name, current_hour, is_peak, action_taken, estimated_savings_kwh):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO peak_load_actions (building_name, current_hour, is_peak, "
            "action_taken, estimated_savings_kwh) VALUES (?, ?, ?, ?, ?)",
            (building_name, current_hour, int(is_peak), action_taken, estimated_savings_kwh),
        )


def get_dashboard_data():
    with get_conn() as conn:
        energy_logs = conn.execute(
            "SELECT * FROM energy_logs ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()
        wastage = conn.execute(
            "SELECT * FROM wastage_alerts ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()
        appliances = conn.execute(
            "SELECT * FROM appliance_checks ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()
        peak_actions = conn.execute(
            "SELECT * FROM peak_load_actions ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()
        return {
            "energy_logs": [dict(r) for r in energy_logs],
            "wastage": [dict(r) for r in wastage],
            "appliances": [dict(r) for r in appliances],
            "peak_actions": [dict(r) for r in peak_actions],
        }
