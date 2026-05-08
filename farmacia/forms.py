from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import Laboratorio, Distribuidora, Medicamento, ProdutoDiverso, Farmacia

FIELD_CLASS = {"class": "form-control"}
CHECK_CLASS = {"class": "form-check-input"}


class LaboratorioForm(forms.ModelForm):
    class Meta:
        model  = Laboratorio
        fields = ["nome", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs=FIELD_CLASS),
            "ativo": forms.CheckboxInput(attrs=CHECK_CLASS),
        }


class DistribuidoraForm(forms.ModelForm):
    class Meta:
        model  = Distribuidora
        fields = ["nome", "cnpj", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs=FIELD_CLASS),
            "cnpj": forms.TextInput(attrs=FIELD_CLASS),
            "ativo": forms.CheckboxInput(attrs=CHECK_CLASS),
        }


class MedicamentoForm(forms.ModelForm):
    class Meta:
        model  = Medicamento
        fields = ["nome", "lote", "quantidade", "data_validade", "controlado", "laboratorio", "distribuidora"]
        widgets = {
            "nome":          forms.TextInput(attrs=FIELD_CLASS),
            "lote":          forms.TextInput(attrs=FIELD_CLASS),
            "quantidade":    forms.NumberInput(attrs=FIELD_CLASS),
            "data_validade": forms.DateInput(attrs={**FIELD_CLASS, "type": "date"}),
            "controlado":    forms.CheckboxInput(attrs=CHECK_CLASS),
            "laboratorio":   forms.Select(attrs=FIELD_CLASS),
            "distribuidora": forms.Select(attrs=FIELD_CLASS),
        }


class ProdutoDiversoForm(forms.ModelForm):
    class Meta:
        model  = ProdutoDiverso
        fields = ["nome", "categoria", "preco", "quantidade", "ativo"]
        widgets = {
            "nome":       forms.TextInput(attrs=FIELD_CLASS),
            "categoria":  forms.TextInput(attrs=FIELD_CLASS),
            "preco":      forms.NumberInput(attrs=FIELD_CLASS),
            "quantidade": forms.NumberInput(attrs=FIELD_CLASS),
            "ativo":      forms.CheckboxInput(attrs=CHECK_CLASS),
        }


class UsuarioForm(UserCreationForm):
    class Meta:
        model  = User
        fields = ["username", "first_name", "last_name", "email", "is_staff", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class GrupoForm(forms.ModelForm):
    class Meta:
        model  = Group
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs=FIELD_CLASS)}


class FarmaciaForm(forms.ModelForm):
    class Meta:
        model = Farmacia
        fields = ["nome_proprietario", "cidade", "estado", "cnpj", "endereco", "grupo"]
        widgets = {
            "nome_proprietario": forms.TextInput(attrs=FIELD_CLASS),
            "cidade": forms.TextInput(attrs=FIELD_CLASS),
            "estado": forms.TextInput(attrs={**FIELD_CLASS, "maxlength": 2}),
            "cnpj": forms.TextInput(attrs=FIELD_CLASS),
            "endereco": forms.TextInput(attrs=FIELD_CLASS),
            "grupo": forms.Select(attrs=FIELD_CLASS),
        }