from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home and static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Authentication routes
    path('accounts/signup/', views.signup, name='signup'),
    
    # Dashboard and main features
    path('dashboard/', views.dashboard, name='dashboard'),
    path('timeline/', views.timeline, name='timeline'),
    path('on-this-day/', views.on_this_day, name='on-this-day'),
    
    # Time Capsule routes
    path('capsules/', views.CapsuleListView.as_view(), name='capsules'),
    path('capsules/<int:pk>/', views.CapsuleDetailView.as_view(), name='capsule-detail'),
    path('capsules/new/', views.CapsuleCreateView.as_view(), name='capsule-create'),
    path('capsules/<int:pk>/edit/', views.CapsuleUpdateView.as_view(), name='capsule-update'),
    path('capsules/<int:pk>/delete/', views.delete_capsule, name='capsule-delete'),
    path('capsules/<int:pk>/open/', views.open_capsule, name='open-capsule'),
    
    # Capsule Item routes
    path('capsules/<int:capsule_id>/add-text/', views.add_text_item, name='add-text-item'),
    path('capsules/<int:capsule_id>/add-image/', views.add_image_item, name='add-image-item'),
    path('capsules/<int:capsule_id>/add-link/', views.add_link_item, name='add-link-item'),
    path('items/<int:item_id>/delete/', views.delete_item, name='delete-item'),
]

# Add media files serving during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 