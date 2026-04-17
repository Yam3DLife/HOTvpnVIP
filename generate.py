import json
import base64
import os
from datetime import datetime, timedelta

def load_keys(tariff):
    """Загружает VLESS/VMess ссылки из файла keys/{tariff}.txt"""
    path = f"keys/{tariff}.txt"
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Файл {path} не найден!")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def build_subscription(keys, expire_timestamp, total_bytes, tariff_name):
    """Собирает подписку: заголовки + ключи в base64"""
    
    headers = f"""#profile-title: HotVPN {tariff_name}
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
    
    needs_save = False
    
    for user_id, user_info in users.items():
        if user_info.get('status') != 'active':
            if os.path.exists(f'subs/{user_id}.txt'):
                os.remove(f'subs/{user_id}.txt')
                print(f"❌ {user_id}: заблокирован, файл удалён")
            continue
        
        tariff = user_info.get('plan', 'lite')
        tariff_name = tariff.upper()
        
        # ===== ЛОГИКА ДАТЫ (TRIAL НЕ ПРОДЛЕВАЕТСЯ) =====
        expire_date_str = user_info.get('expire_date')
        
        if expire_date_str:
            # Дата уже есть — используем её (не пересоздаём!)
            expire_timestamp = int(datetime.strptime(expire_date_str, "%Y-%m-%d").timestamp())
            print(f"📅 {user_id}: существующая дата {expire_date_str}")
        else:
            # Даты нет — создаём один раз
            if tariff == 'trial':
                new_expire_date = datetime.now() + timedelta(days=3)
                expire_date_str = new_expire_date.strftime("%Y-%m-%d")
                expire_timestamp = int(new_expire_date.timestamp())
                user_info['expire_date'] = expire_date_str
                needs_save = True
                print(f"🎁 {user_id}: ТРИАЛ создан, истекает {expire_date_str} (больше не продлится)")
            else:
                # Для платных подписок без даты — безлимит (0 = никогда)
                expire_timestamp = 0
                print(f"📅 {user_id}: безлимит (дата не указана)")
        # ================================================
        
        # Лимит трафика
        traffic_limit_gb = user_info.get('traffic_limit_gb', 50)
        if tariff == 'trial' and 'traffic_limit_gb' not in user_info:
            traffic_limit_gb = 5
        total_bytes = traffic_limit_gb * 1073741824
        
        # Загружаем ключи и собираем подписку
        try:
            keys = load_keys(tariff)
            subscription = build_subscription(keys, expire_timestamp, total_bytes, tariff_name)
            
            with open(f'subs/{user_id}.txt', 'w', encoding='utf-8') as f:
                f.write(subscription)
            
            print(f"✅ {user_id}: {tariff_name}, истекает: {expire_date_str or 'никогда'}, лимит: {traffic_limit_gb} GB")
        except FileNotFoundError as e:
            print(f"❌ {user_id}: {e}")
    
    # Сохраняем users.json, если добавились новые даты для триалов
    if needs_save:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        print("💾 users.json обновлён (даты триалов сохранены)")

if __name__ == "__main__":
    main()
