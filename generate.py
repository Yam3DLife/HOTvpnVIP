import json
import base64
import os
import sys
from datetime import datetime, timedelta

# ===== ТАРИФЫ: КЛЮЧ → ФАЙЛ С КЛЮЧАМИ И ОТОБРАЖАЕМОЕ НАЗВАНИЕ =====
TARIFFS = {
    "trial": {
        "keys_file": "keys/trial.txt",
        "display_name": "TRIAL 🔥",
        "description": "Пробный доступ на 3 дней, 5 ГБ трафика, скорость до 50 Мбит/с",
        "default_days": 3,
        "default_traffic_gb": 5,
        "is_json": False,
        "raw_copy": False
    },
    "lite": {
        "keys_file": "keys/lite.txt",
        "display_name": "LITE ⚡",
        "description": "Самый доступный и недорогой 30 ГБ/мес",
        "default_days": 30,
        "default_traffic_gb": 30,
        "is_json": False,
        "raw_copy": False
    },
    "vip": {
        "keys_file": "keys/vip.txt",
        "display_name": "VIP 👑",
        "description": "Надёжный и продвинутый 50 ГБ/мес",
        "default_days": 30,
        "default_traffic_gb": 50,
        "is_json": False,
        "raw_copy": False
    },
    "ultra": {
        "keys_file": "keys/vip.txt",
        "display_name": "ULTRA 🚀",
        "description": "Полный безлимит на месяц",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False,
        "raw_copy": False
    },
    "family": {
        "keys_file": "keys/vip.txt",
        "display_name": "FAMILY 👨‍👩‍👧‍👦",
        "description": "На всю семью. Недорого. И всегда с интернетом",
        "default_days": 30,
        "default_traffic_gb": 200,
        "is_json": False,
        "raw_copy": False
    },
    "premium": {
        "keys_file": "keys/vip.txt",
        "display_name": "PREMIUM 💎",
        "description": "Премиум доступ на 60 дней, безлимитный трафик",
        "default_days": 60,
        "default_traffic_gb": 0,
        "is_json": False,
        "raw_copy": False
    },
    "RED": {
        "keys_file": "keys/vip.txt",
        "display_name": "RED 🔴",
        "description": "Сезонный тариф. Недорого. Полный безлимит на месяц",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False,
        "raw_copy": False
    },
    "Green": {
        "keys_file": "keys/vip.txt",
        "display_name": "GREEN 🟢",
        "description": "Будь всегда на связи и по выгодной цене. Полный безлимит месяц",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False,
        "raw_copy": False
    },
    "Super": {
        "keys_file": "keys/vip.txt",
        "display_name": "SUPER ⭐",
        "description": "Будь всегда на связи. Полный безлимит месяц",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False,
        "raw_copy": False
    },
    "json_RED": {
        "keys_file": "keys/red_summer.txt",
        "display_name": "REDsUmmer 🔴",
        "description": "Летний безлимит, полный безлимит трафика, серверы: Лондон + Обход, скорость до 1 Гбит/с",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": True,
        "raw_copy": False
    },
    "RED_SUMMER": {
        "keys_file": "keys/red_summer.txt",
        "display_name": "REDsUmmer 🔴",
        "description": "🔥 Летний безлимит\n♾️ Полный безлимит трафика\n🌍 Германия + Нидерланды + Эстония\n⚡ Скорость до 1 Гбит/с",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False,
        "raw_copy": True
    }
}
# ============================================================

def load_keys(tariff):
    """Загружает ключи из файла, указанного в настройках тарифа"""
    if tariff not in TARIFFS:
        raise ValueError(f"Тариф '{tariff}' не найден в TARIFFS!")
    
    path = TARIFFS[tariff]["keys_file"]
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл {path} не найден! Создайте его и добавьте ключи.")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_json_config(tariff):
    """Загружает JSON-конфигурацию из файла"""
    if tariff not in TARIFFS:
        raise ValueError(f"Тариф '{tariff}' не найден в TARIFFS!")
    
    path = TARIFFS[tariff]["keys_file"]
    print(f"Загрузка JSON из: {path}")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON файл {path} не найден!")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_subscription(keys, expire_timestamp, total_bytes, display_name, description):
    """Собирает подписку в base64 с использованием официального параметра #announce"""
    headers = f"""#profile-title: HotVPN {display_name}
#profile-update-interval: 5
#support-url: https://t.me/Wd_Life
#subscription-userinfo: upload=0; download=0; total={total_bytes}; expire={expire_timestamp}
#sub-expire: true
#announce: {description}

"""
    combined = headers + keys
    return base64.b64encode(combined.encode()).decode()

def build_json_subscription(json_config, expire_timestamp, total_bytes, display_name, description):
    """
    Создаёт JSON-подписку в формате, понятном Happ.
    Если json_config — массив, оставляет как есть.
    Если json_config — объект с outbounds, преобразует в массив.
    """
    # Определяем тип JSON
    if isinstance(json_config, list):
        # Уже массив серверов — оставляем
        servers = json_config
    elif isinstance(json_config, dict):
        # Объект — пытаемся извлечь массив из outbounds
        if "outbounds" in json_config and isinstance(json_config["outbounds"], list):
            servers = json_config["outbounds"]
        else:
            servers = [json_config]
    else:
        servers = []
    
    # Добавляем метаданные в JSON (только для отображения в Happ)
    user_info = f"upload=0; download=0; total={total_bytes}; expire={expire_timestamp}"
    
    # Формируем текстовые заголовки (Happ читает их из любого файла)
    headers = f"""#profile-title: HotVPN {display_name}
#profile-update-interval: 5
#support-url: https://t.me/Wd_Life
#subscription-userinfo: {user_info}
#sub-expire: true
#announce: {description}

"""
    # Собираем финальную подписку: заголовки + JSON (без кодирования в base64)
    json_part = json.dumps(servers, indent=2, ensure_ascii=False)
    combined = headers + json_part
    
    # Happ понимает как base64, так и plain text, но для совместимости кодируем
    return base64.b64encode(combined.encode()).decode()

def main():
    os.makedirs('subs', exist_ok=True)
    
    # Читаем пользователей
    users_json_path = 'users.json'
    if not os.path.exists(users_json_path):
        print(f"Файл {users_json_path} не найден!")
        sys.exit(1)
    
    with open(users_json_path, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    needs_save = False
    print(f"Обработка {len(users)} пользователей...")
    
    for user_id, user_info in users.items():
        if user_info.get('status') != 'active':
            # Удаляем оба возможных формата файлов
            for ext in ['.txt', '.json']:
                file_path = f'subs/{user_id}{ext}'
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Удалён файл: {file_path}")
            continue
        
        tariff = user_info.get('plan', 'lite')
        print(f"Обработка {user_id}: тариф={tariff}")
        
        # Проверяем существование тарифа
        if tariff not in TARIFFS:
            print(f"⚠️ {user_id}: тариф '{tariff}' не найден! Использую 'lite'")
            tariff = 'lite'
        
        tariff_config = TARIFFS[tariff]
        display_name = tariff_config["display_name"]
        description = tariff_config.get("description", "")
        is_json = tariff_config.get("is_json", False)
        raw_copy = tariff_config.get("raw_copy", False)
        
        # ===== ЛОГИКА ДАТЫ =====
        expire_date_str = user_info.get('expire_date')
        
        if expire_date_str:
            expire_timestamp = int(datetime.strptime(expire_date_str, "%Y-%m-%d").timestamp())
            print(f"  Дата: {expire_date_str}")
        else:
            default_days = tariff_config.get("default_days", 30)
            new_expire_date = datetime.now() + timedelta(days=default_days)
            expire_date_str = new_expire_date.strftime("%Y-%m-%d")
            expire_timestamp = int(new_expire_date.timestamp())
            user_info['expire_date'] = expire_date_str
            needs_save = True
            print(f"  Новая дата: {expire_date_str}")
        
        # Лимит трафика
        traffic_limit_gb = user_info.get('traffic_limit_gb')
        if traffic_limit_gb is None:
            traffic_limit_gb = tariff_config.get("default_traffic_gb", 50)
            user_info['traffic_limit_gb'] = traffic_limit_gb
            needs_save = True
        
        total_bytes = traffic_limit_gb * 1073741824
        
        # ===== ОБРАБОТКА JSON ИЛИ ОБЫЧНОЙ ПОДПИСКИ =====
        try:
            if raw_copy:
                # Режим прямого копирования (без изменений, без base64)
                with open(tariff_config["keys_file"], 'r', encoding='utf-8') as src:
                    content = src.read()
                output_path = f'subs/{user_id}.txt'
                with open(output_path, 'w', encoding='utf-8') as dst:
                    dst.write(content)
                print(f"✅ {user_id}: {display_name} (RAW COPY) создан, истекает: {expire_date_str}, лимит: {traffic_limit_gb} GB")
                print(f"   Файл: {output_path}")
            elif is_json:
                # JSON-подписка
                json_config = load_json_config(tariff)
                subscription = build_json_subscription(json_config, expire_timestamp, total_bytes, display_name, description)
                
                output_path = f'subs/{user_id}.json'
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(subscription)
                
                print(f"✅ {user_id}: {display_name} (JSON) создан, истекает: {expire_date_str}, лимит: {traffic_limit_gb} GB")
                print(f"   Файл: {output_path}")
            else:
                # Обычная TXT-подписка
                keys = load_keys(tariff)
                subscription = build_subscription(keys, expire_timestamp, total_bytes, display_name, description)
                
                output_path = f'subs/{user_id}.txt'
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(subscription)
                
                print(f"✅ {user_id}: {display_name} (TXT) создан, истекает: {expire_date_str}, лимит: {traffic_limit_gb} GB")
                print(f"   Файл: {output_path}")
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ {user_id}: Ошибка - {e}")
    
    # Сохраняем users.json, если добавились новые даты или лимиты
    if needs_save:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        print("users.json обновлён (даты и лимиты сохранены)")

if __name__ == "__main__":
    main()
