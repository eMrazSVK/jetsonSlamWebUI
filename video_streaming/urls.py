from django.urls import path
from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.home, name='DroneStreaming-home'),
    path('about/', views.about, name='DroneStreaming-about'),
    path('webcam-stream', views.index, name='DroneStreaming-stream'),
    path('html-stream', views.html_stream, name='html-stream'),
]
