import requests
import os

# --- НАСТРОЙКИ TELEGRAM ---
TELEGRAM_TOKEN = "8847922404:AAFIsHxn6QDgfF6ZqWdPNZC7_Jm5sZZLcII"
TELEGRAM_CHAT_ID = "444451877"
# --------------------------

COINS = ["bitcoin", "ethereum", "solana"]
COIN_NAMES = {"bitcoin": "Bitcoin", "ethereum": "Ethereum", "solana": "Solana"}

# 1. Запрос к API CoinGecko с добавлением заголовков
url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    "ids": ",".join(COINS),
    "vs_currencies": "usd,rub",
    "include_24hr_change": "true"
}

# КРИТИЧЕСКИ ВАЖНО: CoinGecko блокирует запросы без User-Agent
headers = {
    "accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    print("⏳ Запрос данных из CoinGecko...")
    response = requests.get(url, params=params, headers=headers, timeout=15)
    
    # Если CoinGecko вернул ошибку 429 (Too Many Requests), мы сразу поймем это
    response.raise_for_status()
    data = response.json()

    # 2. Формируем сообщение
    message = "📊 Курс криптовалют:\n\n"
    for coin_id in COINS:
        if coin_id in data:
            coin_data = data[coin_id]
            name = COIN_NAMES.get(coin_id, coin_id.capitalize())
            usd = coin_data.get("usd", "N/A")
            rub = coin_data.get("rub", "N/A")
            change = coin_data.get("usd_24h_change", 0)

            if change > 0:
                emoji = "📈"
                sign = "+"
            else:
                emoji = "📉"
                sign = ""

            # Форматируем вывод чисел с разделением тысяч
            usd_str = f"{usd:,}" if isinstance(usd, (int, float)) else str(usd)
            rub_str = f"{rub:,}" if isinstance(rub, (int, float)) else str(rub)

            message += (
                f"{emoji} {name}:\n"
                f"   ${usd_str} | {rub_str} ₽\n"
                f"   Изм. за 24ч: {sign}{change:.2f}%\n\n"
            )

    # 3. Отправка в Telegram
    print("⏳ Отправка сообщения в Telegram...")
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    tg_response = requests.post(
        tg_url,
        data={"chat_id": TELEGRAM_CHAT_ID, "text": message},
        timeout=15
    )
    tg_response.raise_for_status()
    print("✅ Уведомление с курсом отправлено успешно!")

except requests.exceptions.HTTPError as http_err:
    print(f"❌ Ошибка HTTP: {http_err}")
    if response.status_code == 429:
        print("💡 Внимание: Бесплатный лимит CoinGecko исчерпан. Попробуйте позже.")
except Exception as e:
    print(f"❌ Произошла непредвиденная ошибка: {e}")
