from rest_framework import generics, permissions
from .models import Category, MenuItem, PizzaSize, CrustType, Sauce, Cheese, Topping
from .serializers import CategorySerializer, MenuItemSerializer, PizzaSizeSerializer, CrustTypeSerializer, \
    SauceSerializer, CheeseSerializer, ToppingSerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]


class PizzaSizeListView(generics.ListAPIView):
    queryset = PizzaSize.objects.all()
    serializer_class = PizzaSizeSerializer
    permission_classes = [permissions.AllowAny]


class CrustTypeListView(generics.ListAPIView):
    queryset = CrustType.objects.all()
    serializer_class = CrustTypeSerializer
    permission_classes = [permissions.AllowAny]


class SauceListView(generics.ListAPIView):
    queryset = Sauce.objects.all()
    serializer_class = SauceSerializer
    permission_classes = [permissions.AllowAny]


class CheeseListView(generics.ListAPIView):
    queryset = Cheese.objects.all()
    serializer_class = CheeseSerializer
    permission_classes = [permissions.AllowAny]


class ToppingListView(generics.ListAPIView):
    queryset = Topping.objects.all()
    serializer_class = ToppingSerializer
    permission_classes = [permissions.AllowAny]
