from django.urls import path

from sys_admin import views

app_name = 'admin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('college_list/', views.college_list, name='college_list'),
    path('create_college/', views.create_college, name='create_college'),
    path('major_list/<str:college_id>', views.major_list, name='major_list'),
    path('create_major/', views.create_major, name='create_major'),
]