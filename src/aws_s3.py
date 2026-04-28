import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
import uuid
import logging

from config import settings

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def upload_file_to_s3(file_bytes: bytes, original_filename: str, content_type: str) -> str:
    unique_filename = f"{uuid.uuid4()}-{original_filename}"
    try:
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=unique_filename,
            Body=file_bytes,
            ContentType=content_type
        )
        return unique_filename 
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        
        logger.error(f"Falha de integracao S3 no upload. Código AWS: {error_code}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao fazer upload do documento para a nuvem."
        )
    
def generate_presigned_url(object_name, expiration=3600):
    """Gera uma URL temporária para download do arquivo no S3"""
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': object_name},
            ExpiresIn=expiration
        )
        return response
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        logger.error(f"Falha de integracao S3 na geracao de URL. Código AWS: {error_code}")
        return None
        
    except Exception:
        logger.error("Erro interno critico ao tentar assinar a URL do S3.")
        return None