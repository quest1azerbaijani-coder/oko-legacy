import threading, time
from server import run as run_server

# Поднимаем keepalive HTTP в фоне
threading.Thread(target=run_server, daemon=True).start()

# Импорт бота: у большинства aiogram-проектов запуск идёт при импорте/в блоке __main__
# Если у тебя в bot.py запуск через executor.start_polling(...) в нижней части файла,
# обычный import достаточно, он его вызовет.
import bot  # не удалять

# Чтобы процесс не завершался, если bot.py работает не блокирующе
while True:
    time.sleep(3600)
