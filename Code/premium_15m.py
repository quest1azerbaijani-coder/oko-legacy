import time
import requests
import hmac
from hashlib import sha256
import telebot
from datetime import datetime, timezone
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
from pyrogram import Client
from pyrogram.enums.parse_mode import ParseMode

APIURL = "https://open-api.bingx.com"
APIKEY = ""
SECRETKEY = ""

api_id = 
api_hash = 
session_name = 

app = Client(session_name, api_id, api_hash)

def send_bold_message(chat_id, message):
    with app:
        try:
            app.send_message(chat_id, f"**{message}**", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

def get_klines(symbol):
    payload = {}
    path = '/openApi/swap/v3/quote/klines'
    method = "GET"
    paramsMap = {
        "symbol": symbol,
        "interval": "15m",
        "limit": "10"
    }
    paramsStr = parseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload)
    
    return response

def get_sign(api_secret, payload):
    return hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()


def send_request(method, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
    headers = {'X-BX-APIKEY': APIKEY}
    try:
        response = requests.request(method, url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса для {url}: {e}")
        return None
    
def parse_param(params_map):
    sorted_keys = sorted(params_map)
    params_str = "&".join(["%s=%s" % (x, params_map[x]) for x in sorted_keys])
    if params_str != "":
        return params_str + "&timestamp=" + str(int(time.time() * 1000))
    else:
        return params_str + "timestamp=" + str(int(time.time() * 1000))

def parseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    if paramsStr != "":
        return paramsStr + "&timestamp=" + str(int(time.time() * 1000))
    else:
        return paramsStr + "timestamp=" + str(int(time.time() * 1000))

def get_recent_trades(symbol, recv_window=5000):
    payload = {}
    path = '/openApi/swap/v2/quote/trades'
    method = "GET"
    
    current_timestamp = int(time.time() * 1000)
    
    params_map = {
        "symbol": symbol,
        "recvWindow": recv_window
    }
    params_str = parse_param(params_map)
    return send_request(method, path, params_str, payload)

def analyze_trades(symbol):
    recv_window = 300000  
    data = get_recent_trades(symbol, recv_window=recv_window)

    if data is None or 'data' not in data:
        print(f"Ошибка получения данных для {symbol}")
        return None, None

    trades = data['data']
    
    buy_lots = 0
    sell_lots = 0
    total_lots = 0

    for trade in trades:
        qty = float(trade['qty'])
        total_lots += qty
        if trade['isBuyerMaker']:
            sell_lots += qty
        else:
            buy_lots += qty

    if total_lots == 0:
        print(f"Нет данных для анализа по {symbol} за последние 5 минут.")
        return None, None

    buy_ratio = buy_lots / total_lots * 100
    sell_ratio = sell_lots / total_lots * 100

    return round(buy_ratio,2), round(sell_ratio,2)

def analyze_volumes_and_notify(symbol):
    data = get_klines(symbol)

    if data is None or 'code' not in data or data['code'] != 0:
        error_msg = data['msg'] if data else "Неизвестная ошибка"
        print(f"Ошибка получения данных о свечах для {symbol}: {error_msg}")
        return

    kline_data = data.get('data', [])
    if not kline_data:
        print(f"Нет данных для {symbol}")
        return
    
    volumes = [float(kline['volume']) for kline in kline_data]
    avg_volume = sum(volumes[1:]) / 9

    last_volume = volumes[0]
    
    if last_volume > avg_volume * 2:
        buy_ratio,sell_ratio = analyze_trades(symbol)
        high = float(kline_data[0]['high'])
        low = float(kline_data[0]['low'])
        close = float(kline_data[0]['close'])
        open_k = float(kline_data[0]['open'])
        action = "🟢BUY" if close > open_k else "🔴SELL"
        lots = round(last_volume, 2)
        
        if close > open_k:
            price_change = round((high - low)*100/low,2)
        else:
            price_change = round((low - high)*100/high,2)
            
        current_price = float(kline_data[0]['close'])
        current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
        lots_usdt = round(lots*current_price,0)
        new_ratio = 0
        
        if close > open_k:
            if buy_ratio > sell_ratio:
                buy_ratio = buy_ratio
                sell_ratio = sell_ratio
            else:
                new_ratio = buy_ratio
                buy_ratio = sell_ratio
                sell_ratio = new_ratio
        else:
            if buy_ratio < sell_ratio:
                buy_ratio = buy_ratio
                sell_ratio = sell_ratio
            else:
                new_ratio = buy_ratio
                buy_ratio = sell_ratio
                sell_ratio = new_ratio


        if last_volume > avg_volume * 4:
            text = (
                f"${symbol.replace('-','')}\n"
                f"⚫️EXTREMAL VOLUME\n"
                f"{action} {lots} lots ~{lots_usdt} USDT\n"
                f"TIMEFRAME: 15m\n"
                f"Price change: {price_change}%\n"
                f"Buy: {buy_ratio}%\n"
                f"Sell: {sell_ratio}%\n"
                f"Price: {current_price}\n"
                f"Time: {current_time} UTC\n\n"
                f"https://swap.bingx.com/en/{symbol}"
            )
        elif last_volume > avg_volume * 3:
            text = (
                f"${symbol.replace('-','')}\n"
                f"🟣HUGE VOLUME\n"
                f"{action} {lots} lots ~{lots_usdt} USDT\n"
                f"TIMEFRAME: 15m\n"
                f"Price change: {price_change}%\n"
                f"Buy: {buy_ratio}%\n"
                f"Sell: {sell_ratio}%\n"
                f"Price: {current_price}\n"
                f"Time: {current_time} UTC\n\n"
                f"https://swap.bingx.com/en/{symbol}"
            )
        elif last_volume > avg_volume * 2:
            text = (
                f"${symbol.replace('-','')}\n"
                f"🔵LARGE VOLUME\n"
                f"{action} {lots} lots ~{lots_usdt} USDT\n"
                f"TIMEFRAME: 15m\n"
                f"Price change: {price_change}%\n"
                f"Buy: {buy_ratio}%\n"
                f"Sell: {sell_ratio}%\n"
                f"Price: {current_price}\n"
                f"Time: {current_time} UTC\n\n"
                f"https://swap.bingx.com/en/{symbol}"
            )
        
        try:
            target_chat_id = -1002412470325
    
            send_bold_message(target_chat_id, text)
        except Exception as e:
            print(f"Ошибка отправки сообщения в Telegram: {e}")
    else:
        print(f"Объем для {symbol} не превышает порог.\nСредний объем: {avg_volume}\nОбъем последней свечи: {last_volume}")

def get_tickers_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

if __name__ == '__main__':
    tickers = get_tickers_from_file('top_50_symbols.txt')

    while True:
        try:
            for ticker in tickers:
                analyze_volumes_and_notify(ticker)
            time.sleep(1500)
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            time.sleep(60)
