from django.contrib import admin
from .models import CustomerProfile, Address


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'date_of_birth']
    search_fields = ['user__username', 'phone_number']
    list_filter = ['date_of_birth']
    readonly_fields = ['user']
    fieldsets = (
        (None, {
            'fields': ('user', 'phone_number', 'date_of_birth')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'street', 'city', 'zip_code', 'is_default', 'address_type']
    search_fields = ['customer__username', 'street', 'city', 'zip_code']
    list_filter = ['is_default', 'address_type']
    fieldsets = (
        (None, {
            'fields': ('customer', 'street', 'city', 'zip_code', 'is_default', 'address_type')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False
