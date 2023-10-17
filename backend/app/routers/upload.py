import logging
import tempfile

import aiofiles
from app.libs.b2 import b2_upload_file
from fastapi import APIRouter, HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

router = APIRouter()

# flow for file lifecycle:
# 1. user uploads file to backend
# 2. temporary stor file in "tempfile"
# 3. backend uploads file to b2
# 4. backend deletes "tempfile"

# for receiving the file:
# - client splits up file in chunks of 1 MB
# - client sends chunks one at a time
# - client sends the last chunk
# - then backend starts upload to backend

CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.post("/upload", status_code=201)
async def upload_file(file: UploadFile):
    """Uploads a file to b2"""
    try:
        with tempfile.NamedTemporaryFile() as temp_file:
            filename = temp_file.name
            logger.info(
                "Saving file to temporary location", extra={"filename": filename}
            )
            async with aiofiles.open(filename, "wb") as f:
                # keep reading all the chunks of the file until last chunk
                while chunk := await file.read(CHUNK_SIZE):
                    # when all chnuks are read, write them to the temporary file
                    await f.write(chunk)
            file_url = b2_upload_file(local_file=filename, file_name=file.filename)
            # Usage example:
            # user.profile_picture_url = file_url
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        )

    return {
        "detail": f"Successfully uploaded file {file.filename}",
        "file_url": file_url,
    }
