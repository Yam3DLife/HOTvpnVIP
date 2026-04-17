import json
import base64
import os
from datetime import datetime, timedelta

# ===== ФУНКЦИИ ДЛЯ ЗАГРУЗКИ ФАЙЛОВ =====
def load_json_config(plan):
    """Загружает JSON-конфиг из файла configs/{plan}.json"""
    config_path = f"configs/{plan}.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"⚠️ Файл {config_path} не найден!")
        return None

def load_vless_links(plan):
    """Загружает VLESS-ссылки из файла vless-links/{plan}.txt"""
    links_path = f"vless-links/{plan}.txt"
    if os.path.exists(links_path):
        with open(links_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        print(f"⚠️ Файл {links_path} не найден!")
        return ""

def add_metadata_to_json(json_config, expire_timestamp, total_bytes):
    """Добавляет метаданные о подписке в JSON-конфиг"""
    json_config["subscription-userinfo"] = {
        "upload": 0,
        "download": 0,
        "total": total_bytes,
        "expire": expire_timestamp
    }
    return json_config

def build_combined_subscription(vless_links, json_config, expire_timestamp, total_bytes, plan_name):
    """Собирает комбинированную подписку: заголовки + VLESS + JSON"""
    
    # 1. Заголовки для Happ
    headers = (
        f"#profile-title: HotVPN {plan_name}\n"
        f"#profile-update-interval: 5\n"
        f"#support-url: https://t.me/Wd_Life\n"
        f"#subscription-userinfo: upload=0; download=0; total={total_bytes}; expire={expire_timestamp}\n"
        f"#sub-expire: true\n"
        f"#sub-info-text: 🌐 Комбинированная подписка (VLESS + JSON)\n"
        f"\n"
    )
    
    # 2. VLESS-ссылки
    vless_section = vless_links + "\n\n" if vless_links else ""
    
    # 3. JSON-конфиг
    json_section = json.dumps(json_config, indent=2, ensure_ascii=False)
    
    # 4. Объединяем всё
    combined = headers + vless_section + json_section
    
    # Кодируем в base64
    return base64.b64encode(combined.encode()).decode()

def main():
    os.makedirs('subs', exist_ok=True)
    
    # Читаем пользователей
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    for user_id, user_info in users.items():
        if user_info.get('status') != 'active':
            # Удаляем файл, если пользователь заблокирован
            if os.path.exists(f'subs/{user_id}.txt'):
                os.remove(f'subs/{user_id}.txt')
                print(f"❌ Удалён (заблокирован): {user_id}")
            continue
        
        # Определяем тариф
        plan = user_info.get('plan', 'lite')
        plan_name = plan.upper()
        
        # Загружаем JSON-конфиг для этого тарифа
        json_config = load_json_config(plan)
        if json_config is None:
            print(f"❌ Нет JSON-конфига для тарифа {plan}, пропускаем {user_id}")
            continue
        
        # Загружаем VLESS-ссылки для этого тарифа
        vless_links = load_vless_links(plan)
        
        # Вычисляем срок подписки
        expire_date_str = user_info.get('expire_date')
        if expire_date_str:
            expire_timestamp = int(datetime.strptime(expire_date_str, "%Y-%m-%d").timestamp())
        else:
            if plan == 'trial':
                expire_timestamp = int((datetime.now() + timedelta(days=3)).timestamp())
            else:
                expire_timestamp = 0
        
        # Вычисляем лимит трафика
        traffic_limit_gb = user_info.get('traffic_limit_gb', 50)
        if plan == 'trial' and 'traffic_limit_gb' not in user_info:
            traffic_limit_gb = 5
        total_bytes = traffic_limit_gb * 1073741824
        
        # Добавляем метаданные в JSON
        json_config = add_metadata_to_json(json_config, expire_timestamp, total_bytes)
        
        # Собираем комбинированную подписку
        subscription = build_combined_subscription(vless_links, json_config, expire_timestamp, total_bytes, plan_name)
        
        # Сохраняем
        with open(f'subs/{user_id}.txt', 'w', encoding='utf-8') as f:
            f.write(subscription)
        
        print(f"✅ {user_id}: {plan_name} | JSON: {bool(json_config)} | VLESS: {bool(vless_links)}")

if __name__ == "__main__":
    main()
