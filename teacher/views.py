from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from accounts.decorators import teacher_required
import random

from sys_admin.models import Major, College
from .models import Course, Attendance
from django.shortcuts import render



@teacher_required
def dashboard(request):
    courses = Course.objects.filter(teacher=request.user.teacher)
    return render(request, 'teacher/dashboard.html', {'courses': courses})

def info(request):
    user = request.user.teacher
    information = {
        'name': user.name,
        'teacher_id': user.teacher_id,
        'college': user.college,

    }
    return render(request, 'teacher/info.html', {'information': information})

#教师创建课程
# teacher/views.py
def go_to_create(request):
    # 当前用户所属学院的全部专业
    if request.user.teacher.college:
        college = request.user.teacher.college
        majors = Major.objects.filter(college=college)
    return render(request, 'teacher/create_course.html', {'majors': majors})

def create_course(request):
    if request.method == 'POST':

        name = request.POST.get('name')
        major_name = request.POST.get('major')
        major = Major.objects.get(major_name=major_name)
        major_id = major.major_id
        college_id = major.college.college_id
        print('学院id', college_id,'专业id',major_id)
        # 课程码为 学院id+专业id+三位随机数
        while True:
            ran = random.randint(100, 999)
            course_id = college_id + major_id + str(ran)
            if Course.objects.filter(course_id=course_id).count() == 0:
                break
        description = request.POST.get('description')
        teacher = request.user.teacher
        Course.objects.create(
            major=major,
            course_id=course_id,
            name=name,
            description=description,
            teacher=teacher)
        return redirect('teacher:dashboard')
    # return redirect('teacher:go_to_create')

# 编辑课程
def edit_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)

    current_attendance = Attendance.objects.filter(
        course=course,
        is_active=True
    ).order_by('-start_time').first()
    remaining_seconds = 0
    if current_attendance:
        now = timezone.now()
        elapsed = (now - current_attendance.start_time).total_seconds()
        remaining = current_attendance.duration * 60 - elapsed
        remaining_seconds = max(round(remaining), 0)

    if request.method == 'POST':
        course.name = request.POST.get('name')
        course.description = request.POST.get('description')
        course.numbers = request.POST.get('numbers')
        course.save()
        return redirect('teacher:dashboard')

    # 传递current_attendance到模板
    return render(request, 'teacher/course_edit.html', {
        'current_course': course,
        'current_attendance': current_attendance,
        'remaining_seconds': remaining_seconds
    })



from django.contrib import messages
from django.shortcuts import redirect


def delete_course(request, course_id):
    if request.method == 'POST':
        try:
            course = Course.objects.get(course_id=course_id)

            # 添加权限验证（示例）
            if course.teacher != request.user.teacher:
                messages.error(request, '无权执行此操作')
                return redirect('teacher:dashboard')

            course.delete()
            messages.success(request, '课程已成功删除')
            return redirect('teacher:dashboard')  # 重定向到课程列表

        except Course.DoesNotExist:
            messages.error(request, '课程不存在')
            return redirect('teacher:dashboard')

    return redirect('teacher:course_edit', course_id=course_id)


@teacher_required
def create_attendance(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)

    if request.method == 'POST':
        attendance = Attendance(course=course)
        attendance.generate_code()
        attendance.duration = request.POST.get('duration', 10)
        attendance.save()
        return redirect('teacher:edit', course_id=course_id)

    return render(request, 'teacher/attendance_form.html', {'course': course})

