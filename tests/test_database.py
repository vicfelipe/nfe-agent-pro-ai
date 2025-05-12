import pytest
from database.adapters import DatabaseFactory, IDatabase # Supondo que config_template.toml seja lido para obter conn_str
import toml
import os

# Caminho para o arquivo de configuração, assumindo que está na raiz do projeto
# e 'tests' é um subdiretório.
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config_template.toml')

# Carregar a configuração para obter a connection string
# Em um cenário real, você pode querer mockar isso ou usar uma config de teste
def load_test_config():
    try:
        config = toml.load(CONFIG_PATH)
        return config
    except FileNotFoundError:
        # Fallback para uma config padrão se o arquivo não existir (útil para CI)
        print(f"Aviso: {CONFIG_PATH} não encontrado, usando config de teste padrão.")
        return {
            "database": {
                "type": "postgresql", # ou mongodb para testar o outro
                "url": "postgresql://user:pass@localhost:5432/test_db" # DB de teste
            }
        }

@pytest.fixture(params=["postgresql", "mongodb"])
def database(request):
    config_data = load_test_config()
    db_type = request.param
    
    # Simular a obtenção da connection string baseada no db_type e na config
    # Para este exemplo, vamos assumir que a config_template.toml tem uma URL genérica
    # e nós a adaptamos ou usamos uma específica para o teste.
    if db_type == "postgresql":
        # Em um teste real, você usaria um banco de dados de teste dedicado.
        # A URL viria de uma configuração de teste ou seria mockada.
        conn_str = config_data.get("database", {}).get("url", "postgresql://test_user:test_pass@localhost/test_db")
        if "mongodb" in conn_str: # Ajuste se a URL genérica for de mongo
            conn_str = "postgresql://test_user:test_pass@localhost/test_db"
    elif db_type == "mongodb":
        conn_str = config_data.get("database", {}).get("url", "mongodb://test_user:test_pass@localhost:27017/test_db")
        if "postgresql" in conn_str: # Ajuste se a URL genérica for de postgres
            conn_str = "mongodb://test_user:test_pass@localhost:27017/test_db"
    else:
        raise ValueError(f"Tipo de banco de dados não suportado para fixture: {db_type}")

    # Para testes reais, você precisaria garantir que os bancos de dados (PostgreSQL e MongoDB)
    # estejam em execução e acessíveis com as connection strings fornecidas.
    # Mockar as classes de repositório pode ser uma alternativa para testes unitários mais rápidos.
    print(f"\nUsando DB: {db_type} com conn_str: {conn_str[:20]}...") # Log para depuração
    
    # Mock simplificado para não depender de um DB real rodando durante o teste básico
    class MockPostgresRepository(IDatabase):
        async def get_nf(self, chave: str) -> dict:
            return {"chave": chave, "dados": "dados mock postgresql", "source": "mock_postgres"}

    class MockMongoRepository(IDatabase):
        async def get_nf(self, chave: str) -> dict:
            return {"chave": chave, "dados": "dados mock mongodb", "source": "mock_mongo"}

    if db_type == "postgresql":
        return MockPostgresRepository()
    elif db_type == "mongodb":
        return MockMongoRepository()

@pytest.mark.asyncio
async def test_nf_query(database: IDatabase):
    """Testa a consulta de NF para diferentes tipos de banco de dados."""
    chave_teste = "12345678901234567890123456789012345678901234"
    nf_data = await database.get_nf(chave_teste)
    assert nf_data is not None
    assert nf_data["chave"] == chave_teste
    assert "dados" in nf_data
    print(f"Teste de consulta NF para {nf_data.get('source', 'desconhecido')} passou.")

# Para rodar os testes: pytest
# Certifique-se de ter o pytest e pytest-asyncio instalados (adicionar ao requirements.txt se necessário)
# pytest-asyncio é necessário para testes com funções async.