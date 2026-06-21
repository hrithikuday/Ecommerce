from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, MediaURL, Product, Category

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-white transition-colors duration-200 placeholder-zinc-500',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-white transition-colors duration-200 placeholder-zinc-500',
            'placeholder': 'Enter your password'
        })
    )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-white transition-colors duration-200 placeholder-zinc-500',
            'placeholder': 'name@example.com'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['email']:
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-white transition-colors duration-200 placeholder-zinc-500'
                })



class MediaURLForm(forms.ModelForm):
    class Meta:
        model = MediaURL
        fields = ['title', 'url', 'url_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-white transition-colors duration-200 placeholder-zinc-500',
                'placeholder': 'e.g. Elegant Campaign Video'
            }),
            'url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-white transition-colors duration-200 placeholder-zinc-500',
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
            'url_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-white transition-colors duration-200'
            })
        }

