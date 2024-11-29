from django.urls import path
from . import views




urlpatterns = [
    path('',views.home),
    path('room/',views.room),
    path('Profile/',views.Profile),
    path('Event/',views.Event),
    path('Main/',views.Main),
    path('Jassibhai/',views.Jassibhai)
]