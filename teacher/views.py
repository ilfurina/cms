from django.shortcuts import render
from accounts.decorators import teacher_required

@teacher_required
def dashboard(request):
    return render(request, 'teacher/dashboard.html')