from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from accounts.decorators import teacher_required
import random
from sys_admin.models import Major, College
from .models import Course, Attendance, CourseResource
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
import csv


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
            course_id =  major_id + str(ran)
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

    course = get_object_or_404(Course, course_id=course_id)
    resources = CourseResource.objects.filter(course=course)  # 资源查询

    # 传递current_attendance到模板
    return render(request, 'teacher/course_edit.html', {
        'current_course': course,
        'current_attendance': current_attendance,
        'remaining_seconds': remaining_seconds,
        'resources': resources,
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

    # return render(request, 'teacher/attendance_form.html', {'course': course})


def export_students(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    students = course.students.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{course.name}_学生名单.csv"'

    writer = csv.writer(response)
    writer.writerow(['学号', '姓名', '学院', '专业'])

    for student in students:
        writer.writerow([
            student.student_id,
            student.name,
            student.college,
            student.class_id
        ])

    return response


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

# 上传课程资源
@login_required
@require_POST
def upload_resource(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)

    if 'resource_file' not in request.FILES:
        return HttpResponseBadRequest("未选择文件")

    uploaded_file = request.FILES['resource_file']
    # 文件大小限制（10MB）
    if uploaded_file.size > 100 * 1024 * 1024:
        return HttpResponseBadRequest("文件大小超过100MB限制")

    # 创建资源记录
    resource = CourseResource(course=course, file=uploaded_file)
    resource.save()

    return redirect('teacher:resources', course_id=course_id)

# 删除课程资源
@login_required
@require_POST
def delete_resource(request, resource_id):
    resource = get_object_or_404(CourseResource, id=resource_id)
    course_id = resource.course.course_id
    resource.file.delete()  # 删除文件
    resource.delete()  # 删除记录
    return redirect('teacher:resources', course_id=course_id)

# 六个选项卡
def students(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    students = course.students.all()
    return render(request, 'teacher/students.html', {'current_course': course, 'students': students})
def resources(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    resources = CourseResource.objects.filter(course=course)
    return render(request, 'teacher/resources.html',
                  {'current_course': course, 'resources': resources})

def attendance(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    attendances = Attendance.objects.filter(course=course)
    return render(request, 'teacher/attendance.html',
          {'current_course': course, 'attendances': attendances})


from django.views import View
from django.shortcuts import get_object_or_404
from teacher.models import (
    Course,
    QuestionBase,
    SingleChoiceQuestion,
    MultipleChoiceQuestion,
    FillInBlankQuestion,
    EssayQuestion,
    Assignment,
    AssignmentQuestion
)


class CreateAssignmentView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)

        # 获取所有子类题目（原生Django方式）
        questions = QuestionBase.objects.filter(course=course).prefetch_related(
            'singlechoicequestion',
            'multiplechoicequestion',
            'fillinblankquestion',
            'essayquestion'
        )

        # 获取已选中的题目
        selected = request.GET.getlist('selected')
        selected_questions = QuestionBase.objects.filter(id__in=selected)

        return render(request, 'teacher/create_exercises.html', {
            'current_course': course,
            'questions': questions,
            'selected_questions': selected_questions
        })

    # post 方法保持不变...

    def post(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)

        # 创建作业
        assignment = Assignment.objects.create(
            course=course,
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            assignment_type='homework',
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time']
        )

        # 关联题目
        selected_questions = request.POST.getlist('questions')
        for order, qid in enumerate(selected_questions, start=1):
            question = QuestionBase.objects.get(id=qid)
            AssignmentQuestion.objects.create(
                assignment=assignment,
                question=question,
                points=10,  # 默认分值
                order=order
            )

        return redirect('teacher:course_edit', course_id=course_id)


from django.utils import timezone


class ActiveAssignmentsView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)
        now = timezone.now()

        # 获取所有任务并按状态分类
        assignments = Assignment.objects.filter(course=course).order_by('-start_time')

        return render(request, 'teacher/active_exercises.html', {
            'current_course': course,
            'assignments': assignments,
            'now': now  # 传递当前时间到模板
        })
