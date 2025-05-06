from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages

from .models import TimeCapsule, CapsuleItem, UserProfile
from .forms import (
    UserRegistrationForm, TimeCapsuleForm, TextItemForm, 
    ImageItemForm, LinkItemForm
)

# Home and public pages
def home(request):
    """View for the landing page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Since all capsules are private, we don't show any on the home page
    context = {}
    return render(request, 'home.html', context)

def about(request):
    """View for the about page"""
    return render(request, 'about.html')

# Authentication views
def signup(request):
    """View for user registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

# Dashboard view
@login_required
def dashboard(request):
    """View for user dashboard"""
    # Get user's capsules
    upcoming_capsules = TimeCapsule.objects.filter(
        user=request.user,
        is_opened=False,
        open_date__gt=timezone.now()
    ).order_by('open_date')[:5]
    
    ready_capsules = TimeCapsule.objects.filter(
        user=request.user,
        is_opened=False,
        open_date__lte=timezone.now()
    )
    
    opened_capsules = TimeCapsule.objects.filter(
        user=request.user,
        is_opened=True
    ).order_by('-created_at')[:5]
    
    # Get on this day capsules
    today = timezone.now().date()
    on_this_day = []
    for capsule in TimeCapsule.objects.filter(user=request.user, is_opened=True):
        if capsule.created_at.day == today.day and capsule.created_at.month == today.month:
            on_this_day.append(capsule)
    
    context = {
        'upcoming_capsules': upcoming_capsules,
        'ready_capsules': ready_capsules,
        'opened_capsules': opened_capsules,
        'on_this_day': on_this_day,
    }
    
    return render(request, 'dashboard.html', context)

# Time Capsule views
class CapsuleListView(LoginRequiredMixin, ListView):
    """View for listing all user's capsules"""
    model = TimeCapsule
    template_name = 'capsules/index.html'
    context_object_name = 'capsules'
    
    def get_queryset(self):
        return TimeCapsule.objects.filter(user=self.request.user)

class CapsuleDetailView(UserPassesTestMixin, DetailView):
    """View for displaying a single capsule"""
    model = TimeCapsule
    template_name = 'capsules/detail.html'
    context_object_name = 'capsule'
    
    def test_func(self):
        """Check if the user can view this capsule"""
        capsule = self.get_object()
        
        # User can view if they own it
        if capsule.user == self.request.user:
            return True
        
        # All capsules are private, so only owner can view
        return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capsule = self.get_object()
        
        # Add items to context
        context['items'] = CapsuleItem.objects.filter(capsule=capsule)
        
        # Check if the user can open the capsule
        context['can_open'] = (
            capsule.user == self.request.user and 
            capsule.is_ready_to_open and 
            not capsule.is_opened
        )
        
        return context

class CapsuleCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new capsule"""
    model = TimeCapsule
    form_class = TimeCapsuleForm
    template_name = 'capsules/form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Time Capsule'
        return context

class CapsuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating a capsule"""
    model = TimeCapsule
    form_class = TimeCapsuleForm
    template_name = 'capsules/form.html'
    
    def test_func(self):
        """Check if user can edit this capsule"""
        capsule = self.get_object()
        return capsule.user == self.request.user and not capsule.is_opened
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Time Capsule'
        return context

@login_required
def delete_capsule(request, pk):
    """View for deleting a capsule"""
    capsule = get_object_or_404(TimeCapsule, pk=pk)
    
    # Ensure the user owns this capsule
    if capsule.user != request.user:
        messages.error(request, "You cannot delete someone else's capsule.")
        return redirect('capsules')
    
    # Delete the capsule
    title = capsule.title
    capsule.delete()
    messages.success(request, f"Capsule '{title}' has been deleted.")
    return redirect('capsules')

@login_required
def open_capsule(request, pk):
    """View for opening a time capsule"""
    capsule = get_object_or_404(TimeCapsule, pk=pk)
    
    # Ensure the user owns this capsule and it's ready to open
    if capsule.user != request.user:
        messages.error(request, "You cannot open someone else's capsule.")
        return redirect('capsules')
    
    if not capsule.is_ready_to_open:
        messages.error(request, "This capsule is not yet ready to be opened.")
        return redirect('capsule-detail', pk=capsule.pk)
    
    # Open the capsule
    capsule.is_opened = True
    capsule.save()
    
    messages.success(request, f"You've opened '{capsule.title}'!")
    return redirect('capsule-detail', pk=capsule.pk)

# Capsule Item views
@login_required
def add_text_item(request, capsule_id):
    """View for adding a text item to a capsule"""
    capsule = get_object_or_404(TimeCapsule, pk=capsule_id)
    
    # Ensure the user owns this capsule and it's not opened
    if capsule.user != request.user:
        messages.error(request, "You cannot add items to someone else's capsule.")
        return redirect('capsules')
    
    if capsule.is_opened:
        messages.error(request, "You cannot add items to an opened capsule.")
        return redirect('capsule-detail', pk=capsule.pk)
    
    if request.method == 'POST':
        form = TextItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.capsule = capsule
            item.item_type = 'text'
            item.save()
            messages.success(request, "Text item added successfully!")
            return redirect('capsule-detail', pk=capsule.pk)
    else:
        form = TextItemForm()
    
    context = {
        'form': form,
        'capsule': capsule,
        'title': 'Add Text Item',
    }
    
    return render(request, 'items/form.html', context)

@login_required
def add_image_item(request, capsule_id):
    """View for adding an image item to a capsule"""
    capsule = get_object_or_404(TimeCapsule, pk=capsule_id)
    
    # Ensure the user owns this capsule and it's not opened
    if capsule.user != request.user:
        messages.error(request, "You cannot add items to someone else's capsule.")
        return redirect('capsules')
    
    if capsule.is_opened:
        messages.error(request, "You cannot add items to an opened capsule.")
        return redirect('capsule-detail', pk=capsule.pk)
    
    if request.method == 'POST':
        form = ImageItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.capsule = capsule
            item.item_type = 'image'
            item.save()
            messages.success(request, "Image item added successfully!")
            return redirect('capsule-detail', pk=capsule.pk)
    else:
        form = ImageItemForm()
    
    context = {
        'form': form,
        'capsule': capsule,
        'title': 'Add Image Item',
    }
    
    return render(request, 'items/form.html', context)

@login_required
def add_link_item(request, capsule_id):
    """View for adding a link item to a capsule"""
    capsule = get_object_or_404(TimeCapsule, pk=capsule_id)
    
    # Ensure the user owns this capsule and it's not opened
    if capsule.user != request.user:
        messages.error(request, "You cannot add items to someone else's capsule.")
        return redirect('capsules')
    
    if capsule.is_opened:
        messages.error(request, "You cannot add items to an opened capsule.")
        return redirect('capsule-detail', pk=capsule.pk)
    
    if request.method == 'POST':
        form = LinkItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.capsule = capsule
            item.item_type = 'link'
            item.save()
            messages.success(request, "Link item added successfully!")
            return redirect('capsule-detail', pk=capsule.pk)
    else:
        form = LinkItemForm()
    
    context = {
        'form': form,
        'capsule': capsule,
        'title': 'Add Link Item',
    }
    
    return render(request, 'items/form.html', context)

@login_required
def delete_item(request, item_id):
    """View for deleting an item from a capsule"""
    item = get_object_or_404(CapsuleItem, pk=item_id)
    capsule = item.capsule
    
    # Ensure the user owns this capsule and it's not opened
    if capsule.user != request.user:
        messages.error(request, "You cannot remove items from someone else's capsule.")
        return redirect('capsules')
    
    if capsule.is_opened:
        messages.error(request, "You cannot remove items from an opened capsule.")
        return redirect('capsule-detail', pk=capsule.pk)
    
    # Delete the item immediately
    item.delete()
    messages.success(request, "Item removed successfully!")
    return redirect('capsule-detail', pk=capsule.pk)

# Timeline views
@login_required
def timeline(request):
    """View for the timeline of user's capsules"""
    capsules = TimeCapsule.objects.filter(
        user=request.user,
        is_opened=True
    ).order_by('created_at')
    
    context = {
        'capsules': capsules
    }
    
    return render(request, 'timeline.html', context)

@login_required
def on_this_day(request):
    """View for 'On This Day' feature"""
    today = timezone.now().date()
    
    # Find capsules created on this day in previous years
    matching_capsules = []
    for capsule in TimeCapsule.objects.filter(user=request.user, is_opened=True):
        if capsule.created_at.day == today.day and capsule.created_at.month == today.month:
            matching_capsules.append(capsule)
    
    context = {
        'today': today,
        'capsules': matching_capsules,
    }
    
    return render(request, 'on_this_day.html', context)
