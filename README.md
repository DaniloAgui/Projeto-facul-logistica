# Gestão Logística

Protótipo web acadêmico para cadastro, consulta e acompanhamento de pedidos logísticos. O sistema organiza pedidos por região, canal de venda, status, histórico e ocorrências. Todos os registros iniciais são fictícios e não há integração com sistemas externos.

## Tecnologias

- Python 3.12
- Flask 3.x, Jinja2 e Flask-SQLAlchemy
- SQLAlchemy 2.x
- SQLite
- pytest

## Instalação no Windows

No terminal do VS Code, dentro desta pasta:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se a política do PowerShell impedir a ativação, execute apenas:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Executar

```powershell
.\.venv\Scripts\python.exe run.py
```

Abra **http://127.0.0.1:5000** no navegador. O banco `instance/logistica.sqlite` é criado automaticamente na primeira execução, com três pedidos demonstrativos.

Para encerrar, volte ao terminal e pressione `Ctrl+C`.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Os testes usam um banco temporário separado e cobrem cadastro válido e inválido, filtros, atualizações com histórico, ocorrências e relacionamentos.

## Capturas para a atividade

1. **Painel:** abra `http://127.0.0.1:5000/`; a tabela já mostra os pedidos 1001, 1002 e 1003.
2. **Cadastro:** clique em **＋ Novo pedido** no cabeçalho; o formulário mostra todos os campos obrigatórios e opcionais.
3. **Detalhes:** no painel, clique em **Ver detalhes** do pedido 1003; a tela apresenta status, histórico e a ocorrência fictícia de devolução.

Em cada tela, use **Windows + Shift + S**, selecione a área do navegador e salve a captura. Para uma captura com um novo pedido, preencha o formulário e clique em **Salvar pedido**; a aplicação persiste os dados no SQLite.

## Escopo

O MVP não implementa GPS em tempo real, otimização de rotas, integrações com marketplaces ou sistemas corporativos, aplicativo móvel ou funções financeiras.




## Validação do MVP

O protótipo Gestão Logística permite cadastrar pedidos, consultar registros por identificador, região e canal de venda, acompanhar o status das entregas e registrar ocorrências.

### Objetivo da revisão

Documentar as funcionalidades centrais do MVP e organizar os próximos passos para validação com um representante da empresa parceira.

### Escopo atual

- Cadastro de pedidos com dados fictícios.
- Consulta e filtragem de pedidos.
- Atualização de status e histórico de acompanhamento.
- Registro de ocorrências e providências adotadas.

### Limitações

Esta versão é um protótipo acadêmico. Não possui integração com sistemas externos, rastreamento GPS ou otimização automática de rotas.

### Próxima etapa

Executar testes com tarefas operacionais, registrar as dificuldades observadas e priorizar melhorias de usabilidade, acessibilidade e segurança.

