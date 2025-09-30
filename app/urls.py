from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, UserRegistrationViewSet, LoginViewSet, LogoutViewSet, ProfileImageViewSet
from django.contrib.auth.models import User
from .serializers import UserSerializer

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'register', UserRegistrationViewSet, basename='register')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'profile', ProfileImageViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
