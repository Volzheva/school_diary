from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
import datetime
from .models import User
from .forms import UserRegistrationForm
from django.urls import reverse_lazy


class RegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'registration.html'
    success_url = reverse_lazy('login')
