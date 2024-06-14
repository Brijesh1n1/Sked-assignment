from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('manage-expense', ExpenseManageView, basename='manage_expense')
urlpatterns = [
  path('', include(router.urls)),
  path('my-expense/<int:pk>/', MyExpenseAPIView.as_view()),
  path('friend-expense/<int:pk>/', ListFreindsExpenseView.as_view()),
]