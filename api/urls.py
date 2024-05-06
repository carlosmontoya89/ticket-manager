from django.urls import path
from rest_framework.authtoken import views

from api.views import (
    TicketDetailAPIView,
    UserRegistrationAPIView,
    TicketListCreateAPIView,
    TicketImagesAPIView,
)

urlpatterns = [
    path('login/', views.obtain_auth_token),
    path('register/', UserRegistrationAPIView.as_view(), name='user_registration'),
    path('tickets/', TicketListCreateAPIView.as_view(), name='ticket_list_create'),
    path(
        'tickets/<int:ticket_id>/', TicketDetailAPIView.as_view(), name='ticket_detail'
    ),
    path(
        'tickets/<int:ticket_id>/images/',
        TicketImagesAPIView.as_view(),
        name='ticket_images',
    ),
]
