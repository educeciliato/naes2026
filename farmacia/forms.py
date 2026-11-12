from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User

from .models import Distribuidora, Farmacia, Laboratorio, Medicamento, ProdutoDiverso

FIELD_CLASS = {"class": "form-control"}
CHECK_CLASS = {"class": "form-check-input"}
# Máscaras do jQuery Mask Plugin (inicializadas em static/js/site.js)
CNPJ_ATTRS = {"class": "form-control mascara-cnpj", "placeholder": "00.000.000/0000-00"}
UF_ATTRS = {"class": "form-control mascara-uf", "placeholder": "UF"}


class FormDoUsuario(forms.ModelForm):
    """ModelForm que recebe o usuário logado (``usuario=``) e limita as
    chaves estrangeiras aos registros DELE: ninguém escolhe — nem enxerga —
    o laboratório ou a distribuidora de outra pessoa."""

    campos_do_usuario = ()

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        for nome in self.campos_do_usuario:
            if nome in self.fields:
                modelo = self.fields[nome].queryset.model
                self.fields[nome].queryset = (
                    modelo.objects.filter(cadastrado_por=usuario).order_by('nome')
                    if usuario is not None else modelo.objects.none()
                )


class LaboratorioForm(FormDoUsuario):
    class Meta:
        model = Laboratorio
        fields = ["nome", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs=FIELD_CLASS),
            "ativo": forms.CheckboxInput(attrs=CHECK_CLASS),
        }


class DistribuidoraForm(FormDoUsuario):
    class Meta:
        model = Distribuidora
        fields = ["nome", "cnpj", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs=FIELD_CLASS),
            "cnpj": forms.TextInput(attrs=CNPJ_ATTRS),
            "ativo": forms.CheckboxInput(attrs=CHECK_CLASS),
        }


class MedicamentoForm(FormDoUsuario):
    campos_do_usuario = ("laboratorio", "distribuidora")

    class Meta:
        model = Medicamento
        fields = ["nome", "lote", "quantidade", "data_validade", "controlado", "laboratorio", "distribuidora"]
        widgets = {
            "nome":          forms.TextInput(attrs=FIELD_CLASS),
            "lote":          forms.TextInput(attrs=FIELD_CLASS),
            "quantidade":    forms.NumberInput(attrs={**FIELD_CLASS, "min": 0}),
            "data_validade": forms.DateInput(attrs={**FIELD_CLASS, "type": "date"}, format="%Y-%m-%d"),
            "controlado":    forms.CheckboxInput(attrs=CHECK_CLASS),
            "laboratorio":   forms.Select(attrs=FIELD_CLASS),
            "distribuidora": forms.Select(attrs=FIELD_CLASS),
        }


class ProdutoDiversoForm(FormDoUsuario):
    class Meta:
        model = ProdutoDiverso
        fields = ["nome", "categoria", "preco", "quantidade", "ativo"]
        widgets = {
            "nome":       forms.TextInput(attrs=FIELD_CLASS),
            "categoria":  forms.TextInput(attrs=FIELD_CLASS),
            "preco":      forms.NumberInput(attrs={**FIELD_CLASS, "min": 0, "step": "0.01"}),
            "quantidade": forms.NumberInput(attrs={**FIELD_CLASS, "min": 0}),
            "ativo":      forms.CheckboxInput(attrs=CHECK_CLASS),
        }


class FarmaciaForm(FormDoUsuario):
    class Meta:
        model = Farmacia
        fields = ["nome_proprietario", "cidade", "estado", "cnpj", "endereco", "grupo"]
        widgets = {
            "nome_proprietario": forms.TextInput(attrs=FIELD_CLASS),
            "cidade": forms.TextInput(attrs=FIELD_CLASS),
            "estado": forms.TextInput(attrs={**UF_ATTRS, "maxlength": 2}),
            "cnpj": forms.TextInput(attrs=CNPJ_ATTRS),
            "endereco": forms.TextInput(attrs=FIELD_CLASS),
            "grupo": forms.Select(attrs=FIELD_CLASS),
        }

    def clean_estado(self):
        return self.cleaned_data["estado"].upper()


def _estilizar(form):
    for field in form.fields.values():
        css = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
        field.widget.attrs["class"] = css


class UsuarioForm(UserCreationForm):
    """Cadastro de usuário (com senha)."""

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_staff", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _estilizar(self)


class UsuarioUpdateForm(forms.ModelForm):
    """Edição de usuário sem obrigar a trocar a senha."""

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_staff", "is_active", "groups"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _estilizar(self)
        self.fields["groups"].widget.attrs["class"] = "form-select"


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs=FIELD_CLASS)}
