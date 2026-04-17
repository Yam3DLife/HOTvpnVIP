import json
import base64
import os
from datetime import datetime, timedelta

def load_json_config(plan):
    """Загружает JSON-конфиг из файла configs/{plan}.json"""
    config_path = f"configs/{plan}.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Файл {config_path} не найден!")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_vless_links(plan):
    """Загружает VLESS-ссылки из файла vless-links/{plan}.txt"""
    links_path = f"vless-links/{plan}.txt"
    if not os.path.exists(links_path):
        raise FileNotFoundError(f"❌ Файл {links_path} не найден!")
    with open(links_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def add_metadata_to_json(json_config, expire_timestamp, total_bytes):
    """Добавляет метаданные в JSON"""
    json_config["subscription-userinfo"] = {
        "upload": 0,
        "download": 0,
        "total": total_bytes,
        "expire": expire_timestamp
    }
    return json_config

def build_combined_subscription(vless_links, json_config, expire_timestamp, total_bytes, plan_name):
    """Собирает подписку"""
    headers = f"""#profile-title: HotVPN {plan_name}
#profile-update-interval: 5
#support-url: https://t.me/Wd_Life
#subscription-userinfo: upload=0; download=0; total={total_bytes}; expire={expire_timestamp}
#sub-expire: true

"""
    json_section = json.dumps(json_config, indent=2, ensure_ascii=False)
    combined = headers + vless_links + "\n\n" + json_section
    return base64.b64encode(combined.encode()).decode()

def main():
    # Создаём папку для подписок
    os.makedirs('subs', exist_ok=True)
    
    # Проверяем наличие обязательных папок
    if not os.path.exists('configs'):
        print("❌ Папка 'configs' не найдена! Создайте её и добавьте vip.json, lite.json, trial.json")
        return
    if not os.path.exists('vless-links'):
        print("❌ Папка 'vless-links' не найдена! Создайте её и добавьте vip.txt, lite.txt, trial.txt")
        return
    if not os.path.exists('users.json'):
        print("❌ Файл users.json не найден!")
        return
    
    # Читаем пользователей
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    if not users:
        print("⚠️ Нет пользователей в users.json")
        return
    
    for user_id, user_info in users.items():
        if user_info.get('status') != 'active':
            # Удаляем файл заблокированного
            if os.path.exists(f'subs/{user_id}.txt'):
                os.remove(f'subs/{user_id}.txt')
                print(f"❌ {user_id}: заблокирован, файл удалён")
            continue
        
        plan = user_info.get('plan', 'lite')
        plan_name = plan.upper()
        
        try:
            # Загружаем из файлов
            json_config = load_json_config(plan)
            vless_links = load_vless_links(plan)
        except FileNotFoundError as e:
            print(f"❌ {user_id}: {e}")
            continue
        
        # Срок подписки
        expire_date_str = user_info.get('expire_date')
        if expire_date_str:
            expire_timestamp = int(datetime.strptime(expire_date_str, "%Y-%m-%d").timestamp())
        elif plan == 'trial':
            expire_timestamp = int((datetime.now() + timedelta(days=3)).timestamp())
        else:
            expire_timestamp = 0
        
        # Лимит трафика
        traffic_limit_gb = user_info.get('traffic_limit_gb', 50)
        if plan == 'trial' and 'traffic_limit_gb' not in user_info:
            traffic_limit_gb = 5
        total_bytes = traffic_limit_gb * 1073741824
        
        # Добавляем метаданные и собираем подписку
        json_config = add_metadata_to_json(json_config, expire_timestamp, total_bytes)
        subscription = build_combined_subscription(vless_links, json_config, expire_timestamp, total_bytes, plan_name)
        
        with open(f'subs/{user_id}.txt', 'w', encoding='utf-8') as f:
            f.write(subscription)
        
        print(f"✅ {user_id}: {plan_name} | JSON: configs/{plan}.json | VLESS: vless-links/{plan}.txt")

if __name__ == "__main__":
    main()
