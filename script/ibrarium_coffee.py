import time
from datetime import datetime


def start_coffee_machine():
    print("[COFFEE] Machine à café en cours de démarrage...")
    # Ici vous pouvez placer le code réel pour activer la machine (via GPIO, API, etc.)
    time.sleep(2)
    print("[COFFEE] Café prêt ! ☕")


def run(minutes_from_now: int = 0, scheduled_time: str = None):
    """
    Main callable function used by the general Telegram bot.

    Args:
        minutes_from_now (int): delay in minutes before running the machine
        scheduled_time (str): optional format "HH:MM" for scheduling
    """
    if scheduled_time:
        now = datetime.now()
        target = datetime.strptime(scheduled_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if target < now:
            target = target.replace(day=now.day + 1)
        delta = (target - now).total_seconds()
        print(f"[COFFEE] Programmation du café à {scheduled_time}...")
        time.sleep(delta)
    elif minutes_from_now:
        print(f"[COFFEE] Café dans {minutes_from_now} minutes...")
        time.sleep(minutes_from_now * 60)
    else:
        print("[COFFEE] Démarrage immédiat...")

    start_coffee_machine()


if __name__ == "__main__":
    run()
