import yaml
import os
from abc import ABC, abstractmethod
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm_config.yaml')

class LLMInterface(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        pass

class AzureOpenAILLM(LLMInterface):
    def __init__(self, api_base: str, deployment: str, api_key: str = None):
        self.api_base = api_base
        self.deployment = deployment
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        print(f"AzureOpenAILLM inicializado: endpoint={api_base}, deployment={deployment}")

    async def generate_response(self, prompt: str, **kwargs) -> str:
        return f"Resposta do Azure OpenAI para: '{prompt}' (deployment: {self.deployment})"

class OpenAILLM(LLMInterface):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
        print(f"OpenAILLM inicializado: model={model}")

    async def generate_response(self, prompt: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content

class LlamaOllamaLLM(LLMInterface):
    def __init__(self, api_base: str, model: str):
        self.api_base = api_base
        self.model = model
        print(f"LlamaOllamaLLM inicializado: api_base={api_base}, model={model}")

    async def generate_response(self, prompt: str, **kwargs) -> str:
        return f"Resposta do Llama/Ollama para: '{prompt}' (model: {self.model} via {self.api_base})"

class LLMGateway:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config = self._load_config(config_path)
        self.llm_service = self._initialize_llm_service()

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise EnvironmentError(f"Arquivo de configuração LLM não encontrado em {path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Erro ao parsear o arquivo YAML de configuração LLM: {e}")

    def _initialize_llm_service(self) -> LLMInterface:
        provider = self.config.get('provider')
        api_base = self.config.get('api_base')
        api_key = self.config.get('api_key')
        deployment = self.config.get('deployment')
        model = self.config.get('model')

        if provider == 'azure':
            if not api_base or not deployment:
                raise ValueError("Para Azure, 'api_base' e 'deployment' são obrigatórios no llm_config.yaml")
            return AzureOpenAILLM(api_base=api_base, deployment=deployment, api_key=api_key)
        elif provider == 'openai':
            if not model:
                 raise ValueError("Para OpenAI, 'model' é obrigatório no llm_config.yaml")
            return OpenAILLM(api_key=api_key, model=model)
        elif provider == 'llama':
            if not api_base or not model:
                raise ValueError("Para Llama/Ollama, 'api_base' e 'model' são obrigatórios no llm_config.yaml")
            return LlamaOllamaLLM(api_base=api_base, model=model)
        else:
            raise ValueError(f"Provedor LLM desconhecido ou não configurado: {provider}")

    async def get_response(self, prompt: str, **kwargs) -> str:
        if not self.llm_service:
            raise RuntimeError("Serviço LLM não inicializado corretamente.")
        return await self.llm_service.generate_response(prompt, **kwargs)


class ChatRequest(BaseModel):
    prompt: str
    # Adicione outros campos como conversation_id, user_id, etc., se necessário
    # Exemplo: conversation_id: str | None = None

router = APIRouter()
llm_gateway_instance = LLMGateway() # Instancia o gateway para ser usado pelo endpoint

@router.post("/chat/invoke", summary="Invoke LLM for chat completion")
async def chat_invoke(chat_request: ChatRequest):
    """
    Receives a prompt and returns the LLM's response.
    """
    try:
        # Aqui você pode adicionar lógica para passar mais parâmetros para o get_response
        # como temperature, max_tokens, etc., vindos do request.kwargs se existirem.
        response = await llm_gateway_instance.get_response(chat_request.prompt)
        return {"response": response}
    except RuntimeError as e:
        print(f"Erro no gateway: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e: # Captura erros de configuração do LLMGateway
        print(f"Erro no gateway 2: {e}")
        raise HTTPException(status_code=500, detail=f"LLM Configuration Error: {str(e)}")
    except Exception as e:
        # Log a exceção aqui para depuração
        print(f"Erro no gateway3: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Exemplo de uso (requer llm_config.yaml configurado e dependências instaladas):
# async def main():
#     gateway = LLMGateway()
#     response = await gateway.get_response("Qual a capital da França?")
#     print(response)
# 
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())