from django.shortcuts import render, redirect
from .models import College,Major

def dashboard(request):

    return render(request, 'admin/dashboard.html')

def college_list(request):
    colleges = College.objects.all()
    return render(request, 'admin/college_list.html', {'colleges': colleges})

def create_college(request):
    if request.method == 'POST':
        college_id = request.POST.get('college_id')
        college_name = request.POST.get('name')
        college = College.objects.create(college_id=college_id, college_name=college_name)
        return redirect('admin:college_list')


def major_list(request, college_id):
    college = College.objects.get(college_id=college_id)
    majors = Major.objects.filter(college_id=college_id)
    return render(request, 'admin/major_list.html', {'majors': majors, 'college': college})

def create_major(request):
    if request.method == 'POST':
        college_id = request.POST.get('college_id')
        major_id = request.POST.get('major_id')
        major_name = request.POST.get('name')
        college = College.objects.get(college_id=college_id)
        major = Major.objects.create(college=college, major_id=major_id, major_name=major_name)
        return redirect('admin:major_list',college_id=college_id)