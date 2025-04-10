from django.urls import path
from . import views

app_name = 'teacher'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('info/', views.info, name='info'),
    path('go_to_create', views.go_to_create, name='go_to_create'),
    path('create_course/', views.create_course, name='create_course'),
    path('edit/<int:course_id>/', views.edit_course, name='edit'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('create_attendance/<int:course_id>/', views.create_attendance, name='create_attendance'),


]