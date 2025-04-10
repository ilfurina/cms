from django.urls import path
from . import views

app_name = 'student'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('info/', views.info, name='info'),

]