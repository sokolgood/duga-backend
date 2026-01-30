import pytest
from fastapi import HTTPException, UploadFile

from src.services.file_storage import LocalFileStorage


class TestLocalFileStorage:
    def test_init(self, mock_file_storage_path):
        storage = LocalFileStorage(base_path=str(mock_file_storage_path))
        assert storage.base_path == mock_file_storage_path

    def test_validate_file_valid(self, mock_file_storage_path, mock_upload_file):
        storage = LocalFileStorage(base_path=str(mock_file_storage_path))
        storage._validate_file(mock_upload_file)

    def test_validate_file_invalid_extension(self, mock_file_storage_path, tmp_path):
        file_path = tmp_path / "test.txt"
        file_path.write_bytes(b"content")
        file_obj = open(file_path, "rb")
        file = UploadFile(filename="test.txt", file=file_obj)
        try:
            storage = LocalFileStorage(base_path=str(mock_file_storage_path))
            with pytest.raises(HTTPException) as exc_info:
                storage._validate_file(file)
            assert exc_info.value.status_code == 400
        finally:
            file_obj.close()

    def test_validate_file_too_large(self, mock_file_storage_path, tmp_path):
        file_path = tmp_path / "test.jpg"
        large_content = b"x" * (11 * 1024 * 1024)
        file_path.write_bytes(large_content)
        file_obj = open(file_path, "rb")
        file = UploadFile(filename="test.jpg", file=file_obj)
        try:
            storage = LocalFileStorage(base_path=str(mock_file_storage_path))
            with pytest.raises(HTTPException) as exc_info:
                storage._validate_file(file)
            assert exc_info.value.status_code == 400
        finally:
            file_obj.close()

    @pytest.mark.asyncio
    async def test_save_file(self, mock_file_storage_path, mock_upload_file):
        storage = LocalFileStorage(base_path=str(mock_file_storage_path))
        location_id = "test-location-id"
        photo_id = "test-photo-id"

        result = await storage.save_file(mock_upload_file, location_id, photo_id)

        assert result.startswith("/static/locations/")
        assert location_id in result
        assert photo_id in result

        saved_file = mock_file_storage_path / location_id / f"{photo_id}.jpg"
        assert saved_file.exists()

    @pytest.mark.asyncio
    async def test_save_file_creates_directory(self, mock_file_storage_path, mock_upload_file):
        storage = LocalFileStorage(base_path=str(mock_file_storage_path))
        location_id = "test-location-id"
        photo_id = "test-photo-id"

        await storage.save_file(mock_upload_file, location_id, photo_id)

        location_dir = mock_file_storage_path / location_id
        assert location_dir.exists()
        assert location_dir.is_dir()

    @pytest.mark.asyncio
    async def test_delete_file(self, mock_file_storage_path, mock_upload_file):
        storage = LocalFileStorage(base_path=str(mock_file_storage_path))
        location_id = "test-location-id"
        photo_id = "test-photo-id"

        await storage.save_file(mock_upload_file, location_id, photo_id)
        await storage.delete_file(location_id, photo_id)

        saved_file = mock_file_storage_path / location_id / f"{photo_id}.jpg"
        assert not saved_file.exists()

    @pytest.mark.asyncio
    async def test_delete_file_nonexistent(self, mock_file_storage_path):
        storage = LocalFileStorage(base_path=str(mock_file_storage_path))
        location_id = "test-location-id"
        photo_id = "test-photo-id"

        await storage.delete_file(location_id, photo_id)

    @pytest.mark.asyncio
    async def test_delete_file_removes_empty_directory(self, mock_file_storage_path, mock_upload_file):
        storage = LocalFileStorage(base_path=str(mock_file_storage_path))
        location_id = "test-location-id"
        photo_id = "test-photo-id"

        await storage.save_file(mock_upload_file, location_id, photo_id)
        await storage.delete_file(location_id, photo_id)

        location_dir = mock_file_storage_path / location_id
        assert not location_dir.exists()
