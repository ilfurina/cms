from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from student.views import info as stu_info
from teacher.views import info as tea_info

def welcome(request):
    return render(request, 'welcome.html')

def info(request):
    user = request.user
    if user.user_type == 'student':
        return stu_info(request)
    elif user.user_type == 'teacher':
        return tea_info(request)
