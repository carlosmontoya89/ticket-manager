from django.urls import path
from rest_framework.authtoken import views

from api.views import UserRegistrationAPIView, TicketListCreateAPIView

urlpatterns = [
    path('login/', views.obtain_auth_token),
    path('register/', UserRegistrationAPIView.as_view(), name='user_registration'),
    path('tickets/', TicketListCreateAPIView.as_view(), name='ticket_list_create'),
]
