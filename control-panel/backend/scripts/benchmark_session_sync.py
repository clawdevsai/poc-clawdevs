import time
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Mocking parts of the app to avoid dependency issues in benchmark
class MockSession:
    def __init__(self, openclaw_session_id, last_active_at, status="completed"):
        self.openclaw_session_id = openclaw_session_id
        self.last_active_at = last_active_at
        self.status = status
        self.agent_slug = "agent"
        self.openclaw_session_key = "key"
        self.channel_type = "cli"
        self.channel_peer = "peer"
        self.message_count = 10
        self.token_count = 100
        self.ended_at = None

class MockDB:
    def __init__(self, existing_sessions):
        self.existing_sessions = {s.openclaw_session_id: s for s in existing_sessions}
        self.query_count = 0
        self.commit_count = 0

    def exec_single(self, session_id):
        self.query_count += 1
        # Simulate DB latency
        time.sleep(0.001)
        return self.existing_sessions.get(session_id)

    def exec_batch(self, session_ids):
        self.query_count += 1
        time.sleep(0.005) # Slightly more for batch but much less than N * single
        return [self.existing_sessions.get(sid) for sid in session_ids if sid in self.existing_sessions]

    def commit(self):
        self.commit_count += 1

def mock_count_messages(path):
    # Simulate disk I/O
    time.sleep(0.002)
    return 10

def current_logic(agents_data, db):
    start_time = time.time()
    for agent_slug, sessions in agents_data.items():
        for session_key, oc_session in sessions.items():
            session_id = oc_session.get("sessionId")

            # N+1 Query
            existing = db.exec_single(session_id)

            # Always count messages (Disk I/O)
            message_count = mock_count_messages("dummy")

            if existing:
                existing.status = "completed"
                existing.message_count = message_count
            else:
                new_s = MockSession(session_id, datetime.now())
                # ...
    db.commit()
    return time.time() - start_time

def optimized_logic(agents_data, db):
    start_time = time.time()
    all_oc_sessions = {}
    for agent_slug, sessions in agents_data.items():
        for session_key, oc_session in sessions.items():
            session_id = oc_session.get("sessionId")
            if session_id:
                # Last one wins
                all_oc_sessions[session_id] = (agent_slug, session_key, oc_session)

    session_ids = list(all_oc_sessions.keys())

    # Batch query
    existing_list = db.exec_batch(session_ids)
    existing_map = {s.openclaw_session_id: s for s in existing_list if s}

    for session_id, (agent_slug, session_key, oc_session) in all_oc_sessions.items():
        existing = existing_map.get(session_id)

        oc_updated_at = datetime.fromtimestamp(oc_session.get("updatedAt") / 1000)

        # Smart skip
        needs_full_update = False
        if not existing:
            needs_full_update = True
        elif existing.last_active_at < oc_updated_at:
            needs_full_update = True

        if needs_full_update:
            message_count = mock_count_messages("dummy")
            # Update existing or create new
        else:
            # Maybe just update status if timed out, but skip disk I/O
            pass

    db.commit()
    return time.time() - start_time

def run_benchmark():
    num_agents = 5
    sessions_per_agent = 20
    total_sessions = num_agents * sessions_per_agent

    agents_data = {}
    existing_sessions = []

    now = datetime.now()
    old_ts = (now - timedelta(days=1)).timestamp() * 1000

    for i in range(num_agents):
        agent_slug = f"agent_{i}"
        sessions = {}
        for j in range(sessions_per_agent):
            sid = f"sid_{i}_{j}"
            sessions[f"key_{j}"] = {"sessionId": sid, "updatedAt": old_ts}
            existing_sessions.append(MockSession(sid, datetime.fromtimestamp(old_ts/1000)))
        agents_data[agent_slug] = sessions

    print(f"--- Benchmark with {total_sessions} sessions (all unchanged) ---")

    db_current = MockDB(existing_sessions)
    t_current = current_logic(agents_data, db_current)
    print(f"Current Logic:   {t_current:.4f}s, Queries: {db_current.query_count}")

    db_opt = MockDB(existing_sessions)
    t_opt = optimized_logic(agents_data, db_opt)
    print(f"Optimized Logic: {t_opt:.4f}s, Queries: {db_opt.query_count}")
    print(f"Speedup: {t_current/t_opt:.2f}x")

if __name__ == "__main__":
    run_benchmark()
