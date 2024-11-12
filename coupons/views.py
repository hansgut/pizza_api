from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Coupon
from .serializers import CouponApplySerializer


class ApplyCouponView(generics.GenericAPIView):
    serializer_class = CouponApplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        coupon = Coupon.objects.get(code=code)
        return Response({"message": "Coupon applied successfully", "discount_value": coupon.discount_value},
                        status=status.HTTP_200_OK)
