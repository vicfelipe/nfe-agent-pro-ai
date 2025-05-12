# **Documentação Técnica - NF Agent Pro**  
**Versão 1.0**  
*Solução modular para automação de suporte fiscal via chatbots empresariais*  

--- 

## **1. Visão Geral**  
O **NF Agent Pro** é um MVP, possuindo agente de IA especializado em consultas de notas fiscais, projetado para integração com plataformas de comunicação (Microsoft Teams, Slack) e sistemas ERP. Combina **LLMs** com recuperação de dados em tempo real (RAG) para respostas precisas, sendo 100% customizável em runtime.
Ou seja, é um suporte automatizado para consultas de NF utilizando as bases de conhecimento (KBC) e dados de NF.

--- 

## **2. Arquitetura do Sistema**  
``` 
    A[Chatbot (Teams/Slack)] --> B[API Gateway] 
    B --> C[Core Service] 
    C --> D[LLM Provider] 
    C --> E[Database Connector] 
    C --> F[Search Engine] 
    D --> G[Azure OpenAI/GPT-4/Llama 3] 
    E --> H[PostgreSQL/SQL Server/MongoDB] 
    F --> I[Azure Cognitive Search/Elasticsearch] 
``` 

--- 

## **3. Componentes Técnicos**  

### **3.1. Módulo de Comunicação**  
- **Tecnologias**:  
  - **Bot Framework** (Microsoft Teams)  
  - **Bolt API** (Slack)  
  - **WhatsApp Business API** (via Twilio)  
- **Protocolos**: HTTPS Webhooks, WebSockets  

### **3.2. Camada de Integração**  
| Componente       | Descrição                                  | Tecnologias                     |  
|------------------|--------------------------------------------|---------------------------------|  
| **API Gateway**  | Roteamento e autenticação                  | FastAPI, Kong, AWS API Gateway  |  
| **Auth Service** | Gerencia tokens JWT/OAuth2                 | Keycloak, Azure AD B2C          |  

### **3.3. Núcleo de IA**  
- **LLM Abstraction Layer**:  
  ```python 
  def get_llm_provider(config: Config) -> LLMClient: 
      providers = { 
          "azure_openai": AzureOpenAIClient, 
          "openai": OpenAIClient, 
          "llama": LlamaClient 
      } 
      return providers[config.llm.provider](config.llm.api_key) 
  ```  
- **RAG Pipeline**:  
  1. Gera embeddings com `text-embedding-ada-002`  
  2. Indexa no **Azure Cognitive Search** ou **FAISS** (local)  

### **3.4. Conectores de Banco de Dados**  
| Banco       | Biblioteca           | Observações                          |  
|-------------|----------------------|--------------------------------------|  
| PostgreSQL  | `asyncpg`            | Suporte a JSONB                      |  
| SQL Server  | `pyodbc`             | Requer driver ODBC                   |  
| MongoDB     | `motor` (async)      | Schema-less para NFs não estruturadas|  

### **3.5. Módulo de Processamento de Arquivos**  
- **Formatos suportados**: CSV, XLSX, PDF (OCR via Azure Form Recognizer)  
- **Fluxo**:  
  ```
  Upload -->|Blob Storage| Trigger -->|Azure Functions| Parser --> Database
  ``` 

--- 

## **4. Configuração Dinâmica**  
Arquivo `config.yaml` padrão:  
```yaml 
logging: 
  level: "INFO" 
  destination: "azure_logs" 

llm: 
  provider: "azure_openai" 
  deployment: "gpt-35-turbo" 
  temperature: 0.7 

database: 
  type: "postgresql" 
  connection: "${DB_CONN_STRING}" 
  pool_size: 10 

search: 
  provider: "azure_search" 
  index: "nf_index" 
``` 

--- 

## **5. Requisitos de Infraestrutura**  
### **5.1. Opções de Hospedagem**  
| Plataforma | Serviços Recomendados                     |  
|------------|-------------------------------------------|  
| **Azure**  | App Service, Azure Functions, AKS         |  
| **AWS**    | ECS Fargate, Lambda, RDS                  |  
| **GCP**    | Cloud Run, BigQuery, Vertex AI            |  

### **5.2. Especificações Mínimas**  
- **CPU**: 2 vCPUs (4 para processamento de lotes)  
- **Memória**: 4 GB RAM  
- **Storage**: 50 GB (SSD para índices de busca)  

--- 

## **6. Segurança**  
- **Criptografia**:  
  - Dados em trânsito: TLS 1.3  
  - Dados em repouso: Azure Storage Service Encryption  
- **Controles de Acesso**:  
  - RBAC via Azure AD  
  - Máscara de dados sensíveis (ex: chaves de NF)  

--- 

## **7. Monitoramento**  
- **Métricas-chave**:  
  - Latência de respostas do LLM (< 2s)  
  - Taxa de acertos no cache RAG (> 80%)  
- **Ferramentas**:  
  - Azure Application Insights  
  - Prometheus + Grafana (on-prem)  

--- 

## **8. Pipeline de CI/CD**  
```
Commit -->|GitHub Actions| Build -->|Docker| Registry -->|Terraform| Deploy
```  
- **Testes automatizados**:  
  - Pytest (unidade)  
  - Locust (carga)  

--- 

## **9. Customização por Cliente**  
### **9.1. Passos para Adaptação**  
1. **Seleção de LLM**:  
   ```bash 
   ./configure.sh --llm=openai --model=gpt-4o 
   ```  
2. **Troca de Banco de Dados**:  
   ```python 
   # .env 
   DB_TYPE=mongodb 
   DB_CONN_STRING="mongodb+srv://..." 
   ```  

### **9.2. Templates Disponíveis**  
| Cenario                | Repositório Git                           |  
|------------------------|-------------------------------------------|  
| **Varejo (High-load)** | `github.com/nf-agent/templates/retail`    |  
| **Gov (On-Prem)**      | `github.com/nf-agent/templates/gov`       |  

--- 

## **10. Tecnologias, Frameworks e Linguagens Utilizadas**

### **10.1. Linguagens de Programação**
- **Python**: Linguagem principal para backend e processamento de dados
- **YAML**: Configuração de serviços e infraestrutura
- **Bash**: Scripts de automação e configuração

### **10.2. Frameworks e Bibliotecas**
- **FastAPI**: API Gateway e serviços web
- **Bot Framework**: Integração com Microsoft Teams
- **Bolt API**: Integração com Slack
- **Twilio**: Integração com WhatsApp Business API
- **Asyncpg**: Conector assíncrono para PostgreSQL
- **Pyodbc**: Conector para SQL Server
- **Motor**: Cliente assíncrono para MongoDB
- **Pytest**: Framework de testes unitários
- **Locust**: Ferramenta para testes de carga

### **10.3. Bancos de Dados e Armazenamento**
- **PostgreSQL**: Banco de dados relacional com suporte a JSONB
- **SQL Server**: Banco de dados relacional da Microsoft
- **MongoDB**: Banco de dados NoSQL para dados não estruturados
- **Azure Blob Storage**: Armazenamento de arquivos e documentos

### **10.4. Serviços de IA e Processamento**
- **Azure OpenAI**: Serviço gerenciado para modelos de linguagem
- **OpenAI GPT-4/GPT-4o**: Modelos de linguagem avançados
- **Llama 3**: Modelo de linguagem alternativo
- **Azure Form Recognizer**: OCR para processamento de documentos
- **Azure Cognitive Search**: Motor de busca para RAG
- **FAISS**: Biblioteca para busca de similaridade vetorial

### **10.5. Infraestrutura e DevOps**
- **Docker**: Containerização de aplicações
- **GitHub Actions**: Automação de CI/CD
- **Terraform**: Infraestrutura como código
- **Azure App Service**: Hospedagem de aplicações web
- **Azure Functions**: Computação serverless
- **Azure Kubernetes Service (AKS)**: Orquestração de containers
- **AWS ECS Fargate**: Serviço de containers gerenciado
- **AWS Lambda**: Computação serverless
- **AWS RDS**: Serviço de banco de dados relacional
- **Google Cloud Run**: Plataforma serverless para containers
- **Google BigQuery**: Data warehouse para análises
- **Google Vertex AI**: Plataforma de machine learning

### **10.6. Segurança e Autenticação**
- **Keycloak**: Gerenciamento de identidade e acesso
- **Azure AD B2C**: Serviço de identidade para aplicações B2C
- **JWT/OAuth2**: Protocolos de autenticação
- **TLS 1.3**: Criptografia para dados em trânsito

### **10.7. Monitoramento e Observabilidade**
- **Azure Application Insights**: Monitoramento de aplicações
- **Prometheus**: Coleta de métricas
- **Grafana**: Visualização de métricas e dashboards
- **Azure Logs**: Serviço de logging centralizado

--- 
--- 



Produto idealizado por [Victor Alencastro](https://www.victorcode.dev)