from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', views.RegistrationView.as_view()),
    path('login/', views.CustomLoginView.as_view())

]
