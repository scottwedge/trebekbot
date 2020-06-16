from django.urls import path

from . import views

urlpatterns = [
    path('', views.test, name='testpage'),
    path('', views.question, name='question')
]