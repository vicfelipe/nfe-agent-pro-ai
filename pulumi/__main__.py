# Arquivo principal do Pulumi para o NF Agent Pro

import pulumi
import pulumi_aws as aws
import pulumi_azure_native as azure_native
import pulumi_gcp as gcp

# Carregar configurações do projeto Pulumi (ex: Pulumi.dev.yaml)
config = pulumi.Config()

cloud_provider = config.get("cloud_provider") or "aws"
db_type = config.get("db_type") or "postgresql"

if cloud_provider == "aws":
    # Exemplo de criação de um bucket S3 com Pulumi
    bucket = aws.s3.Bucket("nf-agent-uploads-pulumi",
        bucket=f"nf-agent-uploads-pulumi-{pulumi.get_stack()}",
        acl="private",
        tags={
            "Environment": "MVP",
            "Name": "NF Agent Pro Uploads Pulumi",
        })
    pulumi.export("aws_s3_bucket_name", bucket.id)

elif cloud_provider == "azure":
    # Exemplo de criação de um Storage Account e Container no Azure com Pulumi
    resource_group = azure_native.resources.ResourceGroup("nf-agent-rg")

    storage_account = azure_native.storage.StorageAccount("nfagentstorage",
        resource_group_name=resource_group.name,
        sku=azure_native.storage.SkuArgs(
            name=azure_native.storage.SkuName.STANDARD_LRS,
        ),
        kind=azure_native.storage.Kind.STORAGE_V2)

    blob_container = azure_native.storage.BlobContainer("nfagentuploadscontainer",
        account_name=storage_account.name,
        resource_group_name=resource_group.name,
        public_access=azure_native.storage.PublicAccess.NONE)
    
    pulumi.export("azure_storage_account_name", storage_account.name)
    pulumi.export("azure_blob_container_name", blob_container.name)

elif cloud_provider == "gcp":
    # Exemplo de criação de um bucket no GCP com Pulumi
    gcp_bucket = gcp.storage.Bucket("nf-agent-uploads-gcp",
        name=f"nf-agent-uploads-gcp-{pulumi.get_project()}-{pulumi.get_stack()}",
        location="US") # Escolha a localização apropriada
    
    pulumi.export("gcp_bucket_name", gcp_bucket.url)

else:
    pulumi.log.warn(f"Provedor de nuvem '{cloud_provider}' não suportado ou não configurado para Pulumi.")

# Adicionar aqui definições de recursos para bancos de dados, serviços de computação, etc.
# Lembre-se de que as credenciais para cada provedor devem ser configuradas
# de acordo com as práticas recomendadas pelo Pulumi (ex: variáveis de ambiente, secrets manager).

# Para executar:
# pulumi stack init dev  (se ainda não existir um stack)
# pulumi config set cloud_provider aws  (ou azure, gcp)
# pulumi up