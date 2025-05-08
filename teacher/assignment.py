# from django import forms
# from django.shortcuts import redirect, render, get_object_or_404
# from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
# from django.urls import reverse_lazy
# from .models import QuestionBank, SingleChoiceQuestion, MultipleChoiceQuestion, FillInBlankQuestion, EssayQuestion, \
#     Question
# from django.contrib import messages
# from django.http import JsonResponse
#
#
# class QuestionBankListView(ListView):
#     model = QuestionBank
#     template_name = 'teacher/exer/question_bank_list.html'
#
#     def get_queryset(self):
#         return QuestionBank.objects.filter(teacher=self.request.user.teacher)
#
#
# class CreateQuestionBankView(CreateView):
#     model = QuestionBank
#     fields = ['name']
#     template_name = 'teacher/exer/create_question_bank.html'
#
#     def form_valid(self, form):
#         form.instance.teacher = self.request.user.teacher
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('teacher:question_bank_detail', kwargs={'pk': self.object.pk})
#
#
# class QuestionBankDetailView(DetailView):
#     model = QuestionBank
#     template_name = 'teacher/exer/question_bank_detail.html'
#
#
# # 公共题目表单基类
# class BaseQuestionForm(forms.ModelForm):
#     class Meta:
#         model = Question
#         fields = ['content', 'difficulty']
#
#
# # 各题型表单
# class SingleChoiceForm(BaseQuestionForm):
#     options = forms.JSONField(
#         help_text='格式示例：["选项A", "选项B", "选项C"]',
#         widget=forms.TextInput(attrs={'placeholder': '输入选项列表'})
#     )
#     correct_answer = forms.CharField(max_length=200)
#
#
# class MultipleChoiceForm(BaseQuestionForm):
#     options = forms.JSONField(
#         help_text='格式示例：["选项A", "选项B", "选项C"]',
#         widget=forms.TextInput(attrs={'placeholder': '输入选项列表'})
#     )
#     correct_answers = forms.JSONField(
#         help_text='格式示例：[0,2] 对应正确选项的索引',
#         widget=forms.TextInput(attrs={'placeholder': '输入正确选项索引列表'})
#     )
#
#
# class FillInBlankForm(BaseQuestionForm):
#     correct_keywords = forms.JSONField(
#         help_text='格式示例：["关键词1", "关键词2"]',
#         widget=forms.TextInput(attrs={'placeholder': '输入正确关键词列表'})
#     )
#
#
# class EssayForm(BaseQuestionForm):
#     reference_answer = forms.CharField(widget=forms.Textarea)
#     max_score = forms.IntegerField(min_value=1, initial=10)
#
#
# def add_question(request, bank_id):
#     bank = get_object_or_404(QuestionBank, pk=bank_id)
#     question_type = request.POST.get('question_type')
#
#     form_classes = {
#         'S': SingleChoiceForm,
#         'M': MultipleChoiceForm,
#         'F': FillInBlankForm,
#         'Q': EssayForm
#     }
#     question_type = request.GET.get('type') or request.POST.get('question_type', 'S')
#
#     if request.method == 'POST':
#         form = form_classes[question_type](request.POST)
#         # 显式创建子类实例
#         if form.is_valid():
#             data = form.cleaned_data
#             # 根据题型创建具体子类
#             question_class = {
#                 'S': SingleChoiceQuestion,
#                 'M': MultipleChoiceQuestion,
#                 'F': FillInBlankQuestion,
#                 'Q': EssayQuestion
#             }[question_type]
#
#             question = question_class(
#                 bank=bank,
#                 content=data['content'],
#                 difficulty=data['difficulty'],
#                 # 添加各题型特有字段
#                 options=data.get('options'),
#                 correct_answer=data.get('correct_answer'),
#                 correct_answers=data.get('correct_answers'),
#                 correct_keywords=data.get('correct_keywords'),
#                 reference_answer=data.get('reference_answer')
#             )
#             question.save()
#
#
#             return redirect('teacher:question_bank_detail', pk=bank_id)
#         else:
#             # 添加错误提示
#             messages.error(request, f'表单验证失败：{form.errors}')
#
#     else:
#         form = form_classes[question_type]()  # 初始化对应表单
#
#
#     return render(request, 'teacher/exer/add_question.html', {
#         'bank': bank,
#         'form': form,
#         'question_types': Question.BANK_TYPE_CHOICES,
#         'selected_type': question_type  # 用于保持选项选中状态
#     })
