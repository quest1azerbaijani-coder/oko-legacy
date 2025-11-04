import json
import time
import requests
import hmac
from hashlib import sha256
import telebot

API_TOKEN = '7886023626:AAGH0zVUNnQqKcD9GNaMaPmRTOuC1_JslH4'
bot = telebot.TeleBot(API_TOKEN)

APIURL = "https://open-api.bingx.com"
APIKEY = "1lKQO6gJHlI1IqFuQIzEaDXFmkYOG8qimslhN8rCJAENRDSqtMdKQepFfdwr9htQGfEs5w1mydrrCzg"
SECRETKEY = "Ze9a44Dl3TDxYJZcB8QTeqS5b7zGsxGmSZpXNtdDdOeKei2mgy2skhty02R4mh2D6BuU8pRxJmTTYriWpg"

USERS_FILE = 'users.json'

def get_registered_uids():
    def demo():
        payload = {}
        path = '/openApi/agent/v1/account/inviteAccountList'
        method = "GET"
        paramsMap = {
            "pageIndex": "1",
            "pageSize": "100"
        }
        paramsStr = parseParam(paramsMap)
        return send_request(method, path, paramsStr, payload)

    def get_sign(api_secret, payload):
        signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature

    def send_request(method, path, urlpa, payload):
        url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
        headers = {
            'X-BX-APIKEY': APIKEY,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        return response.text

    def parseParam(paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        if paramsStr != "":
            return paramsStr + "&timestamp=" + str(int(time.time() * 1000))
        else:
            return paramsStr + "timestamp=" + str(int(time.time() * 1000))

    response = demo()
    data = json.loads(response)
    users = data['data']['list']
    uids = {user['uid']: [] for user in users}
    return uids

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = '''
🔥*KondrashovTrade*-это канал с *авторскими идеями* на рынке криптовалют, *разборами ситуации на рынке, идеями по долгосрочным инвестициям* на рынке криптовалют, а также *обучающими материалами*, которые помогут лучше разбираться в торговле

🚀*Мой 4 летний опыт торговли, уникальными идеями и авторским видением-все это ты можешь получить абсолютно бесплатно*, став моим рефералом на бирже *BingX* - одной из самых крупных и удобных бирж в мире

🎁Зарегестрировавшись по моей реферальной ссылке ты получишь *сниженные комиссии на торговлю на 20%*, а также много других бонусов, например сделав это до конца года ты получишь *ваучер на 40$*

*Помним, что идеи не являются гарантиями прибыли, и отвественность за сделки каждый несет сам, не является ИИС*

📝*Инструкция по использованию BingX:* https://telegra.ph/Instrukciya-po-polzovaniyu-birzhej-BingX-dlya-telefona-11-23

 *🔧Команды бота:* 
/check - Проверить статус
/help - Поддержка

*Присоединяйся, и торгуй вместе с лучшими!*
    '''
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = '''
*Контакты:*
🤝 *Создатель:* @kondrashovvlad
📧 *Поддержка:* @OKOScannerSupport
    '''
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['check'])
def check_status(message):
    msg = bot.reply_to(message, "*Введите ваш UID:*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_uid)

def process_uid(message):
    user_uid = message.text
    registered_uids = get_registered_uids()
    users = load_users()

    if int(user_uid) in registered_uids:
        bot.reply_to(message, "*Поздравляем! Вы зарегистрированы*", parse_mode="Markdown")
        
        user_id = message.from_user.id
        if user_uid not in users:
            users[user_uid] = []
        users[user_uid].append(user_id)
        save_users(users)

        chat_link = "https://t.me/+tRKKV_OszoY2ZTNi"
        bot.send_message(user_id, f"*Для подключения перейдите по следующей ссылке:* [перейти по ссылке]({chat_link})", parse_mode="Markdown")


    else:
        bot.reply_to(message, "*Регистрация по реферальной ссылке или KYC не пройдены. Пожалуйста, завершите процесс.*", parse_mode="Markdown")

if __name__ == '__main__':
    bot.polling(none_stop=True)
