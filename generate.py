import json
import base64
import os
from datetime import datetime, timedelta

# ===== ТАРИФЫ: КЛЮЧ → ФАЙЛ С КЛЮЧАМИ И ОТОБРАЖАЕМОЕ НАЗВАНИЕ =====
TARIFFS = {
    "trial": {
        "keys_file": "keys/trial.txt",
        "display_name": "TRIAL 🔥",
        "description": "🔥 Пробный доступ на 3 дня\n📊 5 ГБ трафика\n⚡ Скорость до 50 Мбит/с",
        "default_days": 3,
        "default_traffic_gb": 5,
        "is_json": False
    },
    "lite": {
        "keys_file": "keys/lite.txt",
        "display_name": "LITE ⚡",
        "description": "🔥 Самый доступный и недорогой 30 гб/мес",
        "default_days": 30,
        "default_traffic_gb": 30,
        "is_json": False
    },
    "vip": {
        "keys_file": "keys/vip.txt",
        "display_name": "VIP 👑",
        "description": "🔥 надёжный и продвинутый 50 гб/мес",
        "default_days": 30,
        "default_traffic_gb": 50,
        "is_json": False
    },
    "ultra": {
        "keys_file": "keys/vip.txt",
        "display_name": "ULTRA 🚀",
        "description": "🔥 полный безлимит на месяц",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False
    },
    "family": {
        "keys_file": "keys/vip.txt",
        "display_name": "FAMILY 👨‍👩‍👧‍👦",
        "description": "🔥 На всю семью. Недорого. И всегда с интернетом",
        "default_days": 30,
        "default_traffic_gb": 200,
        "is_json": False
    },
    "premium": {
        "keys_file": "keys/vip.txt",
        "display_name": "PREMIUM 💎",
        "description": "🔥 Премиум доступ на 60 дней\n♾️ Безлимитный трафик",
        "default_days": 60,
        "default_traffic_gb": 0,
        "is_json": False
    },
    "RED": {
        "keys_file": "keys/vip.txt",
        "display_name": "RED 🔴",
        "description": "🔥 Сезонный тариф. Недорого. Полный безлимит на месяц",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False
    },
    "Green": {
        "keys_file": "keys/vip.txt",
        "display_name": "GREEN 🟢",
        "description": "🔥 Будь всегда на связи и по выгодной цене. Полный безлимит месяц",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False
    },
    "Super": {
        "keys_file": "keys/vip.txt",
        "display_name": "Super 🟢",
        "description": "🔥 Будь всегда на связи. Полный безлимит месяц",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": False
    },
    # ===== НОВЫЙ JSON-ТАРИФ REDsUmmer =====
    "json_RED": {
        "keys_file": "configs/advanced.json",
        "display_name": "REDsUmmer 🔴☀️",
        "description": "🔥 Летний безлимит\n♾️ Полный безлимит трафика\n🌍 Серверы: Лондон + Обход\n⚡ Скорость до 1 Гбит/с",
        "default_days": 30,
        "default_traffic_gb": 0,
        "is_json": True
    }
}
# ============================================================

def load_keys(tariff):
    """Загружает ключи из файла, указанного в настройках тарифа"""
    if tariff not in TARIFFS:
        raise ValueError(f"❌ Тариф '{tariff}' не найден в TARIFFS!")
    
    path = TARIFFS[tariff]["keys_file"]
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Файл {path} не найден! Создай его и добавь ключи.")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_json_config(tariff):
    """Загружает JSON-конфигурацию из файла"""
    if tariff not in TARIFFS:
        raise ValueError(f"❌ Тариф '{tariff}' не найден в TARIFFS!")
    
    path = TARIFFS[tariff]["keys_file"]
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ JSON файл {path} не найден!")
    
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
    """Добавляет метаданные в JSON-конфиг и возвращает его в виде строки"""
    # Добавляем метаданные в JSON
    json_config["subscription-userinfo"] = {
        "upload": 0,
        "download": 0,
        "total": total_bytes,
        "expire": expire_timestamp
    }
    # Добавляем название профиля и описание
    json_config["profile-title"] = f"HotVPN {display_name}"
    json_config["profile-update-interval"] = 5
    json_config["support-url"] = "https://t.me/Wd_Life"
    json_config["sub-expire"] = True
    json_config["announce"] = description
    
    return json.dumps(json_config, indent=2, ensure_ascii=False)

def main():
    os.makedirs('subs', exist_ok=True)
    
    # Читаем пользователей
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    needs_save = False
    
    for user_id, user_info in users.items():
        if user_info.get('status') != 'active':
            # Удаляем оба возможных формата файлов
            if os.path.exists(f'subs/{user_id}.txt'):
                os.remove(f'subs/{user_id}.txt')
            if os.path.exists(f'subs/{user_id}.json'):
                os.remove(f'subs/{user_id}.json')
            print(f"❌ {user_id}: заблокирован, файлы удалены")
            continue
        
        tariff = user_info.get('plan', 'lite')
        
        # Проверяем существование тарифа
        if tariff not in TARIFFS:
            print(f"⚠️ {user_id}: тариф '{tariff}' не найден! Использую 'lite'")
            tariff = 'lite'
        
        tariff_config = TARIFFS[tariff]
        display_name = tariff_config["display_name"]
        description = tariff_config.get("description", "")
        is_json = tariff_config.get("is_json", False)
        
        # ===== ЛОГИКА ДАТЫ =====
        expire_date_str = user_info.get('expire_date')
        
        if expire_date_str:
            expire_timestamp = int(datetime.strptime(expire_date_str, "%Y-%m-%d").timestamp())
            print(f"📅 {user_id}: существующая дата {expire_date_str}")
        else:
            default_days = tariff_config.get("default_days", 30)
            new_expire_date = datetime.now() + timedelta(days=default_days)
            expire_date_str = new_expire_date.strftime("%Y-%m-%d")
            expire_timestamp = int(new_expire_date.timestamp())
            user_info['expire_date'] = expire_date_str
            needs_save = True
            print(f"🎁 {user_id}: {display_name} создан, истекает {expire_date_str}")
        
        # Лимит трафика
        traffic_limit_gb = user_info.get('traffic_limit_gb')
        if traffic_limit_gb is None:
            traffic_limit_gb = tariff_config.get("default_traffic_gb", 50)
            user_info['traffic_limit_gb'] = traffic_limit_gb
            needs_save = True
        
        total_bytes = traffic_limit_gb * 1073741824
        
        # ===== ОБРАБОТКА JSON ИЛИ ОБЫЧНОЙ ПОДПИСКИ =====
        try:
            if is_json:
                # JSON-подписка
                json_config = load_json_config(tariff)
                subscription = build_json_subscription(json_config, expire_timestamp, total_bytes, display_name, description)
                
                with open(f'subs/{user_id}.json', 'w', encoding='utf-8') as f:
                    f.write(subscription)
                
                print(f"✅ {user_id}: {display_name} (JSON), истекает: {expire_date_str}, лимит: {traffic_limit_gb} GB")
            else:
                # Обычная TXT-подписка
                keys = load_keys(tariff)
                subscription = build_subscription(keys, expire_timestamp, total_bytes, display_name, description)
                
                with open(f'subs/{user_id}.txt', 'w', encoding='utf-8') as f:
                    f.write(subscription)
                
                print(f"✅ {user_id}: {display_name} (TXT), истекает: {expire_date_str}, лимит: {traffic_limit_gb} GB")
        except (ValueError, FileNotFoundError) as e:
            print(f"❌ {user_id}: {e}")
    
    # Сохраняем users.json, если добавились новые даты или лимиты
    if needs_save:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        print("💾 users.json обновлён (даты и лимиты сохранены)")

if __name__ == "__main__":
    main()
