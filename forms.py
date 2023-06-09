from django import forms
from django.forms import inlineformset_factory
from .models import Categoria


class CategoriaForm(forms.ModelForm):
    class Meta: 
        model = Categoria
        fields = '__all__'