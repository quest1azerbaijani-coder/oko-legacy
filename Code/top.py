import time
import requests
import hmac
from hashlib import sha256
import json
from datetime import datetime, timedelta

APIURL = "https://open-api.bingx.com"
APIKEY = "g3PaesoH9qeHvHoF1L2qrARbhJrc2DbSFgZWRXOKtBlNny7GtIBlXTcIrV6jbtuKN0F7RnBZad16E00Se1w"
SECRETKEY = "cOuEXXiK9Y7yGQvP3odW8YwivoNPU52dbi3OZDcCLVWfAmXmDG3oPOCopX5TANpI5sYCl4L67TTXTXq1jvwMA"

def demo():
    try:
        payload = {}
        path = '/openApi/swap/v2/quote/ticker'
        method = "GET"
        paramsMap = {
            "timestamp": "1728845500000"
        }
        paramsStr = parseParam(paramsMap)
        return send_request(method, path, paramsStr, payload)
    except Exception as e:
        print(f"Ошибка в функции demo: {e}")
        return None

def get_sign(api_secret, payload):
    try:
        signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    except Exception as e:
        print(f"Ошибка при генерации подписи: {e}")
        return None

def send_request(method, path, urlpa, payload):
    try:
        url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
        headers = {
            'X-BX-APIKEY': APIKEY,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        response.raise_for_status()  # выбросит исключение при ошибке HTTP
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

def parseParam(paramsMap):
    try:
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        if paramsStr != "": 
            return paramsStr+"&timestamp="+str(int(time.time() * 1000))
        else:
            return paramsStr+"timestamp="+str(int(time.time() * 1000))
    except Exception as e:
        print(f"Ошибка в функции parseParam: {e}")
        return ""

def run_script():
    try:
        data = demo()
        if data is None:
            print("Данные не получены.")
            return

        data = json.loads(data)
        data_symbols = data['data']
        symbols_volume = []
        for symbol in data_symbols:
            symbols_volume += [[symbol['symbol'], symbol['quoteVolume']]]

        # Сортировка по второму элементу (преобразуем строки в числа и сортируем по убыванию)
        sorted_data = sorted(symbols_volume, key=lambda x: float(x[1]), reverse=True)

        # Извлекаем первые 50 элементов и оставляем только первый параметр
        top_50_symbols = [item[0] for item in sorted_data[:50]]

        # Запись в текстовый файл построчно
        with open('top_50_symbols.txt', 'w') as file:
            for symbol in top_50_symbols:
                file.write(symbol + '\n')

        print("Данные успешно записаны в файл top_50_symbols.txt")
    except Exception as e:
        print(f"Ошибка в процессе выполнения: {e}")

if __name__ == '__main__':
    while True:
        # Получение текущего времени
        current_time = datetime.utcnow()

        # Проверка на полночь по UTC
        if current_time.hour == 17 and current_time.minute == 10:
            run_script()

            # Ждем 24 часа, чтобы повторить скрипт снова в полночь
            time.sleep(900)
        else:
            # Ждем одну минуту, прежде чем снова проверить время
            time.sleep(60)
