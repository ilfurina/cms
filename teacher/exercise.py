import pandas as pd
from io import BytesIO
from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from teacher.models import Question, Exercise, ExerciseQuestionRelation


def import_questions_from_excel(file, teacher):
    df = pd.read_excel(BytesIO(file.read()))

    for _, row in df.iterrows():
        Question.objects.create(
            teacher=teacher,
            type=row['type'],
            content=row['content'],
            options=eval(row['options']) if pd.notnull(row['options']) else None,
            answer=row['answer'],
            difficulty=row.get('difficulty', 1)
        )


class CreateExerciseView(View):
    def post(self, request):
        teacher = request.user
        question_ids = request.POST.getlist('questions')

        exercise = Exercise.objects.create(
            teacher=teacher,
            title=request.POST['title'],
            description=request.POST.get('description', '')
        )

        # 添加题目并设置顺序和分值
        for order, qid in enumerate(question_ids):
            question = Question.objects.get(id=qid)
            ExerciseQuestionRelation.objects.create(
                exercise=exercise,
                question=question,
                order=order,
                score=request.POST.get(f'score_{qid}', 10)
            )

        return JsonResponse({'status': 'success', 'exercise_id': exercise.id})



# 发布练习
class PublishExerciseView(View):
    def post(self, request, exercise_id):
        exercise = Exercise.objects.get(id=exercise_id)
        exercise.is_published = True
        exercise.published_at = timezone.now()
        exercise.save()

        # 这里可以添加通知学生的逻辑
        return JsonResponse({'status': 'published'})

