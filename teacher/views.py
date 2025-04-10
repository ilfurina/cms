from django.shortcuts import render
from accounts.decorators import teacher_required

@teacher_required
def dashboard(request):
    return render(request, 'teacher/dashboard.html')

def info(request):
    user = request.user.teacher
    information = {
        'name': user.name,
        'teacher_id': user.teacher_id,
        'college': user.college,

    }
    return render(request, 'teacher/info.html', {'information': information})