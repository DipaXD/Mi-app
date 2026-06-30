from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Producto

# 🟢 PRODUCTO
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'descripcion', 'imagen']

# 🔵 REGISTRO
class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🚫 BORRAMOS LOS TEXTOS DE AYUDA DE DJANGO DE RAÍZ 🚫
        if 'password1' in self.fields:
            self.fields['password1'].help_text = ""
        if 'password2' in self.fields:
            self.fields['password2'].help_text = ""