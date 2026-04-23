# Backup Azure DevOps - Acqio

Script para fazer backup automatizado de todos os repositórios Git de uma organização no Azure DevOps.

## 🛠️ Requisitos

- **Python 3.10 ou superior**
- **Git** instalado e no PATH
- **Personal Access Token (PAT)** do Azure DevOps com permissão: `Code (Read)`

## 📦 Instalação

### 1. Instalar UV (se ainda não tiver)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalar dependências

```bash
uv sync
```

### 3. Configurar variáveis de ambiente

1. Copie o arquivo `.env.example` para `.env`:

   ```bash
   cp .env.example .env
   ```

2. Gere um Personal Access Token (PAT) do Azure DevOps:

   - Acesse: https://dev.azure.com/<organization>/_usersSettings/tokens
   - Clique em "New Token"
   - Configure:
     - **Name**: Backup Script
     - **Organization**: <organization>
     - **Scopes**: Code (Read)
   - Copie o token gerado

3. Edite o arquivo `.env` e preencha:

   ```env
   AZURE_PAT=seu_token_aqui_gerado_acima
   ORGANIZATION=<organization>
   BACKUP_PATH=./Backup-AzureDevOps/<organization>
   API_VERSION=7.1
   ```

## 🚀 Uso

Inicie o ambiente virtual e execute o script:

```Bash
source .venv/bin/activate
```

```bash
backup-azure-devops --pull-branches
```

### Flags disponíveis

| Flag              | Descrição                                   |
|-------------------|---------------------------------------------|
| `--pull-branches` | Atualiza branches existentes com `git pull` |

## 📁 Estrutura de Saída

```
Backup-AzureDevOps/<organization>/
├── Project1/
│   ├── Repo1/
│   ├── Repo2/
│   └── ...
├── Project2/
│   ├── RepoA/
│   └── ...
└── backup_log_20240101_120000.csv
```

## 📊 Relatório CSV

O arquivo `backup_log_*.csv` contém:

| Coluna | Descrição |
|--------|-----------|
| Timestamp | Data/hora da execução |
| Project | Nome do project |
| Repository | Nome do repositório |
| Status | `CLONED`, `UPDATED` ou `ERROR` |
| Duration_s | Tempo de execução em segundos |
| LocalPath | Caminho local do backup |

## 🔄 Automação com Cron (Linux/macOS)

Para rodar o backup diariamente às 2 da manhã:

```bash
0 2 * * * cd /path/to/script && uv run backup_azure_devops.py >> /var/log/azure_backup.log 2>&1
```

> **Nota**: Certifique-se que o arquivo `.env` está no mesmo diretório do script

## Rodar Testes

```bash
uv run python -m pytest tests/ -v

# Teste Suites

uv run pytest -v
```

### Com coverage

```bash
uv run python -m pytest tests/ --cov=src/backup_azure_devops
```

### Apenas unit tests

```bash
uv run python -m pytest tests/ -m unit -v
```

## 📝 Próximos Passos (Opcional)

1. **Linting**: `uv run ruff check src/`
2. **Code formatting**: `uv run black src/`

## 🐛 Troubleshooting

### Erro: "Arquivo .env não encontrado"

- Certifique-se que copiou `.env.example` para `.env`
- Execute na raiz do projeto: `cp .env.example .env`
- Verifique se o arquivo `.env` está no mesmo diretório do script

### Erro: "AZURE_PAT not provided" ou "AZURE_PAT" inválido

- Verifique se preencheu corretamente a variável `AZURE_PAT` no arquivo `.env`
- Confirme que o PAT é válido e tem permissão `Code (Read)`
- Gere um novo token se necessário

### Erro: "Nenhum project encontrado"

- Verifique se o PAT é válido
- Confirme que o PAT tem permissão `Code (Read)`
- Verifique a conectividade com o Azure DevOps
- Verifique se `ORGANIZATION` está correto no arquivo `.env`

### Erro: "Permission denied" no diretório de backup

- Verifique permissões: `ls -la /backup/path`
- Use `chmod` ou execute com `sudo` se necessário
- Verifique se o `BACKUP_PATH` no `.env` é válido