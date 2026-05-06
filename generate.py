import json
import os

def main():
    os.makedirs('subs', exist_ok=True)
    
    # Тестовый JSON
    test_data = {"test": "working", "status": "ok"}
    
    with open('subs/test.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    print("✅ test.json создан")

if __name__ == "__main__":
    main()
