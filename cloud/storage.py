import boto3
from azure.storage.blob import BlobServiceClient
from fastapi import UploadFile
from abc import ABC, abstractmethod

class ICloudStorage(ABC):
    @abstractmethod
    def upload_file(self, bucket_name: str, file_name: str, file_content: bytes) -> str:
        pass

    @abstractmethod
    def generate_presigned_url(self, bucket_name: str, file_name: str, expiration: int = 3600) -> str:
        pass

class AWSStorage(ICloudStorage):
    def __init__(self, access_key: str, secret_key: str, region_name: str = 'us-east-1'):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name
        )

    def upload_file(self, bucket_name: str, file_name: str, file_content: bytes) -> str:
        try:
            self.s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
            return f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        except Exception as e:
            print(f"Erro ao fazer upload para AWS S3: {e}")
            raise

    def generate_presigned_url(self, bucket_name: str, file_name: str, expiration: int = 3600) -> str:
        try:
            response = self.s3_client.generate_presigned_url('get_object',
                                                            Params={'Bucket': bucket_name,
                                                                    'Key': file_name},
                                                            ExpiresIn=expiration)
            return response
        except Exception as e:
            print(f"Erro ao gerar URL pré-assinada para AWS S3: {e}")
            raise

class AzureStorage(ICloudStorage):
    def __init__(self, conn_str: str):
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        except Exception as e:
            print(f"Erro ao conectar ao Azure Blob Storage: {e}")
            raise

    def upload_file(self, bucket_name: str, file_name: str, file_content: bytes) -> str:
        try:
            blob_client = self.blob_service_client.get_blob_client(container=bucket_name, blob=file_name)
            blob_client.upload_blob(file_content, overwrite=True)
            return blob_client.url
        except Exception as e:
            print(f"Erro ao fazer upload para Azure Blob Storage: {e}")
            raise

    def generate_presigned_url(self, bucket_name: str, file_name: str, expiration: int = 3600) -> str:
        print(f"Gerando URL pré-assinada para {file_name} no Azure (simulado)")
        blob_client = self.blob_service_client.get_blob_client(container=bucket_name, blob=file_name)
        return blob_client.url

class GCPStorage(ICloudStorage):
    def __init__(self, credentials_path: str = None):
        from google.cloud import storage
        if credentials_path:
            self.storage_client = storage.Client.from_service_account_json(credentials_path)
        else:
            self.storage_client = storage.Client()

    def upload_file(self, bucket_name: str, file_name: str, file_content: bytes) -> str:
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(file_content)
        return blob.public_url

    def generate_presigned_url(self, bucket_name: str, file_name: str, expiration: int = 3600) -> str:
        import datetime
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        url = blob.generate_signed_url(expiration=datetime.timedelta(seconds=expiration), method='GET')
        return url

class CloudStorageFactory:
    @staticmethod
    def get_storage_service(provider: str, config: dict) -> ICloudStorage:
        if provider == "aws":
            return AWSStorage(access_key=config.get('aws_access_key_id'), 
                              secret_key=config.get('aws_secret_access_key'),
                              region_name=config.get('aws_region_name', 'us-east-1'))
        elif provider == "azure":
            return AzureStorage(conn_str=config.get('azure_connection_string'))
        elif provider == "gcp":
            return GCPStorage(credentials_path=config.get('gcp_credentials_path'))
        else:
            raise ValueError(f"Provedor de nuvem desconhecido: {provider}")

# Exemplo de uso (requer configuração adequada):
# config_aws = {'aws_access_key_id': 'YOUR_KEY', 'aws_secret_access_key': 'YOUR_SECRET'}
# aws_storage = CloudStorageFactory.get_storage_service('aws', config_aws)
# aws_storage.upload_file('meu-bucket-teste', 'meu_arquivo.txt', b'Ola mundo S3')

# config_azure = {'azure_connection_string': 'YOUR_AZURE_CONN_STRING'}
# azure_storage = CloudStorageFactory.get_storage_service('azure', config_azure)
# azure_storage.upload_file('meu-container-teste', 'meu_arquivo_azure.txt', b'Ola mundo Azure')