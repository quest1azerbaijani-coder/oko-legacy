BOT_TOKEN = "7908138908:AAHmg6qaUsNW1QFvrQzScU2ucZhbwB4EzYg"

SUBSCRIPTION_END_ALERT = 3 # in days

WORKING_CHANNELS = [-1002412470325] # -1001975205525

WORKING_GROUPS = [-1002412470325] # -821993749

hello_message = "Добро пожаловать, для активации бота введите код полученный от @OKOScanner_ru_bot"

error_key_not_exists_message = "Ошибка, код неверный!"

error_key_already_used_message = "Похоже произошла ошибка"

error_registration_required_message = "Для начала работы нажмите /start"

successful_enrollment_message = "Оплата подтверждена. Для старта введите команду /settings"

alert_settings_message = f'Пожалуйста,выберите нужные алерты'

subscription_ending_alert = "Ваша подписка скоро закончится, желаете продолжить пользоваться ботом?"

invalid_key_alert = "К сожалению вас нет в базе данных"

# ==== override from environment (safe) ====
import os

def _int_list(name, fallback):
    v = os.getenv(name, "")
    if not v:
        return fallback
    try:
        return [int(x.strip()) for x in v.split(",") if x.strip()]
    except Exception:
        return fallback

# На случай если каких-то дефолтов вверху нет — защитимcя
if 'BOT_TOKEN' not in globals(): BOT_TOKEN = None
if 'ADMIN_IDS' not in globals(): ADMIN_IDS = []
if 'CHANNEL_ADMIN_ID' not in globals(): CHANNEL_ADMIN_ID = 0
if 'WORKING_CHANNELS' not in globals(): WORKING_CHANNELS = []
if 'WORKING_GROUPS' not in globals(): WORKING_GROUPS = []
if 'BINGX_API_KEY' not in globals(): BINGX_API_KEY = None
if 'BINGX_SECRET_KEY' not in globals(): BINGX_SECRET_KEY = None
if 'MIN_BALANCE_USDT' not in globals(): MIN_BALANCE_USDT = 0

BOT_TOKEN          = os.getenv("BOT_TOKEN", BOT_TOKEN)
ADMIN_IDS          = _int_list("ADMIN_IDS", ADMIN_IDS)
CHANNEL_ADMIN_ID   = int(os.getenv("CHANNEL_ADMIN_ID", CHANNEL_ADMIN_ID))
WORKING_CHANNELS   = _int_list("WORKING_CHANNELS", WORKING_CHANNELS)
WORKING_GROUPS     = _int_list("WORKING_GROUPS", WORKING_GROUPS)
BINGX_API_KEY      = os.getenv("BINGX_API_KEY", BINGX_API_KEY)
BINGX_SECRET_KEY   = os.getenv("BINGX_SECRET_KEY", BINGX_SECRET_KEY)
MIN_BALANCE_USDT   = int(os.getenv("MIN_BALANCE_USDT", MIN_BALANCE_USDT))
