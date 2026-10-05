import requests
import os

# --- НАСТРОЙКИ TELEGRAM ---
# Токен лучше хранить в секретах GitHub, но для простоты можно оставить здесь
TELEGRAM_TOKEN = "8847922404:AAFIsHxn6QDgfF6ZqWdPNZC7_Jm5sZZLcII"
TELEGRAM_CHAT_ID = "444451877"
# --------------------------

# Список криптовалют, которые хотим отслеживать (ID из CoinGecko)
COINS = ["bitcoin", "ethereum", "solana"]
COIN_NAMES = {"bitcoin": "Bitcoin", "ethereum": "Ethereum", "solana": "Solana"}

# 1. Запрос к API CoinGecko
url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    "ids": ",".join(COINS),
    "vs_currencies": "usd,rub",  # Запрашиваем цену в долларах и рублях
    "include_24hr_change": "true" # Добавляем изменение за 24 часа
}

try:
    response = requests.get(url, params=params, timeout=15)
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

            # Определяем эмодзи для изменения цены
            if change > 0:
                emoji = "📈"
                sign = "+"
            else:
                emoji = "📉"
                sign = ""

            message += (
                f"{emoji} {name}:\n"
                f"   ${usd:,} | {rub:,} ₽\n"
                f"   Изм. за 24ч: {sign}{change:.2f}%\n\n"
            )

    # 3. Отправка в Telegram
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    tg_response = requests.post(
        tg_url,
        data={"chat_id": TELEGRAM_CHAT_ID, "text": message},
        timeout=15
    )
    tg_response.raise_for_status()
    print("✅ Уведомление с курсом отправлено успешно!")

except Exception as e:
    print(f"❌ Произошла ошибка: {e}")
