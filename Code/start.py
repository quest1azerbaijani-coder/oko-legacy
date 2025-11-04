# Code/OKO/start.py
import threading
from server import run as run_server
from aiogram import executor
from bot import dp

if __name__ == "__main__":
    # HTTP keep-alive сервер поднимем в потоке
    threading.Thread(target=run_server, daemon=True).start()
    # Aiogram-пуллинг
    executor.start_polling(dp, skip_updates=True)
