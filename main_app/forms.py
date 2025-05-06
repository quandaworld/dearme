from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import TimeCapsule, CapsuleItem

class UserRegistrationForm(UserCreationForm):
    """Form for user registration with additional fields"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # The UserProfile will be created automatically via the signal
            
        return user

class TimeCapsuleForm(forms.ModelForm):
    """Form for creating and editing time capsules"""
    open_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        help_text='When would you like to open this capsule?'
    )
    
    class Meta:
        model = TimeCapsule
        fields = ['title', 'description', 'open_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_open_date(self):
        open_date = self.cleaned_data.get('open_date')
        
        # Ensure open_date is in the future
        if open_date and open_date <= timezone.now():
            raise forms.ValidationError("The opening date must be in the future")
        
        return open_date
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Always set visibility to private
        instance.visibility = 'private'
        if commit:
            instance.save()
        return instance

class TextItemForm(forms.ModelForm):
    """Form for creating and editing text items"""
    class Meta:
        model = CapsuleItem
        fields = ['title', 'text_content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super(TextItemForm, self).__init__(*args, **kwargs)
        self.instance.item_type = 'text'

class ImageItemForm(forms.ModelForm):
    """Form for creating and editing image items"""
    class Meta:
        model = CapsuleItem
        fields = ['title', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ImageItemForm, self).__init__(*args, **kwargs)
        self.instance.item_type = 'image'

class LinkItemForm(forms.ModelForm):
    """Form for creating and editing link items"""
    class Meta:
        model = CapsuleItem
        fields = ['title', 'link_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'link_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(LinkItemForm, self).__init__(*args, **kwargs)
        self.instance.item_type = 'link'
