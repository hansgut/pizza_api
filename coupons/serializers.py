from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'description', 'discount_type', 'discount_value', 'expiration_date', 'is_active',
                  'usage_limit', 'used_count']


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")

        if not coupon.is_valid():
            raise serializers.ValidationError("This coupon is not valid.")

        return value
