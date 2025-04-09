#权限装饰器
from django.http import HttpResponseForbidden
from functools import wraps

def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'teacher':
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'student':
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)
    return _wrapped_view