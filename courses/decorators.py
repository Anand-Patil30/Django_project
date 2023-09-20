from django.http import HttpResponseForbidden
from functools import wraps

from django.shortcuts import render

def teacher_required(func):
    @wraps(func)
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated and request.user.role == "teacher":
            return func(request,*args,**kwargs)
        else:
            return render( request,'courses/error.html')

    return wrapper

def student_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "student":
            return func(request, *args, **kwargs)
        else:
            return render( request,'courses/error.html')
    return wrapper