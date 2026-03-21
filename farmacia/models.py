from django.db import models
from django.contrib.auth.models import User


class Laboratorio(models.Model):
    nome  = models.CharField(max_length=120)
    ativo = models.BooleanField(default=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome


class Distribuidora(models.Model):
    nome  = models.CharField(max_length=120)
    cnpj  = models.CharField(max_length=18, blank=True)
    ativo = models.BooleanField(default=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome


class Medicamento(models.Model):
    nome          = models.CharField(max_length=200)
    lote          = models.CharField(max_length=50)
    quantidade    = models.IntegerField(default=0)
    data_validade = models.DateField()
    controlado    = models.BooleanField(default=False)
    laboratorio   = models.ForeignKey(Laboratorio,  on_delete=models.PROTECT)
    distribuidora = models.ForeignKey(Distribuidora, on_delete=models.PROTECT)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome


class ProdutoDiverso(models.Model):
    nome       = models.CharField(max_length=200)
    categoria  = models.CharField(max_length=80, blank=True)
    preco      = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField(default=0)
    ativo      = models.BooleanField(default=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome