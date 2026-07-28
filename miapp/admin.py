from django.contrib import admin
from .models import Producto
from .models import Categoria # Asegúrate de incluir Category (o el nombre exacto de tu modelo de categorías)

# Register your models here.

admin.site.register(Producto)
admin.site.register(Categoria)
