from os.path import basename
from cms.settings import BASE_DIR
from django.http import HttpResponseForbidden, FileResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.decorators import student_required
from django.contrib import messages
from teacher.models import Course, CourseResource
from sys_admin.models import College, Major
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .recommender import CourseRecommender



@student_required
def dashboard(request):
    student = request.user.student
    enrolled_courses = student.courses.all()
    recommended_courses = CourseRecommender.get_recommendations(student)
    return render(request, 'student/dashboard.html', {
        'enrolled_courses': enrolled_courses,
        'recommended_courses': recommended_courses,
    })
def info(request):
    user = request.user.student
    information = {
        'name': user.name,
        'student_id': user.student_id,
        'college': user.college,
        'major': user.major,
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


class CourseRecommendationsView(LoginRequiredMixin, View):

    def get(self, request):
        student = request.user.student  # 假设已建立用户到Student的关联
        enrolled_courses = student.courses.all()
        recommended_courses = CourseRecommender.get_recommendations(student)

        return render(request, 'student/recommendations.html', {
            'enrolled_courses':enrolled_courses,
            'recommended_courses': recommended_courses,
        })


def course_detail(request, course_id):
    student = request.user.student
    course = get_object_or_404(Course, course_id=course_id)

    # 验证学生是否已选该课程
    if not course.students.filter(pk=student.pk).exists():
        return HttpResponseForbidden("未加入该课程")

    assignments = Assignment.objects.filter(course=course).order_by('-start_time')
    now = timezone.now()
    resources = CourseResource.objects.filter(course=course)


    return render(request, 'student/course_detail.html', {
        'course': course,
        'assignments': assignments,
        'now': now,
        'resources': resources,
    })


def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = request.user.student

    # 验证权限
    if not assignment.course.students.filter(pk=student.pk).exists():
        return HttpResponseForbidden("无访问权限")

    # 获取题目列表（按顺序）
    questions = assignment.assignmentquestion_set.order_by('order')

    return render(request, 'student/assignment_detail.html', {
        'assignment': assignment,
        'questions': questions
    })


@student_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = request.user.student

    # 创建或更新提交记录
    Submission.objects.update_or_create(
        student=student,
        assignment=assignment,
        defaults={
            'is_submitted': True,
            'submitted_at': timezone.now()
        }
    )
    messages.success(request, '作业提交成功')
    return redirect('student:assignment_detail', assignment_id=assignment_id)


from urllib.parse import quote
def download_resource(request, filename):
    resource = get_object_or_404(CourseResource, file=filename)
    file_path = resource.file.path

    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'application/octet-stream'

    encoded_filename = quote(resource.filename)
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"

    return response

