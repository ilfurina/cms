from os.path import basename

from django.views.decorators.http import require_POST
from django.views.generic import DetailView, CreateView

from cms.settings import BASE_DIR
from django.http import HttpResponseForbidden, FileResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.decorators import student_required
from django.contrib import messages
from teacher.models import Course, CourseResource, Assignment
from sys_admin.models import College, Major
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .recommender import CourseRecommender



@student_required
def dashboard(request):
    student = request.user.student
    enrolled_courses = student.courses.all()
    recommender = CourseRecommender()
    recommended_courses = recommender.get_recommendations(student)
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
from .models import Student, AssignmentSubmission, StudentAnswer
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

    submitted_assignments = AssignmentSubmission.objects.filter(
        student=student,
        is_submitted=1,
        assignment__in=assignments
    ).values_list('assignment_id', flat=True)

    return render(request, 'student/course_detail.html', {
        'course': course,
        'assignments': assignments,
        'now': now,
        'resources': resources,
        'submitted_assignments': set(submitted_assignments),

    })

from polymorphic.query import PolymorphicQuerySet
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    now = timezone.now()

    # 验证时间有效性
    if not (assignment.start_time <= now <= assignment.end_time):
        return HttpResponseForbidden("当前不在作业有效期内")

    # 获取或创建提交记录
    submission, created = AssignmentSubmission.objects.get_or_create(
        assignment=assignment,
        student=request.user.student
    )

    # 获取已答题目
    # answered = {ans.question_id: ans.answer for ans in submission.studentanswer_set.all()}
    answered = {
        ans.question_id: ans.answer
        for ans in submission.studentanswer_set.all().prefetch_related('question')
    }

    return render(request, 'student/assignment_detail.html', {
        'assignment': assignment,
        'submission': submission,
        'answered': answered
    })

@require_POST
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = get_object_or_404(AssignmentSubmission,
                                   assignment=assignment,
                                   student=request.user.student
                                   )

    if submission.is_submitted:
        return HttpResponseBadRequest("作业已提交，不可重复提交")

    # 处理每道题的答案
    for question in assignment.questions.all():
        answer_key = f"question_{question.id}"
        if answer_key in request.POST:
            StudentAnswer.objects.update_or_create(
                submission=submission,
                question=question,
                defaults={'answer': request.POST[answer_key]}
            )

    # 标记为已提交
    submission.is_submitted = True
    submission.save()

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

from teacher.models import DiscussionTopic, DiscussionPost

class StudentDiscussionView(DetailView):
    model = DiscussionTopic
    template_name = 'student/discussion_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = get_object_or_404(DiscussionTopic, pk=self.kwargs['pk'])
        if not self.object.course:  # 增加课程存在性校验
            raise Http404("讨论主题未关联有效课程")
        return context

class CreatePostView(LoginRequiredMixin, CreateView):
    model = DiscussionPost
    fields = ['content']
    template_name = 'student/create_post.html'

    def form_valid(self, form):
        form.instance.topic = get_object_or_404(DiscussionTopic, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = get_object_or_404(DiscussionTopic, pk=self.kwargs['pk'])
        return context

