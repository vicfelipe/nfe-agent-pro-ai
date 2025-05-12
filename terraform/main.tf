# Arquivo principal do Terraform para o NF Agent Pro

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Variáveis para configuração do provedor e recursos
variable "cloud_provider" {
  description = "Provedor de nuvem a ser usado (aws, azure, gcp)"
  type        = string
  default     = "aws"
}

variable "db_type" {
  description = "Tipo de banco de dados (postgresql, mongodb)"
  type        = string
  default     = "postgresql"
}

variable "aws_region" {
  description = "Região AWS para implantar os recursos"
  type        = string
  default     = "us-east-1"
}

# Configuração do provedor (exemplo para AWS)
provider "aws" {
  region = var.aws_region
  # As credenciais devem ser configuradas via variáveis de ambiente ou perfis AWS
}

# Adicionar aqui as definições de recursos para S3, RDS/DocumentDB, etc.
# Exemplo de um bucket S3 (simplificado)
resource "aws_s3_bucket" "nf_agent_uploads" {
  count = var.cloud_provider == "aws" ? 1 : 0
  bucket = "nf-agent-uploads-${random_id.bucket_suffix.hex}" # Nome do bucket único

  tags = {
    Name        = "NF Agent Pro Uploads"
    Environment = "MVP"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}

# Adicionar configurações para Azure e GCP condicionalmente ou em módulos separados.

output "s3_bucket_name" {
  description = "Nome do bucket S3 criado para uploads."
  value       = var.cloud_provider == "aws" ? aws_s3_bucket.nf_agent_uploads[0].id : "N/A (Não é AWS)"
}

# Placeholder para outros recursos (ex: banco de dados, instâncias de computação)
# Lembre-se de adicionar recursos para Azure e GCP conforme necessário.