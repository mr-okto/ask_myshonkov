from django import forms
from django.core.exceptions import ValidationError
from django.core import validators
import re


class AskForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    text = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    tags = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_tags(self):
        tags = [tag.strip() for tag in self.cleaned_data['tags'].split(',')]
        tags_limit = 3
        if len(tags) > tags_limit:
            print('Fatal tags')
            raise forms.ValidationError(f'Question must not contain more than {tags_limit} tags')
        for tag in tags:
            if not re.fullmatch(r'^[\w-]+$', tag):
                raise forms.ValidationError('Tags must consist of letters, numbers and underscores. '
                                            'Use comma as a separator')
        return tags
