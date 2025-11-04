import json
import asyncio
import websockets
import aiohttp
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta

# Открытие файла и считывание данных построчно
with open('BYBIT.txt', 'r') as f:
    symbols = [line.strip() for line in f.readlines()]

# Вывод результата
print("Symbols:", symbols)

# Ваш Telegram Bot токен и ID чата
TELEGRAM_TOKEN = "6281593343:AAGTATyH-WtYX8WvnqieSgEgJHJVKCOFnsM"
CHAT_ID = "-1001916655401"

alert_timers = {}

async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)

print(len(symbols))

async def consumer_handler(websocket, symbols):
    async for message in websocket:
        parsed_message = json.loads(message)
        #print(parsed_message)
        if 'topic' in parsed_message:
            symbol = parsed_message['topic'].split('.')[-1]
            coin_name_form = f'`{symbol}`'
            data = parsed_message['data'][0]
            delta = round((float(data['high']) - float(data['low'])) * 100 / float(data['close']), 2)
            
            last_alert_time = alert_timers.get(symbol, None)
            current_time = datetime.now()
            
            if last_alert_time is None or current_time - last_alert_time >= timedelta(minutes=3):
                if delta > 2:
                    signal = f'🔥BYBIT SPOT {coin_name_form}\nДельта: {delta}%'
                    await send_telegram_message(signal)
                    alert_timers[symbol] = current_time
        else:
            print(f"Unexpected message: {message}")

async def manage_websocket_connection(sub_symbols, url):
    try:
        args = [f"kline.1.{symbol}" for symbol in sub_symbols]
        sub_request = json.dumps({
            "op": "subscribe",
            "args": args
        })

        async with websockets.connect(url) as websocket:
            await websocket.send(sub_request)
            await consumer_handler(websocket, sub_symbols)
    except websockets.exceptions.ConnectionClosedError:
        print("Connection was closed unexpectedly. Trying to reconnect...")
        await manage_websocket_connection(sub_symbols, url)  # This will recursively try to reconnect.


async def main():
    url = "wss://stream.bybit.com/v5/public/spot"
    tasks = []

    # Разделение списка символов на части по 10 элементов и создание асинхронных тасков
    for i in range(0, len(symbols), 10):
        sub_symbols = symbols[i:i + 10]
        task = asyncio.create_task(manage_websocket_connection(sub_symbols, url))
        tasks.append(task)

    # Ожидание завершения всех тасков
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
