from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id',
            'title',
            'description',
            'status',
            'created_at',
            'updated_at',
            'num_images',
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate_num_images(self, value):
        if value < 1:
            raise serializers.ValidationError("Number of images must be at least 1.")
        return value


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
