# PharmaSys — como o sistema funciona

O PharmaSys é um sistema web de gestão de estoque para farmácias. Cada
usuário cadastra e gerencia os SEUS próprios registros: ninguém vê, edita ou
exclui os registros de outra pessoa (nem mesmo os gerentes).

## Acesso

- **Entrar**: botão no canto superior direito, com usuário e senha. Não existe
  cadastro público: as contas são criadas por um gerente em **Usuários**.
- **Alterar senha**: menu com o nome do usuário → **Alterar Senha**.
- **Sair**: menu com o nome do usuário → **Sair**.

## Dashboard

Página inicial depois do login. Mostra quantos medicamentos, produtos,
laboratórios e distribuidoras o usuário cadastrou, a lista de medicamentos
vencidos ou que vencem nos próximos 30 dias e atalhos para as telas.

## Cadastros (menus "Cadastrar" e "Listar")

Ordem recomendada para começar: **Laboratório** e **Distribuidora** primeiro,
depois **Medicamento** (que exige escolher um laboratório e uma distribuidora
já cadastrados pelo próprio usuário).

- **Laboratório**: nome e se está ativo.
- **Distribuidora**: nome, CNPJ (com máscara 00.000.000/0000-00) e se está ativa.
- **Medicamento**: nome, lote, quantidade, data de validade, se é controlado,
  laboratório e distribuidora.
- **Produto diverso** (itens que não são medicamentos, ex.: higiene, cosméticos):
  nome, categoria, preço, quantidade e se está ativo.
- **Farmácia**: nome do proprietário, cidade, UF, CNPJ, endereço e grupo.

## Listas, filtros e ações

- Cada lista mostra 10 registros por página. A paginação fica abaixo da tabela
  e mantém os filtros aplicados.
- O painel **Filtros** (acima da tabela) permite buscar por nome e outros
  campos. Em **Medicamentos** dá para filtrar por laboratório, distribuidora,
  controlado e validade (**Vencido**, **Vence em 30 dias**, **No prazo**).
  **Limpar** remove todos os filtros.
- O menu **⋮** de cada linha tem **Detalhes**, **Editar** e **Excluir**. A
  exclusão pede confirmação numa janela e não pode ser desfeita.
- Um laboratório ou distribuidora que ainda tem medicamentos ligados não pode
  ser excluído: exclua ou altere esses medicamentos antes (ou marque como inativo).
- Depois de cadastrar, alterar ou excluir, aparece uma mensagem de confirmação
  no topo da página.

## Gestão (somente gerentes)

Gerentes (grupo "Gerentes" ou administradores) também veem:

- **Usuários** e **Grupos**: criar, editar e excluir contas e grupos.
- **IA → Requisições**: auditoria de todas as chamadas à IA.
- **IA → IA por usuário**: habilitar/bloquear a IA e definir a cota de cada usuário.
- **IA → Configuração**: ligar/desligar a IA, escolher o modelo e testar a conexão.

## Assistente virtual e cota de IA

- Este assistente responde dúvidas sobre o uso do PharmaSys e sobre os dados
  do próprio usuário mostrados no contexto. Ele não cadastra, altera nem
  exclui nada e não dá orientação de saúde.
- Para responder, ele recebe as últimas mensagens desta conversa. O botão
  **Limpar conversa** apaga o histórico do usuário.
- Cada usuário tem uma cota mensal de tokens, visível em **IA → Meu consumo**.
  A cota é renovada no dia 1º de cada mês.
