import streamlit as st
import toml
import os

# Default options for selectboxes if not defined in config_template.toml
DEFAULT_CLOUD_PROVIDERS = ['aws', 'azure', 'gcp']
DEFAULT_DB_TYPES = ['postgresql', 'mongodb']
DEFAULT_LLM_PROVIDERS = ['azure', 'openai', 'ollama']

# Caminho para os arquivos de configuração
CONFIG_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config_template.toml')
CONFIG_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.toml')

def load_config_template():
    """Carrega o template de configuração."""
    try:
        with open(CONFIG_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return toml.load(f)
    except FileNotFoundError:
        st.error(f"Arquivo 'config_template.toml' não encontrado em {CONFIG_TEMPLATE_PATH}")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar 'config_template.toml': {e}")
        return None

def save_config(config_data):
    """Salva a configuração finalizada."""
    try:
        with open(CONFIG_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            toml.dump(config_data, f)
        st.success(f"Configuração salva com sucesso em {CONFIG_OUTPUT_PATH}!")
    except Exception as e:
        st.error(f"Erro ao salvar 'config.toml': {e}")

st.set_page_config(page_title="Assistente de Configuração NFProAI", layout="wide")

st.title("🚀 Assistente de Configuração NFProAI")
st.markdown("""
Bem-vindo ao assistente de configuração do NFProAI! 
Este guia ajudará você a configurar as principais seções do seu projeto.
""")

config_template = load_config_template()

if config_template:
    st.sidebar.header("Navegação")
    # Tentar carregar configuração existente para preencher os campos
    current_config = {}
    if os.path.exists(CONFIG_OUTPUT_PATH):
        try:
            with open(CONFIG_OUTPUT_PATH, 'r', encoding='utf-8') as f:
                current_config = toml.load(f)
        except Exception as e:
            st.warning(f"Não foi possível carregar a configuração existente de {CONFIG_OUTPUT_PATH}: {e}")

    # Inicializa o dicionário para armazenar as configurações do usuário
    user_config = {}

    # --- Seção Cloud ---
    st.header("☁️ Configuração da Cloud")
    cloud_options = config_template.get('cloud', {})
    user_config['cloud'] = {}
    if cloud_options:
        _cloud_provider_opts = list(cloud_options.get('available_providers', DEFAULT_CLOUD_PROVIDERS))
        _cloud_provider_val = current_config.get('cloud', {}).get('provider', cloud_options.get('provider'))
        _cloud_provider_idx = 0
        if _cloud_provider_opts: # Check if list is not empty
            if _cloud_provider_val and _cloud_provider_val in _cloud_provider_opts:
                _cloud_provider_idx = _cloud_provider_opts.index(_cloud_provider_val)
            # If _cloud_provider_val is None or not in opts, idx remains 0 (first item)
            
        selected_provider = st.selectbox(
            "Provedor de Cloud Principal", 
            options=_cloud_provider_opts,
            index=_cloud_provider_idx,
            help="Selecione o provedor de nuvem que você usará para armazenamento e outros serviços."
        )
        user_config['cloud']['provider'] = selected_provider

        if selected_provider == "aws":
            st.subheader("AWS S3")
            user_config['cloud']['aws_s3_bucket'] = st.text_input("Nome do Bucket S3", value=current_config.get('cloud', {}).get('aws_s3_bucket', cloud_options.get('aws_s3_bucket', '')))
            user_config['cloud']['aws_access_key_id'] = st.text_input("AWS Access Key ID", value=current_config.get('cloud', {}).get('aws_access_key_id', ''), type="password")
            user_config['cloud']['aws_secret_access_key'] = st.text_input("AWS Secret Access Key", value=current_config.get('cloud', {}).get('aws_secret_access_key', ''), type="password")
            user_config['cloud']['aws_region'] = st.text_input("Região AWS", value=current_config.get('cloud', {}).get('aws_region', cloud_options.get('aws_region', 'us-east-1')))
        elif selected_provider == "azure":
            st.subheader("Azure Blob Storage")
            user_config['cloud']['azure_storage_account_name'] = st.text_input("Nome da Conta de Armazenamento Azure", value=current_config.get('cloud', {}).get('azure_storage_account_name', cloud_options.get('azure_storage_account_name', '')))
            user_config['cloud']['azure_storage_container_name'] = st.text_input("Nome do Contêiner Azure", value=current_config.get('cloud', {}).get('azure_storage_container_name', cloud_options.get('azure_storage_container_name', '')))
            user_config['cloud']['azure_storage_connection_string'] = st.text_input("String de Conexão do Armazenamento Azure", value=current_config.get('cloud', {}).get('azure_storage_connection_string', ''), type="password")
        elif selected_provider == "gcp":
            st.subheader("Google Cloud Storage")
            user_config['cloud']['gcp_bucket_name'] = st.text_input("Nome do Bucket GCP", value=current_config.get('cloud', {}).get('gcp_bucket_name', cloud_options.get('gcp_bucket_name', '')))
            user_config['cloud']['gcp_project_id'] = st.text_input("ID do Projeto GCP", value=current_config.get('cloud', {}).get('gcp_project_id', cloud_options.get('gcp_project_id', '')))
            st.markdown("Para autenticação no GCP, configure a variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS` com o caminho para o seu arquivo JSON de chave de serviço.")
    else:
        st.info("Seção 'cloud' não encontrada no template.")

    st.markdown("---")

    # --- Seção Database ---
    st.header("🗄️ Configuração do Banco de Dados")
    db_options = config_template.get('database', {})
    user_config['database'] = {}
    if db_options:
        _db_type_opts = list(db_options.get('available_types', DEFAULT_DB_TYPES))
        _db_type_val = current_config.get('database', {}).get('type', db_options.get('type'))
        _db_type_idx = 0
        if _db_type_opts: # Check if list is not empty
            if _db_type_val and _db_type_val in _db_type_opts:
                _db_type_idx = _db_type_opts.index(_db_type_val)

        selected_db_type = st.selectbox(
            "Tipo de Banco de Dados", 
            options=_db_type_opts,
            index=_db_type_idx,
            help="Escolha o sistema de banco de dados que será utilizado."
        )
        user_config['database']['type'] = selected_db_type

        if selected_db_type == "postgresql":
            st.subheader("PostgreSQL")
            user_config['database']['db_host'] = st.text_input("Host do Banco", value=current_config.get('database', {}).get('db_host', db_options.get('db_host', 'localhost')))
            user_config['database']['db_port'] = st.number_input("Porta do Banco", value=current_config.get('database', {}).get('db_port', db_options.get('db_port', 5432)), min_value=1, max_value=65535)
            user_config['database']['db_user'] = st.text_input("Usuário do Banco", value=current_config.get('database', {}).get('db_user', db_options.get('db_user', 'user')))
            user_config['database']['db_password'] = st.text_input("Senha do Banco", value=current_config.get('database', {}).get('db_password', ''), type="password")
            user_config['database']['db_name'] = st.text_input("Nome do Banco de Dados", value=current_config.get('database', {}).get('db_name', db_options.get('db_name', 'nf_agent_db')))
        elif selected_db_type == "mongodb":
            st.subheader("MongoDB")
            user_config['database']['mongo_uri'] = st.text_input("URI de Conexão MongoDB", value=current_config.get('database', {}).get('mongo_uri', db_options.get('mongo_uri', 'mongodb://user:password@localhost:27017/nf_agent_db')))
            user_config['database']['mongo_db_name'] = st.text_input("Nome do Banco de Dados MongoDB", value=current_config.get('database', {}).get('mongo_db_name', db_options.get('mongo_db_name', 'nf_agent_db')))
    else:
        st.info("Seção 'database' não encontrada no template.")

    st.markdown("---")

    # --- Seção LLM ---
    st.header("🧠 Configuração do LLM Gateway")
    llm_options = config_template.get('llm', {})
    user_config['llm'] = {}
    if llm_options:
        _llm_provider_opts = list(llm_options.get('available_providers', DEFAULT_LLM_PROVIDERS))
        _llm_provider_val = current_config.get('llm', {}).get('provider', llm_options.get('provider'))
        _llm_provider_idx = 0
        if _llm_provider_opts: # Check if list is not empty
            if _llm_provider_val and _llm_provider_val in _llm_provider_opts:
                _llm_provider_idx = _llm_provider_opts.index(_llm_provider_val)

        selected_llm_provider = st.selectbox(
            "Provedor de LLM", 
            options=_llm_provider_opts,
            index=_llm_provider_idx,
            help="Escolha o provedor de LLM para processamento de linguagem."
        )
        user_config['llm']['provider'] = selected_llm_provider

        if selected_llm_provider == "openai":
            st.subheader("OpenAI")
            user_config['llm']['openai_api_key'] = st.text_input("Chave da API OpenAI", value=current_config.get('llm', {}).get('openai_api_key', ''), type="password")
            user_config['llm']['openai_default_model'] = st.text_input("Modelo Padrão OpenAI", value=current_config.get('llm', {}).get('openai_default_model', llm_options.get('openai_default_model', 'gpt-3.5-turbo')))
        elif selected_llm_provider == "ollama":
            st.subheader("Ollama")
            user_config['llm']['ollama_api_base_url'] = st.text_input("URL Base da API Ollama", value=current_config.get('llm', {}).get('ollama_api_base_url', llm_options.get('ollama_api_base_url', 'http://localhost:11434')))
            user_config['llm']['ollama_default_model'] = st.text_input("Modelo Padrão Ollama", value=current_config.get('llm', {}).get('ollama_default_model', llm_options.get('ollama_default_model', 'llama2')))
        # Adicionar outros provedores conforme necessário
    else:
        st.info("Seção 'llm' não encontrada no template.")

    st.markdown("---")

    # Botão para salvar
    if st.button("💾 Salvar Configurações", type="primary"):
        # Limpar chaves vazias ou com valores padrão não alterados, se desejado
        # (Opcional, dependendo da lógica de como o config.toml deve ser gerado)
        final_config = {section: {k: v for k, v in params.items() if v} 
                        for section, params in user_config.items() if params}
        save_config(final_config)
        st.balloons()

    st.sidebar.markdown("### Pré-visualização do `config.toml`")
    st.sidebar.code(toml.dumps(user_config), language='toml')

else:
    st.error("Não foi possível carregar o template de configuração. O assistente não pode continuar.")

st.markdown("--- ")
st.caption("NFProAI Setup Wizard v0.1.0")