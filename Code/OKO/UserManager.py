import sqlite3
from time import time
from config import *

cursor = None
connection = None

def begin():
    try:
        global cursor, connection
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        print("DB connected")

        cursor.execute("select sqlite_version();")
        record = cursor.fetchall()
        print("DB version: ", record)

        query = '''CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        subscription REAL NOT NULL,
        alerts TEXT NOT NULL,
        used_keys TEXT NOT NULL);'''
        try:
            cursor.execute(query)
        except:
            pass

    except sqlite3.Error as error:
        print("DB error", error)

def enroll(uid, key, long):
    cursor.execute("SELECT used_keys FROM users WHERE id = ?", (uid,))
    record = cursor.fetchall()
    if(key in str(record)):
        return False
    
    set_membership(uid, long*86400)

    cursor.execute("UPDATE users SET used_keys = used_keys || ? WHERE id = ?", (" "+key,uid))
    connection.commit()

    return True

def set_alert_configuration(uid, new_config):
    """
    Устанавливает новую конфигурацию алертов для пользователя.
    :param uid: ID пользователя
    :param new_config: Новая конфигурация в виде строки (например, "111101001111")
    """
    cursor.execute("UPDATE users SET alerts = ? WHERE id = ?", (new_config, uid))
    connection.commit()
    
def set_membership(uid, long):
    from AlertManager import get_alerts  # Lazy import to avoid circular dependency

    names, _ = get_alerts()  # Получаем доступные алерты
    alerts_count = len(names)

    if not has_user(uid):
        # Создаем строку с включенными алертами
        default_alerts = "1" * alerts_count
        cursor.execute(
            "INSERT INTO users (id, subscription, alerts, used_keys) VALUES (?,?,?,?)",
            (uid, time() + long, default_alerts, "")
        )
    else:
        cursor.execute("UPDATE users SET subscription = ? WHERE id = ?", (time() + long, uid))

    connection.commit()

def is_key(key):
    with open('keys.txt') as file:
        for k, long in map(lambda k: k.strip().split() ,file.readlines()):
            if(key==k):
                return long
    return False

def get_alerts(uid):
    from AlertManager import get_alerts  # Lazy import to avoid circular dependency

    # Получаем текущую конфигурацию alerts из базы данных
    cursor.execute("SELECT alerts FROM users WHERE id = ?", (uid,))
    record = cursor.fetchall()

    if not record:
        return []

    current_alerts = list(map(int, list(record[0][0])))

    # Получаем количество доступных алертов
    names, _ = get_alerts()
    alerts_count = len(names)

    # Приводим конфигурацию пользователя к нужной длине
    if len(current_alerts) < alerts_count:
        current_alerts += [0] * (alerts_count - len(current_alerts))  # Дополняем 0
    elif len(current_alerts) > alerts_count:
        current_alerts = current_alerts[:alerts_count]  # Обрезаем

    return current_alerts

def set_alert(uid, id, new_state):
    state = get_alerts(uid)
    state[id] = int(new_state)
    cursor.execute("UPDATE users SET alerts = ? WHERE id = ?", ("".join(map(str,state)),uid))
    connection.commit()

def has_user(uid):
    cursor.execute("SELECT id FROM users WHERE id = ?", (uid,))
    has_user = cursor.fetchall()
    return len(has_user)>0

def get_users_by_alert(alert_type):
    cursor.execute("SELECT id, alerts, subscription FROM users")
    record = cursor.fetchall()
    return [id for id, alerts, subscr in record if alerts[alert_type]=="1" and subscr>time()]

def get_ending_members(period):
    cursor.execute("SELECT id, subscription FROM users")
    record = cursor.fetchall()
    return [id for id, subscr in record if subscr-time()<=period*86400]

def get_all_members():
    cursor.execute("SELECT id, subscription subscription FROM users")
    record = cursor.fetchall()
    return [id for id, subscr in record if subscr>time()]

def get_active_key(uid):
    cursor.execute("SELECT used_keys FROM users WHERE id = ?", (uid,))
    record = cursor.fetchall()
    return record[0][0].split()[-1]

def get_users_with_invalid_keys():
    cursor.execute("SELECT id FROM users")
    record = cursor.fetchall()
    return [uid for uid, in record if not is_key(get_active_key(uid))]