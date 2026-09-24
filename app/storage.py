import boto3
from botocore.exceptions import ClientError
from app.config import settings

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,  # http://minio:9000
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    )

def upload_file_to_s3(file_bytes: bytes, bucket_name: str, object_name: str) -> str:
    s3_client = get_s3_client()
    try:
        s3_client.put_object(Body=file_bytes, Bucket=bucket_name, Key=object_name)
        return f"{bucket_name}/{object_name}"
    except ClientError as e:
        raise RuntimeError(f"Ошибка загрузки в S3: {e}")

def download_file_from_s3(bucket_name: str, object_name: str) -> bytes:
    s3_client = get_s3_client()
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        return response["Body"].read()
    except ClientError as e:
        raise RuntimeError(f"Ошибка скачивания из S3: {e}")