# ----- ENV override (не ломает дефолты ниже) -----
import os as _os

_BOT_TOKEN = _os.getenv("BOT_TOKEN")
_WORKING_CHANNELS = _os.getenv("WORKING_CHANNELS")   # формат: -1001,-1002
_WORKING_GROUPS = _os.getenv("WORKING_GROUPS")       # формат: -1001,-1002
_CHANNEL_ADMIN_ID = _os.getenv("CHANNEL_ADMIN_ID")
_ADMIN_IDS = _os.getenv("ADMIN_IDS")                 # формат: 630089739,1344488824

# ниже идут твои исходные константы config.py...

# а после их объявления — мягко переопределим из ENV, если заданы
try: BOT_TOKEN = _BOT_TOKEN or BOT_TOKEN
except NameError: BOT_TOKEN = _BOT_TOKEN or ""

def _to_int_list(v):
    if not v: return None
    return [int(x.strip()) for x in v.split(",") if x.strip()]

try:
    WORKING_CHANNELS = _to_int_list(_WORKING_CHANNELS) or WORKING_CHANNELS
except NameError:
    WORKING_CHANNELS = _to_int_list(_WORKING_CHANNELS) or []

try:
    WORKING_GROUPS = _to_int_list(_WORKING_GROUPS) or WORKING_GROUPS
except NameError:
    WORKING_GROUPS = _to_int_list(_WORKING_GROUPS) or []

try:
    CHANNEL_ADMIN = int(_CHANNEL_ADMIN_ID) if _CHANNEL_ADMIN_ID else CHANNEL_ADMIN
except NameError:
    CHANNEL_ADMIN = int(_CHANNEL_ADMIN_ID) if _CHANNEL_ADMIN_ID else None

# необязательный список админов (если в твоей логике есть проверки)
if _ADMIN_IDS:
    try:
        ADMIN_IDS = _to_int_list(_ADMIN_IDS) or ADMIN_IDS  # если у тебя такая переменная уже есть
    except NameError:
        ADMIN_IDS = _to_int_list(_ADMIN_IDS)
# ----- /ENV override -----
