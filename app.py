from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time

app = Flask(__name__)

# Настройка кэширования
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Настройка ограничения частоты запросов
limiter = Limiter(
    get_remote_address,
    default_limits=["10 per hour"]
)

@app.route('/weather/', methods=['GET'])
@limiter.limit("10 per hour")
@cache.cached(timeout=3600)  # Кэширование на 1 час
def get_weather():
    city = request.args.get('city')
    
    if not city:
        return jsonify({"error": "City parameter is required."}), 400
    
    # Статические данные о погоде (пример)
    weather_data = {
        "Moscow": {"temperature": -5, "condition": "Snow"},
        "New York": {"temperature": 3, "condition": "Cloudy"},
        "Tokyo": {"temperature": 12, "condition": "Sunny"}
    }
    
    data = weather_data.get(city)
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "City not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)
