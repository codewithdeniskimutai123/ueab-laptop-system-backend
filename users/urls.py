from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register-user'),
    path('list/', views.get_users, name='get-users'),
    path('<int:pk>/', views.get_user, name='get-user'),
]