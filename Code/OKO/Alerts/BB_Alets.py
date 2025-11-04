import json
import asyncio
import websockets
import aiohttp
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta

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

session = HTTP(testnet=True)
data = session.get_instruments_info(category="linear")

symbols = [symbol['symbol'] for symbol in data['result']['list']]

async def consumer_handler(websocket, symbols):
    async for message in websocket:
        parsed_message = json.loads(message)
        if 'topic' in parsed_message:
            symbol = parsed_message['topic'].split('.')[-1]
            coin_name_form = f'`{symbol}`'
            data = parsed_message['data'][0]
            delta = round((float(data['high']) - float(data['low'])) * 100 / float(data['close']), 2)
            
            last_alert_time = alert_timers.get(symbol, None)
            current_time = datetime.now()
            
            if last_alert_time is None or current_time - last_alert_time >= timedelta(minutes=3):
                if delta > 2:
                    signal = f'🔥BYBIT {coin_name_form}\nДельта: {delta}%'
                    await send_telegram_message(signal)
                    alert_timers[symbol] = current_time
        else:
            print(f"Unexpected message: {message}")

async def main():
    url = "wss://stream.bybit.com/v5/public/linear"
    args = [f"kline.1.{symbol}" for symbol in symbols]
    sub_request = json.dumps({
        "op": "subscribe",
        "args": args
    })

    async with websockets.connect(url) as websocket:
        await websocket.send(sub_request)
        await consumer_handler(websocket, symbols)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
