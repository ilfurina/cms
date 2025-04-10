from django.shortcuts import render
from accounts.decorators import student_required

@student_required
def dashboard(request):
    return render(request, 'student/dashboard.html')

def info(request):
    user = request.user.student
    information = {
        'name': user.name,
        'student_id': user.student_id,
        'college': user.college,
        'class_id': user.class_id,
    }
    return render(request, 'student/info.html', {'information': information})