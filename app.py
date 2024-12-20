from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Настройка кэширования
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Настройка лимитирования запросов
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per hour"]
)

# Статические данные о погоде
weather_data = {
    "Moscow": {"temperature": -5, "condition": "snow"},
    "Saint Petersburg": {"temperature": -3, "condition": "cloudy"},
    "Sochi": {"temperature": 10, "condition": "sunny"}
}

@app.route('/weather/', methods=['GET'])
@limiter.limit("10 per hour")
@cache.cached(timeout=3600, query_string=True)  # Кэшировать на 1 час
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400

    data = weather_data.get(city)
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "City not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)


