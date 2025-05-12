from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
from llm_gateway.gateway import router as llm_gateway_router  # Importa o roteador
import secrets
import toml # Para carregar configurações

# Carregar configurações (simulado - idealmente de um arquivo ou variáveis de ambiente)
# Exemplo: config = toml.load('../config_template.toml')
# API_KEY_ADMIN = config.get('admin', {}).get('api_key', 'admin_secret_key') # Chave de admin para gerar outras chaves

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Simulação de um "banco de dados" de API keys válidas
# Em produção, isso seria armazenado de forma segura (ex: Redis, banco de dados)
VALID_API_KEYS = {
    "dev_key_123": "developer_user",
    # Chaves geradas podem ser adicionadas aqui
}

ADMIN_API_KEY = "supersecretadminkey123" # Chave de admin para gerar novas chaves

app = FastAPI(
    title="NF Agent Pro - Core Service",
    description="Serviço principal para processamento de Notas Fiscais e interações.",
    version="0.1.0"
)

# Inclui o roteador do LLM Gateway com o prefixo /llm
app.include_router(llm_gateway_router, prefix="/llm", tags=["LLM Gateway"]) 

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header in VALID_API_KEYS:
        return api_key_header
    elif api_key_header == ADMIN_API_KEY:
        return api_key_header # Admin key também é válida para rotas protegidas
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )

class NFRequest(BaseModel):
    content: str # Conteúdo da NF, pode ser XML, JSON, etc.

class BatchNFRequest(BaseModel):
    nf_requests: list[NFRequest]

class SefazCodeResponse(BaseModel):
    code: str
    description: str

class NewAPIKeyResponse(BaseModel):
    api_key: str
    user_identifier: str # Para associar a chave a um usuário/cliente

@app.post("/nf", summary="Processa uma única Nota Fiscal")
async def process_nf(nf_request: NFRequest, api_key: APIKey = Depends(get_api_key)):
    # Lógica para processar a NF (ex: extrair dados, validar, armazenar)
    # Integrar com LLM Gateway, Camada de Armazenamento, etc.
    return {"message": "NF recebida com sucesso", "data": nf_request.content[:50] + "..."}

@app.post("/batch", summary="Processa um lote de Notas Fiscais")
async def process_batch_nf(batch_request: BatchNFRequest, api_key: APIKey = Depends(get_api_key)):
    results = []
    for nf_req in batch_request.nf_requests:
        # Lógica similar ao /nf, mas para cada item do lote
        results.append({"message": "NF do lote recebida", "data_preview": nf_req.content[:30] + "..."})
    return {"message": f"{len(results)} NFs processadas no lote", "results": results}

@app.get("/sefaz_codes", summary="Consulta códigos da SEFAZ", response_model=list[SefazCodeResponse])
async def get_sefaz_codes(api_key: APIKey = Depends(get_api_key)):
    # Lógica para buscar e retornar códigos da SEFAZ (pode ser de um DB ou serviço externo)
    return [
        {"code": "100", "description": "Autorizado o uso da NF-e"},
        {"code": "204", "description": "Duplicidade de NF-e"}
    ]

# Rotas de Administração
@app.post("/admin/generate_api_key", summary="Gera uma nova API Key (requer chave de admin)", response_model=NewAPIKeyResponse)
async def generate_api_key(user_identifier: str, api_key: APIKey = Depends(get_api_key)):
    if api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to generate API keys"
        )
    new_key = secrets.token_urlsafe(32)
    VALID_API_KEYS[new_key] = user_identifier # Adiciona a nova chave ao "banco de dados"
    print(f"Nova API Key gerada para '{user_identifier}': {new_key}")
    return {"api_key": new_key, "user_identifier": user_identifier}

@app.get("/admin/list_api_keys", summary="Lista API Keys ativas (requer chave de admin)")
async def list_api_keys(api_key: APIKey = Depends(get_api_key)):
    if api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to list API keys"
        )
    # Em um cenário real, não exponha as chaves diretamente. Retorne identificadores ou metadados.
    return {"active_keys_count": len(VALID_API_KEYS), "keys_users": VALID_API_KEYS}

# Para executar localmente: uvicorn core_service.main:app --reload
# Adicionar um requirements.txt com: fastapi, uvicorn[standard], pydantic, python-multipart, toml