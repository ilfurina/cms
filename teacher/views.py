import string
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from accounts.decorators import teacher_required
import random
from student.models import Student
from sys_admin.models import Major, College
from .models import Course, Attendance, CourseResource, Teacher, CourseApplication,ReportAssignment,DiscussionTopic
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
import csv
from django.contrib import messages
from django.views.generic import CreateView, ListView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

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

def create_course(request):
    if request.method == 'GET':
        college = request.user.teacher.college
        majors = Major.objects.filter(college=college)
        return render(request, 'teacher/create_course.html', {'majors': majors})

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
        CourseApplication.objects.create(
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
        'resources': resources,
    })

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
        ])

    return response

# 上传课程资源
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
    colleges = College.objects.all()
    course = get_object_or_404(Course, course_id=course_id)
    students = course.students.all()
    return render(request, 'teacher/students.html', {'current_course': course, 'students': students,  'colleges': colleges})
def resources(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    resources = CourseResource.objects.filter(course=course)
    return render(request, 'teacher/resources.html',
                  {'current_course': course, 'resources': resources})

def attendance(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    # attendances = Attendance.objects.filter(course=course)
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

        if remaining_seconds <= 0:
            current_attendance.is_active = False
            current_attendance.save()

    return render(request, 'teacher/attendance.html',
          {'current_course': course,
           'current_attendance': current_attendance,
           'remaining_seconds': remaining_seconds,
           })
@teacher_required
def create_attendance(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)

    if request.method == 'POST':
        attendance = Attendance(course=course)
        attendance.checkin_code = "".join(random.sample(string.digits, 4))
        attendance.duration = request.POST.get('duration', 10)
        attendance.save()
        return redirect('teacher:attendance', course_id=course_id)

    # return render(request, 'teacher/attendance_form.html', {'course': course})

def reports(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)

    return render(request, 'teacher/report_list.html', {'current_course': course})

def import_by_student_id(request):
    course_id = request.POST.get('course_id')
    student_id = request.POST.get('student_id')
    course = Course.objects.get(course_id=course_id)
    student = Student.objects.get(student_id=student_id)
    course.students.add(student)
    course.numbers += 1
    course.save()

    return redirect('teacher:students', course_id=course_id)

# 按部门导入学生
def import_by_department(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        major_id = request.POST.get('major_id')

        try:
            course = Course.objects.get(course_id=course_id)
            major = Major.objects.get(major_id=major_id)
            # 获取该专业所有学生
            students = Student.objects.filter(major=major)
            # 批量添加（自动去重）
            added = 0
            for student in students:
                if course.students.filter(student_id=student.student_id).exists():
                    continue
                course.students.add(student)
                added += 1

            course.numbers += added
            course.save()
            messages.success(request, f'成功导入{added}名学生')

        except Exception as e:
            messages.error(request, f'导入失败：{str(e)}')

        return redirect('teacher:students', course_id=course_id)

def get_majors(request):
    college_id = request.GET.get('college_id')
    majors = Major.objects.filter(college_id=college_id).values('major_id', 'major_name')
    return JsonResponse(list(majors), safe=False)


def delete_student(request, course_id,student_id):
    # course_id = request.POST.get('course_id')
    # student_id = request.POST.get('student_id')
    course = Course.objects.get(course_id=course_id)
    student = Student.objects.get(student_id=student_id)
    course.students.remove(student)
    course.numbers -= 1
    course.save()

    return redirect('teacher:students', course_id=course_id)

class CreateReportView(CreateView):
    model = ReportAssignment
    fields = ['title', 'description', 'attachment', 'deadline']
    template_name = 'teacher/report_create.html'

    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        form.instance.course = course
        form.instance.created_by = self.request.user.teacher
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('teacher:reports',
                       kwargs={'course_id': self.kwargs['course_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前课程到上下文
        context['current_course'] = get_object_or_404(
            Course,
            course_id=self.kwargs['course_id']
        )
        return context

class ReportListView(ListView):
    model = ReportAssignment
    template_name = 'teacher/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return ReportAssignment.objects.filter(
            course_id=self.kwargs['course_id']
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前课程到上下文
        context['current_course'] = get_object_or_404(
            Course,
            course_id=self.kwargs['course_id']
        )
        return context


class DiscussionListView(ListView):
    template_name = 'teacher/discussion_list.html'

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return DiscussionTopic.objects.filter(course_id=course_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前课程到上下文
        context['current_course'] = get_object_or_404(
            Course,
            course_id=self.kwargs['course_id']
        )
        return context

class CreateDiscussionView(CreateView):
    model = DiscussionTopic
    fields = ['title', 'content']
    template_name = 'teacher/create_discussion.html'

    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        form.instance.course = course
        form.instance.created_by = self.request.user.teacher
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前课程到上下文
        context['current_course'] = get_object_or_404(
            Course,
            course_id=self.kwargs['course_id']
        )
        return context

    def get_success_url(self):
        return reverse('teacher:discussion_list',
                     kwargs={'course_id': self.kwargs['course_id']})

