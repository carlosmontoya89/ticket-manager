from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ticket, Image

MAX_FILE_SIZE_MB = 10  # Maximum file size allowed in megabytes


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


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


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'cloudinary_url', 'uploaded_at', 'ticket']
        read_only_fields = ['id', 'created_at']


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, value):
        self.validate_file_size(value)
        self.validate_file_format(value)
        return value

    def validate_file_size(self, value):
        # Check if file size exceeds the maximum allowed size
        max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
        if value.size > max_size_bytes:
            raise ValidationError(f"File size exceeds the maximum limit of {MAX_FILE_SIZE_MB} MB.")

    def validate_file_format(self, value):
        # Get the file extension
        ext = value.name.split('.')[-1].lower()
        # Define allowed image formats
        allowed_formats = ['jpg', 'jpeg', 'png', 'gif']
        # Validate if the file format is allowed
        if ext not in allowed_formats:
            raise ValidationError(f"Only {', '.join(allowed_formats)} formats are allowed.")