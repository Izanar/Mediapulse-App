import os
import uuid
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from app.config import settings


def get_s3_client():
    """Возвращает инициализированный клиент S3/MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    )


def upload_file_to_s3(file_bytes: bytes, bucket_name: str, object_name: str) -> str:
    """Загружает байты файла в S3."""
    s3_client = get_s3_client()
    try:
        s3_client.put_object(Body=file_bytes, Bucket=bucket_name, Key=object_name)
        return f"{bucket_name}/{object_name}"
    except ClientError as e:
        raise RuntimeError(f"Ошибка загрузки в S3: {e}")


def download_file_from_s3(bucket_name: str, object_name: str) -> bytes:
    """Скачивает объект из S3."""
    s3_client = get_s3_client()
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        return response["Body"].read()
    except ClientError as e:
        raise RuntimeError(f"Ошибка скачивания из S3: {e}")


def delete_file_from_s3(bucket_name: str, object_name: str) -> None:
    """Удаляет объект из S3 по ключу."""
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
    except ClientError as e:
        raise RuntimeError(f"Ошибка удаления из S3: {e}")


def generate_s3_paths(username: str, user_filename: str, filename: str) -> tuple[str, str, str]:
    """
    Генерирует чистые пути S3 БЕЗ промежуточных подпапок:
    - original/{username}.{safe_user_filename}.{date}__{uuid_short}.ext
    - changed/{username}.{safe_user_filename}.invert.{date}__{uuid_short}.ext
    """
    date_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    uuid_short = str(uuid.uuid4())[:8]
    ext = os.path.splitext(filename)[1].lower() or ".jpg"

    # Безопасная очистка имени файла
    stem = os.path.splitext(user_filename)[0]
    safe_user_filename = "".join(
        c if c.isalnum() or c in ("_", "-") else "_" for c in stem
    )

    storage_path = f"original/{username}_{safe_user_filename}_{date_str}__{uuid_short}{ext}"
    processed_path = f"changed/{username}_{safe_user_filename}_invert_{date_str}__{uuid_short}{ext}"

    return storage_path, processed_path, ext