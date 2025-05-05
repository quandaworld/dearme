"""
URL configuration for dearme project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

urlpatterns = [
    path('accounts/logout/', LogoutView.as_view(next_page='/', http_method_names=['post', 'get']), name='logout'),
    
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    
    # Include the rest of the auth URLs
    path('accounts/', include('django.contrib.auth.urls')),
]
