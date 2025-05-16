from django.urls import path

from sys_admin import views

app_name = 'admin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('college_list/', views.college_list, name='college_list'),
    path('create_college/', views.create_college, name='create_college'),
    path('major_list/<str:college_id>', views.major_list, name='major_list'),
    path('create_major/', views.create_major, name='create_major'),
    path('news_list/', views.news_list, name='news_list'),
    path('news_create/', views.news_create, name='news_create'),
    path('news_edit/<int:news_id>/', views.news_edit, name='news_edit'),
    path('news_delete/<int:news_id>/', views.news_delete, name='news_delete'),
    path('news_detail/<news_id>', views.news_detail, name='news_detail'),
    path('carousel_list/', views.carousel_list, name='carousel_list'),
    path('create_carousel/', views.create_carousel, name='create_carousel'),
    path('delete_carousel/<int:carousel_id>/', views.delete_carousel, name='delete_carousel'),
    path('course_applications/', views.course_applications, name='course_applications'),
    path('process_application/<int:app_id>/', views.process_application, name='process_application'),

]