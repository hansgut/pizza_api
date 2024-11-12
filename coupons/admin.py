from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_value', 'expiration_date', 'is_active', 'used_count']
    list_filter = ['is_active', 'used_count']
    search_fields = ['code']
