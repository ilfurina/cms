from django.urls import path
from . import views

app_name = 'student'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('info/', views.info, name='info'),
    path('join_course/', views.join_course, name='join_course'),
    path('edit/', views.edit_info, name='edit_info'),
    path('recommendations/', views.course_recommendations, name='course-recommendations'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('download/<path:filename>/', views.download_resource, name='download_resource'),

    path('submit_assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('discussion/<int:pk>/', views.discussion_detail,
         name='discussion_detail'),
    path('discussion/<int:pk>/reply/', views.create_post,
         name='create_post'),
    path('upload_face/', views.upload_face, name='upload_face'),
    path('start_capture/', views.start_capture, name='start_capture'),
    path('check_in/<int:course_id>/', views.check_in, name='check_in'),
path('submit_report/<int:report_id>/', views.submit_report, name='submit_report'),

]
