import logging
from pathlib import Path
from typing import ClassVar

import aiofiles
from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)


class LocalFileStorage:
    # Разрешенные типы файлов
    ALLOWED_EXTENSIONS: ClassVar[set[str]] = {".jpg", ".jpeg", ".png", ".webp"}
    # Максимальный размер файла (10MB)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024

    def __init__(self, base_path: str = "data/locations") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _validate_file(self, file: UploadFile) -> None:
        """Проверяет тип и размер файла"""
        # Проверяем расширение
        ext = Path(file.filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(self.ALLOWED_EXTENSIONS)}",
            )

        # Проверяем размер файла
        file.file.seek(0, 2)  # Перемещаемся в конец файла
        size = file.file.tell()  # Получаем текущую позицию (размер)
        file.file.seek(0)  # Возвращаемся в начало

        if size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Размер файла превышает максимально допустимый ({self.MAX_FILE_SIZE // 1024 // 1024}MB)",
            )

    async def save_file(self, file: UploadFile, location_id: str, photo_id: str) -> str:
        """Сохраняет файл в локальное хранилище и возвращает путь для доступа к файлу"""
        try:
            # Валидируем файл
            self._validate_file(file)

            # Создаем папку для файлов локации, если её нет
            folder_path = self.base_path / str(location_id)
            folder_path.mkdir(parents=True, exist_ok=True)

            # Используем photo_id и расширение оригинального файла
            file_ext = Path(file.filename).suffix.lower()
            file_name = f"{photo_id}{file_ext}"
            file_path = folder_path / file_name

            # Сохраняем файл
            async with aiofiles.open(file_path, "wb") as out_file:
                while True:
                    content = await file.read(1024)
                    if not content:
                        break
                    await out_file.write(content)

            logger.info(f"Файл {file.filename} успешно сохранен как {file_path}")

            # Возвращаем путь для доступа к файлу через API
            return f"/static/locations/{location_id}/{file_name}"

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {file.filename}: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при сохранении файла {file.filename}: {e!s}",
            )

    async def delete_file(self, location_id: str, photo_id: str) -> None:
        """Удаляет файл из локального хранилища"""
        try:
            # Формируем путь к директории с фото
            photo_dir = self.base_path / location_id

            if not photo_dir.exists():
                logger.warning(f"Директория {photo_dir} не существует")
                return

            # Находим файл по photo_id
            for file_path in photo_dir.glob(f"{photo_id}.*"):
                if file_path.is_file():
                    file_path.unlink()
                    logger.info(f"Файл {file_path} успешно удален")

                    # Проверяем, пуста ли директория
                    if not any(photo_dir.iterdir()):
                        photo_dir.rmdir()
                        logger.info(f"Пустая директория {photo_dir} удалена")
                    return

            logger.warning(f"Файл с id {photo_id} не найден в {photo_dir}")

        except Exception as e:
            logger.error(f"Ошибка при удалении файла: {e!s}")
            raise
