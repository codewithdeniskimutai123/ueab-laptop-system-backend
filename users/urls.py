from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register-user'),
    path('list/', views.get_users, name='get-users'),
    path('<int:pk>/', views.get_user, name='get-user'),
    path("student_profile/", views.student_profile, name="student_profile"),
    path("update_profile/", views.update_profile, name="update_profile"),
    path("search_student/", views.search_student, name="search_student"),
]


  