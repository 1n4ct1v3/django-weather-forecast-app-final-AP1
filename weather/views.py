import requests
from django.shortcuts import render, redirect
from .forms import CityForm, ContactForm
from .models import city, ContactMessage
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
    api_key = ''
    current_weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid='
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid='

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

    for citi in cities:
        weather, forecasts = fetch_weather_and_forecast(citi.name, api_key, current_weather_url, forecast_url)
        weather['daily_forecasts'] = forecasts  # Add daily_forecasts to weather_data
        weather_data.append(weather)

    context = {
        'weather_data': weather_data,
        'form': form,
        'message': message,
        'message_class': message_class
    }

    return render(request, 'weather/weather.html', context)


def about(request):
    return render(request, 'weather/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'weather/contact.html', {'form': form})


def success(request):
    return render(request, 'weather/success.html')


def delete_city(request, city_name):
    city.objects.get(name=city_name).delete()
    return redirect('home')
