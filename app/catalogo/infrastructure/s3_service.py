import boto3
import os
import uuid
# pyrefly: ignore [missing-import]
from fastapi import UploadFile

# CLIENTE S3 CONFIGURADO CON LAS CREDENCIALES DEL ENTORNO
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

async def subir_imagen(archivo: UploadFile, carpeta: str = "imagenes") -> str:
    """
    Sube cualquier imagen al bucket S3 en la carpeta indicada.
    Devuelve la URL pública del objeto subido.
    """
    extension = archivo.filename.split(".")[-1]
    nombre_unico = f"{carpeta}/{uuid.uuid4()}.{extension}"

    contenido = await archivo.read()

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=nombre_unico,
        Body=contenido,
        ContentType=archivo.content_type
    )

    region = os.getenv("AWS_REGION", "us-east-1")
    url = f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{nombre_unico}"
    return url
