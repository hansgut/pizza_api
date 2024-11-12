from django.contrib import admin
from .models import Category, MenuItem, PizzaSize, CrustType, Sauce, Cheese, Topping

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_pizza', 'is_active', 'category']
    search_fields = ['name']
    list_filter = ['is_pizza', 'is_active', 'category']
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'is_pizza', 'is_active', 'category', 'image')
        }),
    )


@admin.register(PizzaSize)
class PizzaSizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'diameter', 'base_price']
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'diameter', 'base_price')
        }),
    )


@admin.register(CrustType)
class CrustTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'price')
        }),
    )


@admin.register(Sauce)
class SauceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'price')
        }),
    )


@admin.register(Cheese)
class CheeseAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'price')
        }),
    )


@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'price')
        }),
    )
