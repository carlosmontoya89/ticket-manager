from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Image, Ticket
from .serializers import (
    ImageUploadSerializer,
    UserSerializer,
    TicketSerializer,
    ImageSerializer,
)
from .authentication import BearerTokenAuthentication
from .pagination import TicketPagination
from .tasks import upload_image_to_cloudinary


class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketListCreateAPIView(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [BearerTokenAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'created_at']
    pagination_class = TicketPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class TicketImagesAPIView(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [BearerTokenAuthentication]

    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        return Image.objects.filter(ticket_id=ticket_id, ticket__user=self.request.user)

    def create(self, request, *args, **kwargs):
        ticket_id = kwargs['ticket_id']
        try:
            ticket = Ticket.objects.get(pk=ticket_id, user=request.user)
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND
            )
        if ticket.status == 'COMPLETED':
            return Response(
                {'error': 'Cannot upload more images. Ticket status is completed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            upload_image_to_cloudinary.delay(image.read(), ticket_id)
            return Response(
                {'message': 'Image uploaded successfully'},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetailAPIView(generics.RetrieveAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [BearerTokenAuthentication]

    def get_object(self):
        ticket_id = self.kwargs.get('ticket_id')
        return get_object_or_404(Ticket, pk=ticket_id, user=self.request.user)
