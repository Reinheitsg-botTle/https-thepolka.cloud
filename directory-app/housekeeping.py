"""Run once a day from a scheduler to prove the Housekeeping Agent is alive."""
from app import init_db, record_housekeeping_heartbeat


if __name__ == "__main__":
    init_db()
    record_housekeeping_heartbeat()
    print("Housekeeping Agent daily heartbeat recorded.")
