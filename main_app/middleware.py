import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings

class CloudinaryInitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
            secure=True
        )

    def __call__(self, request):
        return self.get_response(request) 