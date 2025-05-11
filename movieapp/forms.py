from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.validators import FileExtensionValidator


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].validators = [
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ]
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2*1024*1024: 
                raise forms.ValidationError("Файл слишком большой (максимум 2MB)")
            return avatar
        return None