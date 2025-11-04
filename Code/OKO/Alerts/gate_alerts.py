import json
import time
import threading
from websocket import create_connection, WebSocketConnectionClosedException
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, executor
import asyncio

TOKEN = '6436042859:AAG_r8yuT8kyIcOfkscCn8j_edBJ-fty4P0'
CHAT_ID = '-1001916655401'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
loop = asyncio.SelectorEventLoop()
asyncio.set_event_loop(loop)
alert_timers = {}

thread_limiter = threading.Semaphore(3)  # Создайте семафор

def subscribe_to_candlesticks(ws, contract_name):
    request_payload = {
        "time": int(time.time()),
        "channel": "futures.candlesticks",
        "event": "subscribe",
        "payload": ["1m", contract_name]
    }
    ws.send(json.dumps(request_payload))

async def send_telegram_message(message):
    await bot.send_message(CHAT_ID, message, parse_mode="Markdown")

def reconnect(ws, contract_name):
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            ws = create_connection("wss://fx-ws.gateio.ws/v4/ws/usdt")
            subscribe_to_candlesticks(ws, contract_name)
            return ws
        except:
            time.sleep(10)
            continue
    raise Exception(f"Failed to reconnect after {max_attempts} attempts.")

def listen_for_updates(ws, contract_name):
    try:
        while True:
            try:
                response = ws.recv()
            except WebSocketConnectionClosedException:
                print(f"Connection for {contract_name} was lost. Trying to reconnect...")
                ws = reconnect(ws, contract_name)
                continue

            data = json.loads(response)
            print(contract_name, data)
            if data["event"] == "update" and "result" in data:
                for candlestick in data["result"]:
                    high = float(candlestick['h'])
                    low = float(candlestick['l'])
                    open_price = float(candlestick['o'])
                    close_price = float(candlestick['c'])
                    volume = float(candlestick['v'])
                    avg_price = (open_price + close_price) / 2
                    
                    usdt_volume = volume * avg_price
                    usdt_volume_in_thousands = usdt_volume / 1000
                    delta = ((high - low) / high) * 100
                    print(contract_name,' ', delta, ' ', usdt_volume_in_thousands)
                    if delta > 0.2:
                        now = datetime.utcnow()
                        if contract_name not in alert_timers or now - alert_timers[contract_name] > timedelta(minutes=3):
                            alert_message = f"💥️GateIO FUT `{contract_name}`\nДельта: {delta:.2f}%\nОбъем: {usdt_volume_in_thousands:.2f}K USDT"
                            asyncio.run(send_telegram_message(alert_message))
                            alert_timers[contract_name] = now
    except Exception as e:
        print(f"Error for {contract_name}: {e}")
    finally:
        ws.close()
        thread_limiter.release()  # Освободите семафор


if __name__ == "__main__":
    with open('gate.txt', 'r') as f:
        instruments = f.readlines()

    threads = []

    for instrument in instruments:
        instrument = instrument.strip()
        ws = create_connection("wss://fx-ws.gateio.ws/v4/ws/usdt")
        subscribe_to_candlesticks(ws, instrument)

        thread_limiter.acquire()  # Ожидайте, пока не освободится место
        t = threading.Thread(target=listen_for_updates, args=(ws, instrument))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
