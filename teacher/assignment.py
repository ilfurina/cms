from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from accounts.decorators import teacher_required
from student.models import Student
from django.db.models import Count
from django.http import Http404

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
        # teacher = get_object_or_404(Teacher, teacher_id=request.user.teacher.teacher_id)


        questions = QuestionBase.objects.filter(teacher=request.user.teacher).prefetch_related(
            'singlechoicequestion',
            'multiplechoicequestion',
            'fillinblankquestion',
            'essayquestion'
        )
        # questions = (QuestionBase.objects.filter(teacher=request.user.teacher)
        #              .non_polymorphic().instance_of(SingleChoiceQuestion, MultipleChoiceQuestion, FillInBlankQuestion, EssayQuestion))

        # 获取已选中的题目
        selected = request.GET.getlist('selected')
        selected_questions = QuestionBase.objects.filter(id__in=selected)

        return render(request, 'teacher/assignment/create_exercises.html', {
            'current_course': course,
            'questions': questions,
            'selected_questions': selected_questions
        })

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

        return redirect('teacher:edit', course_id=course_id)




class ActiveAssignmentsView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)
        now = timezone.localtime()

        # 获取所有任务并按状态分类
        assignments = Assignment.objects.filter(course=course).order_by('-start_time')

        # 转换作业时间为本地时区
        # for assignment in assignments:
        #     assignment.start_time = timezone.localtime(assignment.start_time)
        #     assignment.end_time = timezone.localtime(assignment.end_time)

        return render(request, 'teacher/assignment/active_assignment.html', {
            'current_course': course,
            'assignments': assignments,
            'now': now  # 传递当前时间到模板
        })

# 题库导入功能

# 从题库中选择题目创建作业功能

@teacher_required
def assignment_progress(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    # 验证教师权限
    if course.teacher != request.user.teacher:
        raise Http404

    # 获取已提交学生
    submitted = Student.objects.filter(
        assignmentsubmission__assignment=assignment,
        assignmentsubmission__is_submitted=1
    ).distinct()

    # 获取未提交学生
    all_students = course.students.all()
    not_submitted = all_students.difference(submitted)

    # 统计比例
    total = all_students.count()
    submitted_count = submitted.count()
    not_submitted_count = total - submitted_count

    # 图表数据
    chart_data = {
        'labels': ['已完成', '未完成'],
        'datasets': [{
            'data': [submitted_count, not_submitted_count],
            'backgroundColor': ['#36a2eb', '#ff6384']
        }]
    }

    return render(request, 'teacher/assignment/assignment_progress.html', {
        'assignment': assignment,
        'submitted_students': submitted,
        'not_submitted_students': not_submitted,
        'chart_data': chart_data
    })
