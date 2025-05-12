from fastapi import FastAPI, Request, File, UploadFile, HTTPException, status
from pydantic import BaseModel
import shutil
import os

UPLOAD_DIR = "./temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app_bot = FastAPI(
    title="Bot Framework Webhook Handler",
    description="Recebe e processa webhooks de plataformas de Bot (Teams, Slack, Discord)",
    version="0.1.0"
)

class WebhookPayload(BaseModel):
    platform: str
    user_id: str
    text: str = None

@app_bot.post("/webhook/{platform}", summary="Recebe webhooks de bots")
async def handle_webhook(platform: str, request: Request, payload: WebhookPayload = None):
    if platform.lower() not in ["teams", "slack", "discord"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plataforma '{platform}' não suportada.")

    if not payload:
        try:
            payload_data = await request.json()
            print(f"Webhook recebido de {platform} (JSON bruto): {payload_data}")
            return {"status": "received", "platform": platform, "message": "Payload JSON genérico recebido. Adapte o parsing."}

        except Exception as e:
            print(f"Erro ao processar payload JSON do webhook de {platform}: {e}")
            pass

    if payload:
        print(f"Webhook recebido de {platform}: User {payload.user_id} disse '{payload.text}'")
        response_message = f"Recebido de {platform}: '{payload.text}' por {payload.user_id}"
        return {"status": "received", "platform": platform, "response": response_message}
    
    return {"status": "received_empty_payload", "platform": platform, "message": "Webhook recebido, mas sem payload Pydantic claro. Verifique o log para JSON bruto."}

@app_bot.post("/webhook/{platform}/upload", summary="Recebe webhooks com upload de arquivos")
async def handle_webhook_upload(
    platform: str, 
    request: Request,
    file: UploadFile = File(None)
):
    if platform.lower() not in ["teams", "slack", "discord"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plataforma '{platform}' não suportada.")

    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum arquivo enviado.")

    allowed_extensions = {".csv", ".xlsx"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo de arquivo '{file_ext}' não suportado. Apenas CSV e XLSX são permitidos.")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        print(f"Arquivo '{file.filename}' de {platform} salvo em {file_location}")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao salvar o arquivo: {e}")
    finally:
        pass

    return {
        "status": "file_received", 
        "platform": platform, 
        "filename": file.filename, 
        "content_type": file.content_type,
        "saved_path": file_location
    }

# Para integrar este app_bot ao app principal do core_service/main.py:
# No main.py:
# from bot_framework.webhook import app_bot as bot_webhook_app
# app.mount("/bot", bot_webhook_app) # Monta o app do bot sob o prefixo /bot

# Exemplo de como rodar standalone para teste (se necessário):
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app_bot, host="0.0.0.0", port=8001)