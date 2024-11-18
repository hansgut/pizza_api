from rest_framework import generics, status

from .models import Order
from .serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Coupon
from rest_framework.response import Response


class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class OrderCouponView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        order = self.get_object()
        coupon_code = request.data.get('coupon', None)
        if coupon_code:
            try:
                # Fetch the coupon object
                coupon = Coupon.objects.get(code=coupon_code)
                # Apply the coupon to the order
                order.coupon = coupon
                order.apply_coupon()
                order.save()
            except Coupon.DoesNotExist:
                return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Coupon code not provided'}, status=status.HTTP_400_BAD_REQUEST)
        # Serialize the updated order
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        # Unapply the coupon from the order
        order.unapply_coupon()
        order.coupon = None
        order.save()
        # Serialize the updated order
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
