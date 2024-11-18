from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCouponView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/coupon/', OrderCouponView.as_view(), name='order-coupon'),
]
