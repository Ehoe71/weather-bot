import requests
from datetime import datetime
import pytz

# --- НАСТРОЙКИ TELEGRAM ---
TELEGRAM_TOKEN = "8847922404:AAGfmnFQXE-0S3uhOCr17HUVqnY2GM4njeI"
TELEGRAM_CHAT_ID = "444451877"
# --------------------------

LAT, LON = 55.4490, 65.3434  # Координаты Кургана
TIMEZONE = "Asia/Yekaterinburg"

# 1. Определяем текущее время в Кургане
tz = pytz.timezone(TIMEZONE)
now_local = datetime.now(tz)
current_hour = now_local.hour
current_date_str = now_local.strftime("%Y-%m-%d")

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
    
    # 2. Формируем блок текущей погоды
    weather_desc_now = weather_codes.get(current["weather_code"], "Неизвестно")
    message = (
        f"🌤 Погода в Кургане сейчас:\n"
        f"🌡 {current['temperature_2m']}°C (ощущается как {current['apparent_temperature']}°C)\n"
        f"💧 Влажность: {current['relative_humidity_2m']}%\n"
        f"💨 Ветер: {current['wind_speed_10m']} м/с\n"
        f"☁️ {weather_desc_now}\n\n"
    )

    # 3. Динамический блок прогноза в зависимости от времени (16:00)
    forecast_lines = []
    
    if current_hour < 16:
        # ДО 16:00 — показываем прогноз на остаток СЕГОДНЯШНЕГО дня (начиная со следующего часа)
        forecast_lines.append("⏳ Прогноз на сегодня:")
        for i, t in enumerate(hourly["time"]):
            if t.startswith(current_date_str):
                hour = int(t.split("T")[1].split(":")[0])
                if hour > current_hour:
                    time_label = t.split("T")[1][:5]
                    temp = hourly["temperature_2m"][i]
                    precip_prob = hourly["precipitation_probability"][i]
                    code = hourly["weather_code"][i]
                    desc = weather_codes.get(code, "")
                    forecast_lines.append(f"{time_label}: {temp}°C, {desc} (осадки {precip_prob}%)")
    else:
        # ПОСЛЕ 16:00 — переключаемся на ЗАВТРАШНЕЕ УТРО (с 06:00 до 12:00)
        forecast_lines.append("🌅 Прогноз на ЗАВТРАШНЕЕ УТРО:")
        # Ищем индекс начала завтрашнего дня в массиве Open-Meteo
        for i, t in enumerate(hourly["time"]):
            # Если это не сегодняшний день, значит начался завтрашний (или последующий)
            if not t.startswith(current_date_str):
                hour = int(t.split("T")[1].split(":")[0])
                # Фильтруем утренний интервал: от 6 утра до 12 дня
                if 6 <= hour <= 12:
                    time_label = t.split("T")[1][:5]
                    temp = hourly["temperature_2m"][i]
                    precip_prob = hourly["precipitation_probability"][i]
                    code = hourly["weather_code"][i]
                    desc = weather_codes.get(code, "")
                    forecast_lines.append(f"{time_label}: {temp}°C, {desc} (осадки {precip_prob}%)")

    # Добавляем блок прогноза к итоговому сообщению
    if len(forecast_lines) > 1:
        message += "\n".join(forecast_lines)
    else:
        message += "Не удалось загрузить детальный прогноз."

    # 4. Отправка в Telegram
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    tg_response = requests.post(tg_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=15)
    tg_response.raise_for_status()
    print("Уведомление отправлено успешно!")

except Exception as e:
    print(f"Произошла ошибка: {e}")
    raise e
