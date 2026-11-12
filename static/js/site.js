// Inicialização dos plugins jQuery do PharmaSys.
// Carregado no fim do modelo.html, depois do jQuery, dos plugins e do Bootstrap:
//   1. jQuery Mask Plugin — máscaras de CNPJ (.mascara-cnpj) e UF (.mascara-uf)
//   2. Bootbox.js         — confirmação antes de enviar <form data-confirmar="...">
//   3. DataTables         — <table class="table-datatable"> (só tabelas SEM paginação no servidor)
$(function () {
  'use strict';

  // ---------------------------------------------------------------------
  // 1. jQuery Mask Plugin
  // ---------------------------------------------------------------------
  if ($.fn.mask) {
    $('.mascara-cnpj').mask('00.000.000/0000-00');
    // UF: duas letras, sempre maiúsculas.
    $('.mascara-uf').mask('SS', {
      onKeyPress: function (valor, e, campo) { campo.val(valor.toUpperCase()); }
    });
  }

  // ---------------------------------------------------------------------
  // 2. Bootbox.js
  // Qualquer formulário com data-confirmar="Pergunta?" pede confirmação num
  // modal do Bootstrap antes de ser enviado. Opcional:
  // data-confirmar-classe="btn-danger" muda a cor do botão de confirmar.
  // A pergunta entra no modal como TEXTO (nunca como HTML).
  // ---------------------------------------------------------------------
  if (window.bootbox) {
    bootbox.addLocale('pt-BR', { OK: 'OK', CANCEL: 'Cancelar', CONFIRM: 'Confirmar' });
    bootbox.setDefaults({ locale: 'pt-BR', centerVertical: true });
  }

  $(document).on('submit', 'form[data-confirmar]', function (evento) {
    var form = this;
    if (form.dataset.confirmado === '1' || !window.bootbox) return;  // já confirmado: segue o envio
    evento.preventDefault();
    bootbox.confirm({
      title: 'Confirmação',
      message: $('<p class="mb-0">').text(form.dataset.confirmar),
      buttons: {
        cancel: { label: 'Cancelar', className: 'btn-outline-secondary' },
        confirm: { label: 'Confirmar', className: form.dataset.confirmarClasse || 'btn-primary' }
      },
      callback: function (confirmou) {
        if (!confirmou) return;
        form.dataset.confirmado = '1';
        if (form.requestSubmit) form.requestSubmit(); else form.submit();
      }
    });
  });

  // ---------------------------------------------------------------------
  // 3. DataTables
  // Só para tabelas que mostram TODOS os registros de uma vez (sem
  // paginação no servidor), ex.: "IA por usuário". Nas listas paginadas
  // pelo Django o DataTables buscaria/ordenaria só a página atual.
  // ---------------------------------------------------------------------
  if ($.fn.DataTable) {
    $('table.table-datatable').each(function () {
      $(this).DataTable({
        pageLength: 10,
        lengthMenu: [10, 25, 50, 100],
        order: [],  // mantém a ordem da view até o usuário clicar
        language: {
          search: 'Buscar:',
          lengthMenu: 'Mostrar _MENU_ por página',
          info: 'Mostrando _START_ a _END_ de _TOTAL_',
          infoEmpty: 'Nenhum registro',
          infoFiltered: '(filtrado de _MAX_)',
          zeroRecords: 'Nenhum registro encontrado',
          emptyTable: 'Nenhum registro encontrado',
          paginate: { first: 'Primeira', last: 'Última', next: 'Próxima', previous: 'Anterior' }
        }
      });
    });
  }
});
