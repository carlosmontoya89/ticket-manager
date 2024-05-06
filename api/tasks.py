from django_rq import job
from django.core.files.base import ContentFile

from .utils import CloudinaryStrategy, ImageUploader
from .models import Image, Ticket

uploader = ImageUploader(CloudinaryStrategy())


@job('default')
def upload_image_to_cloudinary(image_bytes, ticket_id):
    image_file = ContentFile(image_bytes)
    # Upload image to Cloudinary
    image_url = uploader.upload_image(image_file)
    # Save image URL to the Image model
    ticket = Ticket.objects.get(pk=ticket_id)
    Image.objects.create(ticket=ticket, cloudinary_url=image_url)
    # Check if all images for the ticket are uploaded
    if ticket.images.count() == ticket.num_images:
        # Update ticket status to completed
        ticket.status = 'COMPLETED'
        ticket.save()
