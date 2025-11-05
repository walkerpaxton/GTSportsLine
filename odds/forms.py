from django import forms
from .models import BetComment

class BetCommentForm(forms.ModelForm):
    class Meta:
        model = BetComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...',
                'maxlength': 1000
            })
        }
        labels = {
            'content': ''
        }

