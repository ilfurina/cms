from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, FileResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from accounts.decorators import student_required
from django.contrib import messages
from teacher.models import Course, CourseResource, Assignment,Attendance,DiscussionTopic, DiscussionPost
from sys_admin.models import Major
from django.views import View
from .recommender import CourseRecommender
from student.train import train_model
from .models import Student, AssignmentSubmission, StudentAnswer
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

import base64
import json
import pickle
import cv2
import numpy as np
from PIL.Image import Image

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
        'face_collected':user.face_collected,
    }
    return render(request, 'student/info.html', {'information': information})

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

@student_required
def course_recommendations(request):
    student = request.user.student
    enrolled_courses = student.courses.all()
    recommended_courses = CourseRecommender().get_recommendations(student)

    return render(request, 'student/recommendations.html', {
        'enrolled_courses': enrolled_courses,
        'recommended_courses': recommended_courses
    })

def course_detail(request, course_id):
    student = request.user.student
    course = get_object_or_404(Course, course_id=course_id)
    attendance = Attendance.objects.filter(
        course=course,
        is_active=True
    ).first()
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

    # 获取已批改作业的分数
    graded_submissions = AssignmentSubmission.objects.filter(
        student=student,
        assignment__in=assignments,
        is_submitted=True
    ).values('assignment_id', 'score')

    assignment_scores = {s['assignment_id']: s['score'] for s in graded_submissions}

    return render(request, 'student/course_detail.html', {
        'course': course,
        'assignments': assignments,
        'now': now,
        'resources': resources,
        'submitted_assignments': set(submitted_assignments),
        'attendance': attendance,
        'assignment_scores': assignment_scores,
    })


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

    total_score = 0
    for answer in submission.studentanswer_set.all():
        question = answer.question
        if question.question_type == 'single':
            correct = question.singlechoicequestion.correct_answer
            score = 10 if answer.answer == correct else 0
        elif question.question_type == 'multiple':
            correct = set(question.multiplechoicequestion.correct_answers)
            score = 10 if set(answer.answer) == correct else 0
        elif question.question_type == 'fill':
            keywords = question.fillinblankquestion.keywords
            matches = sum(1 for kw in keywords if kw.lower() in answer.answer.lower())
            score = round(10 * (matches / len(keywords)))
        else:
            score = 0  # 问答题等待教师批改

        answer.score = score
        answer.save()
        total_score += score

    submission.score = total_score
    submission.save()

    return redirect('student:course_detail', course_id=assignment.course.course_id)


from urllib.parse import quote
def download_resource(request, filename):
    resource = get_object_or_404(CourseResource, file=filename)
    file_path = resource.file.path

    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'application/octet-stream'

    encoded_filename = quote(resource.filename)
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"

    return response

# 讨论主题详情视图
def discussion_detail(request, pk):
    topic = get_object_or_404(DiscussionTopic, pk=pk)

    # 课程存在性校验
    if not topic.course:
        raise Http404("讨论主题未关联有效课程")

    context = {
        'topic': topic,
        'object': topic  # 保持与原有模板变量兼容
    }
    return render(request, 'student/discussion_detail.html', context)


# 创建帖子视图
@login_required
def create_post(request, pk):
    topic = get_object_or_404(DiscussionTopic, pk=pk)
    student = get_object_or_404(Student, user=request.user)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            DiscussionPost.objects.create(
                topic=topic,
                author=request.user,
                content=content
            )
            return redirect('student:discussion_detail', pk=pk)

    context = {
        'topic': topic,
        'form': {'content': ''}  # 保持与模板兼容
    }
    return render(request, 'student/create_post.html', context)


# class StudentDiscussionView(DetailView):
#     model = DiscussionTopic
#     template_name = 'student/discussion_detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['topic'] = get_object_or_404(DiscussionTopic, pk=self.kwargs['pk'])
#         if not self.object.course:  # 增加课程存在性校验
#             raise Http404("讨论主题未关联有效课程")
#         return context
#
# class CreatePostView(LoginRequiredMixin, CreateView):
#     model = DiscussionPost
#     fields = ['content']
#     template_name = 'student/create_post.html'
#
#     def form_valid(self, form):
#         form.instance.topic = get_object_or_404(DiscussionTopic, pk=self.kwargs['pk'])
#         form.instance.author = self.request.user
#         return super().form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['topic'] = get_object_or_404(DiscussionTopic, pk=self.kwargs['pk'])
#         return context


@login_required
def start_capture(request):
    """初始化采集，清空旧数据"""
    if request.method == 'POST':
        student = request.user.student  # 假设Student模型与User关联
        save_dir = os.path.join('files', 'face_pictures', str(student.student_id))

        try:
            # 删除已有文件
            if os.path.exists(save_dir):
                for filename in os.listdir(save_dir):
                    file_path = os.path.join(save_dir, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
            else:
                os.makedirs(save_dir, exist_ok=True)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def upload_face(request):
    """处理图片上传"""
    if request.method == 'POST':
        student = request.user.student
        student_id = student.student_id
        save_dir = os.path.join('files', 'face_pictures', str(student_id))

        try:
            # 创建存储目录
            os.makedirs(save_dir, exist_ok=True)

            # 获取当前图片序号
            existing = len(os.listdir(save_dir))
            if existing >= 30:
                return JsonResponse({'success': False, 'error': '已达到最大数量'})

            # 处理上传的图片
            image_file = request.FILES.get('image')
            if image_file:
                # 生成文件名
                filename = f"{existing + 1:03d}.jpg"
                save_path = os.path.join(save_dir, filename)

                # 转换为灰度并保存
                img = Image.open(image_file)
                gray_img = img.convert('L')
                gray_img.save(save_path, 'JPEG', quality=85)
                # 图片上传后调用图片进行训练
                label_dict = train_model()
                with open('files/face_data/label_dict.pkl', 'wb') as f:
                    pickle.dump(label_dict, f) #将训练结果保存到文件中

                student.face_collected  = True
                student.save() #将状态改为已保存

                return JsonResponse({'success': True, 'saved_path': save_path})
            return JsonResponse({'success': False, 'error': '未接收到图片'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@student_required
@require_http_methods(["POST"])
def check_in(request, course_id):
    # 获取必要数据
    student = request.user.student
    course = get_object_or_404(Course, course_id=course_id)
    data = json.loads(request.body)

    # 验证签到活动
    attendance = Attendance.objects.filter(
        course=course,
        is_active=True
    ).order_by('-start_time').first()

    if not attendance:
        return JsonResponse({'success': False, 'error': '没有进行中的签到'})

    # 验证验证码
    if data['code'] != attendance.checkin_code:
        return JsonResponse({'success': False, 'error': '验证码错误'})

    # 人脸识别验证
    try:
        # 转换Base64图像
        image_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        # 加载模型和标签
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('files/face_data/face_model.yml')

        with open('files/face_data/label_dict.pkl', 'rb') as f:
            label_dict = pickle.load(f)

        # 人脸检测
        detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        faces = detector.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)

        if len(faces) != 1:
            return JsonResponse({'success': False, 'error': '检测到多张人脸或未检测到人脸'})

        # 识别处理
        x, y, w, h = faces[0]
        face_roi = img[y:y + h, x:x + w]
        label, confidence = recognizer.predict(face_roi)

        # 验证结果
        expected_id = student.student_id
        recognized_id = label_dict.get(label)
        student = Student.objects.filter(student_id=recognized_id).first()
        name = student.name

        if confidence > 70 or recognized_id != expected_id:
            return JsonResponse({'success': False, 'error': '人脸识别验证失败','recognized_id': recognized_id})

        # 记录签到
        attendance.checked_students.add(student)
        return JsonResponse({'success': True,'recognized_id': recognized_id})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

