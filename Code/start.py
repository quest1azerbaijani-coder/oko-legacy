# в самом начале main/start.py вашего OKO
import os, sys
try:
    import fcntl
    lock_path = "/var/lock/oko-bot.lock"
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    lock_fd = open(lock_path, "w")
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except Exception as e:
    print(f"[LOCK] Уже запущен или нет доступа к lock-файлу: {e}")
    sys.exit(1)
