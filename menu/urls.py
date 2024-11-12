from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryListView, MenuItemListView, PizzaSizeListView, CrustTypeListView, SauceListView, \
    CheeseListView, ToppingListView

router = DefaultRouter()

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('menu-items/', MenuItemListView.as_view(), name='menu-item-list'),
    path('pizza-sizes/', PizzaSizeListView.as_view(), name='pizza-size-list'),
    path('crust-types/', CrustTypeListView.as_view(), name='crust-type-list'),
    path('sauces/', SauceListView.as_view(), name='sauce-list'),
    path('cheeses/', CheeseListView.as_view(), name='cheese-list'),
    path('toppings/', ToppingListView.as_view(), name='topping-list'),
    path('', include(router.urls)),
]
