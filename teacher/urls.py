from django.urls import path
from . import views
from . import assignment
from student.views import download_resource

app_name = 'teacher'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('info/', views.info, name='info'),
    # path('go_to_create', views.go_to_create, name='go_to_create'),
    path('create_course/', views.create_course, name='create_course'),
    path('edit/<int:course_id>/', views.edit_course, name='edit'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    # 课程签到
    path('create_attendance/<int:course_id>/', views.create_attendance, name='create_attendance'),
    path('attendance/<str:course_id>/', views.attendance, name='attendance'),

    # 学生操作
    path('export_students/<int:course_id>/', views.export_students, name='export_students'),
    path('students/<int:course_id>/', views.students, name='students'),
    path('importByStudentID/', views.import_by_student_id, name='importByStudentID'),
    path('import/department/', views.import_by_department, name='import_by_department'),
    path('get_majors/', views.get_majors, name='get_majors'),
    path('delete_student/{<int:course_id>,<int:student_id>}',
         views.delete_student, name='delete_student'),

    # 课程资源
    path('upload_resource/<int:course_id>/', views.upload_resource, name='upload_resource'),
    path('delete_resource/<int:resource_id>/', views.delete_resource, name='delete_resource'),
    path('resources/<int:course_id>/', views.resources, name='resources'),
    path('download/<path:filename>/', download_resource, name='download_resource'),

    # 课程作业
    path('course/<int:course_id>/assignments/active/',
         assignment.ActiveAssignmentsView.as_view(), name='active_assignments'),
    path('course/<int:course_id>/assignments/create/',
         assignment.CreateAssignmentView.as_view(), name='create_assignment'),
    path('assignment/<int:assignment_id>/progress/',
         assignment.assignment_progress, name='assignment_progress'),
    path('assignment/<int:assignment_id>/delete/',
         assignment.delete_assignment, name='delete_assignment'),
    path('question_bank/', assignment.question_bank, name='question_bank'),
    path('grade_submission/<int:submission_id>/', assignment.grade_submission, name='grade_submission'),

    # 实验报告
    # path('course/<int:course_id>/reports/',
    #      views.ReportListView.as_view(), name='reports'),
    # path('course/<int:course_id>/report/create/',
    #      views.CreateReportView.as_view(), name='create_report'),
    path('course/<int:course_id>/reports/',
         views.report_list, name='reports'),
    path('course/<int:course_id>/report/create/',
         views.create_report, name='create_report'),

    # 课程讨论
    path('course/<int:course_id>/discussions/',
         views.DiscussionListView.as_view(), name='discussion_list'),
    path('course/<int:course_id>/discussions/create/',
         views.CreateDiscussionView.as_view(), name='create_discussion'),

]
