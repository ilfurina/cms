from django.urls import path
from . import views
from . import exercise
from student.views import download_resource

app_name = 'teacher'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('info/', views.info, name='info'),
    path('go_to_create', views.go_to_create, name='go_to_create'),
    path('create_course/', views.create_course, name='create_course'),
    path('edit/<int:course_id>/', views.edit_course, name='edit'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('create_attendance/<int:course_id>/', views.create_attendance, name='create_attendance'),
    path('export_students/<int:course_id>/', views.export_students, name='export_students'),
    path('upload_resource/<int:course_id>/', views.upload_resource, name='upload_resource'),
    path('delete_resource/<int:resource_id>/', views.delete_resource, name='delete_resource'),
    path('attendance/<str:course_id>/', views.attendance, name='attendance'),
    path('resources/<int:course_id>/', views.resources, name='resources'),
    path('download/<path:filename>/', download_resource, name='download_resource'),
    path('students/<int:course_id>/', views.students, name='students'),
    # path('course/<int:course_id>/exercises/', CreateAssignmentView.as_view(), name='exercises'),
    path('course/<int:course_id>/assignment/',
         exercise.CreateExerciseView.as_view(),  name='create_assignment'),
    # path('assignments/<int:course_id>/active/',
    #      views.ActiveAssignmentsView.as_view(), name='active_assignments'),
    path('assignments/<int:course_id>/create/',
         exercise.PublishExerciseView.as_view(), name='pub_assignment'),
    # path('assignment/<int:course_id>/<int:assignment_id>/',
    #      views.assignment_detail, name='assignment_detail'),

    path('importByStudentID/', views.import_by_student_id, name='importByStudentID'),
    path('import/department/', views.import_by_department, name='import_by_department'),
    path('get_majors/', views.get_majors, name='get_majors'),
    path('delete_student/{<int:course_id>,<int:student_id>}', views.delete_student, name='delete_student'),

]
