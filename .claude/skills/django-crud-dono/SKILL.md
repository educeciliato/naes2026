---
name: django-crud-dono
description: Use ao criar ou alterar um CRUD de registros que pertencem ao usuário logado (campo cadastrado_por) — garante que só o dono lista, vê, edita e exclui, com mensagens de sucesso, FKs limitadas ao dono e testes de 404.
---

## Regra

Registro com `cadastrado_por` só existe para o dono. Outro usuário (inclusive
staff) recebe **404** em detalhe, edição e exclusão, e não vê o registro na
lista. A fronteira é o `get_queryset()`, não o template.

## Passo a passo

1. **Model** com o dono e `Meta.verbose_name` (usado nas mensagens):

   ```python
   class Fornecedor(models.Model):
       nome = models.CharField(max_length=120)
       cadastrado_em = models.DateTimeField(auto_now_add=True)
       cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT)

       class Meta:
           verbose_name = 'fornecedor'
           verbose_name_plural = 'fornecedores'

       def __str__(self):
           return self.nome
   ```

2. **Form** herdando `farmacia.forms.FormDoUsuario`. Se tiver FK para outro
   registro com dono, liste em `campos_do_usuario` (o queryset passa a ter só
   os do usuário). **Não** inclua `cadastrado_por` nos `fields`.

3. **Views** herdando as bases de `farmacia/views.py`:

   ```python
   class FornecedorList(DonoListView):          # FilterView + paginate_by=10
       model = Fornecedor
       filterset_class = FornecedorFilter        # skill django-filter-listagens
       template_name = 'website/fornecedor.html'
       context_object_name = 'fornecedores'
       relacionados = ('farmacia',)              # select_related do que a tabela mostra

   class FornecedorDetail(DonoDetailView):      # usa website/detalhe.html
       model = Fornecedor
       url_base = 'fornecedor'                   # fornecedor_listar/_editar/_excluir

   class FornecedorCreate(DonoCreateView):      # grava cadastrado_por + messages.success
       model = Fornecedor
       form_class = FornecedorForm
       success_url = reverse_lazy('fornecedor_listar')
       extra_context = {'titulo': 'Novo Fornecedor', 'botao': 'Criar Fornecedor'}

   class FornecedorUpdate(DonoUpdateView): ...  # mesma estrutura
   class FornecedorDelete(DonoDeleteView): ...  # ProtectedError vira messages.error
   ```

   `genero = 'a'` para substantivos femininos ("Distribuidora … excluída").

4. **URLs** no padrão `<base>_listar`, `<base>_novo`, `<base>_editar`,
   `<base>_excluir`, `<base>_detalhe`.

5. **Template da lista**: copie `website/templates/website/distribuidora.html`
   (filtro, `_acoes.html` com exclusão por POST + Bootbox, `_paginacao.html`).

6. **Menu**: itens em "Cadastrar" e "Listar" do `modelo.html`.

## Nunca

- `Model.objects.get(pk=...)` direto numa view de dono (use o queryset filtrado).
- Esconder o botão no template como única proteção.
- `form_valid` que salva e redireciona sem chamar `super()` (perde a mensagem).
- Exclusão por GET.

## Testes obrigatórios

```python
def test_outro_usuario_recebe_404(self):
    self.client.force_login(self.outro)
    for nome in ('fornecedor_detalhe', 'fornecedor_editar', 'fornecedor_excluir'):
        self.assertEqual(self.client.get(reverse(nome, args=[self.obj.pk])).status_code, 404)
    self.assertNotContains(self.client.get(reverse('fornecedor_listar')), self.obj.nome)
```

E também: o `cadastrado_por` é preenchido na criação; as três mensagens de
sucesso aparecem; a exclusão bloqueada por `PROTECT` gera mensagem de erro.
Exemplos em `farmacia/test_requisitos.py` (`DonoTest`, `MensagensTest`).
