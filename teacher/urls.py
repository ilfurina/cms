from django.urls import path
from . import views
from . import assignment
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
    path('course/<int:course_id>/assignments/active/',
         views.ActiveAssignmentsView.as_view(), name='active_assignments'),
    path('course/<int:course_id>/assignments/create/',
         views.CreateAssignmentView.as_view(), name='create_assignment'),
    path('assignment/<int:assignment_id>/progress/', views.assignment_progress, name='assignment_progress'),

    path('importByStudentID/', views.import_by_student_id, name='importByStudentID'),
    path('import/department/', views.import_by_department, name='import_by_department'),
    path('get_majors/', views.get_majors, name='get_majors'),
    path('delete_student/{<int:course_id>,<int:student_id>}', views.delete_student, name='delete_student'),

    path('course/<int:course_id>/reports/',
         views.ReportListView.as_view(), name='reports'),
    path('course/<int:course_id>/report/create/',
         views.CreateReportView.as_view(), name='create_report'),
    path('course/<int:course_id>/discussions/',
         views.DiscussionListView.as_view(), name='discussion_list'),
    path('course/<int:course_id>/discussions/create/',
         views.CreateDiscussionView.as_view(), name='create_discussion'),

    # path('question_banks/', assignment.QuestionBankListView.as_view(), name='question_bank_list'),
    # path('question_bank/create/', assignment.CreateQuestionBankView.as_view(), name='create_question_bank'),
    # path('question_bank/<int:pk>/', assignment.QuestionBankDetailView.as_view(), name='question_bank_detail'),
    # path('question_bank/<int:bank_id>/add_question/', assignment.add_question, name='add_question'),
    # path('question_bank/<int:pk>/delete/', exercise.DeleteQuestionBankView.as_view(), name='delete_question_bank'),

]
