from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import os

def get_image_path(instance, filename):
    """Generate a file path for an image uploaded to a capsule item"""
    return os.path.join('capsule_images', str(instance.capsule.user.id), filename)

# This function is kept only for migration compatibility
def get_audio_path(instance, filename):
    """Generate a file path for an audio uploaded to a capsule item"""
    return os.path.join('capsule_audio', str(instance.capsule.user.id), filename)

class TimeCapsule(models.Model):
    """Model representing a time capsule"""
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('friends', 'Friends Only'),
        ('public', 'Public'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    open_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='capsules')
    is_opened = models.BooleanField(default=False)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('capsule-detail', kwargs={'pk': self.pk})
    
    @property
    def is_ready_to_open(self):
        """Check if the capsule is ready to be opened based on open_date"""
        return timezone.now() >= self.open_date
    
    @property
    def days_until_open(self):
        """Calculate the number of days until the capsule can be opened"""
        if self.is_opened or self.is_ready_to_open:
            return 0
        
        delta = self.open_date - timezone.now()
        return max(0, delta.days)

class CapsuleItem(models.Model):
    """Model representing an item in a time capsule"""
    ITEM_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('link', 'Link'),
    ]
    
    capsule = models.ForeignKey(TimeCapsule, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    title = models.CharField(max_length=200)
    text_content = models.TextField(blank=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    link_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('capsule-detail', kwargs={'pk': self.capsule.pk})
        
    @property
    def preview(self):
        """Return a preview of the item based on its type"""
        if self.item_type == 'text':
            return self.text_content[:100] + '...' if len(self.text_content) > 100 else self.text_content
        elif self.item_type == 'image':
            return self.image.url if self.image else None
        elif self.item_type == 'link':
            return self.link_url
        return self.title

class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})
