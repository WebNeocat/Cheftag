from django.urls import path
from . import views

app_name = 'super'

urlpatterns = [
    path('home/', views.home, name='home')
    
]