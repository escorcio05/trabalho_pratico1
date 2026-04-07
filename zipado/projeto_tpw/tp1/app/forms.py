from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PesquisaFilmeForm(forms.Form):
    query = forms.CharField(
        label='', # Removemos o label para ficar igual à imagem
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for a movie, tv show, person...',
            'style': 'border: none; background: transparent; color: black; outline: none; box-shadow: none;'
        })
    )

class RegistoForm(UserCreationForm):
    first_name = forms.CharField(label="Primeiro Nome", max_length=30, required=True)
    last_name = forms.CharField(label="Último Nome", max_length=30, required=True)
    email = forms.EmailField(label="Email", required=True)


    class Meta(UserCreationForm.Meta):
        model = User
        # Definimos a ordem: o que aparece primeiro no site
        fields = ("username", "first_name", "last_name", "email")