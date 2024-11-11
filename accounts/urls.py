from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, UserDetailView

router = DefaultRouter()

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserDetailView.as_view(), name='user-profile'),
    path('', include(router.urls)),
]
