import requests
from django.shortcuts import render, redirect
from .forms import CityForm
from .models import city
import datetime


def index(request):
    current_weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=0ea449ea42cebe07f77febdfc966759d'
    forecast_url = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid=0ea449ea42cebe07f77febdfc966759d'

    err_msg = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = city.objects.filter(name=new_city).count()
            if existing_city_count == 0:
                r = requests.get(current_weather_url.format(new_city)).json()
                print(r)
                if r['cod'] == 200:
                    form.save()
                else:
                    err_msg = "City doesnt exist"
            else:
                err_msg = "City already exist in the list!"
        if err_msg:
            message = err_msg
            message_class = 'alert-danger'
        else:
            message = 'City added successfully!'
            message_class = "alert-success"
    
    print(err_msg)
    form = CityForm()
    cities = city.objects.all()

    weather_data = []

    for citi in cities:

        r = requests.get(current_weather_url.format(citi)).json()
        temperature = round(r['main']['temp'])

        city_weather = {
            'city': citi.name,
            'temperature': temperature,
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        weather_data.append(city_weather)

    context = {
        'weather_data': weather_data,
        'form': form,
        'message': message,
        'message_class': message_class
    }

    return render(request, 'weather/weather.html', context)


def about(request) :
    return render(request,'weather/about.html')


def contact(request):
    return render(request, 'weather/contact.html')


def delete_city(request, city_name):
    city.objects.get(name=city_name).delete()
    return redirect('home')
