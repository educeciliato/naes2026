from django.contrib import admin
from .models import Laboratorio, Distribuidora, Medicamento, ProdutoDiverso

admin.site.register(Laboratorio)
admin.site.register(Distribuidora)
admin.site.register(Medicamento)
admin.site.register(ProdutoDiverso)