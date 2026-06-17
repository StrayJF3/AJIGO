import boto3
import os
import uuid
from fastapi import UploadFile

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

async def subir_comprobante(archivo: UploadFile) -> str:
    """
    Sube el comprobante al S3 y devuelve la URL pública.
    """
    extension = archivo.filename.split(".")[-1]
    nombre_unico = f"comprobantes/{uuid.uuid4()}.{extension}"

    contenido = await archivo.read()

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=nombre_unico,
        Body=contenido,
        ContentType=archivo.content_type
    )

    url = f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{nombre_unico}"
    return url