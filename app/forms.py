from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from app.models import Profile

MAX_UPLOAD_SIZE = 4*1024*1024


def validate_username_unused(username):
    if User.objects.filter(username=username).exists():
        raise forms.ValidationError('Username already registered')


def validate_nickname_unused(nickname):
    if Profile.objects.filter(nickname=nickname).exists():
        raise forms.ValidationError('Nickname already registered')


def validate_email_unused(email):
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError('E-mail already registered')


def validate_image_size(image):
    if image._size > MAX_UPLOAD_SIZE:
        raise ValidationError(f"Image size exceeds {MAX_UPLOAD_SIZE // 1024 // 1024} mb")


class AskForm(forms.Form):
    title = forms.CharField(max_length=140,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    text = forms.CharField(max_length=1000,
                           widget=forms.Textarea(attrs={'class': 'form-control'}))

    tags = forms.CharField(max_length=100, required=False, label_suffix=' (optional):',
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_tags(self):
        tags = [tag.strip() for tag in self.cleaned_data['tags'].split(',')]
        tags_limit = 3
        tag_len = 30
        if len(tags) > tags_limit:
            raise forms.ValidationError(f'Question must not contain more than {tags_limit} tags')
        for tag in tags:
            if len(tag) > tag_len:
                raise forms.ValidationError(f'Tag length must not exceed {tag_len} symbols')

            if not re.fullmatch(r'^[\w-]+$', tag):
                raise forms.ValidationError('Tags must consist of letters, numbers, hyphens and underscores. '
                                            'Use comma as a separator')
        return tags


class AnswerForm(forms.Form):
    text = forms.CharField(max_length=1000, label='',
                           widget=forms.Textarea(attrs={'class': 'form-control',
                                                        'placeholder': 'Enter your answer here...'}))


class ProfileSettingsForm(forms.Form):
    username = forms.CharField(max_length=30, label='Login',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(max_length=100,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))

    nickname = forms.CharField(max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    avatar = forms.ImageField(required=False, validators=[validate_image_size],
                              widget=forms.FileInput(attrs={'class': 'custom-file-input',
                                                            'id': 'avatar-file'}))

    # Form returns only modified fields
    def clean_username(self):
        if 'username' not in self.changed_data:
            return
        username = self.cleaned_data['username']
        validate_username_unused(username)
        return username

    def clean_email(self):
        if 'email' not in self.changed_data:
            return
        email = self.cleaned_data['email']
        validate_email_unused(email)
        return email

    def clean_nickname(self):
        if 'nickname' not in self.changed_data:
            return
        nickname = self.cleaned_data['nickname']
        validate_nickname_unused(nickname)
        return nickname


class LoginForm(forms.Form):
    login = forms.CharField(max_length=30,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    password = forms.CharField(max_length=50,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class SignupForm(forms.Form):
    username = forms.CharField(max_length=30, label='Login',
                               validators=[validate_username_unused],
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(max_length=100,
                             validators=[validate_email_unused],
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))

    nickname = forms.CharField(max_length=30, required=False,
                               validators=[validate_nickname_unused],
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    password = forms.CharField(max_length=50, min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    password_rep = forms.CharField(max_length=50, min_length=6, label='Repeat password',
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    avatar = forms.ImageField(required=False, label='Upload avatar (optional):',
                              validators=[validate_image_size],
                              widget=forms.FileInput(attrs={'class': 'custom-file-input',
                                                            'id': 'avatar-file'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_rep = cleaned_data.get('password_rep')
        if password != password_rep:
            self.add_error('password_rep', forms.ValidationError('Passwords do not match'))
        return cleaned_data
