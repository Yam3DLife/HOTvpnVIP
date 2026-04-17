import json
import base64
import os
from datetime import datetime, timedelta

# ===== ТАРИФЫ: КЛЮЧ → ФАЙЛ С КЛЮЧАМИ И ОТОБРАЖАЕМОЕ НАЗВАНИЕ =====
TARIFFS = {
    "trial": {
        "keys_file": "keys/trial.txt",
        "display_name": "HotTRIAL 🔥",
        "description": "🔥 Пробный доступ на 3 дня\n📊 5 ГБ трафика\n⚡ Скорость до 50 Мбит/с",
        "default_days": 3,
        "default_traffic_gb": 5
    },
    "lite": {
        "keys_file": "keys/lite.txt",
        "display_name": "HotLITE ⚡",
        "description": "🔥 Самый доступный и недорогой 30 гб/мес",
        "default_days": 30,
        "default_traffic_gb": 30
    },
    "vip": {
        "keys_file": "keys/vip.txt",
        "display_name": "HotVIP 👑",
        "description": "🔥 надёжный и продвинутый 50 гб/мес",
        "default_days": 30,
        "default_traffic_gb": 50
    },
    "ultra": {
        "keys_file": "keys/ultra.txt",
        "display_name": "ULTRAhot 🚀",
        "description": "🔥 полный безлимит на месяц",
        "default_days": 30,
        "default_traffic_gb": 0
    },
    "family": {
        "keys_file": "keys/family.txt",
        "display_name": "FAMILYhot 👨‍👩‍👧‍👦",
        "description": "🔥 На всю семью. Недорого. И всегда с интернетом",
        "default_days": 30,
        "default_traffic_gb": 200
    },
    "premium": {
        "keys_file": "keys/premium.txt",
        "display_name": "PREMIUM Hot 💎",
        "description": "🔥 Премиум доступ на 60 дней\n♾️ Безлимитный трафик",
        "default_days": 60,
        "default_traffic_gb": 0
    },
    "RED": {
        "keys_file": "keys/RED.txt",
        "display_name": "hotRED 🔴",
        "description": "🔥 Сезонный тариф. Недорого. Полный безлимит на месяц",
        "default_days": 30,
        "default_traffic_gb": 0
    },
    "Green": {
        "keys_file": "keys/Green.txt",
        "display_name": "hotGREEN 🟢",
        "description": "🔥 Будь всегда на связи и по выгодной цене. Полный безлимит месяц",
        "default_days": 30,
        "default_traffic_gb": 0
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

def build_subscription(keys, expire_timestamp, total_bytes, display_name, description):
    """Собирает подписку в base64"""
    headers = f"""#profile-title: HotVPN {display_name}
#profile-update-interval: 5
#support-url: https://t.me/Wd_Life
#subscription-userinfo: upload=0; download=0; total={total_bytes}; expire={expire_timestamp}
#sub-expire: true
#sub-info-text: {description}

"""
    combined = headers + keys
    return base64.b64encode(combined.encode()).decode()

def main():
    os.makedirs('subs', exist_ok=True)
    
    # Читаем пользователей
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    needs_save = False
    
    for user_id, user_info in users.items():
        if user_info.get('status') != 'active':
            if os.path.exists(f'subs/{user_id}.txt'):
                os.remove(f'subs/{user_id}.txt')
                print(f"❌ {user_id}: заблокирован, файл удалён")
            continue
        
        tariff = user_info.get('plan', 'lite')
        
        # Проверяем существование тарифа
        if tariff not in TARIFFS:
            print(f"⚠️ {user_id}: тариф '{tariff}' не найден! Использую 'lite'")
            tariff = 'lite'
        
        tariff_config = TARIFFS[tariff]
        display_name = tariff_config["display_name"]
        description = tariff_config.get("description", "")
        
        # ===== ЛОГИКА ДАТЫ (TRIAL НЕ ПРОДЛЕВАЕТСЯ) =====
        expire_date_str = user_info.get('expire_date')
        
        if expire_date_str:
            # Дата уже есть — используем её
            expire_timestamp = int(datetime.strptime(expire_date_str, "%Y-%m-%d").timestamp())
            print(f"📅 {user_id}: существующая дата {expire_date_str}")
        else:
            # Даты нет — создаём из настроек тарифа
            default_days = tariff_config.get("default_days", 30)
            new_expire_date = datetime.now() + timedelta(days=default_days)
            expire_date_str = new_expire_date.strftime("%Y-%m-%d")
            expire_timestamp = int(new_expire_date.timestamp())
            user_info['expire_date'] = expire_date_str
            needs_save = True
            print(f"🎁 {user_id}: {display_name} создан, истекает {expire_date_str}")
        # ================================================
        
        # Лимит трафика: сначала из users.json, потом из настроек тарифа
        traffic_limit_gb = user_info.get('traffic_limit_gb')
        if traffic_limit_gb is None:
            traffic_limit_gb = tariff_config.get("default_traffic_gb", 50)
            user_info['traffic_limit_gb'] = traffic_limit_gb
            needs_save = True
        
        total_bytes = traffic_limit_gb * 1073741824
        
        # Загружаем ключи и собираем подписку
        try:
            keys = load_keys(tariff)
            subscription = build_subscription(keys, expire_timestamp, total_bytes, display_name, description)
            
            with open(f'subs/{user_id}.txt', 'w', encoding='utf-8') as f:
                f.write(subscription)
            
            print(f"✅ {user_id}: {display_name}, истекает: {expire_date_str}, лимит: {traffic_limit_gb} GB")
        except (ValueError, FileNotFoundError) as e:
            print(f"❌ {user_id}: {e}")
    
    # Сохраняем users.json, если добавились новые даты или лимиты
    if needs_save:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        print("💾 users.json обновлён (даты и лимиты сохранены)")

if __name__ == "__main__":
    main()
