from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('delete/<city_name>/', views.delete_city,name="delete_city"),
]
