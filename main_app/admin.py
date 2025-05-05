from django.contrib import admin
from .models import TimeCapsule, CapsuleItem, UserProfile

@admin.register(TimeCapsule)
class TimeCapsuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'open_date', 'is_opened', 'visibility')
    list_filter = ('is_opened', 'visibility', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(CapsuleItem)
class CapsuleItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'capsule', 'created_at')
    list_filter = ('item_type', 'created_at')
    search_fields = ('title', 'text_content', 'capsule__title')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth')
    search_fields = ('user__username', 'user__email', 'bio')
