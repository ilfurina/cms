from django.shortcuts import render, redirect
from accounts.decorators import student_required
from django.contrib import messages
from teacher.models import Course
from sys_admin.models import College, Major


@student_required
def dashboard(request):
    student = request.user.student
    enrolled_courses = student.courses.all()  # 假设Student模型有courses关联字段
    return render(request, 'student/dashboard.html', {
        'enrolled_courses': enrolled_courses
    })
def info(request):
    user = request.user.student
    information = {
        'name': user.name,
        'student_id': user.student_id,
        'college': user.college,
        'major': user.major,
        # 'class_id': user.class_id,
    }
    return render(request, 'student/info.html', {'information': information})


from django.contrib.auth.decorators import login_required
from .models import Student
from django.shortcuts import get_object_or_404


@student_required
def edit_info(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == 'POST':
        # 更新可修改字段（示例字段，根据实际需求调整）
        major_id = request.POST.get('major')
        try:
            student.major = Major.objects.get(major_id=major_id)
            student.save()
            messages.success(request, '信息更新成功')
        except Major.DoesNotExist:
            messages.error(request, '无效的专业选择')
        return redirect('student:info')


    college = student.college
    majors = college.major_set.all()

    return render(request, 'student/edit_info.html', {
        'student': student,
        'majors': majors,
    })


@student_required
def join_course(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        try:
            course = Course.objects.get(course_id=course_id)
            student = request.user.student

            if course.students.filter(pk=student.pk).exists():
                messages.warning(request, '您已加入该课程')
            else:
                course.students.add(student)
                course.numbers += 1  # 更新班级人数
                course.save()
                messages.success(request, '成功加入课程')
        except Course.DoesNotExist:
            messages.error(request, '课程不存在')

    return redirect('student:dashboard')

