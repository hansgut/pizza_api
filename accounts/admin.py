from django.contrib import admin
from .models import CustomerProfile


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
