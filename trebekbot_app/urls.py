from django.urls import path

from . import views

urlpatterns = [
    path('trebekbot-django.herokuapp.com', views.index, name='index'),
]