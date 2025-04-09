from django.shortcuts import render
from accounts.decorators import student_required

@student_required
def dashboard(request):
    return render(request, 'student/dashboard.html')