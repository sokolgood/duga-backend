import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile


class S3Service:
    def __init__(self, s3_params: dict, s3_bucket: str) -> None:
        self.s3_client = boto3.client(**s3_params)
        self.bucket_name = s3_bucket

    async def upload_file(self, file: UploadFile, path: str) -> str:
        """Загружает фото в S3 и возвращает URL"""
        try:
            await self.s3_client.upload_fileobj(file.file, self.bucket_name, path)

            # url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{path}"
            # return url
        except ClientError as e:
            # TODO: добавить специальное исключение для ошибок S3
            raise Exception(f"Ошибка загрузки файла в S3: {e!s}")

    async def delete_file(self, path: str) -> None:
        """Удаляет фото из S3"""
        try:
            await self.s3_client.delete_object(Bucket=self.bucket_name, Key=path)
        except ClientError:
            # Возможно, стоит просто залогировать ошибку, если файл не найден
            pass
