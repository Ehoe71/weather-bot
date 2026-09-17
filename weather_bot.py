import requests

# --- НАСТРОЙКИ TELEGRAM ---
TELEGRAM_TOKEN = "8847922404:AAGfmnFQXE-0S3uhOCr17HUVqnY2GM4njeI"
TELEGRAM_CHAT_ID = "444451877"
# --------------------------

LAT, LON = 55.4490, 65.3434  # Координаты Кургана
TIMEZONE = "Asia/Yekaterinburg"

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": LAT,
    "longitude": LON,
    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
    "hourly": "temperature_2m,precipitation_probability,weather_code",
    "timezone": TIMEZONE,
    "forecast_days": 3
}

try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    current = data["current"]
    hourly = data["hourly"]
    
    weather_codes = {
        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
        45: "Туман", 48: "Изморозь", 51: "Легкая морось", 53: "Морось", 55: "Сильная морось",
        61: "Небольшой дождь", 63: "Дождь", 65: "Сильный дождь",
        71: "Небольшой снег", 73: "Снег", 75: "Сильный снег",
        80: "Ливень", 81: "Сильный ливень", 82: "Очень сильный ливень",
        95: "Гроза", 96: "Гроза с градом", 99: "Сильная гроза с градом"
    }
    
    # 1. Текущая погода
    weather_desc_now = weather_codes.get(current["weather_code"], "Неизвестно")
    message = (
        f"🌤 Погода в Кургане сейчас:\n"
        f"🌡 {current['temperature_2m']}°C (ощущается как {current['apparent_temperature']}°C)\n"
        f"💧 Влажность: {current['relative_humidity_2m']}%\n"
        f"💨 Ветер: {current['wind_speed_10m']} м/с\n"
        f"☁️ {weather_desc_now}\n\n"
    )

    # 2. Прогноз на завтра после 16:00
    today_str = hourly["time"][0].split("T")[0]
    tomorrow_str = (datetime.strptime(today_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    
    evening_lines = ["🌙 Прогноз на завтра (после 16:00):"]
    
    for i, t in enumerate(hourly["time"]):
        if t.startswith(tomorrow_str):
            hour = int(t.split("T")[1].split(":")[0])
            if hour >= 16:
                time_label = t.split("T")[1][:5]
                temp = hourly["temperature_2m"][i]
                precip_prob = hourly["precipitation_probability"][i]
                code = hourly["weather_code"][i]
                desc = weather_codes.get(code, "")
                evening_lines.append(f"{time_label}: {temp}°C, {desc} (осадки {precip_prob}%)")
    
    if len(evening_lines) > 1:
        message += "\n".join(evening_lines)
    else:
        message += "Не удалось загрузить прогноз на завтра."

    # 3. Отправка в Telegram
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    tg_response = requests.post(tg_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=15)
    tg_response.raise_for_status()
    print("Уведомление отправлено успешно!")

except Exception as e:
    raise e
