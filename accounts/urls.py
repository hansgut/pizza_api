from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, UserDetailView, UserAddressView, UserAddressDetailView

router = DefaultRouter()

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserDetailView.as_view(), name='user-profile'),
    path('addresses/', UserAddressView.as_view(), name='user-address'),
    path("addresses/<int:pk>/", UserAddressDetailView.as_view(), name='user-address-detail'),
    path('', include(router.urls)),
]
