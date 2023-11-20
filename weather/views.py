import requests
from django.shortcuts import render, redirect
from .forms import CityForm
from .models import city
import datetime
from collections import defaultdict


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    current_weather_response = requests.get(current_weather_url.format(city, api_key)).json()
    lat, lon = current_weather_response['coord']['lat'], current_weather_response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    weather_data = {
        'city': city,
        'temperature': round(current_weather_response['main']['temp']),
        'description': current_weather_response['weather'][0]['description'],
        'icon': current_weather_response['weather'][0]['icon'],
    }

    daily_forecasts_dict = defaultdict(list)
    for daily_data in forecast_response['list']:
        day = datetime.datetime.fromtimestamp(daily_data['dt']).strftime('%A')
        temperature = daily_data['main']
        daily_forecasts_dict[day].append({
            'temperature': round(temperature['temp']),
            'description': daily_data['weather'][0]['description'],
            'icon': daily_data['weather'][0]['icon'],
        })

    daily_forecasts = []
    for day, forecasts in daily_forecasts_dict.items():
        avg_temperature = round(sum(forecast['temperature'] for forecast in forecasts) / len(forecasts))

        daily_forecasts.append({
            'day': day,
            'temperature': avg_temperature,
            'description': forecasts[0]['description'],
            'icon': forecasts[0]['icon'],
        })

    return weather_data, daily_forecasts


def index(request):
    current_weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=0ea449ea42cebe07f77febdfc966759d'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid=0ea449ea42cebe07f77febdfc966759d'

    err_msg = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = city.objects.filter(name=new_city).count()
            if existing_city_count == 0:
                form.save()
            else:
                err_msg = "City already exists in the list!"
        if err_msg:
            message = err_msg
            message_class = 'alert-danger'
        else:
            message = 'City added successfully!'
            message_class = "alert-success"

    form = CityForm()
    cities = city.objects.all()

    weather_data = []
    daily_forecasts = []

    for citi in cities:
        weather, forecasts = fetch_weather_and_forecast(citi.name, '0ea449ea42cebe07f77febdfc966759d',
                                                        current_weather_url, forecast_url)
        weather_data.append(weather)
        daily_forecasts.extend(forecasts)

    context = {
        'weather_data': weather_data,
        'daily_forecasts': daily_forecasts,
        'form': form,
        'message': message,
        'message_class': message_class
    }

    return render(request, 'weather/weather.html', context)


def about(request):
    return render(request, 'weather/about.html')


def contact(request):
    return render(request, 'weather/contact.html')


def delete_city(request, city_name):
    city.objects.get(name=city_name).delete()
    return redirect('home')
