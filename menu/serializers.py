from rest_framework import serializers
from .models import Category, MenuItem, PizzaSize, CrustType, Sauce, Cheese, Topping


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'is_pizza', 'is_active', 'category', 'image']


class PizzaSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PizzaSize
        fields = ['id', 'name', 'diameter', 'base_price']


class CrustTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrustType
        fields = ['id', 'name', 'price']


class SauceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sauce
        fields = ['id', 'name', 'price']


class CheeseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cheese
        fields = ['id', 'name', 'price']


class ToppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topping
        fields = ['id', 'name', 'price', 'is_vegetarian', 'is_vegan', 'is_meat', 'is_active']
