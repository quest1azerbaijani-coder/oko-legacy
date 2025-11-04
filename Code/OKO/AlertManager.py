import UserManager

def get_message_configuration(text):
    _, sigs = get_alerts()  # Получаем сигнатуры из alerts.txt
    configuration = "".join(["1" if sig in text else "0" for sig in sigs])
    return configuration

def get_members(text):
    from UserManager import get_all_members, get_alerts  # Ленивый импорт для разрыва цикла

    message_config = get_message_configuration(text)  # Конфигурация сообщения
    users = get_all_members()  # Получаем всех пользователей с активной подпиской

    matching_users = []
    for user_id in users:
        # Конфигурация пользователя (например, "111101111111")
        user_config = "".join(map(str, get_alerts(user_id)))
        
        # Проверяем, что все `1` в message_config совпадают с `1` в user_config
        match = all(
            user_bit == '1' or msg_bit == '0'
            for msg_bit, user_bit in zip(message_config, user_config)
        )
        
        if match:
            matching_users.append(user_id)
        
        print(f"Конфигурация сообщения: {message_config}")
        print(f"Конфигурация пользователя {user_id}: {user_config}")

    print(f"Сообщение отправляется следующим пользователям: {matching_users}")
    return matching_users

def get_alerts():
    names = []
    sigs = []
    with open("alerts.txt", encoding="utf-8") as file:
        for line in file.readlines():
            name, sig = line.strip().split("|")
            names.append(name.strip())
            sigs.append(sig.strip())
    return names, sigs

def get_message_type(text):
    names, sigs = get_alerts()

    for n, sig in enumerate(sigs):
        if sig in text:
            return n
    
    return -1