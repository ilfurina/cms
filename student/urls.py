from django.urls import path
from . import views

app_name = 'student'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('info/', views.info, name='info'),
    path('join_course/', views.join_course, name='join_course'),
    path('edit/', views.edit_info, name='edit_info'),

]