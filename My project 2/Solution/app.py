from flask import Flask as fl, render_template, request, redirect, url_for
import requests as rq
import os
from dotenv import load_dotenv

app = fl(__name__)

load_dotenv()

API_KEY = "qJcANj36YaSOABDrbyig90t737tyar13"

def get_weather(city):
    try:
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}&language=ru-ru"
        location_data = rq.get(location_url).json()

        if location_data:
            location_key = location_data[0]['Key']
            weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={API_KEY}&language=ru-ru&details=true"
            weather_data = rq.get(weather_url).json()

        return {
            "city": city,
            "temperature": int(weather_data[0]['Temperature']['Metric']['Value']),
            "humidity": weather_data[0]['RelativeHumidity'],
            "wind_speed": weather_data[0]['Wind']['Speed']['Metric']['Value'],
            "weather": weather_data[0]['WeatherText'],
        }
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None  
    
def check_bad_weather(weather):
    data = []
    bad_weather_ind = 0
    
    if weather['temperature'] < 0 or weather['temperature'] > 35:
        data.append('Температура')
        bad_weather_ind += 1
    if weather['humidity'] > 75 or weather['humidity'] < 15:
        data.append('Влажность')
        bad_weather_ind += 1
    if weather['wind_speed'] > 50:
        bad_weather_ind += 1
        data.append('Скорость ветра')
        
    return [bad_weather_ind,data]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_weather', methods=['POST'])
def check_weather():
    start_city = request.form['start_city']
    end_city = request.form['end_city']
    
    start_weather = get_weather(start_city)
    end_weather = get_weather(end_city)
    
    #if not start_weather or not end_weather:
    #    print("Ошибка: не удалось получить данные о погоде.")
    #    return redirect(url_for('index'))

    
    start_data = check_bad_weather(start_weather)
    end_data = check_bad_weather(end_weather)
    
    overall_score = start_data[0] + end_data[0]
    if overall_score < 1:
        conditions = "Хорошая погода"
    elif overall_score < 3:
        conditions = "Средняя погода"
    elif overall_score >= 3:
        conditions = "Плохая погода"
    
    return render_template('result.html', 
                           start_weather=start_weather, 
                           end_weather=end_weather, 
                           conditions=conditions, 
                           start_conditions = start_data[1],
                           end_conditions = end_data[1])
    
    
if __name__ == '__main__':
    app.run(debug=True)
    