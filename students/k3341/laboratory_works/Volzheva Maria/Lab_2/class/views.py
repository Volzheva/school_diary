from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
import datetime
from .models import User, Subject, Homework, Submission
from .forms import UserRegistrationForm, CustomAuthenticationForm, CreateSubmissionForm
from django.urls import reverse_lazy
from Lab_2 import settings
from django.contrib.auth.decorators import login_required
import re
from django.http import HttpResponse


def get_welcome(request):
    return render(request, template_name='welcome.html')


class RegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'registration.html'
    success_url = '/login/'


class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomAuthenticationForm
    LOGIN_REDIRECT_URL = '/home/'


@login_required
def get_home(request):
    print("IMPORTANT ", request)
    try:
        our_user = request.user
        if our_user.role == 'student':
            all_homeworks = Homework.objects.all().filter(classes=our_user.student_class)
            all_submissions = Submission.objects.all().filter(student=our_user)
            context = {'our_user': our_user, 'all_homeworks': all_homeworks, 'all_submissions': all_submissions}
            return render(request, 'home_student.html', context)
        context = {"our_user": our_user}
        return render(request, 'home_teacher.html', context)
    except Exception as e:
        # Логгирование или обработка ошибки
        raise Http404("Страница не найдена")  # Измените на нужный вам ответ


@login_required
def get_homework(request, pk):
    try:
        our_user = request.user
        homework_info = Homework.objects.get(pk=pk)
        context = {'our_user': our_user, 'homework_info': homework_info}
        return render(request, 'homework_info.html', context)
    except Exception as e:
        raise Http404("Страница не найдена")


class HomeworkRetrieveView(DetailView):
    model = Homework


def create_submission(request, pk):
    homework = Homework.objects.get(pk=pk)
    form = CreateSubmissionForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.homework = homework
        instance.student = request.user
        instance.submitted_at = datetime.datetime.now()
        instance.save()
    return render(request, "create_submission.html", {'form': CreateSubmissionForm(), 'our_user': request.user})


@login_required
def get_submission(request, pk):
    try:
        our_user = request.user
        submission_info = Submission.objects.get(pk=pk)
        context = {'our_user': our_user, 'submission_info': submission_info}
        return render(request, 'submission_info.html', context)
    except Exception as e:
        raise Http404("Страница не найдена")


# class SubmissionCreateView(CreateView):
#     model = Submission
#     template_name = 'create_submission.html'
#     fields = ['state_number', 'brand', 'model', 'color']
#     homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
#     student = models.ForeignKey(User, on_delete=models.CASCADE)
#     submitted_text = models.TextField()
#     submitted_at = models.DateTimeField(auto_now_add=True)
#     grade = models.IntegerField(blank=True, null=True)
#
#
# def get_homework_create_submission(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}
#     form = HomeworkForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#     context = {'form': form}
#     return render(request, "create_сar_owner.html", context)





