from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):
    class Meta:
        ordering = ['-id']

    STATUS_CHOICES = (
        ('CREATED', 'Created'),
        ('COMPLETED', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CREATED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_images = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class Image(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='images', on_delete=models.CASCADE)
    cloudinary_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
