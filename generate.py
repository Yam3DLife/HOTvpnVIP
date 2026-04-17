import json
import base64
import os
from datetime import datetime

# ===== ТАРИФЫ: КЛЮЧ → ФАЙЛ С КЛЮЧАМИ И ОТОБРАЖАЕМОЕ НАЗВАНИЕ =====
TARIFFS = {
    "trial": {
        "keys_file": "keys/trial.txt",
        "display_name": "HotTRIAL 🔥",
        "description": "🔥 Пробный доступ на 3 дня\n📊 5 ГБ трафика\n⚡ Скорость до 50 Мбит/с"
    },
    "lite": {
        "keys_file": "keys/lite.txt",
        "display_name": "HotLITE ⚡",
        "description": "🔥 Самый доступный и недорогой 30 гб/мес"
    },
    "vip": {
        "keys_file": "keys/vip.txt",
        "display_name": "HotVIP 👑",
        "description": "🔥 надёжный и продвинутый 50 гб/мес"
    },
    "ultra": {
        "keys_file": "keys/vip.tx",
        "display_name": "ULTRAhot 🚀",
        "description": "🔥 полный безлимит на месяц"
    },
    "family": {
        "keys_file": "keys/vip.tx",
        "display_name": "FAMILYhot 👨‍👩‍👧‍👦",
        "description": "🔥 На всю семью. Недорого. И всегда с интернетом"
    },
    "premium": {
        "keys_file": "keys/vip.tx",
        "display_name": "PREMIUM Hot 💎",
        "description": "🔥 Пробный доступ на 3 дня\n📊 5 ГБ трафика\n⚡ Скорость до 50 Мбит/с"
    },
    "RED": {
        "keys_file": "keys/vip.tx",
        "display_name": "hotRED🔴",
        "description": "🔥 Сезонный тариф. Недорого. Полный безлимит на месяц"
    },
    "Green": {
        "keys_file": "keys/vip.txt",
        "display_name": "hotGREEN🟢",
        "description": "🔥 Будь всегда на связи и по выгодной цене. Полный безлимит месяц"
    }
}
# ============================================================

def load_keys(tariff):
    """Загружает ключи из файла, указанного в настройках тарифа"""
    if tariff not in TARIFFS:
        raise ValueError(f"❌ Тариф '{tariff}' не найден в TARIFFS!")
    
    path = TARIFFS[tariff]["keys_file"]
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Файл {path} не найден!")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def build_subscription(keys, expire_timestamp, total_bytes, display_name):
    """Собирает подписку в base64"""
    headers = f"""#profile-title: HotVPN {display_name}
#profile-update-interval: 5
#support-url: https://t.me/Wd_Life
#subscription-userinfo: upload=0; download=0; total={total_bytes}; expire={expire_timestamp}
#sub-expire: true

"""
    combined = headers + keys
    return base64.b64encode(combined.encode()).decode()

def main():
    os.makedirs('subs', exist_ok=True)
    
    # Читаем пользователей
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
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
        
        # Данные из users.json (ты указываешь сам)
        expire_date_str = user_info.get('expire_date')
        if expire_date_str:
            expire_timestamp = int(datetime.strptime(expire_date_str, "%Y-%m-%d").timestamp())
        else:
            expire_timestamp = 0  # 0 = безлимит по времени
        
        traffic_limit_gb = user_info.get('traffic_limit_gb', 50)
        total_bytes = traffic_limit_gb * 1073741824
        
        # Загружаем ключи и собираем подписку
        try:
            keys = load_keys(tariff)
            subscription = build_subscription(keys, expire_timestamp, total_bytes, display_name)
            
            with open(f'subs/{user_id}.txt', 'w', encoding='utf-8') as f:
                f.write(subscription)
            
            print(f"✅ {user_id}: {display_name}, истекает: {expire_date_str or 'никогда'}, лимит: {traffic_limit_gb} GB")
        except (ValueError, FileNotFoundError) as e:
            print(f"❌ {user_id}: {e}")

if __name__ == "__main__":
    main()
