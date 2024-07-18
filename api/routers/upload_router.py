import asyncio
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from utils.aws_services import AWSS3
import os

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/upload", operation_id="upload")
async def upload(files: list[UploadFile] = File(...)):
    """
    Upload a file on S3

    """
    try:
        s3 = AWSS3(os.getenv('AWS_S3_BUCKET_NAME'))
        for file in files:
            await s3.upload_file(file.file, file.filename)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Error uploading file")
    