from django import forms

class PesquisaFilmeForm(forms.Form):
    query = forms.CharField(
        label='Pesquisar Filme',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o título...'})
    )