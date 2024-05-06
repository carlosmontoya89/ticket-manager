import cloudinary
from cloudinary.uploader import upload as cloudinary_upload


class ImageUploader:
    def __init__(self, strategy):
        self.strategy = strategy

    def upload_image(self, image_file, **kwargs):
        return self.strategy.upload_image(image_file, **kwargs)


class CloudinaryStrategy:
    def __init__(self):
        self._authenticate()

    def _authenticate(self):
        cloudinary.config()

    def upload_image(self, image_file, **kwargs):
        response = cloudinary_upload(image_file, **kwargs)
        return response['url']
