import requests

# --- НАСТРОЙКИ TELEGRAM ---
# Можете использовать тот же токен и ID, что и для погоды!
TELEGRAM_TOKEN = "ВАШ_ТОКЕН"
TELEGRAM_CHAT_ID = "ВАШ_CHAT_ID"
# --------------------------

url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    "ids": "bitcoin,ethereum",
    "vs_currencies": "usd,rub"
}

try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    btc_usd = data["bitcoin"]["usd"]
    btc_rub = data["bitcoin"]["rub"]
    eth_usd = data["ethereum"]["usd"]
    eth_rub = data["ethereum"]["rub"]

    message = (
        f"💰 Курс криптовалют:\n\n"
        f"🟡 Bitcoin (BTC):\n"
        f"   ${btc_usd:,.0f} / {btc_rub:,.0f} руб.\n\n"
        f"🔵 Ethereum (ETH):\n"
        f"   ${eth_usd:,.0f} / {eth_rub:,.0f} руб."
    )

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(tg_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=15)
    print("Уведомление отправлено успешно!")

except Exception as e:
    print(f"Ошибка: {e}")
    raise e
