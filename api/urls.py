from django.urls import path
from rest_framework.authtoken import views

from api.views import UserRegistrationAPIView

urlpatterns = [
    path('login/', views.obtain_auth_token),
    path('register/', UserRegistrationAPIView.as_view(), name='user_registration'),
]