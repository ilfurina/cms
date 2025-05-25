from django.utils import timezone
from datetime import datetime
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from accounts.decorators import teacher_required
from student.models import Student, AssignmentSubmission, StudentAnswer
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
    # def get(self, request, course_id):
    #     course = get_object_or_404(Course, course_id=course_id)
    #     # teacher = get_object_or_404(Teacher, teacher_id=request.user.teacher.teacher_id)
    #
    #
    #     questions = QuestionBase.objects.filter(teacher=request.user.teacher).prefetch_related(
    #         'singlechoicequestion',
    #         'multiplechoicequestion',
    #         'fillinblankquestion',
    #         'essayquestion'
    #     )
    #
    #     # 获取已选中的题目
    #     selected = request.GET.getlist('selected')
    #     selected_questions = QuestionBase.objects.filter(id__in=selected)
    #
    #     return render(request, 'teacher/assignment/create_assignment.html', {
    #         'current_course': course,
    #         'questions': questions,
    #         'selected_questions': selected_questions
    #     })
    def get(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)
        selected_ids = request.GET.getlist('selected')
        selected_questions = QuestionBase.objects.filter(id__in=selected_ids)

        return render(request, 'teacher/assignment/create_assignment.html', {
            'current_course': course,
            'selected_questions': selected_questions
        })

    def post(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)

        # 创建作业
        # 转换 naive datetime 为 aware datetime
        naive_start = datetime.fromisoformat(request.POST['start_time'])
        naive_end = datetime.fromisoformat(request.POST['end_time'])

        assignment = Assignment.objects.create(
            course=course,
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            assignment_type='homework',
            start_time=timezone.make_aware(naive_start),  # 转换为 aware datetime
            end_time=timezone.make_aware(naive_end)  # 转换为 aware datetime
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

        return redirect('teacher:active_assignments', course_id=course_id)

class ActiveAssignmentsView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)
        now = timezone.now()

        # 获取所有任务并按状态分类
        assignments = Assignment.objects.filter(course=course).order_by('-start_time')


        return render(request, 'teacher/assignment/active_assignment.html', {
            'current_course': course,
            'assignments': assignments,
            'now': now  # 传递当前时间到模板
        })

# 题库导入功能

# 从题库中选择题目创建作业功能
@teacher_required
def question_bank(request):
    current_course = get_object_or_404(Course, course_id=request.GET.get('course_id'))
    # 按子类直接查询
    question_types = {
        'single': SingleChoiceQuestion.objects.filter(teacher=request.user.teacher),
        'multiple': MultipleChoiceQuestion.objects.filter(teacher=request.user.teacher),
        'fill': FillInBlankQuestion.objects.filter(teacher=request.user.teacher),
        'essay': EssayQuestion.objects.filter(teacher=request.user.teacher)
    }

    selected = request.GET.getlist('selected')

    return render(request, 'teacher/assignment/question_bank.html', {
        'question_types': question_types,
        'selected_questions': selected,
        'current_course': current_course
    })


@teacher_required
def assignment_progress(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    # 验证教师权限
    if course.teacher != request.user.teacher:
        raise Http404

    # 获取已提交学生
    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment,
        is_submitted=True
    ).select_related('student')
    # 获取未提交学生
    all_students = course.students.all()
    # not_submitted = all_students.difference(submitted)
    submitted_ids = submissions.values_list('student_id', flat=True)
    not_submitted = course.students.exclude(student_id__in=submitted_ids)

    # 统计比例
    total = all_students.count()
    submitted_count = submissions.count()
    not_submitted_count = total - submitted_count

    # 图表数据
    chart_data = {
        'labels': ['已完成', '未完成'],
        'datasets': [{
            'data': [submitted_count, not_submitted_count],
            'backgroundColor': ['#36a2eb', '#ff6384']
        }]
    }



    # 将提交记录按学生ID映射
    # submission_map = {s.student_id: s for s in submissions}

    return render(request, 'teacher/assignment/assignment_progress.html', {
        'assignment': assignment,
        'not_submitted_students': not_submitted,
        'chart_data': chart_data,
        'submissions': submissions,
    })

# 批改作业
@teacher_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    essay_questions = submission.assignment.questions.filter(question_type='essay')

    if request.method == 'POST':
        # 只更新问答题分数
        for question in essay_questions:
            score = int(request.POST.get(f'score_{question.id}', 0))
            StudentAnswer.objects.update_or_create(
                submission=submission,
                question=question,
                defaults={'score': score}
            )

        # 计算新总分（自动评分 + 教师批改）
        auto_score = sum(
            answer.score
            for answer in submission.studentanswer_set.exclude(question__question_type='essay')
        )
        essay_score = sum(
            answer.score
            for answer in submission.studentanswer_set.filter(question__question_type='essay')
        )

        submission.score = auto_score + essay_score
        submission.save()
        return redirect('teacher:assignment_progress', assignment_id=submission.assignment.id)

    return render(request, 'teacher/assignment/grade_submission.html', {
        'submission': submission,
        'essay_answers': submission.studentanswer_set.filter(question__question_type='essay')
    })



@teacher_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    # 验证教师权限
    if assignment.course.teacher != request.user.teacher:
        raise Http404("无权操作该作业")

    # 级联删除相关数据
    assignment.delete()
    return redirect('teacher:active_assignments', course_id=assignment.course.course_id)
