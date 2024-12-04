from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.get_welcome),
    path('registration/', views.RegistrationView.as_view()),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('home/', views.get_home),
    path('homework/<int:pk>/', views.get_homework),
    path('homework/<int:pk>/new_submission/', views.create_submission),
    path('submission/<int:pk>/', views.get_submission),

]
