# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt requirements.txt

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação para o diretório de trabalho
COPY . .

# Exponha a porta que o FastAPI estará rodando (configurada no uvicorn command)
EXPOSE 8000

# Comando para rodar a aplicação
# O comando real pode ser sobrescrito pelo docker-compose.yml
# Este é um comando padrão se o Dockerfile for usado de forma independente.
CMD ["uvicorn", "core_service.main:app", "--host", "0.0.0.0", "--port", "8000"]