from flask import Flask, request, jsonify
from flask_caching import Cache #Класс для работы с кэшированием в Flask.
# Он позволяет сохранять результаты запросов или вычислений, чтобы уменьшить нагрузку на сервер и ускорить ответы.
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta, timezone #timedelta:  Используется для выполнения арифметических операций с датами и временем
#timezone: Он может использоваться для создания объектов времени с учетом часового пояса

app = Flask(__name__)

# Настройка кэширования
cache = Cache(app, config={'CACHE_TYPE': 'simple'})#тип кэширования. simple- кэш будет храниться оперативной памяти на сервере.

# Настройка лимитирования запросов
limiter = Limiter(
    get_remote_address,#возвращает IP-адрес клиента
    app=app,#параметр привязывает Flask-Limiter к  Flask-приложению
    default_limits=["10 per hour"] # Ограничение по умолчанию: 10 запросов в час
    # Устанавливает лимиты по умолчанию для всех маршрутов, если не указаны иные ограничения.
)

# Статические данные о погоде
weather_data = {
    "Moscow": {"температура": -5, "состояние": "снег"},
    "Saint Petersburg": {"температура": -3, "состояние": "прохладно"},
    "Sochi": {"температура": 10, "состояние": "солнечно"}
}

@app.route('/weather/', methods=['GET'])
@limiter.limit("10 per hour")#Используется для установки индивидуального лимита для конкретного маршрута
@cache.cached(timeout=3600, query_string=True)  # Кэшировать на 1 час
#query_string=True означает, что кэширование будет зависеть от строки запроса.
# Это позволяет кэшировать разные результаты для разных значений параметра city.
def get_weather():
    city = request.args.get('city')#извлекает значение параметра city из строки запроса
    if not city:
        return jsonify({"error": "Требуется город"}), 400

    data = weather_data.get(city)#ищет данные о погоде для указанного города в словаре weather_data
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Город не найден"}), 404

# Обработчик ошибок для превышения лимита запросов
@app.errorhandler(429)
def ratelimit_error(e):
    retry_after = e.description  # e.description строка указывает , сколько времени клиенту нужно подождать перед повторной попыткой
    # получить числовое значение, которое затем используется для вычисления времени следующего запроса

    # Парсим строку, чтобы получить количество секунд
    seconds = int(retry_after.split()[0])  #  разбивает строку по пробелам и извлекает первое слово, то есть число

    # Преобразуем секунды в часы
    next_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)#datetime.now(timezone.utc) получает текущее время в формате UTC
    # timedelta(seconds=seconds) создает временной интервал, равный количеству секунд, которое клиент должен подождать


    # Форматируем время
    formatted_next_time = next_time.strftime("%Y-%m-%d %H:%M:%S") #strftime форматирует объект времени в строку в заданном формате

    return jsonify(
        error="превышен лимит запросов",
        message=f"Повторите попытку через 1 час.",
        next_request_time=formatted_next_time
    ), 429

if __name__ == '__main__':
    app.run(debug=True)



