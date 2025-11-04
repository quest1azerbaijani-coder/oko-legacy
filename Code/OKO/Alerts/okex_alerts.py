import json
import asyncio
import websockets
from aiogram import Bot, Dispatcher
from datetime import datetime, timedelta

TOKEN = '5826228849:AAHZSOKtRonqaWOWnbdHQN8ZGO4k-MxkcA8'
CHAT_ID = '-1001916655401'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

alert_timers = {}  # Словарь для отслеживания времени последнего алерта

async def read_instruments_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

async def generate_websocket_request(instruments, channel="candle1m"):
    args = [{"channel": channel, "instId": inst} for inst in instruments]
    request = {
        "op": "subscribe",
        "args": args
    }
    return request

async def send_telegram_message(message):
    await bot.send_message(CHAT_ID, message, parse_mode="Markdown")

async def main():
    file_path = 'okx.txt'
    instruments = await read_instruments_from_file(file_path)
    request = await generate_websocket_request(instruments, channel="candle1m")
    
    while True:
        try:
            async with websockets.connect('wss://ws.okx.com:8443/ws/v5/business') as websocket:
                await websocket.send(json.dumps(request))
                async for message in websocket:
                    data = json.loads(message)
                    if 'data' in data: 
                        symbol = data['arg']['instId']
                        coin_name_form = f'`{symbol}`'
                        delta = round((float(data['data'][0][2]) - float(data['data'][0][3]))*100/float(data['data'][0][2]), 2)
                        
                        if delta > 2:
                            now = datetime.utcnow()
                            
                            # Если символ еще не в словаре или последний алерт был более 3 минут назад
                            if symbol not in alert_timers or now - alert_timers[symbol] > timedelta(minutes=3):
                                signal = f'⚡️OKX FUT {coin_name_form}\nДельта: {delta}%'
                                await send_telegram_message(signal)
                                alert_timers[symbol] = now
                            
        except websockets.exceptions.ConnectionClosedError:
            print("Соединение было прервано. Попробуем снова через 10 секунд.")
            await asyncio.sleep(10)

asyncio.run(main())


